# Western Blot 定量计算完整流程

## 概述

本流程将 ImageJ 定量得到的原始 Western Blot 数据（目的蛋白 Mean 值 + beta-actin 内参 Mean 值）转化为归一化后的柱状图（含散点、误差线、t 检验显著性标注）。

整个流程分为 **3 个步骤**：
1. **准备输入 CSV** — 整理 ImageJ 定量结果
2. **数据归一化 + 统计检验** — 除以内参、计算统计量、保存中间 CSV
3. **作图** — 生成柱状图 PNG

> **注意**：步骤 2 和步骤 3 已合并封装为本技能的 `scripts/wb_pipeline.py`（CLI 参数传入，无需改代码），本文档内嵌的两个脚本是**原始参考版本**（含硬编码路径，仅供理解计算逻辑）。实际执行统一使用：
>
> ```bash
> python scripts/wb_pipeline.py <input.csv> --control "Ctrl" [--output-dir <目录>]
> ```

---

## 步骤 1 — 准备输入 CSV

### 输入文件格式

CSV 必须包含以下列（列名严格一致）：

```csv
Protein,Sample,Mean_Rep1,Mean_Rep2,Mean_Rep3,beta_actin_mean
p-TBK1,Ctrl,148.526,154.316,147.763,128.6593333
p-TBK1,Stress,181.056,193.876,187.727,122.8193333
p-IRF3,Ctrl,166.994,180.175,173.015,128.6593333
p-IRF3,Stress,196.338,213.772,191.681,122.8193333
FOXP3,Ctrl,118.478,134.568,110.583,128.6593333
FOXP3,Stress,211.114,206.834,207.731,122.8193333
```

### 字段说明

| 字段 | 说明 |
|------|------|
| `Protein` | 目的蛋白名称（如 p-TBK1, p-IRF3, FOXP3），用作 X 轴标签 |
| `Sample` | **样本条件/分组**（如 Ctrl, Stress, TreatmentA, TreatmentB...），最多支持 **6 个**不同的 Sample 值 |
| `Mean_Rep1/2/3` | 该蛋白在 3 次重复中的 ImageJ 定量 Mean 值 |
| `beta_actin_mean` | **内参（beta-actin）的 Mean 值**，按 Sample 分组，同一 Sample 下所有 Protein 共享此值 |

### 灵活扩展规则

- **Sample 数量**：可以是 2~6 个（2组、3组、4组、5组、6组均可）
- **Protein 数量**：可以是任意数量（1个、多个）
- **重复次数**：`scripts/wb_pipeline.py` 会自动检测 `Mean_Rep1/2/3...` 列数，不限于 3 次；本文档内嵌的原始参考脚本固定为 3 次重复
- **beta_actin_mean**：每个 Sample 只能有 **一个** beta_actin_mean 值，该 Sample 下的所有 Protein 行使用同一数值

#### 示例：3 个 Sample × 2 个 Protein 的输入 CSV

```csv
Protein,Sample,Mean_Rep1,Mean_Rep2,Mean_Rep3,beta_actin_mean
ProA,Ctrl,100.0,105.0,102.0,120.0
ProA,Treat_Low,130.0,135.0,132.0,118.0
ProA,Treat_High,160.0,165.0,162.0,115.0
ProB,Ctrl,80.0,82.0,81.0,120.0
ProB,Treat_Low,90.0,95.0,92.0,118.0
ProB,Treat_High,110.0,115.0,112.0,115.0
```

#### 示例：6 个 Sample × 1 个 Protein 的输入 CSV

```csv
Protein,Sample,Mean_Rep1,Mean_Rep2,Mean_Rep3,beta_actin_mean
ProA,Ctrl,100.0,105.0,102.0,120.0
ProA,S1,110.0,115.0,112.0,119.0
ProA,S2,120.0,125.0,122.0,118.0
ProA,S3,130.0,135.0,132.0,117.0
ProA,S4,140.0,145.0,142.0,116.0
ProA,S5,150.0,155.0,152.0,115.0
```

---

## 步骤 2 — 数据归一化 + t 检验计算

### 归一化公式

对每个 `(Protein, Sample)` 行：

```
Normalized_RepX = Mean_RepX / beta_actin_mean
```

### 输出文件格式

