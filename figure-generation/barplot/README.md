# barplot

Grouped bar plot generator that auto-selects the right script based on CSV column count.

根据 CSV 列数自动选择对应脚本的分组柱状图生成工具。

## Features

- Reads a wide-format CSV, one column per group
- Auto-selects the 2/3/4/5/6-group script based on the number of numeric columns
- 2 groups: unpaired t-test
- ≥3 groups: one-way ANOVA + Tukey HSD pairwise comparisons
- Outputs a 300-dpi PNG with mean, SD, scatter points, and P value annotations

## Installation

Python 3.10+ with:

```bash
pip install pandas numpy scipy matplotlib statsmodels
```

## Quick start

```bash
cd barplot
python scripts/run_barplot.py examples/input/data.csv
```

The output is saved next to the input CSV as `<input>_barplot.png`. To place it in `examples/output/`, move it manually or use the `--output` option (see individual script docs).

## Input CSV format

Wide format: one column per experimental group, one row per biological replicate. Example:

```csv
Ctrl-BD-sEVs,Stress-BD-sEVs
18533,13055
20650,10017
19467,21995
23250,8965
21240,16695
```

## Script reference

| Columns | Default script | Statistics | Default palette |
|---|---|---|---|
| 2 | `barplot_2col.py` | t-test | blue/orange |
| 2 (alt green/pink) | `barplot_2col_green_pink.py` | t-test | green/pink |
| 3 | `barplot_3col.py` | ANOVA + Tukey | blue/orange/green |
| 3 (alt light) | `barplot_3col_light.py` | ANOVA + Tukey | orange/blue/green (light) |
| 4 | `barplot_4col.py` | ANOVA + Tukey | blue/orange/green/pink |
| 5 | `barplot_5col.py` | ANOVA + Tukey | five colors |
| 6 | `barplot_6col.py` | ANOVA + Tukey | six colors |

**About alternative palettes**:
- `barplot_2col_green_pink.py` is an **alternative palette** (green/pink) for 2-group data, with statistics identical to the default `barplot_2col.py` (blue/orange).
- `barplot_3col_light.py` is an **alternative palette** (lighter orange/blue/green) for 3-group data, with statistics identical to the default `barplot_3col.py`.
- The default launcher `run_barplot.py` auto-selects the default script by column count; call the alternative script directly when you want its palette.

## Custom title and Y-axis label

Edit at the top of the corresponding script:

```python
FIGURE_NAME = 'ELISA'
Y_LABEL     = 'IFNβ (pg/mL)'
```

## Calling a specific script directly

To force a palette or script, run it directly:

```bash
python scripts/barplot_3col_light.py examples/input/data_4col.csv
```

## File structure

```
barplot/
├── README.md
├── SKILL.md
├── scripts/
│   ├── run_barplot.py              # auto-selects script by column count
│   ├── barplot_2col.py
│   ├── barplot_2col_green_pink.py
│   ├── barplot_3col.py
│   ├── barplot_3col_light.py
│   ├── barplot_4col.py
│   ├── barplot_5col.py
│   └── barplot_6col.py
├── examples/
│   ├── input/
│   │   ├── data.csv        # 2-group example
│   │   ├── data_4col.csv   # 4-group example
│   │   └── data_6col.csv   # 6-group example
│   └── output/
│       ├── data_barplot.png
│       ├── data_4col_barplot.png
│       └── data_6col_barplot.png
└── .gitignore
```

## Automatic Y-axis range

The scripts compute the Y-axis range dynamically:

1. Use `max(data max, mean + SD)` as the data ceiling;
2. Pick a "pretty" step size so the tick count falls between 3 and 6;
3. If scatter points/error bars with a 5% visual margin would overflow, extend the ceiling by one more step to avoid truncation.

Resulting ranges for the bundled examples:
- 2-column example: Y axis 0–30000
- 4-column example (data near the boundary): Y axis 0–8000
- 6-column example: Y axis 0–200

## Notes

- Hard-coded paths in the original scripts have been replaced with command-line arguments.
- Title, Y-axis label, and colors remain hard-coded at the top of each script, so each figure can be tuned individually.
- The output PNG is saved next to the input CSV by default; to route outputs into `examples/output/`, move them after running or customize the `output_path` variable at the top of the script.
