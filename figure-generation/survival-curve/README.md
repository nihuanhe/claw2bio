# survival-curve

Publication-ready Kaplan-Meier survival curve (+ univariate Cox) from a
clinical follow-up table with a continuous biomarker column.

- **Pipeline**: clean → `surv_cutpoint` (maxstat, min group ≥30%) → KM +
  log-rank + risk table → univariate Cox (HR forest plot) → 600 dpi PNG/PDF + CSV.
- **Form**: single R template with a CONFIG block (paths / column-name
  mapping / palette). No CLI, no WSL needed.
- **Examples**: the tutorial's public teaching dataset (52 patients,
  synthetic) — see below.

Read [SKILL.md](SKILL.md) first.

## Example data provenance

`examples/input/Survival-data.csv` derives from the **public teaching example
file** distributed by the WeChat tutorial《零基础——R语言生存分析出图》(公众号
"小云科研", 2025-11-02, https://mp.weixin.qq.com/s/K8SQgnX2mBHqu7JW_NU15g).
It is synthetic teaching data, **no real patient information**. We converted
the original xlsx to UTF-8 CSV (AI-agent friendly: readable, diffable) and
**dropped the `患者名字` column** (placeholder fake names such as 张三/张四 —
unused by the pipeline, removed to keep the repo free of anything resembling
patient identifiers).

| Column | Meaning |
|---|---|
| `存活0,死亡1` | event indicator: 1 = death, 0 = censored/alive |
| `术后x月` | follow-up time in months |
| `IHC` | continuous biomarker score (IHC pathology score) |

Note: if you edit the CSV in Excel, save as "CSV UTF-8" — Chinese-locale
Excel otherwise writes GBK, which breaks the column names.

The original tutorial script is kept verbatim at
`scripts/Survival_original.R` for comparison; the reusable template is
`scripts/survival_curve_template.R`.

## Quick start

```r
cd figure-generation/survival-curve
Rscript scripts/survival_curve_template.R
```

Expected anchors: `cutpoint = 39.49`, `n_low = 36 | n_high = 16`,
`logrank p = 0.06897`, `Cox HR (High vs Low) = 3.47 (0.853-14.114)`.

To use your own data: keep the same 3 required columns (event 0/1, time,
marker), then edit only the CONFIG block at the top of the template.