生成的文件在输入 CSV **同目录**，文件名自动与输入 CSV 同名（保留原文件名，不追加任何后缀）。

以 `FigureR9 - 输入数据.csv` 为例，输出为 `FigureR9 - 输入数据.csv`（覆盖原文件）。

### 计算逻辑（归一化脚本自动完成）

1. **归一化**：`Normalized_RepX = Mean_RepX / beta_actin_mean`
2. **均值**：`Normalized_Mean = average(Normalized_Rep1, Normalized_Rep2, Normalized_Rep3)`
3. **标准差**（样本标准差，ddof=1）：`Normalized_SD`
4. **标准误**：`Normalized_SEM = Normalized_SD / sqrt(3)`
5. **统计检验**（`scripts/wb_pipeline.py` 按 Sample 数自动分支）：
   - **2 个 Sample**：独立样本 t 检验（`scipy.stats.ttest_ind(..., equal_var=True)`），对每个 Protein 比较两组，p 值写入该 Protein 的所有行
   - **≥3 个 Sample**：单因素 ANOVA + Tukey HSD，ANOVA_F/ANOVA_p 写入该 Protein 所有行；与对照组（`--control` 指定）两两比较的校正后 p 值写入对应非对照行
   - 下方内嵌的原始参考脚本仅演示 2 组 t 检验逻辑：以该 Protein 下出现的第一个 Sample 为对照（通常为 Ctrl），自由度 df = n1 + n2 - 2 = 3 + 3 - 2 = 4

> **注意**：内嵌参考脚本的 t 检验结果写入**非对照 Sample 行**（对照行留空）；`wb_pipeline.py` 在 2 组时写入该 Protein 的所有行。

### 归一化脚本

```python
import pandas as pd
import numpy as np
from scipy import stats
import math

# ==================== 配置（每次使用前修改） ====================
INPUT_CSV = r'D:\小文章\WB计算\示例\FigureR9 - 输入数据.csv'
CONTROL_SAMPLE = 'Ctrl'   # 对照组的 Sample 名称，用于 t 检验对照
# ================================================================

df = pd.read_csv(INPUT_CSV)

# 归一化
df['Normalized_Rep1'] = df['Mean_Rep1'] / df['beta_actin_mean']
df['Normalized_Rep2'] = df['Mean_Rep2'] / df['beta_actin_mean']
df['Normalized_Rep3'] = df['Mean_Rep3'] / df['beta_actin_mean']
df['Normalized_Mean'] = (df['Normalized_Rep1'] + df['Normalized_Rep2'] + df['Normalized_Rep3']) / 3

def calc_sd(row):
    vals = [row['Normalized_Rep1'], row['Normalized_Rep2'], row['Normalized_Rep3']]
    return np.std(vals, ddof=1)

df['Normalized_SD'] = df.apply(calc_sd, axis=1)
df['Normalized_SEM'] = df['Normalized_SD'] / math.sqrt(3)

# 新增列
df['t_statistic'] = None
df['df'] = None
df['p_value'] = None
df['Significance'] = ''

# t 检验：每个 Protein，每个非对照 Sample vs 对照 Sample
proteins = df['Protein'].unique()
for prot in proteins:
    control = df[(df['Protein'] == prot) & (df['Sample'] == CONTROL_SAMPLE)]
    if len(control) == 0:
        continue
    control_vals = control[['Normalized_Rep1', 'Normalized_Rep2', 'Normalized_Rep3']].values[0]

    others = df[(df['Protein'] == prot) & (df['Sample'] != CONTROL_SAMPLE)]
    for idx in others.index:
        other_vals = others.loc[idx, ['Normalized_Rep1', 'Normalized_Rep2', 'Normalized_Rep3']].values

        t_stat, p_val = stats.ttest_ind(control_vals, other_vals, equal_var=True)

        df.at[idx, 't_statistic'] = round(t_stat, 4) if not math.isnan(t_stat) else None
        df.at[idx, 'df'] = len(control_vals) + len(other_vals) - 2  # = 4
        df.at[idx, 'p_value'] = round(p_val, 4) if not math.isnan(p_val) else None
        if p_val < 0.001:
            df.at[idx, 'Significance'] = '***'
        elif p_val < 0.01:
            df.at[idx, 'Significance'] = '**'
        elif p_val < 0.05:
            df.at[idx, 'Significance'] = '*'
        else:
            df.at[idx, 'Significance'] = 'ns'

# 保存（覆盖原文件）
df.to_csv(INPUT_CSV, index=False, encoding='utf-8-sig')
print(f'归一化结果已保存到: {INPUT_CSV}')
```

