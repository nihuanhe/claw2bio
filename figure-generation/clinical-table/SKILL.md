---
name: clinical-table
description: Auto-generate publication-ready clinical statistics tables (three-line Markdown tables) from a patient-level CSV. Includes baseline characteristics tables, correlation matrices, Cox survival regression, and Fisher exact test OR summaries.（中文摘要：根据患者 CSV 自动生成发表级 Markdown 三线表：基线特征表、相关性矩阵、Cox 生存回归表、Fisher 精确检验 OR 汇总。）
---

# Skill: clinical-table

## Trigger phrases

- clinical baseline table
- Table 1 / baseline characteristics
- clinical statistics table
- Cox regression table
- 生成临床统计表 / 临床基线特征表 / 三线表

## What it does

Generates publication-ready three-line Markdown tables from a patient CSV:

1. Baseline characteristics tables (marker high vs low × clinical variables)
2. Correlation matrix for the marker columns (Pearson + Spearman)
3. Cox survival regression table (optional; requires `survival_time` / `survival_event` columns)
4. Fisher exact test OR (95% CI) summary

## Usage

### Mode 1: groups already assigned

The input CSV must contain `<MARKER>--` columns (e.g. `HAMA--`) with values `high` / `low`.

```bash
python scripts/clinical_table.py <input.csv> <output.md>
```

### Mode 2: automatic grouping by cutoff

If only continuous marker columns (e.g. `HAMA`) are present:

```bash
# median-based automatic grouping
python scripts/clinical_table.py <input.csv> <output.md> --auto-group

# grouping by explicit cutoffs
python scripts/clinical_table.py <input.csv> <output.md> --auto-group --group-cutoffs '{"HAMA":29,"NOXA":25,"FOXP3":30}'
```

## Input CSV field requirements

| Field | Required | Description |
|---|---|---|
| marker columns (e.g. `HAMA`) | yes | continuous variables |
| `<MARKER>--` (e.g. `HAMA--`) | either/or | pre-assigned high/low groups; if missing, enable `--auto-group` |
| `Age` or `Age-` | yes | age category or numeric age |
| `Sex` | yes | Female / Male |
| `BMI` or `BMI-` | yes | BMI category or numeric BMI |
| `Tumor differentiation` | yes | e.g. G2 / G3 / Miss |
| `Cancer stage` or `Cancer stage--` | yes | e.g. I - II / III - IV |
| `survival_time` | no | survival time (months) |
| `survival_event` | no | 0 = censored, 1 = event |

Note: marker names are configurable via `--config`; the bundled example uses HAMA / FOXP3 / NOXA.

## Output

- Markdown three-line tables: `output.md`
- Convert to DOCX with Pandoc: `pandoc output.md -o output.docx`

## Example

```bash
cd clinical-table
python scripts/clinical_table.py examples/input/demo_patients.csv examples/output/clinical_tables.md
```

## Dependencies

Python 3.10+ with:

```bash
pip install pandas numpy scipy statsmodels
```

## Notes

- Never modifies the input CSV.
- Cox regression uses statsmodels PHReg (lifelines is not required).
- Significance marks: `* p<0.05`, `** p<0.01`, `*** p<0.001`.

> 中文提示：不修改原始 CSV；Cox 回归用 statsmodels PHReg 实现，无需 lifelines；标志物列名可通过 `--config` 自定义，示例使用 HAMA/FOXP3/NOXA。
