# qpcr-mrna

General-purpose mRNA qPCR ΔΔCt analysis with publication-ready bar plots.

通用 mRNA qPCR ΔΔCt 分析与发表级柱状图生成工具。

## Features

- Reads a raw Ct table (`Target, Sample, Rep1, Rep2, Rep3`).
- Auto-detects reference-gene rows (default `GAPDH`; multiple references supported, e.g. `GAPDH,ACTB`).
- For each non-reference Target computes:
  - `ΔCt = Ct_target - mean(Ct_refs)`
  - `ΔΔCt = ΔCt - mean(ΔCt_of_control_group)`
  - `Fold = 2^(-ΔΔCt)`
- Appends results to the output CSV.
- Generates one 300-dpi bar plot per Target.
- Statistics:
  - 2 groups: independent-samples t-test
  - ≥3 groups: one-way ANOVA + Dunnett (each treatment vs control)

## Installation

Python 3.10+ with:

```bash
pip install pandas numpy scipy matplotlib
```

## Quick start

### Process a single CSV

```bash
cd qpcr-mrna
python scripts/run_mrna.py \
  examples/input/mrna-input.csv \
  examples/output \
  --name Figure1 --overwrite
```

Outputs:
- `examples/output/Figure1.csv`
- `examples/output/Figure1_IL6_barplot.png`
- `examples/output/Figure1_TNF_barplot.png`

### Batch mode

```bash
python scripts/batch_mrna.py \
  "path/to/mrna-qpcr-folder" \
  --ref-targets GAPDH \
  --overwrite
```

## Input CSV format

```csv
Target,Sample,Rep1,Rep2,Rep3
IL6,Ctrl,20.10,20.30,20.20
IL6,Treat,17.50,17.80,17.60
TNF,Ctrl,22.00,22.20,22.10
TNF,Treat,21.90,22.10,22.00
GAPDH,Ctrl,18.00,18.10,18.05
GAPDH,Treat,18.20,18.30,18.25
```

- Reference-gene rows use the same format as regular Target rows.
- The `Sample` column defines the x-axis group names.
- The first Sample encountered is the control group by default; override with `--control`.
- Supports 2–6 groups (and more, with an extended layout).

## Output CSV columns

| Column | Description |
|--------|-------------|
| `Target`, `Sample`, `Rep1~Rep3` | Raw input |
| `Delta_Ct_Rep1~Rep3` | ΔCt normalized to reference genes |
| `Fold_Rep1~Rep3` | Fold change relative to control |
| `Fold_Mean` / `Fold_SD` | Mean and SD of fold change |
| `P_Value` | P value of this Sample vs control (NaN for control) |
| `Stat_Test` | Statistical method used |
| `Significance` | `*`, `**`, `***`, `ns` |
| `Skip_Reason` | Reason given if a Target was skipped |

## Plot style

- Color-blind-friendly Wong 2011 palette (shared with the `barplot` skill).
- 2 groups: green `#009E73` / pink `#CC79A7`
- 3 groups: blue `#0072B2` / orange `#D55E00` / green `#009E73`
- 6 groups: full Wong palette
- Error bars: SD
- Points: 3 biological replicates with jitter
- Significance: shown as text on the right side only; no bracket lines on the plot

## File structure

```
qpcr-mrna/
├── SKILL.md                 ← agent-facing skill definition
├── README.md                ← human-readable usage doc (this file)
├── scripts/
│   ├── run_mrna.py          ← single-file processing
│   └── batch_mrna.py        ← batch processing
├── examples/
│   ├── README.md
│   ├── input/mrna-input.csv
│   └── output/
│       ├── Figure1.csv
│       ├── Figure1_IL6_barplot.png
│       └── Figure1_TNF_barplot.png
└── .gitignore
```

## Parameters

| Flag | Description |
|------|-------------|
| `--name` | Output file name prefix |
| `--ref-targets` | Reference-gene Target names, comma-separated |
| `--control` | Control-group Sample name |
| `--y-label` | Y-axis label |
| `--dpi` | PNG resolution |
| `--overwrite` | Overwrite existing outputs |

## Statistical methods

- 2 groups: two-tailed independent-samples t-test (equal variance).
- ≥3 groups: `scipy.stats.f_oneway` + `scipy.stats.dunnett` (each treatment vs control).
- Significance marks: `* P<0.05`, `** P<0.01`, `*** P<0.001`.

## Notes

- The tool never modifies the input CSV; results are written to the specified **output directory**.
- If an output file already exists and `--overwrite` is not set, the script stops with an error.
- Batch mode skips unparseable files and continues with the rest.