---

## 步骤 3 — 作图（柱状图 + 散点 + 误差线）

### Sample 数量与配色关系

根据 Sample 数量自动选择配色（`scripts/wb_pipeline.py` 内置 `COLOR_SCHEMES`）：

| Sample 数 | 柱子颜色（bar_colors） | 散点颜色（point_colors） | 参考来源 |
|-----------|----------------------|------------------------|----------|
| 2 | `#009E73`, `#CC79A7` | `#80FFD7`, `#EBC8E1` | 之前的绿粉配色 |
| 3 | `#808080`, `#009E73`, `#CC79A7` | `#D3D3D3`, `#80FFD7`, `#EBC8E1` | 灰/绿/粉 |
| 4 | `#0072B2`, `#D55E00`, `#009E73`, `#CC79A7` | `#80FFFF`, `#EDA461`, `#90EE90`, `#D683F1` | 6色调色板取前4 |
| 5 | `#0072B2`, `#D55E00`, `#009E73`, `#CC79A7`, `#E69F00` | `#80FFFF`, `#EDA461`, `#90EE90`, `#D683F1`, `#FAD7A0` | 6色调色板取前5 |
| 6 | `#0072B2`, `#D55E00`, `#009E73`, `#CC79A7`, `#E69F00`, `#56B4E9` | `#80FFFF`, `#EDA461`, `#90EE90`, `#D683F1`, `#FAD7A0`, `#A8E6FF` | `barplot_6col.py` 完整6色 |

> 6 色调色板基于 Wong 2011 色盲友好配色方案。

### 作图脚本关键逻辑

1. **自动检测** Sample 数量和 Protein 数量
2. **动态布局**：
   - 每对柱子间距根据 Protein 数量自动适配
   - X 轴标签为 Protein 名称
   - 图例说明底部标注柱子的对应关系
3. **每个 Protein 为一组**：组内 Show 所有 Sample 的柱子+散点
4. **统计标注**：右侧列出每个 Protein 的 t 检验结果
5. **Y 轴**：自动从 0 开始，3~6 个刻度

### 作图脚本（完整版，兼容 2~6 个 Sample）

