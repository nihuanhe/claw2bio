import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import pandas as pd
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import itertools

# ===== 配置 =====
DATA_FILE = sys.argv[1] if len(sys.argv) > 1 else r'D:\小文章\data\画柱状图\data.csv'

# ============================================================
# ★ 修改图片标题和Y轴名称：直接改下面两行的引号内文字即可
# ============================================================
FIGURE_NAME = 'CD4'          # ← 图片标题（显示在图表上方）
Y_LABEL     = 'Treg%'                # ← Y轴标签（显示在Y轴左侧）

def calc_y_axis_limits(data_list):
    """动态计算Y轴范围，确保3-6个等差刻度线。"""
    # 先按原始最大值（数据最大值或 mean + SD）计算 nice Y_MAX
    raw_max = max([np.max(d) for d in data_list])
    error_max = max([np.mean(d) + np.std(d, ddof=1) for d in data_list])
    data_max = max(raw_max, error_max)

    # 额外溢出空间：散点半径 + 边缘线（约 5%）
    visual_max = data_max * 1.05

    candidate_steps = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
    chosen = None
    for step in candidate_steps:
        Y_MAX = np.ceil(data_max / step) * step
        yticks = np.arange(0, Y_MAX + step * 0.01, step)
        n_ticks = len(yticks)
        if 3 <= n_ticks <= 6:
            chosen = (Y_MAX, step, yticks)
            # 如果加上视觉边距后会超出当前 Y_MAX，则向上取一个 step
            if visual_max > Y_MAX:
                Y_MAX = Y_MAX + step
                yticks = np.arange(0, Y_MAX + step * 0.01, step)
                chosen = (Y_MAX, step, yticks)
            break
    if chosen is not None:
        return 0, chosen[0], chosen[1], chosen[2]
    step = candidate_steps[-1]
    Y_MAX = np.ceil(visual_max / step) * step
    yticks = np.arange(0, Y_MAX + step * 0.01, step)
    return 0, Y_MAX, step, yticks

# ===== 读取数据 =====
df = pd.read_csv(DATA_FILE)
col_names = df.columns.tolist()
print(f"检测到列: {col_names}")

data_list = [df[c].dropna().values for c in col_names]
n_groups = len(col_names)

# ===== 动态计算Y轴范围 =====
Y_MIN, Y_MAX, Y_STEP, yticks = calc_y_axis_limits(data_list)
print(f"Y轴范围: {Y_MIN} ~ {Y_MAX}, 步长: {Y_STEP}, 刻度数: {len(yticks)}")

# ===== 统计量 =====
means = [np.mean(d) for d in data_list]
sds   = [np.std(d, ddof=1) for d in data_list]

# ===== One-way ANOVA =====
f_stat, anova_p = stats.f_oneway(*data_list)
print(f"One-way ANOVA: F={f_stat:.4f}, P={anova_p:.4f}")

# ===== Tukey HSD 两两比较 =====
all_values = np.concatenate(data_list)
all_labels = np.concatenate([[col_names[i]] * len(data_list[i]) for i in range(n_groups)])
tukey = pairwise_tukeyhsd(all_values, all_labels, alpha=0.05)
print(tukey)

tukey_df = pd.DataFrame(data=tukey._results_table.data[1:],
                        columns=tukey._results_table.data[0])
pair_p = {}
for _, row in tukey_df.iterrows():
    g1, g2 = str(row['group1']), str(row['group2'])
    pair_p[(g1, g2)] = float(row['p-adj'])
    pair_p[(g2, g1)] = float(row['p-adj'])

def p_to_star(p):
    if p < 0.001:
        return f'*** P<0.001'
    elif p < 0.01:
        return f'** P={p:.3f}'
    elif p < 0.05:
        return f'* P={p:.3f}'
    else:
        return f'P={p:.3f}'

pairs = list(itertools.combinations(range(n_groups), 2))

