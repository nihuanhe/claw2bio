import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import pandas as pd

# ===== 用户配置区域 =====
# 默认数据文件路径；可通过命令行参数覆盖：python barplot_2col_green_pink.py <input.csv>
DATA_FILE = sys.argv[1] if len(sys.argv) > 1 else r'd:\小文章\data\画柱状图\data.csv'

# ============================================================
# ★ 修改图片标题和Y轴名称：直接改下面两行的引号内文字即可
# ============================================================
FIGURE_NAME = 'ELISA'          # ← 图片标题（显示在图表上方）
Y_LABEL     = 'IFNβ (pg/mL)'       # ← Y轴标签（显示在Y轴左侧）
# ===== 配置结束 =====

# 读取数据，自动获取列名作为X轴标签
df = pd.read_csv(DATA_FILE)
col_names = df.columns.tolist()
data0 = df[col_names[0]].values
data1 = df[col_names[1]].values

# 计算统计量
mean0 = np.mean(data0)
sd0 = np.std(data0, ddof=1)
mean1 = np.mean(data1)
sd1 = np.std(data1, ddof=1)

# unpaired t-test, two-tailed, assume equal variance
t_stat, p_value = stats.ttest_ind(data0, data1, equal_var=True)

# 自动计算y轴范围和刻度（≤6个刻度线，从0开始，整数刻度）
# 上限需容纳：数据最大值、mean + SD 误差线顶端；若散点边距溢出，再向上取一个 step
all_values = np.concatenate([data0, data1])
data_max = max(all_values.max(), mean0 + sd0, mean1 + sd1)
visual_max = data_max * 1.05

# 确保数据为0时也有合理的范围
if data_max == 0:
    data_max = 1

nice_steps = [1, 2, 3, 4, 5, 10, 20, 50, 100, 200, 500, 1000]
step = nice_steps[-1]
y_max = None
for s in nice_steps:
    candidate_y_max = np.ceil(data_max / s) * s
    num_ticks = int(candidate_y_max / s) + 1
    if num_ticks <= 6:
        step = s
        y_max = candidate_y_max
        # 若视觉边距会溢出当前 y_max，则向上取一个 step
        if visual_max > y_max:
            y_max = y_max + s
        break

if y_max is None:
    y_max = np.ceil(visual_max / step) * step

yticks = np.arange(0, y_max + step, step)

# 创建图表，设置横纵比例3:4
fig, ax = plt.subplots(figsize=(5.3, 6))

# 柱状图设置 - 横坐标7等分，两个柱子各占1.7份
bar_width = 1.7 / 7
x_pos = np.array([2 / 7, 5 / 7])
colors = ['#009E73', '#CC79A7']

means = [mean0, mean1]
errors = [sd0, sd1]
labels = col_names[:2]

# 绘制柱状图
bars = ax.bar(x_pos, means, width=bar_width,
              color=colors, alpha=0.9, edgecolor='black', linewidth=3)

# 误差线
eb = ax.errorbar(x_pos, means, yerr=errors, fmt='none', capsize=8,
                 elinewidth=3, capthick=3, ecolor='black')

# 数据点
point_colors = ['#80FFD7', '#EBC8E1']
for i, (data, x) in enumerate(zip([data0, data1], x_pos)):
    np.random.seed(42 + i)
    jitter = np.random.normal(0, 0.04, size=len(data))
    ax.scatter(x + jitter, data, color=point_colors[i], edgecolor='black',
               s=200, zorder=5, alpha=0.9, linewidth=3)

# 坐标轴标签
ax.set_ylabel(Y_LABEL, fontsize=16, fontfamily='Arial', fontweight='normal', labelpad=15)
ax.set_xticks(x_pos)
ax.set_xticklabels(labels, fontsize=14, fontfamily='Arial', fontweight='normal', rotation=45, ha='right')

# y轴刻度
ax.set_yticks(yticks)

# 横坐标范围
ax.set_xlim(0, 1)

# 刻度参数
ax.tick_params(axis='y', pad=10, labelsize=14, length=10, width=3)
ax.tick_params(axis='x', length=10, width=3)

# 设置所有字体为Arial
for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
             ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontfamily('Arial')
    item.set_fontweight('normal')

# 添加P值标注
if p_value < 0.001:
    p_text = '***\nP < 0.001'
elif p_value < 0.01:
    p_text = f'**\nP = {p_value:.3f}'
elif p_value < 0.05:
    p_text = f'*\nP = {p_value:.3f}'
else:
    p_text = f'P = {p_value:.3f}'

ax.text(1.09, 0.5, p_text, transform=ax.transAxes, fontsize=14,
        verticalalignment='center', fontfamily='Arial', fontweight='normal')

# 添加图片名称
ax.text(0.5, 1.05, FIGURE_NAME, transform=ax.transAxes,
        fontsize=16, fontfamily='Arial', fontweight='normal',
        horizontalalignment='center', verticalalignment='bottom')

# 背景与网格
ax.set_facecolor('white')
fig.patch.set_facecolor('white')
ax.grid(False)

# 边框
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_linewidth(3)
ax.spines['left'].set_linewidth(3)

# y轴范围
ax.set_ylim(0, y_max)

# 用 subplots_adjust 固定边距，确保 axes 物理尺寸不随标签内容变化
# 值来源：tight_layout() 在 2组数据 + 300dpi + 标准标签 下的一次性计算结果
plt.subplots_adjust(left=0.198736, right=0.744637, bottom=0.120917, top=0.903010)

# 保存图表（自动根据数据文件名生成输出路径）
output_path = DATA_FILE.replace('.csv', '_barplot.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f'图表已保存到: {output_path}')
print(f'{col_names[0]}: 均值={mean0:.3f}, 标准差={sd0:.3f}')
print(f'{col_names[1]}: 均值={mean1:.3f}, 标准差={sd1:.3f}')
print(f'P值 = {p_value:.4f}')
print(f'Y轴刻度: {yticks.tolist()}')