```python
import csv
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import math

# ==================== 配置（每次使用前修改） ====================
INPUT_CSV = r'D:\小文章\WB计算\示例\FigureR9.csv'
FIGURE_NAME = 'Figure Title'
Y_LABEL     = 'Relative protein expression'
CONTROL_SAMPLE = 'Ctrl'
ERROR_TYPE = 'SD'        # 'SD' 或 'SEM'
DRAW_POINTS = True
# ================================================================

# 6色调色板（Wong 2011 色盲友好）
BAR_COLORS = ['#0072B2', '#D55E00', '#009E73', '#CC79A7', '#E69F00', '#56B4E9']
POINT_COLORS = ['#80FFFF', '#EDA461', '#90EE90', '#D683F1', '#FAD7A0', '#A8E6FF']

OUTPUT_PNG = os.path.splitext(INPUT_CSV)[0] + '.png'

# ===== 读取CSV =====
rows = []
with open(INPUT_CSV, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    numeric_cols = ['Mean_Rep1', 'Mean_Rep2', 'Mean_Rep3',
                    'beta_actin_mean', 'Normalized_Rep1', 'Normalized_Rep2', 'Normalized_Rep3',
                    'Normalized_Mean', 'Normalized_SD', 'Normalized_SEM',
                    't_statistic', 'df', 'p_value']
    for row in reader:
        for k in numeric_cols:
            if k in row and row[k].strip() == '':
                row[k] = None
            elif k in row:
                row[k] = float(row[k].strip())
        rows.append(row)

# ===== 解析分组 =====
samples_ordered = []
for r in rows:
    if r['Sample'] not in samples_ordered:
        samples_ordered.append(r['Sample'])
n_samples = len(samples_ordered)

proteins_ordered = []
for r in rows:
    if r['Protein'] not in proteins_ordered:
        proteins_ordered.append(r['Protein'])
n_proteins = len(proteins_ordered)

print(f"检测到 {n_proteins} 个蛋白: {proteins_ordered}")
print(f"检测到 {n_samples} 个Sample: {samples_ordered}")

# 验证 Sample 数不超过 6
if n_samples > 6:
    raise ValueError(f"当前支持最多6个Sample，检测到{n_samples}个")

# ===== 提取归一化数据 =====
# data_by_protein[protein][sample] = {'vals': [3个值], 'mean': float, 'sd': float, 'sem': float, 'p': float}
data_by_protein = {}
for prot in proteins_ordered:
    data_by_protein[prot] = {}
    for samp in samples_ordered:
        matched = [r for r in rows if r['Protein'] == prot and r['Sample'] == samp]
        if matched:
            r = matched[0]
            data_by_protein[prot][samp] = {
                'vals': [r['Normalized_Rep1'], r['Normalized_Rep2'], r['Normalized_Rep3']],
                'mean': r['Normalized_Mean'] if r['Normalized_Mean'] is not None else 0,
                'sd': r['Normalized_SD'] if r['Normalized_SD'] is not None else 0,
                'sem': r['Normalized_SEM'] if r['Normalized_SEM'] is not None else 0,
                'p': r['p_value'] if r['p_value'] is not None else 1.0,
            }
        else:
            data_by_protein[prot][samp] = None

# ===== Y轴范围 =====
all_vals = []
for prot in proteins_ordered:
    for samp in samples_ordered:
        d = data_by_protein[prot][samp]
        if d:
            all_vals.append(d['mean'] + d['sd'])
if not all_vals:
    all_vals = [1]
ymax_raw = max(all_vals)
candidate_steps = [0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
y_max = None
step = None
for s in candidate_steps:
    cand = math.ceil(ymax_raw / s) * s
    n_ticks = int(cand / s) + 1
    if 3 <= n_ticks <= 6:
        step = s
        y_max = cand
        break
if y_max is None:
    step = candidate_steps[-1]
    y_max = math.ceil(ymax_raw / step) * step
yticks = np.arange(0, y_max + step, step)

# ===== 布局 =====
bar_width = 1.7 / 7
intra_gap = 0.08
inter_gap = 1.0
fig_width = max(7.5, n_proteins * inter_gap + 4.0)
fig, ax = plt.subplots(figsize=(fig_width, 6.5))

x_centers = np.arange(n_proteins) * inter_gap
# n_samples 个柱子：分布在宽度 bar_width 范围内，两侧各留 (bar_width - bar_width*n_samples/(n_samples+1)) 空隙
# 简化：每个 Sample 偏移
sample_offsets = np.linspace(-bar_width/2 + intra_gap/2, bar_width/2 - intra_gap/2, n_samples)

# 颜色（取前 n_samples 个）
bar_colors = BAR_COLORS[:n_samples]
point_colors = POINT_COLORS[:n_samples]

# ===== 绘图 =====
for si, samp in enumerate(samples_ordered):
    means_arr = []
    errs_arr = []
    vals_arr = []
    for pi, prot in enumerate(proteins_ordered):
        d = data_by_protein[prot][samp]
        if d is None:
            means_arr.append(0)
            errs_arr.append(0)
            vals_arr.append([])
        else:
            means_arr.append(d['mean'])
            errs_arr.append(d['sd'] if ERROR_TYPE == 'SD' else d['sem'])
            vals_arr.append(d['vals'])

    x_pos = x_centers + sample_offsets[si]

    # 柱子
    ax.bar(x_pos, means_arr, width=bar_width * 0.85 / n_samples,
           color=bar_colors[si], edgecolor='black', linewidth=1.2, zorder=3,
           label=samp)

    # 误差线
    zeros = np.zeros_like(errs_arr)
    ax.errorbar(x_pos, means_arr, yerr=[zeros, errs_arr], fmt='none',
                capsize=5, elinewidth=1.5, capthick=1.5, ecolor='black', zorder=4)

    # 散点
    if DRAW_POINTS:
        np.random.seed(42 + si)
        for pi, prot in enumerate(proteins_ordered):
            vals = data_by_protein[prot][samp]
            if vals is None or len(vals['vals']) == 0:
                continue
            n_pts = len(vals['vals'])
            jitter = np.random.normal(0, 0.02, size=n_pts)
            ax.scatter(x_pos[pi] + jitter, vals['vals'],
                       marker='o', facecolors=point_colors[si], edgecolors='black',
                       s=120, zorder=5, linewidths=1.2, alpha=0.9)

# ===== 坐标轴 =====
ax.set_xticks(x_centers)
ax.set_xticklabels(proteins_ordered, fontsize=13, fontfamily='Arial',
                   fontweight='normal', rotation=45, ha='right')
ax.set_yticks(yticks)
ax.set_ylim(0, y_max)
ax.set_ylabel(Y_LABEL, fontsize=14, fontfamily='Arial', fontweight='normal', labelpad=12)
ax.tick_params(axis='y', pad=8, labelsize=13, length=8, width=2)
ax.tick_params(axis='x', length=8, width=2)

for item in ([ax.xaxis.label, ax.yaxis.label] +
             ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontfamily('Arial')
    item.set_fontweight('normal')

# ===== 图例 =====
ax.legend(fontsize=10, frameon=False)

# ===== P 值标注 =====
p_lines = []
for prot in proteins_ordered:
    for samp in samples_ordered:
        d = data_by_protein[prot][samp]
        if d is None or samp == CONTROL_SAMPLE:
            continue
        p = d['p']
        if p < 0.001:
            p_str = '***'
        elif p < 0.01:
            p_str = '**'
        elif p < 0.05:
            p_str = '*'
        else:
            p_str = 'ns'
        p_lines.append(f'{prot} {samp}: {p_str} (P≈{p:.3f})')

if p_lines:
    p_text = '\n'.join(p_lines)
    ax.text(1.02, 0.98, p_text, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', fontfamily='Arial', fontweight='normal',
            linespacing=1.4)

# ===== 标题 =====
ax.text(0.5, 1.02, FIGURE_NAME, transform=ax.transAxes,
        fontsize=14, fontfamily='Arial', fontweight='normal',
        horizontalalignment='center', verticalalignment='bottom')

# ===== 样式 =====
ax.set_facecolor('white')
fig.patch.set_facecolor('white')
ax.grid(False)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_linewidth(2)
ax.spines['left'].set_linewidth(2)

# ===== 保存 =====
plt.tight_layout()
plt.savefig(OUTPUT_PNG, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print(f'图表已保存到: {OUTPUT_PNG}')
```

