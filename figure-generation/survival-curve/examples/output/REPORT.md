# REPORT — survival-curve example run (2026-09-16)

Example: the public teaching dataset from the WeChat tutorial《零基础——R语言
生存分析出图》(公众号"小云科研", synthetic, 52 patients). No patient data.

## Step executed

`Rscript scripts/survival_curve_template.R` (Windows R 4.5.2;
survival 3.x / survminer 0.5.2 / readxl / dplyr)

Console anchors:

```
ANCHOR: input rows = 52
ANCHOR: clean rows = 52 | events = 9
ANCHOR: cutpoint = 39.49            (surv_cutpoint, maxstat, minprop=0.30)
ANCHOR: n_low = 36 | n_high = 16
ANCHOR: logrank p = 0.06897
ANCHOR: Cox HR (High vs Low) = 3.47 | 95%CI = 0.853 - 14.114 | p = 0.08216
ANCHOR: Cox HR (marker per unit) = 1.0422
```

The cutpoint (39.49), group sizes (36/16) and log-rank p (0.069) match the
values published in the tutorial article — external consistency confirmed.

## Output files

| File | Purpose |
|---|---|
| `KM_curve.png` / `KM_curve.pdf` | Kaplan-Meier curves (Low=blue, High=red) with log-rank p and Number-at-risk table; 600 dpi / cairo PDF |
| `cox_forest.png` / `cox_forest.pdf` | Univariate Cox forest plot (HR High vs Low = 3.47, 95%CI 0.85–14.11, p=0.082) |
| `group_summary.csv` | Per-group n and event counts |
| `risk_table.csv` | Full per-timepoint n.risk / n.event / n.censor / survival by group |
| `stats_summary.csv` | All key statistics in one table (cutpoint, p values, HRs) |

## Method note

The original tutorial script searched all candidate cutpoints for the
minimum log-rank p (min-p). This template uses `surv_cutpoint` (maxstat)
instead; on this dataset both give the same cutpoint (39.49). Data-driven
cutpoints inflate between-group differences — report the cutpoint method in
the manuscript and ideally validate in an independent cohort.

## Sanitization record (2026-09-16)

- Scan command: `Grep "C:\\Users|D:\\|F:\\|<作者姓名/单位词>|Patient|身份证|手机|电话"`
  (pattern included the source author's name and location words, elided here)
  over the whole skill directory.
- Hits and verdicts:
  - `scripts/Survival_original.R` line 9: `D:\Survival\...` — the **tutorial's
    own generic instruction path** (public article), not a user-identifying
    machine path. Kept verbatim on purpose (provenance copy).
  - All other hits are documentation lines stating "no patient data".
- Patient-ID check: the source xlsx `患者名字` column contained only
  placeholder fake names (张三/张四/张五…). The column was **dropped** when the
  example was converted from xlsx to UTF-8 CSV (2026-09-16, decided for
  AI-agent friendliness); the repo keeps only the 3 analysis columns.
- F:\Survival.zip disposition: `Survival.R` → `scripts/Survival_original.R`
  (in repo, verbatim); `Survival-data.xlsx` → converted to
  `examples/input/Survival-data.csv` (ID column dropped); nothing else in the zip.
- Machine-checkable anchors frozen in `expected_anchors.txt` (this directory).
