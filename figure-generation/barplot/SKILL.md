---
name: barplot
description: Grouped bar plots from a wide-format CSV (one group per column), auto-selecting the right 2–6 group script. Publication-ready PNG with error bars, scatter points, and significance annotations.（中文摘要：输入宽表 CSV（每列一组），自动按列数选择 2–6 组柱状图脚本，生成带误差线、散点和统计标注的发表级 PNG。）
---

# Skill: barplot

## Trigger phrases

- bar plot / barplot
- grouped bar chart
- draw a bar plot
- 画柱状图 / 分组柱状图

## What it does

Takes a wide-format CSV (one column per group), auto-selects the matching 2–6 group bar plot script by column count, and generates a publication-ready PNG with error bars, scatter points, and statistics annotations.

## Usage

### Auto-select script

```bash
python scripts/run_barplot.py <input.csv>
```

### Call a specific script (alternative palettes)

The default launcher picks the standard palette by column count. The following scripts are **alternative palettes** with identical statistics logic:

- 2 groups, alternative (green/pink): `barplot_2col_green_pink.py`
- 3 groups, alternative (light orange/blue/green): `barplot_3col_light.py`

```bash
python scripts/barplot_2col_green_pink.py <input.csv>
python scripts/barplot_3col_light.py <input.csv>
```

## Input format

Wide-format CSV: one column per experimental group, one row per biological replicate:

```csv
Ctrl,Stress
10,12
11,9
13,14
```

## Output

- PNG saved next to the input CSV by default, named `<input>_barplot.png`
- 2 groups: t-test P value annotation
- ≥3 groups: ANOVA P value + Tukey HSD pairwise annotations
- Y-axis range auto-computed as `max(data max, mean + SD)`, automatically extended by one extra step when scatter points/error bars would overflow, avoiding truncation

## Customization

- Title and Y-axis label: edit `FIGURE_NAME` and `Y_LABEL` at the top of the script
- Colors: edit the `bar_colors` / `point_colors` lists at the top of the script

## Example

```bash
cd barplot
python scripts/run_barplot.py examples/input/data.csv
```

## Dependencies

Python 3.10+ with:

```bash
pip install pandas numpy scipy matplotlib statsmodels
```

## Notes

- Supports 2–6 columns (groups).
- Non-numeric columns (e.g. a `sample` name column) are ignored automatically.

> 中文提示：支持 2–6 组；非数值列会被自动忽略；标题、Y 轴标签和配色在各脚本顶部修改。
