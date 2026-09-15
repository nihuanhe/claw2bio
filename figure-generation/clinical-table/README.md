# clinical-table

Automated clinical statistics table generator. Takes a patient-level CSV and outputs publication-ready three-line Markdown tables, directly convertible to DOCX with Pandoc.

临床统计表自动化生成工具。输入患者级别的 CSV，自动输出发表级 Markdown 三线表，可直接用 Pandoc 转换为 DOCX。

## Features

1. **Baseline characteristics tables**: marker high vs low groups cross-tabulated with Age, Sex, BMI, Tumor differentiation, and Cancer stage; outputs n (%) and p values.
2. **Correlation matrix**: Pearson and Spearman correlations among the continuous marker columns.
3. **Cox regression**: if the CSV contains survival time (`survival_time`) and event (`survival_event`) columns, univariate and multivariate Cox regression tables are produced automatically.
4. **OR summary**: OR (95% CI) reported separately for Fisher exact 2×2 tables.

## Installation

Python 3.10+ with:

```bash
pip install pandas numpy scipy statsmodels
```

(`lifelines` conflicts with pandas 3.x; this tool implements Cox regression via `statsmodels.duration.hazard_regression.PHReg`.)

## Quick start

```bash
cd clinical-table
python scripts/clinical_table.py examples/input/demo_patients.csv examples/output/clinical_tables.md
```

## Input CSV format

See `examples/input/demo_patients.csv`. Required columns:

| Column | Description |
|---|---|
| marker columns (e.g. `HAMA` / `FOXP3` / `NOXA`) | continuous variables (numeric) |
| `<MARKER>--` (e.g. `HAMA--`) | group variable: `high` / `low` (pre-assigned by the user) |
| `Age` / `Age-` | age category or raw age |
| `Sex` | `Female` / `Male` |
| `BMI` / `BMI-` | BMI category or raw BMI |
| `Tumor differentiation` | tumor differentiation: G2 / G3 / Miss, etc. |
| `Cancer stage` / `Cancer stage--` | cancer stage: I - II / III - IV, etc. |
| `survival_time` (optional) | survival time |
| `survival_event` (optional) | survival event (0 = censored, 1 = event) |

## Grouping modes

By default the script reads existing `<MARKER>--` columns as high/low groups. If they are missing:

```bash
# median-based automatic grouping
python scripts/clinical_table.py input.csv output.md --auto-group

# grouping by explicit cutoffs
python scripts/clinical_table.py input.csv output.md --auto-group --group-cutoffs '{"HAMA":29,"NOXA":25}'
```

## Custom configuration

Use `--config config.json` to override default field mappings, grouping variables, clinical variables, etc. See `DEFAULT_CONFIG` in `scripts/clinical_table.py` for the defaults.

## Output

Markdown three-line tables at `examples/output/clinical_tables.md`. Convert directly with Pandoc:

```bash
pandoc clinical_tables.md -o clinical_tables.docx
```

## File structure

```
clinical-table/
├── README.md
├── SKILL.md
├── scripts/
│   ├── clinical_table.py   # main pipeline
│   └── stats_utils.py      # statistics utilities
├── examples/
│   ├── input/demo_patients.csv
│   └── output/clinical_tables.md
└── .gitignore
```

## Statistical methods

- Contingency tables: Fisher exact test when any expected count < 5, otherwise χ² test.
- OR and 95% CI: Woolf method; reported only for Fisher exact 2×2 tables.
- Correlations: both Pearson r and Spearman ρ reported.
- Cox regression: the multivariate model includes variables with univariate p < 0.10 plus Cancer stage.
- Significance marks: `* p<0.05`, `** p<0.01`, `*** p<0.001`.