### 作图脚本参数速查

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `INPUT_CSV` | 步骤 2 输出的归一化 CSV 路径 | 必填 |
| `FIGURE_NAME` | 图表标题文字 | `'Figure Title'` |
| `Y_LABEL` | Y 轴标签 | `'Relative protein expression'` |
| `CONTROL_SAMPLE` | 对照组的 Sample 名称 | `'Ctrl'` |
| `ERROR_TYPE` | 误差线显示 SD 还是 SEM | `'SD'` |
| `DRAW_POINTS` | 是否显示散点 | `True` |

---

## 完整执行流程

```
输入 CSV（原始 Mean 值 + beta_actin_mean）
        │
        ▼
  [归一化脚本]  → 步骤 2
        │
        ▼
  同一 CSV 文件（新增归一化列 + t检验结果）
        │
        ▼
  [作图脚本]  → 步骤 3
        │
        ▼
  PNG 文件（与 CSV 同名，同一目录）
```

### 快速开始（新对话使用）

1. **确认数据路径**：确保输入 CSV 存在
2. **修改归一化脚本的 `INPUT_CSV` 和 `CONTROL_SAMPLE`**
3. **运行归一化脚本**（依赖：`pandas`, `numpy`, `scipy`）
4. **修改作图脚本的配置**（`INPUT_CSV`, `FIGURE_NAME`, `Y_LABEL` 等）
5. **运行作图脚本**（依赖：`matplotlib`, `numpy`）
6. **检查输出的 PNG**

### 依赖包

```bash
pip install pandas numpy scipy matplotlib
```

---

## 已知限制

- 内嵌的原始参考脚本每组固定 3 次重复；`scripts/wb_pipeline.py` 已改为自动检测 `Mean_RepN` 列数
- 最多支持 6 个不同的 Sample
- 2 组比较为等方差独立样本 t 检验（Student's t-test）
