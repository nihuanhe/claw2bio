# Clinical Tables

> One-line: patient-level CSV in — publication-ready three-line tables out (baseline characteristics, correlation matrix, Cox regression, OR summary).

::: info Get this skill · 获取本技能
**Option A — one-click agent prompt (recommended).** Copy this into your AI agent IDE:

```
Please set up the "clinical-table" skill from the Claw2Bio library for me:
1. Fetch only the folder "figure-generation/clinical-table" from the GitHub repo
   https://github.com/claw2bio/claw2bio (use sparse checkout; do not clone the whole repo).
2. Read its SKILL.md and register the skill.
3. Run the bundled example in examples/ to verify my environment, and show me the output tables.
```

**Option B — standalone zip** (few MB, Tencent COS direct link): *available at site launch*.

**Option C — full example dataset** (COS, per-skill folder): *available at site launch*.
:::

## What it does

1. **Baseline characteristics tables** — marker high/low groups × Age, Sex, BMI, Tumor differentiation, Cancer stage, with n (%) and p values.
2. **Correlation matrix** — Pearson + Spearman among marker columns.
3. **Cox regression** — automatic univariate + multivariate tables when `survival_time` / `survival_event` columns exist.
4. **OR summary** — OR (95% CI) for Fisher exact 2×2 tables.

Output is Markdown three-line tables, convertible to DOCX with Pandoc (`pandoc output.md -o output.docx`).

## Quick start (30 seconds)

```bash
cd figure-generation/clinical-table
pip install pandas numpy scipy statsmodels
python scripts/clinical_table.py examples/input/demo_patients.csv examples/output/clinical_tables.md
```

## Input format

Patient-level CSV. Required: marker columns (continuous, e.g. `HAMA`), `Sex`, `Age`(or `Age-`), `BMI`(or `BMI-`), `Tumor differentiation`, `Cancer stage`. Grouping columns `<MARKER>--` with `high`/`low` — or let the skill group automatically:

```bash
# median-based grouping
python scripts/clinical_table.py input.csv output.md --auto-group
# explicit cutoffs
python scripts/clinical_table.py input.csv output.md --auto-group --group-cutoffs '{"HAMA":29}'
```

Marker names are configurable via `--config config.json` (see `DEFAULT_CONFIG` in the script).

## Output files

| File | Content |
|---|---|
| `clinical_tables.md` | All tables in three-line Markdown format |

## Troubleshooting

- **Grouping columns missing** → add `--auto-group`.
- **Cox table absent** → it only appears when both `survival_time` and `survival_event` columns exist.
- ** lifelines install fails** → not needed; Cox is implemented with statsmodels PHReg.

## Links

- [Source & SKILL.md on GitHub](https://github.com/claw2bio/claw2bio/tree/main/figure-generation/clinical-table)
- Related skills: [Grouped bar plot](/skills/barplot)
