"""
mtDNA qPCR 计算与绘图脚本
==========================
输入格式：Target, Sample, Rep1, Rep2, Rep3
支持 Target：ND1 Ct / ND5 Ct / B2M Ct / POLG Ct

计算规则：
- ND1 Ct 配对 B2M Ct，ND5 Ct 配对 POLG Ct
- Delta Ct = 核内参 Ct - mtDNA Ct
- 2^Delta Ct 后，对 ND1 行计算 Mean copy number = (2^(B2M-ND1) + 2^(POLG-ND5)) / 2
- 以 ND1 行的 Mean copy number 绘制柱状图

统计：
- 2 组：独立样本 t-test（等方差）
- ≥3 组：Tukey HSD 所有两两比较

输出：
- <name>.csv：原表 + Delta Ct + 2^Delta Ct + Mean copy number
- <name>.png：300 dpi 发表级柱状图
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

# matplotlib 缓存重定向到临时目录，避免访问用户主目录下的 .matplotlib
if "MPLCONFIGDIR" not in os.environ:
    os.environ["MPLCONFIGDIR"] = os.path.join(
        tempfile.gettempdir(), ".mpl-cache-qpcr-mtdna"
    )

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ------------------------------------------------------------
# 配色与布局参数
# ------------------------------------------------------------

# 通用扩展配色（2 组时实际使用前两个）
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

# 3 组：参考 barplot_3col.py
BAR_COLORS_3 = ["#0072B2", "#D55E00", "#009E73"]
POINT_COLORS_3 = ["#80FFFF", "#EDA461", "#90EE90"]

# 6 组：参考 barplot_6col.py（Wong 2011 色盲友好 palette）
BAR_COLORS_6 = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9"]
POINT_COLORS_6 = ["#80FFFF", "#EDA461", "#90EE90", "#D683F1", "#FAD7A0", "#A8E6FF"]

Y_LABEL_DEFAULT = "Cytosolic mtDNA (Mean copy number)"
DPI_DEFAULT = 300


# ------------------------------------------------------------
# 工具函数
# ------------------------------------------------------------

def p_to_star_text(p):
    """P 值转文字标注。"""
    if pd.isna(p):
        return ""
    if p < 0.001:
        return "*** P<0.001"
    elif p < 0.01:
        return f"** P={p:.3f}"
    elif p < 0.05:
        return f"* P={p:.3f}"
    else:
        return f"P={p:.3f}"


def auto_yticks(all_values, max_with_error):
    """根据数据范围自动选择 0 起始、≤6 个刻度的 Y 轴。"""
    all_max = max(np.nanmax(all_values), max_with_error)
    if np.isnan(all_max) or all_max <= 0:
        all_max = 1.0

    nice_steps = [
        0.001,
        0.002,
        0.005,
        0.01,
        0.02,
        0.05,
        0.1,
        0.2,
        0.5,
        1,
        2,
        3,
        4,
        5,
        10,
        20,
        50,
        100,
        200,
        500,
        1000,
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
    """读取 CSV，仅保留原始列。"""
    df = pd.read_csv(csv_path)
    raw_cols = ["Target", "Sample", "Rep1", "Rep2", "Rep3"]
    missing = [c for c in raw_cols if c not in df.columns]
    if missing:
        raise ValueError(f"缺少必需列: {missing}")
    df = df[raw_cols].copy()
    for col in ["Rep1", "Rep2", "Rep3"]:
        df[col] = pd.to_numeric(df[col].replace("", np.nan), errors="coerce")
    return df


def compute_calculations(df):
    """计算 Delta Ct、2^Delta Ct、Mean copy number。"""
    ct_dict = (
        df.set_index(["Target", "Sample"])[["Rep1", "Rep2", "Rep3"]]
        .to_dict("index")
    )

    def get_ct(target, sample):
        key = (target, sample)
        if key not in ct_dict:
            return np.array([np.nan, np.nan, np.nan])
        row = ct_dict[key]
        return np.array([row["Rep1"], row["Rep2"], row["Rep3"]], dtype=float)

    delta_cts = []
    powers = []
    mean_copies = []

    for _, row in df.iterrows():
        target = row["Target"]
        sample = row["Sample"]
        reps = get_ct(target, sample)
        target_base = target.split()[0]

        if target_base == "ND1":
            ref = get_ct("B2M Ct", sample)
            delta = ref - reps
        elif target_base == "ND5":
            ref = get_ct("POLG Ct", sample)
            delta = ref - reps
        elif target_base in ("B2M", "POLG"):
            delta = np.array([0.0, 0.0, 0.0])
        else:
            delta = np.array([np.nan, np.nan, np.nan])

        power = 2.0 ** delta

        if target_base == "ND1":
            b2m = get_ct("B2M Ct", sample)
            polg = get_ct("POLG Ct", sample)
            nd5 = get_ct("ND5 Ct", sample)
            if not (
                np.isnan(b2m).any()
                or np.isnan(reps).any()
                or np.isnan(polg).any()
                or np.isnan(nd5).any()
            ):
                nd1_power = 2.0 ** (b2m - reps)
                nd5_power = 2.0 ** (polg - nd5)
                mean_copy = (nd1_power + nd5_power) / 2.0
            else:
                mean_copy = np.array([np.nan, np.nan, np.nan])
        else:
            mean_copy = np.array([np.nan, np.nan, np.nan])

        delta_cts.append(delta)
        powers.append(power)
        mean_copies.append(mean_copy)

    delta_cts = np.array(delta_cts)
    powers = np.array(powers)
    mean_copies = np.array(mean_copies)

    df["Delta Ct(Rep1)"] = np.round(delta_cts[:, 0], 2)
    df["Delta Ct(Rep2)"] = np.round(delta_cts[:, 1], 2)
    df["Delta Ct(Rep3)"] = np.round(delta_cts[:, 2], 2)
    df["2^Delta Ct(Rep1)"] = np.round(powers[:, 0], 2)
    df["2^Delta Ct(Rep2)"] = np.round(powers[:, 1], 2)
    df["2^Delta Ct(Rep3)"] = np.round(powers[:, 2], 2)
    df["Mean copy number(Rep1)"] = np.round(mean_copies[:, 0], 2)
    df["Mean copy number(Rep2)"] = np.round(mean_copies[:, 1], 2)
    df["Mean copy number(Rep3)"] = np.round(mean_copies[:, 2], 2)

    return df


def get_mean_copy_by_sample(df):
    """从 ND1 Ct 行提取每个 Sample 的 3 个 Mean copy number 值。"""
    nd1_df = df[df["Target"] == "ND1 Ct"].copy()
    data_by_sample = {}
    for _, row in nd1_df.iterrows():
        sample = row["Sample"]
        vals = np.array(
            [
                row["Mean copy number(Rep1)"],
                row["Mean copy number(Rep2)"],
                row["Mean copy number(Rep3)"],
            ],
            dtype=float,
        )
        if not np.all(np.isnan(vals)):
            data_by_sample[sample] = vals
    return data_by_sample


def tukey_pairwise(data_by_sample):
    """Tukey HSD 所有两两比较。"""
    samples = list(data_by_sample.keys())
    arrays = [data_by_sample[s] for s in samples]
    res = stats.tukey_hsd(*arrays)
    pmat = res.pvalue
    results = []
    for i in range(len(samples)):
        for j in range(i + 1, len(samples)):
            results.append((samples[i], samples[j], float(pmat[i, j])))
    return results


def plot_bar(data_by_sample, figure_name, output_png, y_label=Y_LABEL_DEFAULT, dpi=DPI_DEFAULT):
    """绘制 Mean copy number 柱状图。"""
    samples = list(data_by_sample.keys())
    n_groups = len(samples)

    if n_groups == 0:
        print("  警告: 没有可用于画图的 Mean copy number 数据")
        return False

    means = [np.mean(data_by_sample[s]) for s in samples]
    errors = [np.std(data_by_sample[s], ddof=1) for s in samples]

    all_values = np.concatenate([data_by_sample[s] for s in samples])
    max_with_error = max([m + e for m, e in zip(means, errors)])

    # 统计检验
    if n_groups == 2:
        _, p_value = stats.ttest_ind(
            data_by_sample[samples[0]], data_by_sample[samples[1]], equal_var=True
        )
        # 与旧脚本/已有 Figure 保持一致的 P 值文字格式
        if p_value < 0.001:
            p_text = "***\nP < 0.001"
        elif p_value < 0.01:
            p_text = f"**\nP = {p_value:.3f}"
        elif p_value < 0.05:
            p_text = f"*\nP = {p_value:.3f}"
        else:
            p_text = f"P = {p_value:.3f}"
        pairwise_results = None
    else:
        pairwise_results = tukey_pairwise(data_by_sample)
        p_text = None

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
        # 4/5 组：扩展布局
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
        x_pos,
        means,
        width=bar_width,
        color=colors,
        alpha=0.9,
        edgecolor="black",
        linewidth=3,
    )
    ax.errorbar(
        x_pos,
        means,
        yerr=errors,
        fmt="none",
        capsize=8,
        elinewidth=3,
        capthick=3,
        ecolor="black",
    )

    for i, sample in enumerate(samples):
        data = data_by_sample[sample]
        np.random.seed(42 + i)
        jitter = np.random.normal(0, jitter_std, size=len(data))
        ax.scatter(
            x_pos[i] + jitter,
            data,
            color=point_colors[i],
            edgecolor="black",
            s=200,
            zorder=5,
            alpha=0.9,
            linewidth=3,
        )

    # 显著性文字区
    if n_groups >= 3:
        sig_pairs = [(a, b, p) for a, b, p in pairwise_results if p < 0.05]
        if sig_pairs:
            p_lines = [
                f"{b} vs {a}:\n  {p_to_star_text(p)}" for a, b, p in sig_pairs
            ]
            p_text_combined = "\n".join(p_lines)
        else:
            p_text_combined = "ns"
        if n_groups == 6:
            label_y = 0.70
            label_fontsize = 7.5
            label_linespacing = 1.3
        else:
            label_y = 0.55
            label_fontsize = 10
            label_linespacing = 1.5
        ax.text(
            1.03,
            label_y,
            p_text_combined,
            transform=ax.transAxes,
            fontsize=label_fontsize,
            verticalalignment="center",
            fontfamily="Arial",
            fontweight="normal",
            linespacing=label_linespacing,
        )
        ax.text(
            1.03,
            0.10,
            "Tukey HSD",
            transform=ax.transAxes,
            fontsize=10,
            fontfamily="Arial",
            verticalalignment="bottom",
        )

    ax.set_ylabel(
        y_label, fontsize=16, fontfamily="Arial", fontweight="normal", labelpad=15
    )
    ax.set_xticks(x_pos)
    ax.set_xticklabels(
        samples,
        fontsize=14,
        fontfamily="Arial",
        fontweight="normal",
        rotation=45,
        ha="right",
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
            1.09,
            0.5,
            p_text,
            transform=ax.transAxes,
            fontsize=fontsize_p,
            verticalalignment="center",
            fontfamily="Arial",
            fontweight="normal",
        )

    ax.text(
        0.5,
        1.05,
        figure_name.replace("_", " "),
        transform=ax.transAxes,
        fontsize=16,
        fontfamily="Arial",
        fontweight="normal",
        horizontalalignment="center",
        verticalalignment="bottom",
    )

    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")
    ax.grid(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_linewidth(3)
    ax.spines["left"].set_linewidth(3)

    plt.subplots_adjust(
        left=left_margin,
        right=right_margin,
        bottom=bottom_margin,
        top=top_margin,
    )

    plt.savefig(output_png, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"  柱状图已保存: {output_png}")
    return True


def process_one(input_csv, output_dir, name, y_label, dpi, overwrite=False):
    """处理单个 CSV。"""
    input_csv = Path(input_csv)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_csv = output_dir / f"{name}.csv"
    output_png = output_dir / f"{name}.png"

    if (output_csv.exists() or output_png.exists()) and not overwrite:
        raise FileExistsError(
            f"输出文件已存在: {output_csv} 或 {output_png}。"
            f"使用 --overwrite 覆盖，或更换 --name。"
        )

    df = read_raw_csv(input_csv)
    df = compute_calculations(df)
    df.to_csv(output_csv, index=False, float_format="%.2f")
    print(f"  已保存 CSV: {output_csv}")

    data_by_sample = get_mean_copy_by_sample(df)
    if not data_by_sample:
        print("  警告: 没有可用的 Mean copy number 数据，跳过画图")
        return

    plot_bar(data_by_sample, name, output_png, y_label=y_label, dpi=dpi)


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="mtDNA qPCR ΔCt 计算与柱状图生成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run_mtdna.py examples/input/mtDNA-input.csv examples/output --name Figure18B
  python run_mtdna.py "D:/data/Figure20B.csv" "D:/results" --y-label "mtDNA copy number"
""",
    )
    parser.add_argument("input_csv", help="输入 CSV 路径（Target, Sample, Rep1, Rep2, Rep3）")
    parser.add_argument(
        "output_dir",
        nargs="?",
        default=None,
        help="输出目录（默认与输入 CSV 同目录）",
    )
    parser.add_argument(
        "--name",
        default=None,
        help="输出文件名前缀（默认使用输入 CSV 的文件名主干）",
    )
    parser.add_argument(
        "--y-label", default=Y_LABEL_DEFAULT, help=f"Y 轴标签（默认: {Y_LABEL_DEFAULT}）"
    )
    parser.add_argument("--dpi", type=int, default=DPI_DEFAULT, help="PNG 分辨率（默认 300）")
    parser.add_argument(
        "--overwrite", action="store_true", help="覆盖已存在的输出文件"
    )
    args = parser.parse_args()

    input_csv = Path(args.input_csv).resolve()
    if not input_csv.exists():
        print(f"错误: 输入文件不存在: {input_csv}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir).resolve() if args.output_dir else input_csv.parent
    name = args.name if args.name else input_csv.stem

    process_one(
        input_csv=input_csv,
        output_dir=output_dir,
        name=name,
        y_label=args.y_label,
        dpi=args.dpi,
        overwrite=args.overwrite,
    )


if __name__ == "__main__":
    main()
