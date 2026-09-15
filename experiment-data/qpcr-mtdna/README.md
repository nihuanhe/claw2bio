# qpcr-mtdna

mtDNA qPCR (ND1/ND5/B2M/POLG) ΔCt calculation and publication-ready bar plot tool.

mtDNA qPCR（ND1/ND5/B2M/POLG）ΔCt 计算与发表级柱状图生成工具。

## Features

- Reads a raw Ct table (`Target, Sample, Rep1, Rep2, Rep3`).
- Auto-pairs nuclear references with mtDNA targets:
  - `ND1 Ct` ↔ `B2M Ct`
  - `ND5 Ct` ↔ `POLG Ct`
- Computes ΔCt, 2^ΔCt, and Mean copy number:

  ```
  Mean copy number = (2^(B2M-ND1) + 2^(POLG-ND5)) / 2
  ```
- Appends calculation columns to the output CSV for easy verification in Excel.
- Plots a 300-dpi bar plot from the Mean copy number of the `ND1 Ct` rows.
- Statistics:
  - 2 groups: independent-samples t-test
  - ≥3 groups: Tukey HSD pairwise comparisons

## Installation

Python 3.10+ with:

```bash
pip install pandas numpy scipy matplotlib
```

## Quick start

### Process a single figure

```bash
cd qpcr-mtdna
python scripts/run_mtdna.py \
  examples/input/mtDNA-input.csv \
  examples/output \
  --name Figure18B --overwrite
```

Outputs:

- `examples/output/Figure18B.csv`
- `examples/output/Figure18B.png`

### Batch mode (a whole experiment directory)

```bash
python scripts/batch_mtdna.py \
  "path/to/experiment-folder" \
  --overwrite
```

The script recursively finds all CSVs, uses each containing folder name as the Figure name, and outputs same-named CSV and PNG files.

## Input CSV format

```csv
Target,Sample,Rep1,Rep2,Rep3
ND1 Ct,Ctrl-BD-sEVs,15.10,14.19,14.66
ND1 Ct,Stress-BD-sEVs,14.27,14.08,14.72
ND5 Ct,Ctrl-BD-sEVs,14.25,14.64,14.47
ND5 Ct,Stress-BD-sEVs,14.88,14.93,14.87
B2M Ct,Ctrl-BD-sEVs,22.99,22.40,22.53
B2M Ct,Stress-BD-sEVs,22.62,22.73,22.27
POLG Ct,Ctrl-BD-sEVs,22.14,22.53,22.43
POLG Ct,Stress-BD-sEVs,22.80,22.00,22.48
```

- Must include the four Target rows `ND1 Ct`, `ND5 Ct`, `B2M Ct`, `POLG Ct`.
- The `Sample` column defines the x-axis group names; freely customizable.
- Supports 2–6 groups (and more, with an extended layout).

## Output CSV columns

| Column | Description |
|--------|-------------|
| `Target`, `Sample`, `Rep1~Rep3` | Raw input |
| `Delta Ct(Rep1~Rep3)` | Nuclear reference Ct − mtDNA Ct |
| `2^Delta Ct(Rep1~Rep3)` | 2 to the power of ΔCt |
| `Mean copy number(Rep1~Rep3)` | Only on `ND1 Ct` rows; mean of the ND1 and ND5 pathway 2^ΔCt values |

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
qpcr-mtdna/
├── SKILL.md                 ← agent-facing skill definition
├── README.md                ← human-readable usage doc (this file)
├── scripts/
│   ├── run_mtdna.py         ← single-file processing
│   └── batch_mtdna.py       ← batch processing
├── examples/
│   ├── input/mtDNA-input.csv
│   └── output/
│       ├── Figure18B.csv
│       └── Figure18B.png
└── .gitignore
```

## Parameters

| Flag | Description |
|------|-------------|
| `--name` | Output file name prefix |
| `--y-label` | Y-axis label |
| `--dpi` | PNG resolution |
| `--overwrite` | Overwrite existing outputs |

## Statistical methods

- 2 groups: two-tailed independent-samples t-test (equal variance).
- ≥3 groups: `scipy.stats.tukey_hsd` for all pairwise comparisons.
- Significance marks: `* P<0.05`, `** P<0.01`, `*** P<0.001`.

## Notes

- The tool never modifies the input CSV; results are written to the specified **output directory**.
- If an output file already exists and `--overwrite` is not set, the script stops with an error.
- Batch mode skips unparseable files and continues with the rest.
