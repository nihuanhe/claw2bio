# qPCR mtDNA Copy Number

> One-line: mitochondrial DNA copy number from ND1/ND5 qPCR — auto-paired with B2M/POLG nuclear references, statistics and a 300-dpi plot included.

::: info Get this skill · 获取本技能
**Option A — one-click agent prompt (recommended).** Copy this into your AI agent IDE:

```
Please set up the "qpcr-mtdna" skill from the Claw2Bio library for me:
1. Fetch only the folder "experiment-data/qpcr-mtdna" from the GitHub repo
   https://github.com/claw2bio/claw2bio (use sparse checkout; do not clone the whole repo).
2. Read its SKILL.md and register the skill.
3. Run the bundled example in examples/ to verify my environment, and show me the output figure.
```

**Option B — standalone zip** (few MB, Tencent COS direct link): *available at site launch*.

**Option C — full example dataset** (COS, per-skill folder): *available at site launch*.
:::

## What it does

Reads a raw Ct table containing `ND1 Ct`, `ND5 Ct`, `B2M Ct`, `POLG Ct` rows, computes

```
Mean copy number = (2^(B2M-ND1) + 2^(POLG-ND5)) / 2
```

runs statistics (2 groups: t-test; ≥3 groups: Tukey HSD) and draws a 300-dpi bar plot:

![qPCR mtDNA example output](/cards/qpcr-mtdna.png)

## Quick start (30 seconds)

```bash
cd experiment-data/qpcr-mtdna
pip install pandas numpy scipy matplotlib
python scripts/run_mtdna.py examples/input/mtDNA-input.csv examples/output --name Figure18B --overwrite
```

Expected: `Figure18B.csv` (with ΔCt / 2^ΔCt / Mean copy number columns) and `Figure18B.png`. The bundled example gives P = 0.986 (ns).

## Input format

```csv
Target,Sample,Rep1,Rep2,Rep3
ND1 Ct,Ctrl,15.10,14.19,14.66
ND1 Ct,Treat,14.27,14.08,14.72
ND5 Ct,Ctrl,14.25,14.64,14.47
ND5 Ct,Treat,14.88,14.93,14.87
B2M Ct,Ctrl,22.99,22.40,22.53
B2M Ct,Treat,22.62,22.73,22.27
POLG Ct,Ctrl,22.14,22.53,22.43
POLG Ct,Treat,22.80,22.00,22.48
```

All four Target rows (`ND1 Ct`, `ND5 Ct`, `B2M Ct`, `POLG Ct`) are required.

## Output files

| File | Content |
|---|---|
| `<name>.csv` | Raw Ct + Delta Ct + 2^Delta Ct + Mean copy number |
| `<name>.png` | 300-dpi bar plot with statistics |

## Parameters

| Flag | Default | Description |
|---|---|---|
| `--name` | — | Output file prefix |
| `--y-label` | — | Y-axis label |
| `--dpi` | 300 | PNG resolution |
| `--overwrite` | off | Allow overwriting existing outputs |

Batch mode over a whole experiment folder: `python scripts/batch_mtdna.py <root_dir> --overwrite`.

## Troubleshooting

- **Missing target rows** → the input must contain exactly `ND1 Ct`, `ND5 Ct`, `B2M Ct`, `POLG Ct` (watch the trailing "Ct").
- **"Output file exists"** → add `--overwrite`.

## Links

- [Source & SKILL.md on GitHub](https://github.com/claw2bio/claw2bio/tree/main/experiment-data/qpcr-mtdna)
- Related skills: [qPCR mRNA](/skills/qpcr-mrna) · [Grouped bar plot](/skills/barplot)
