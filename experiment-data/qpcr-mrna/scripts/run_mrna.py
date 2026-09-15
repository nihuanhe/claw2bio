"""
mRNA qPCR ΔΔCt 计算与绘图脚本
=============================
输入格式：Target, Sample, Rep1, Rep2, Rep3
参考基因行也按同样格式放入 CSV（默认 GAPDH，可用 --ref-targets 指定）。

对每个 Target（除参考基因外）：
  ΔCt_i    = Ct_target_rep_i - mean(Ct_ref_rep_i)
  ΔΔCt_i   = ΔCt_i - mean(ΔCt_of_control_group)
  Fold_i   = 2^(-ΔΔCt_i)

统计：
  2 组：独立样本 t-test
  ≥3 组：One-way ANOVA + Dunnett（各处理组 vs 对照组）

输出：
  <name>.csv：原表 + Fold 相关列
  <name>_<target>_barplot.png：每个 Target 一张 300 dpi 柱状图
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

# 重定向 matplotlib 缓存，避免访问用户主目录下的 .matplotlib
if "MPLCONFIGDIR" not in os.environ:
    os.environ["MPLCONFIGDIR"] = os.path.join(
        tempfile.gettempdir(), ".mpl-cache-qpcr-mrna"
    )

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ------------------------------------------------------------
# 配色与布局参数
# ------------------------------------------------------------

BAR_COLORS = [
    "#009E73",
    "#CC79A7",
    "#56B4E9",
    "#E69F00",
    "#0072B2",
    "#D55E00",
    "#F0E442",
    "#999999",
]
POINT_COLORS = [
    "#80FFD7",
    "#EBC8E1",
    "#B3D9F7",
    "#F5D5A3",
    "#9BC9E3",
    "#EAB8A8",
    "#F7F2A8",
    "#CCCCCC",
]

BAR_COLORS_3 = ["#0072B2", "#D55E00", "#009E73"]
POINT_COLORS_3 = ["#80FFFF", "#EDA461", "#90EE90"]

BAR_COLORS_6 = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9"]
POINT_COLORS_6 = ["#80FFFF", "#EDA461", "#90EE90", "#D683F1", "#FAD7A0", "#A8E6FF"]

Y_LABEL_DEFAULT = "Relative mRNA expression (Fold change)"
DPI_DEFAULT = 300


# ------------------------------------------------------------
# 工具函数
# ------------------------------------------------------------

def p_to_star(p):
    """P 值转星号标记。"""
    if pd.isna(p):
        return ""
    if p < 0.001:
        return "***"
    elif p < 0.01:
        return "**"
    elif p < 0.05:
        return "*"
    else:
        return "ns"


def auto_yticks(all_values, max_with_error):
    """自动选择 0 起始、≤6 个刻度的 Y 轴。"""
    all_max = max(np.nanmax(all_values), max_with_error)
    if np.isnan(all_max) or all_max <= 0:
        all_max = 1.0

    nice_steps = [
        0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5,
        1, 2, 3, 4, 5, 10, 20, 50, 100, 200, 500, 1000,
    ]
    step = nice_steps[-1]
    y_max = None
    for s in nice_steps:
        candidate = np.ceil(all_max / s) * s
        n_ticks = int(round(candidate / s)) + 1
        if 3 <= n_ticks <= 6:
            step = s
            y_max = candidate
            break
    if y_max is None:
        y_max = np.ceil(all_max / step) * step
    yticks = np.arange(0, y_max + step * 0.001, step)
    return yticks, y_max


def read_raw_csv(csv_path):
    """读取 CSV 并校验必需列。"""
    df = pd.read_csv(csv_path)
    required = ["Target", "Sample", "Rep1", "Rep2", "Rep3"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"缺少必需列: {missing}")
    df = df[required].copy()
    for col in ["Rep1", "Rep2", "Rep3"]:
        df[col] = pd.to_numeric(df[col].replace("", np.nan), errors="coerce")
    return df


def parse_ref_targets(ref_arg):
    """解析逗号分隔的参考基因名列表。"""
    return [x.strip() for x in ref_arg.split(",") if x.strip()]


def find_ref_rows(df, ref_targets):
    """根据参考基因名找到对应行（大小写不敏感）。返回 ref_names 的实际大小写集合。"""
    lower_map = {str(t).lower(): t for t in df["Target"].unique()}
    actual = set()
    for rt in ref_targets:
        if rt.lower() in lower_map:
            actual.add(lower_map[rt.lower()])
    return actual


def compute_fold_changes(df, ref_names, control_sample):
    """计算 ΔCt、ΔΔCt、Fold change，并追加到 df。"""
    # 数值列初始化为 NaN，文本列初始化为空字符串（避免 pandas dtype 警告）
    numeric_cols = [
        "Delta_Ct_Rep1", "Delta_Ct_Rep2", "Delta_Ct_Rep3",
        "Fold_Rep1", "Fold_Rep2", "Fold_Rep3",
        "Fold_Mean", "Fold_SD", "P_Value",
    ]
    text_cols = ["Stat_Test", "Significance", "Skip_Reason"]
    for col in numeric_cols:
        df[col] = np.nan
    for col in text_cols:
        df[col] = ""

    # 构建 (Target, Sample) -> reps 字典
    ct_dict = df.set_index(["Target", "Sample"])[["Rep1", "Rep2", "Rep3"]].to_dict("index")

    def get_reps(target, sample):
        key = (target, sample)
        if key not in ct_dict:
            return np.array([np.nan, np.nan, np.nan])
        row = ct_dict[key]
        return np.array([row["Rep1"], row["Rep2"], row["Rep3"]], dtype=float)

    # 每个 Sample 的参考基因 Ct（按 rep 取几何/算术平均）
    samples = df["Sample"].unique()
    sample_ref_mean = {}
    for sample in samples:
        ref_reps = []
        for ref in ref_names:
            reps = get_reps(ref, sample)
            if not np.isnan(reps).all():
                ref_reps.append(reps)
        if not ref_reps:
            sample_ref_mean[sample] = np.array([np.nan, np.nan, np.nan])
        else:
            # 多内参：同一 rep 下多个内参的算术平均
            sample_ref_mean[sample] = np.nanmean(np.array(ref_reps), axis=0)

    # 对照组存在性检查
    if control_sample not in samples:
        raise ValueError(f"指定的对照组 '{control_sample}' 不在 Sample 列中")

    targets = [t for t in df["Target"].unique() if t not in ref_names]

    for target in targets:
        sub_idx = df["Target"] == target
        sub_df = df.loc[sub_idx].copy()

        # 检查缺失值
        if sub_df[["Rep1", "Rep2", "Rep3"]].isnull().any().any():
            df.loc[sub_idx, "Skip_Reason"] = "Target 存在缺失 Ct 值"
            continue

        target_samples = sub_df["Sample"].tolist()
        delta_ct = np.zeros((len(target_samples), 3))
        valid = True
        for i, sample in enumerate(target_samples):
            reps = get_reps(target, sample)
            ref = sample_ref_mean.get(sample)
            if ref is None or np.isnan(ref).any() or np.isnan(reps).any():
                valid = False
                break
            delta_ct[i, :] = reps - ref

        if not valid:
            df.loc[sub_idx, "Skip_Reason"] = "参考基因或 Target 重复值缺失/不匹配"
            continue

        # 对照组平均 ΔCt
        ctrl_idx = target_samples.index(control_sample)
        ctrl_delta_mean = np.mean(delta_ct[ctrl_idx, :])
        delta_delta_ct = delta_ct - ctrl_delta_mean
        fold = 2.0 ** (-delta_delta_ct)

        for i, idx in enumerate(sub_df.index):
            df.at[idx, "Delta_Ct_Rep1"] = np.round(delta_ct[i, 0], 2)
            df.at[idx, "Delta_Ct_Rep2"] = np.round(delta_ct[i, 1], 2)
            df.at[idx, "Delta_Ct_Rep3"] = np.round(delta_ct[i, 2], 2)
            df.at[idx, "Fold_Rep1"] = np.round(fold[i, 0], 2)
            df.at[idx, "Fold_Rep2"] = np.round(fold[i, 1], 2)
            df.at[idx, "Fold_Rep3"] = np.round(fold[i, 2], 2)
            df.at[idx, "Fold_Mean"] = np.round(np.mean(fold[i, :]), 2)
            df.at[idx, "Fold_SD"] = np.round(np.std(fold[i, :], ddof=1), 2)

        # 统计
        try:
            stat_test, p_values, anova_p = perform_statistics(fold)
        except Exception as e:
            df.loc[sub_idx, "Skip_Reason"] = f"统计检验失败: {e}"
            continue

        for i, idx in enumerate(sub_df.index):
            df.at[idx, "Stat_Test"] = stat_test
            df.at[idx, "P_Value"] = p_values[i]
            df.at[idx, "Significance"] = p_to_star(p_values[i])

    return df


def perform_statistics(fold):
    """按组数选择统计方法。fold: (n_groups, 3)。"""
    n_groups = fold.shape[0]
    fold_list = [fold[i, :] for i in range(n_groups)]

    if n_groups == 2:
        stat_test = "t-test"
        _, p_val = stats.ttest_ind(fold_list[0], fold_list[1])
        p_values = [np.nan, p_val]
        anova_p = np.nan
    else:
        stat_test = "One-way ANOVA + Dunnett"
        _, anova_p = stats.f_oneway(*fold_list)
        control_sample = fold_list[0]
        treatment_samples = fold_list[1:]
        res = stats.dunnett(*treatment_samples, control=control_sample)
        p_values = [np.nan] + list(res.pvalue)

    return stat_test, p_values, anova_p


def safe_filename(name):
    """把 Target 名转成安全的文件名字符串。"""
    return str(name).replace(" ", "_").replace("/", "_").replace("\\", "_")


def plot_target(target, samples, fold, p_values, anova_p, stat_test, output_png,
                figure_name, y_label=Y_LABEL_DEFAULT, dpi=DPI_DEFAULT):
    """绘制单个 Target 的柱状图。"""
    n_groups = len(samples)
    if n_groups == 0:
        return False

    means = [np.mean(fold[i, :]) for i in range(n_groups)]
    sds = [np.std(fold[i, :], ddof=1) for i in range(n_groups)]
    all_values = fold.ravel()
    max_with_error = max([m + s for m, s in zip(means, sds)])

    # 布局与颜色
    if n_groups == 2:
        fig, ax = plt.subplots(figsize=(5.3, 6))
        bar_width = 1.7 / 7
        x_pos = np.array([2 / 7, 5 / 7])
        colors = BAR_COLORS[:2]
        point_colors = POINT_COLORS[:2]
        left_margin = 0.198736
        right_margin = 0.744637
        bottom_margin = 0.120917
        top_margin = 0.903010
        xlim_max = 1.0
        jitter_std = 0.04
        fontsize_p = 14
    elif n_groups == 3:
        fig, ax = plt.subplots(figsize=(6.844187, 6))
        bar_width = 1.7 / 7
        x_pos = np.array([2 / 7 + i * 3 / 7 for i in range(n_groups)])
        colors = BAR_COLORS_3
        point_colors = POINT_COLORS_3
        left_margin = 0.068266
        right_margin = 0.820333
        bottom_margin = 0.064537
        top_margin = 0.975000
        xlim_max = 10 / 7
        jitter_std = 0.015
        fontsize_p = 14
    elif n_groups == 6:
        fig, ax = plt.subplots(figsize=(13.18, 6))
        bar_width = 1.7 / 7
        x_pos = np.array([2 / 7 + i * 3 / 7 for i in range(n_groups)])
        colors = BAR_COLORS_6
        point_colors = POINT_COLORS_6
        left_margin = 0.055
        right_margin = 0.798
        bottom_margin = 0.064537
        top_margin = 0.975000
        xlim_max = 19 / 7
        jitter_std = 0.015
        fontsize_p = 14
    else:
        extra_width = max(0, n_groups - 2) * 1.2
        fig, ax = plt.subplots(figsize=(5.3 + extra_width, 6))
        bar_width = 1.7 / 7
        x_pos = np.linspace(0.15, 0.85, n_groups)
        colors = BAR_COLORS[:n_groups]
        point_colors = POINT_COLORS[:n_groups]
        left_margin = 0.15
        right_margin = 0.88
        bottom_margin = 0.22
        top_margin = 0.88
        xlim_max = 1.0
        jitter_std = 0.04
        fontsize_p = 14

    yticks, y_max = auto_yticks(all_values, max_with_error)

    ax.bar(
        x_pos, means, width=bar_width,
        color=colors, alpha=0.9, edgecolor="black", linewidth=3,
    )
    ax.errorbar(
        x_pos, means, yerr=sds, fmt="none",
        capsize=8, elinewidth=3, capthick=3, ecolor="black",
    )

    for i in range(n_groups):
        np.random.seed(42 + i)
        jitter = np.random.normal(0, jitter_std, size=3)
        ax.scatter(
            x_pos[i] + jitter, fold[i, :],
            color=point_colors[i], edgecolor="black",
            s=200, zorder=5, alpha=0.9, linewidth=3,
        )

    # 显著性文字区
    p_lines = []
    if n_groups == 2:
        p = p_values[1]
        if p < 0.001:
            p_text = "***\nP < 0.001"
        elif p < 0.01:
            p_text = f"**\nP = {p:.3f}"
        elif p < 0.05:
            p_text = f"*\nP = {p:.3f}"
        else:
            p_text = f"P = {p:.3f}"
    else:
        if not np.isnan(anova_p):
            p_lines.append(f"ANOVA P = {anova_p:.4f}")
            p_lines.append("")
        for i in range(1, n_groups):
            p = p_values[i]
            if p < 0.05:
                p_lines.append(f"{samples[i]} vs {samples[0]}:")
                if p < 0.001:
                    p_lines.append("  *** P < 0.001")
                elif p < 0.01:
                    p_lines.append(f"  ** P = {p:.3f}")
                else:
                    p_lines.append(f"  * P = {p:.3f}")
        if n_groups == 6:
            label_y = 0.70
            label_fontsize = 7.5
            label_linespacing = 1.3
        else:
            label_y = 0.55
            label_fontsize = 10
            label_linespacing = 1.5
        if p_lines:
            p_text = "\n".join(p_lines)
        else:
            p_text = "ns"
        ax.text(
            1.03, label_y, p_text, transform=ax.transAxes,
            fontsize=label_fontsize, verticalalignment="center",
            fontfamily="Arial", fontweight="normal",
            linespacing=label_linespacing,
        )
        ax.text(
            1.03, 0.10, "Dunnett", transform=ax.transAxes,
            fontsize=10, fontfamily="Arial", verticalalignment="bottom",
        )
        p_text = None

    ax.set_ylabel(
        y_label, fontsize=16, fontfamily="Arial",
        fontweight="normal", labelpad=15,
    )
    ax.set_xticks(x_pos)
    ax.set_xticklabels(
        samples, fontsize=14, fontfamily="Arial",
        fontweight="normal", rotation=45, ha="right",
    )
    ax.set_yticks(yticks)
    ax.set_ylim(0, y_max)
    ax.set_xlim(0, xlim_max)

    ax.tick_params(axis="y", pad=10, labelsize=14, length=10, width=3)
    ax.tick_params(axis="x", length=10, width=3)

    for item in [ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels():
        item.set_fontfamily("Arial")
        item.set_fontweight("normal")

    if p_text is not None:
        ax.text(
            1.09, 0.5, p_text, transform=ax.transAxes,
            fontsize=fontsize_p, verticalalignment="center",
            fontfamily="Arial", fontweight="normal",
        )

    ax.text(
        0.5, 1.05, f"{target} ({figure_name})",
        transform=ax.transAxes, fontsize=16,
        fontfamily="Arial", fontweight="normal",
        horizontalalignment="center", verticalalignment="bottom",
    )

    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")
    ax.grid(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_linewidth(3)
    ax.spines["left"].set_linewidth(3)

    plt.subplots_adjust(
        left=left_margin, right=right_margin,
        bottom=bottom_margin, top=top_margin,
    )

    plt.savefig(output_png, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"  柱状图已保存: {output_png}")
    return True


def process_one(input_csv, output_dir, name, ref_targets, control_sample,
                y_label, dpi, overwrite):
    """处理单个 CSV。"""
    input_csv = Path(input_csv)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_csv = output_dir / f"{name}.csv"
    if output_csv.exists() and not overwrite:
        raise FileExistsError(
            f"输出 CSV 已存在: {output_csv}。使用 --overwrite 覆盖，或更换 --name。"
        )

    df = read_raw_csv(input_csv)
    ref_names = find_ref_rows(df, ref_targets)
    if not ref_names:
        raise ValueError(
            f"未在 CSV 的 Target 列中找到参考基因: {ref_targets}"
        )
    print(f"  识别到参考基因: {', '.join(ref_names)}")

    # 默认对照组为第一个出现的 Sample
    all_samples = df["Sample"].unique().tolist()
    if control_sample is None:
        control_sample = all_samples[0]
    print(f"  对照组: {control_sample}")

    df = compute_fold_changes(df, ref_names, control_sample)
    df.to_csv(output_csv, index=False, float_format="%.2f")
    print(f"  已保存 CSV: {output_csv}")

    # 为每个非参考 Target 绘图
    targets = [t for t in df["Target"].unique() if t not in ref_names]
    output_pngs = []
    for target in targets:
        sub_df = df[df["Target"] == target]
        if sub_df["Skip_Reason"].notna().any() and sub_df["Skip_Reason"].iloc[0]:
            print(f"  [跳过 Target={target}] {sub_df['Skip_Reason'].iloc[0]}")
            continue

        samples = sub_df["Sample"].tolist()
        fold = sub_df[["Fold_Rep1", "Fold_Rep2", "Fold_Rep3"]].to_numpy(dtype=float)
        p_values = sub_df["P_Value"].to_numpy(dtype=float)
        stat_test = sub_df["Stat_Test"].iloc[0]
        anova_p = np.nan
        if "ANOVA" in stat_test:
            # 从 Stat_Test 中解析 ANOVA P 值？这里只需知道是否 ANOVA。
            # 由于每个 Target 的 anova_p 未保存，重新计算一次代价低。
            fold_list = [fold[i, :] for i in range(fold.shape[0])]
            _, anova_p = stats.f_oneway(*fold_list)

        output_png = output_dir / f"{name}_{safe_filename(target)}_barplot.png"
        if output_png.exists() and not overwrite:
            print(f"  [跳过] 输出 PNG 已存在: {output_png}")
            continue

        plot_target(
            target=target,
            samples=samples,
            fold=fold,
            p_values=p_values,
            anova_p=anova_p,
            stat_test=stat_test,
            output_png=output_png,
            figure_name=name,
            y_label=y_label,
            dpi=dpi,
        )
        output_pngs.append(output_png)

    return output_csv, output_pngs


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="mRNA qPCR ΔΔCt 计算与柱状图生成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run_mrna.py examples/input/mrna-input.csv examples/output --name Figure1
  python run_mrna.py data.csv results --ref-targets GAPDH,ACTB --control Ctrl --overwrite
""",
    )
    parser.add_argument("input_csv", help="输入 CSV 路径")
    parser.add_argument(
        "output_dir", nargs="?", default=None,
        help="输出目录（默认与输入 CSV 同目录）",
    )
    parser.add_argument("--name", default=None, help="输出文件名前缀（默认使用输入 CSV 主干）")
    parser.add_argument(
        "--ref-targets", default="GAPDH",
        help="参考基因 Target 名，多个用逗号分隔（默认: GAPDH）",
    )
    parser.add_argument(
        "--control", default=None,
        help="对照组 Sample 名（默认 CSV 中第一个 Sample）",
    )
    parser.add_argument(
        "--y-label", default=Y_LABEL_DEFAULT,
        help=f"Y 轴标签（默认: {Y_LABEL_DEFAULT}）",
    )
    parser.add_argument("--dpi", type=int, default=DPI_DEFAULT, help="PNG 分辨率（默认 300）")
    parser.add_argument("--overwrite", action="store_true", help="覆盖已存在输出")
    args = parser.parse_args()

    input_csv = Path(args.input_csv).resolve()
    if not input_csv.exists():
        print(f"错误: 输入文件不存在: {input_csv}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir).resolve() if args.output_dir else input_csv.parent
    name = args.name if args.name else input_csv.stem
    ref_targets = parse_ref_targets(args.ref_targets)

    process_one(
        input_csv=input_csv,
        output_dir=output_dir,
        name=name,
        ref_targets=ref_targets,
        control_sample=args.control,
        y_label=args.y_label,
        dpi=args.dpi,
        overwrite=args.overwrite,
    )


if __name__ == "__main__":
    main()