# ===== 图表布局 =====
# 保持与 3-col / 5-col 相同的 inches_per_xunit (~3.6031)，
# 确保柱子物理宽度一致。
# 6柱: x_range = 19/7, 需要 axes_width = 3.6031 * 19/7 ≈ 9.78
# figwidth = axes_width / (right - left)
fig, ax = plt.subplots(figsize=(13.18, 6))
plt.subplots_adjust(left=0.055, right=0.798, bottom=0.064537, top=0.975000)

bar_width = 1.7 / 7
# 6组数据，x_pos 按 7等分网格：每组分 3/7，左/右边距各 2/7
n_pos = 6
x_pos = np.array([2/7 + i * 3/7 for i in range(n_pos)])

# ===== 配色方案（色盲友好，基于 Wong 2011 palette） =====
# 前5色与 5-col 保持一致，第6色使用 #56B4E9（天蓝色，色盲友好）
bar_colors   = ['#0072B2', '#D55E00', '#009E73', '#CC79A7', '#E69F00', '#56B4E9']
point_colors = ['#80FFFF', '#EDA461', '#90EE90', '#D683F1', '#FAD7A0', '#A8E6FF']

# ===== 绘制柱 + 误差线 + 数据点 =====
for i in range(n_groups):
    ax.bar(x_pos[i], means[i], width=bar_width,
           color=bar_colors[i], alpha=0.9, edgecolor='black', linewidth=3)
    ax.errorbar(x_pos[i], means[i], yerr=sds[i], fmt='none',
                capsize=8, elinewidth=3, capthick=3, ecolor='black')
    np.random.seed(42 + i)
    jitter = np.random.normal(0, 0.015, size=len(data_list[i]))
    ax.scatter(x_pos[i] + jitter, data_list[i],
               color=point_colors[i], edgecolor='black',
               s=200, zorder=5, alpha=0.9, linewidth=3)

# ===== 坐标轴 =====
ax.set_ylabel(Y_LABEL, fontsize=16, fontfamily='Arial', fontweight='normal', labelpad=15)
ax.set_xticks(x_pos)
ax.set_xticklabels(col_names, fontsize=14, fontfamily='Arial', fontweight='normal', rotation=45, ha='right')

ax.set_yticks(yticks)
ax.set_ylim(Y_MIN, Y_MAX)
ax.set_xlim(0, 19/7)  # x_pos[-1]=17/7 + 右边距2/7=19/7

ax.tick_params(axis='y', pad=10, labelsize=14, length=10, width=3)
ax.tick_params(axis='x', length=10, width=3)

for item in ([ax.xaxis.label, ax.yaxis.label] +
             ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontfamily('Arial')
    item.set_fontweight('normal')

# ===== P值标注（右侧文字列表，六组两两共15个比较） =====
p_lines = []
for (i, j) in pairs:
    g1, g2 = col_names[i], col_names[j]
    p = pair_p.get((g1, g2), float('nan'))
    line = f'{g1} vs {g2}:\n  {p_to_star(p)}'
    p_lines.append(line)

p_text_combined = '\n'.join(p_lines)
ax.text(1.03, 0.70, p_text_combined, transform=ax.transAxes, fontsize=7.5,
        verticalalignment='center', fontfamily='Arial', fontweight='normal',
        linespacing=1.3)

# ANOVA总P值标注
ax.text(1.03, 0.10, f'ANOVA P={anova_p:.4f}', transform=ax.transAxes,
        fontsize=9, fontfamily='Arial', verticalalignment='bottom')

# ===== 图片标题 =====
ax.text(0.5, 1.05, FIGURE_NAME, transform=ax.transAxes,
        fontsize=16, fontfamily='Arial', fontweight='normal',
        horizontalalignment='center', verticalalignment='bottom')

# ===== 样式 =====
ax.set_facecolor('white')
fig.patch.set_facecolor('white')
ax.grid(False)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_linewidth(3)
ax.spines['left'].set_linewidth(3)

output_path = DATA_FILE.replace('.csv', '_barplot6col.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f'图表已保存到: {output_path}')
for i in range(n_groups):
    print(f'{col_names[i]}: 均值={means[i]:.3f}, SD={sds[i]:.3f}')
