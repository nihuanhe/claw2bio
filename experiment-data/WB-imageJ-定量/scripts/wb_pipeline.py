#!/usr/bin/env python3
"""
Western Blot 定量全流程：归一化 → 统计 → 柱状图

输入: ImageJ 导出的灰度 CSV（经人工整理为 Protein/Sample/Mean_RepX/beta_actin_mean）
输出: 归一化 CSV（追加统计列） + 300dpi 柱状图 PNG

用法:
    # 单文件
    python wb_pipeline.py FigureR3/FigureR3.csv

    # 批量
    python wb_pipeline.py --batch ./灰度定量和归一化数据/

    # 指定对照组名（默认 Ctrl）
    python wb_pipeline.py FigureR3.csv --control "Ctrl-BD-sEV"
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import os
import re
import glob
from argparse import ArgumentParser


# ============================================================
# 全局配色方案（Wong 2011 色盲友好）
# ============================================================
COLOR_SCHEMES = {
    2: {'bar': ['#009E73', '#CC79A7'], 'point': ['#80FFD7', '#EBC8E1']},
    3: {'bar': ['#808080', '#009E73', '#CC79A7'], 'point': ['#D3D3D3', '#80FFD7', '#EBC8E1']},
    4: {'bar': ['#0072B2', '#D55E00', '#009E73', '#CC79A7'], 'point': ['#80FFFF', '#EDA461', '#90EE90', '#D683F1']},
    5: {'bar': ['#0072B2', '#D55E00', '#009E73', '#CC79A7', '#E69F00'], 'point': ['#80FFFF', '#EDA461', '#90EE90', '#D683F1', '#FAD7A0']},
    6: {'bar': ['#0072B2', '#D55E00', '#009E73', '#CC79A7', '#E69F00', '#56B4E9'], 'point': ['#80FFFF', '#EDA461', '#90EE90', '#D683F1', '#FAD7A0', '#A8E6FF']},
}

POINT_SIZE    = 120
EDGE_WIDTH    = 1.2
BAR_EDGE_LW   = 2.0
ERROR_LW      = 2.0
ERROR_CAP     = 5
Y_LABEL       = 'Relative protein expression'
DPI           = 300


# ============================================================
# S1: 归一化
# ============================================================

def detect_reps(df):
    """从列名自动检测重复数。查找 Mean_Rep1, Mean_Rep2, ... """
    rep_cols = sorted([c for c in df.columns if re.match(r'Mean_Rep\d+$', c)],
                      key=lambda x: int(re.search(r'\d+', x).group()))
    if not rep_cols:
        raise ValueError("CSV 缺少 Mean_Rep1/2/3... 列，请检查格式")
    return rep_cols


def normalize(df, rep_cols):
    """
    归一化: Normalized_RepX = Mean_RepX / beta_actin_mean
    如果 CSV 已含 Normalized_Rep 列则跳过。
    """
    norm_cols = [c.replace('Mean', 'Normalized') for c in rep_cols]

    # 如果已有归一化列，跳过
    if all(c in df.columns for c in norm_cols):
        return df

    for mc, nc in zip(rep_cols, norm_cols):
        df[nc] = df[mc] / df['beta_actin_mean']

    df['Normalized_Mean'] = df[norm_cols].mean(axis=1)
    df['Normalized_SD']   = df[norm_cols].std(ddof=1, axis=1)
    n_reps = len(rep_cols)
    df['Normalized_SEM']  = df['Normalized_SD'] / np.sqrt(n_reps)

    return df


# ============================================================
# S2: 统计检验
# ============================================================

def compute_statistics(df, sample_order, control_sample=None):
    """
    2 组: Student's t-test (equal variance)
    3+ 组: 单因素 ANOVA + Tukey HSD
    写回 CSV 列: p_value, Significance, ANOVA_F, ANOVA_p
    """
    proteins = df['Protein'].unique()
    n_samples = len(sample_order)

    if n_samples == 2:
        # ---- t-test per protein ----
        p_vals = {}
        for prot in proteins:
            g1_rows = df[(df['Protein'] == prot) & (df['Sample'] == sample_order[0])]
            g2_rows = df[(df['Protein'] == prot) & (df['Sample'] == sample_order[1])]
            if len(g1_rows) == 0 or len(g2_rows) == 0:
                p_vals[prot] = 1.0
                continue
            g1_vals = g1_rows.iloc[0]
            g2_vals = g2_rows.iloc[0]
            rep_cols = [c for c in df.columns if c.startswith('Normalized_Rep')]
            v1 = [float(g1_vals[c]) for c in rep_cols if pd.notna(g1_vals[c])]
            v2 = [float(g2_vals[c]) for c in rep_cols if pd.notna(g2_vals[c])]
            if len(v1) < 2 or len(v2) < 2:
                p_vals[prot] = 1.0
                continue
            _, p = stats.ttest_ind(v1, v2, equal_var=True)
            p_vals[prot] = p

        # 写回
        for prot in proteins:
            p = p_vals.get(prot, 1.0)
            mask = df['Protein'] == prot
            df.loc[mask, 'p_value'] = p
            df.loc[mask, 'Significance'] = _p_to_star(p)
            df.loc[mask, 't_statistic'] = None
            df.loc[mask, 'df'] = None

    else:
        # ---- ANOVA + Tukey HSD per protein ----
        for prot in proteins:
            rows = df[df['Protein'] == prot]
            groups = []
            labels = []
            rep_cols = [c for c in df.columns if c.startswith('Normalized_Rep')]
            for _, row in rows.iterrows():
                vals = [float(row[c]) for c in rep_cols if pd.notna(row[c])]
                groups.append(vals)
                labels.extend([row['Sample']] * len(vals))

            if len(groups) < 2:
                continue

            try:
                f_stat, anova_p = stats.f_oneway(*groups)
            except Exception:
                f_stat, anova_p = 0.0, 1.0

            mask = df['Protein'] == prot
            df.loc[mask, 'ANOVA_F'] = f_stat
            df.loc[mask, 'ANOVA_p'] = anova_p

            # Tukey HSD
            all_vals = np.concatenate(groups)
            all_labs = np.array(labels)
            try:
                tukey = pairwise_tukeyhsd(all_vals, all_labs, alpha=0.05)
                tukey_data = tukey._results_table.data
                tukey_df = pd.DataFrame(data=tukey_data[1:], columns=tukey_data[0])

                # 找对照组 vs 其他组的 p-adj
                if control_sample:
                    ctrl_rows = tukey_df[
                        ((tukey_df['group1'] == control_sample) | (tukey_df['group2'] == control_sample))
                    ]
                    for _, tr in ctrl_rows.iterrows():
                        g1, g2 = str(tr['group1']), str(tr['group2'])
                        p_adj = float(tr['p-adj'])
                        other = g2 if g1 == control_sample else g1
                        smask = (df['Protein'] == prot) & (df['Sample'] == other)
                        df.loc[smask, 'p_value'] = p_adj
                        df.loc[smask, 'Significance'] = _p_to_star(p_adj)
            except Exception:
                pass


def _p_to_star(p):
    if p < 0.001: return '***'
    elif p < 0.01: return '**'
    elif p < 0.05: return '*'
    else: return 'ns'


def _format_p(p):
    if p < 0.001: return 'P<0.001'
    else: return f'P={p:.3f}'


# ============================================================
# S3: Y轴计算
# ============================================================

def calc_y_limits(data_lists):
    max_val = max([np.max(d) for d in data_lists if len(d) > 0])
    if max_val == 0:
        max_val = 1
    candidate_steps = [0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
    for step in candidate_steps:
        y_max = np.ceil(max_val / step) * step
        yticks = np.arange(0, y_max + step * 0.01, step)
        if 3 <= len(yticks) <= 6:
            return 0, y_max, step, yticks
    step = candidate_steps[-1]
    y_max = np.ceil(max_val / step) * step
    yticks = np.arange(0, y_max + step * 0.01, step)
    return 0, y_max, step, yticks


# ============================================================
# S4: 绘图
# ============================================================

def get_color_scheme(n_samples):
    if n_samples in COLOR_SCHEMES:
        return COLOR_SCHEMES[n_samples]
    return {'bar': COLOR_SCHEMES[6]['bar'][:n_samples],
            'point': COLOR_SCHEMES[6]['point'][:n_samples]}


def figure_title_from_name(name):
    return name.replace('FigureR', 'Figure R').replace('_', ' ')


def plot_wb(proteins, sample_order, rows_by_protein, csv_dir, png_path, n_reps):
    n_proteins = len(proteins)
    n_samples = len(sample_order)
    colors = get_color_scheme(n_samples)

    # 提取数据
    means  = np.zeros((n_proteins, n_samples))
    sds    = np.zeros((n_proteins, n_samples))
    rep_data = [[[] for _ in range(n_samples)] for _ in range(n_proteins)]

    for pi, prot in enumerate(proteins):
        for si, samp in enumerate(sample_order):
            row = rows_by_protein[prot][samp]
            means[pi, si] = float(row['Normalized_Mean'])
            sds[pi, si]   = float(row['Normalized_SD'])
            for k in range(1, n_reps + 1):
                col = f'Normalized_Rep{k}'
                v = row.get(col, None)
                if v is not None and not (isinstance(v, float) and np.isnan(v)):
                    rep_data[pi][si].append(float(v))

    # Y 轴
    all_rep = [np.array(rep_data[pi][si]) for pi in range(n_proteins) for si in range(n_samples)]
    y_min, y_max, y_step, yticks = calc_y_limits(all_rep)

    # 布局
    if n_samples == 2:
        _plot_2group(proteins, sample_order, means, sds, rep_data, colors,
                     n_proteins, n_samples, y_min, y_max, yticks,
                     rows_by_protein, csv_dir, png_path)
    else:
        _plot_multigroup(proteins, sample_order, means, sds, rep_data, colors,
                         n_proteins, n_samples, n_reps, y_min, y_max, yticks,
                         rows_by_protein, csv_dir, png_path)


def _plot_2group(proteins, sample_order, means, sds, rep_data, colors,
                 n_proteins, n_samples, y_min, y_max, yticks,
                 rows_by_protein, csv_dir, png_path):
    bar_width = 1.7 / 7
    intra_gap = 0.08
    protein_spacing = 1.0

    x_protein = np.arange(n_proteins) * protein_spacing
    x_ctrl  = x_protein - bar_width / 2 - intra_gap / 2
    x_treat = x_protein + bar_width / 2 + intra_gap / 2
    x_pos = [x_ctrl, x_treat]

    x_range_min = min(x_ctrl[0] - bar_width - 0.2, 0)
    x_range_max = max(x_treat[-1] + bar_width + 0.2, protein_spacing)

    fig_width = max(6, n_proteins * protein_spacing + 2.5)
    fig, ax = plt.subplots(figsize=(fig_width, 6.5))

    for pi in range(n_proteins):
        for si in range(n_samples):
            ax.bar(x_pos[si][pi], means[pi, si], width=bar_width,
                   color=colors['bar'][si], edgecolor='black',
                   linewidth=BAR_EDGE_LW, zorder=3, alpha=0.9)
            ax.errorbar(x_pos[si][pi], means[pi, si],
                        yerr=[[0], [sds[pi, si]]], fmt='none',
                        capsize=ERROR_CAP, elinewidth=ERROR_LW,
                        capthick=ERROR_LW, ecolor='black', zorder=4)

            if len(rep_data[pi][si]) > 0:
                np.random.seed(42 + pi * 10 + si)
                jitter = np.random.normal(0, 0.04, size=len(rep_data[pi][si]))
                ax.scatter(x_pos[si][pi] + jitter, rep_data[pi][si],
                           facecolors=colors['point'][si], edgecolors='black',
                           s=POINT_SIZE, zorder=5, linewidths=EDGE_WIDTH, alpha=0.9)

    _style_axes(ax, x_protein, proteins, yticks, y_min, y_max, x_range_min, x_range_max,
                n_proteins, sample_order, rows_by_protein, csv_dir)
    _style_figure(fig, ax)

    # 显著性（仅显著）
    sig_lines = []
    for pi, prot in enumerate(proteins):
        for samp in sample_order:
            row = rows_by_protein[prot][samp]
            pv = row.get('p_value', None)
            if pv is not None and str(pv).strip() != '':
                try:
                    p = float(pv)
                except (ValueError, TypeError):
                    continue
                star = _p_to_star(p)
                if star != 'ns':
                    sig_lines.append(f'{prot}: {star} ({_format_p(p)})')
                break

    if sig_lines:
        ax.text(1.02, 0.98, '\n'.join(sig_lines), transform=ax.transAxes,
                fontsize=9, verticalalignment='top', fontfamily='Arial',
                fontweight='normal', linespacing=1.4, color='#333333')
    else:
        ax.text(1.02, 0.98, 'No significant\ndifferences', transform=ax.transAxes,
                fontsize=9, verticalalignment='top', fontfamily='Arial',
                fontweight='normal', color='#888888')

    plt.tight_layout()
    plt.savefig(png_path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  [OK] {os.path.basename(png_path)}  ({n_proteins}P, t-test)')


def _plot_multigroup(proteins, sample_order, means, sds, rep_data, colors,
                     n_proteins, n_samples, n_reps,
                     y_min, y_max, yticks,
                     rows_by_protein, csv_dir, png_path):
    bar_width = 0.70 / n_samples
    intra_gap_inner = 0.03
    total_width = n_samples * bar_width + (n_samples - 1) * intra_gap_inner
    protein_spacing = max(1.0, total_width + 0.25)

    x_protein = np.arange(n_proteins) * protein_spacing
    x_pos = np.zeros((n_proteins, n_samples))
    for pi in range(n_proteins):
        start = x_protein[pi] - total_width / 2 + bar_width / 2
        for si in range(n_samples):
            x_pos[pi, si] = start + si * (bar_width + intra_gap_inner)

    x_range_min = min(x_pos[0, 0] - bar_width - 0.15, 0)
    x_range_max = x_pos[-1, -1] + bar_width + 0.15

    fig_width = max(6, n_proteins * protein_spacing + 2.5)
    fig, ax = plt.subplots(figsize=(fig_width, 6.5))

    for pi in range(n_proteins):
        for si in range(n_samples):
            ax.bar(x_pos[pi, si], means[pi, si], width=bar_width,
                   color=colors['bar'][si], edgecolor='black',
                   linewidth=BAR_EDGE_LW, zorder=3, alpha=0.9)
            ax.errorbar(x_pos[pi, si], means[pi, si],
                        yerr=[[0], [sds[pi, si]]], fmt='none',
                        capsize=ERROR_CAP, elinewidth=ERROR_LW,
                        capthick=ERROR_LW, ecolor='black', zorder=4)

            if len(rep_data[pi][si]) > 0:
                np.random.seed(42 + pi * 10 + si)
                jitter = np.random.normal(0, 0.025, size=len(rep_data[pi][si]))
                ax.scatter(x_pos[pi, si] + jitter, rep_data[pi][si],
                           facecolors=colors['point'][si], edgecolors='black',
                           s=POINT_SIZE, zorder=5, linewidths=EDGE_WIDTH, alpha=0.9)

    # ANOVA + Tukey HSD
    anova_results = {}
    sig_pairs_all = []
    for pi, prot in enumerate(proteins):
        groups_vals = [rep_data[pi][si] for si in range(n_samples)]
        group_labels = []
        for si in range(n_samples):
            group_labels.extend([sample_order[si]] * len(rep_data[pi][si]))

        all_vals = np.concatenate(groups_vals)
        all_labs = np.array(group_labels)

        try:
            f_stat, anova_p = stats.f_oneway(*groups_vals)
        except Exception:
            f_stat, anova_p = 0.0, 1.0
        anova_results[prot] = (f_stat, anova_p)

        try:
            tukey = pairwise_tukeyhsd(all_vals, all_labs, alpha=0.05)
            tukey_df = pd.DataFrame(data=tukey._results_table.data[1:],
                                    columns=tukey._results_table.data[0])
            for _, tr in tukey_df.iterrows():
                g1, g2 = str(tr['group1']), str(tr['group2'])
                p_adj = float(tr['p-adj'])
                if p_adj < 0.05:
                    sig_pairs_all.append((prot, g1, g2, p_adj))
        except Exception:
            pass

    _style_axes(ax, x_protein, proteins, yticks, y_min, y_max, x_range_min, x_range_max,
                n_proteins, sample_order, rows_by_protein, csv_dir)
    _style_figure(fig, ax)

    # 显著性文字
    if sig_pairs_all:
        seen = set()
        unique = []
        for prot, g1, g2, p in sig_pairs_all:
            key = (prot, tuple(sorted([g1, g2])))
            if key not in seen:
                seen.add(key)
                unique.append((prot, g1, g2, p))
        sig_lines = []
        for prot, g1, g2, p in unique:
            g1s = g1 if len(g1) <= 20 else g1[:18] + '...'
            g2s = g2 if len(g2) <= 20 else g2[:18] + '...'
            sig_lines.append(f'{prot}: {g1s}\n  vs {g2s}: {_p_to_star(p)} ({_format_p(p)})')
        anova_p_vals = [v[1] for v in anova_results.values()]
        sig_lines.append('')
        sig_lines.append(f'ANOVA P={min(anova_p_vals):.4f}')
        ax.text(1.02, 0.98, '\n'.join(sig_lines), transform=ax.transAxes,
                fontsize=7.5, verticalalignment='top', fontfamily='Arial',
                fontweight='normal', linespacing=1.2, color='#333333')
    else:
        anova_p_vals = [v[1] for v in anova_results.values()]
        overall = min(anova_p_vals) if anova_p_vals else 1.0
        ax.text(1.02, 0.98, f'No significant\ndifferences\nANOVA P={overall:.4f}',
                transform=ax.transAxes, fontsize=9, verticalalignment='top',
                fontfamily='Arial', fontweight='normal', color='#888888')

    plt.tight_layout()
    plt.savefig(png_path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  [OK] {os.path.basename(png_path)}  ({n_proteins}P, {n_samples}S, {len(sig_pairs_all)} sig pairs)')


def _style_axes(ax, x_protein, proteins, yticks, y_min, y_max, x_min, x_max,
                n_proteins, sample_order, rows_by_protein, csv_dir):
    ax.set_xticks(x_protein)
    ax.set_xticklabels(proteins, fontsize=13, fontfamily='Arial',
                       fontweight='normal', rotation=45 if n_proteins > 1 else 0, ha='right')
    ax.set_ylabel(Y_LABEL, fontsize=14, fontfamily='Arial', fontweight='normal', labelpad=12)
    ax.set_yticks(yticks)
    ax.set_ylim(y_min, y_max)
    ax.set_xlim(x_min, x_max)
    ax.tick_params(axis='y', pad=8, labelsize=13, length=8, width=2)
    ax.tick_params(axis='x', length=8, width=2)
    for item in ([ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontfamily('Arial')
        item.set_fontweight('normal')


def _style_figure(fig, ax):
    fig_title = figure_title_from_name(os.path.basename(os.path.dirname(os.path.abspath('.'))))
    # Override: use the actual CSV directory name
    ax.set_facecolor('white')
    fig.patch.set_facecolor('white')
    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_linewidth(2)
    ax.spines['left'].set_linewidth(2)


# ============================================================
# 主入口
# ============================================================

def process_csv(csv_path, control_sample=None, output_dir=None):
    csv_dir = os.path.dirname(csv_path)
    if output_dir is None:
        output_dir = csv_dir

    csv_name = os.path.basename(csv_path)
    base_name = os.path.splitext(csv_name)[0]
    out_csv = os.path.join(output_dir, csv_name)
    out_png = os.path.join(output_dir, base_name + '.png')

    print(f'\n{"="*60}')
    print(f'Processing: {csv_path}')

    # 读取
    df = pd.read_csv(csv_path)
    required_cols = ['Protein', 'Sample', 'beta_actin_mean']
    for c in required_cols:
        if c not in df.columns:
            raise ValueError(f"CSV 缺少必需列: {c}")

    rep_cols = detect_reps(df)
    n_reps = len(rep_cols)
    print(f'  检测到 {n_reps} 个重复')

    proteins = df['Protein'].unique().tolist()
    sample_order = df['Sample'].unique().tolist()
    print(f'  Proteins: {proteins}')
    print(f'  Samples: {sample_order}')

    # S1: 归一化
    df = normalize(df, rep_cols)
    print(f'  归一化完成')

    # S2: 统计
    compute_statistics(df, sample_order, control_sample=control_sample)
    print(f'  统计完成')

    # 保存 CSV
    df.to_csv(out_csv, index=False, encoding='utf-8-sig', float_format='%.4f')
    print(f'  [CSV] {out_csv}')

    # S3: 准备绘图数据
    rows_by_protein = {}
    for prot in proteins:
        rows_by_protein[prot] = {}
        for samp in sample_order:
            sub = df[(df['Protein'] == prot) & (df['Sample'] == samp)]
            if len(sub) == 0:
                print(f'  [WARN] 缺失 {prot}/{samp}')
                return
            rows_by_protein[prot][samp] = sub.iloc[0].to_dict()

    # S4: 绘图
    plot_wb(proteins, sample_order, rows_by_protein, csv_dir, out_png, n_reps)

    return out_csv, out_png


def main():
    parser = ArgumentParser(description="WB 定量全流程：归一化 → 统计 → 柱状图")
    parser.add_argument("input", nargs='?', help="输入 CSV 路径")
    parser.add_argument("--batch", default=None, help="批量模式：指定扫描根目录")
    parser.add_argument("--control", default=None, help="对照组样本名（如 Ctrl）")
    parser.add_argument("--output-dir", default=None, help="输出目录（默认与输入同目录）")
    args = parser.parse_args()

    if args.batch:
        pattern = os.path.join(args.batch, 'FigureR*', 'FigureR*.csv')
        csv_files = sorted(glob.glob(pattern))
        print(f'批量模式：找到 {len(csv_files)} 个 CSV')
        for csv_path in csv_files:
            try:
                process_csv(csv_path, control_sample=args.control, output_dir=args.output_dir)
            except Exception as e:
                print(f'  [ERROR] {csv_path}: {e}')
    elif args.input:
        process_csv(args.input, control_sample=args.control, output_dir=args.output_dir)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
