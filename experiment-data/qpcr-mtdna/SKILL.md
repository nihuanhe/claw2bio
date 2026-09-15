---
name: qpcr-mtdna
description: mtDNA qPCR (ND1/ND5/B2M/POLG) ΔCt calculation and publication-ready bar plots. Takes a CSV in Target/Sample/Rep1~Rep3 format, computes Mean copy number automatically, outputs a CSV with calculation columns and a 300-dpi PNG.（中文摘要：mtDNA qPCR（ND1/ND5/B2M/POLG）ΔCt 计算，自动计算 Mean copy number，输出带计算列的 CSV 和 300 dpi 发表级柱状图。）
---

# Skill: qpcr-mtdna

## Trigger phrases

- mtDNA qPCR
- run mtDNA bar plot
- qpcr-mtdna
- mtDNA copy number
- Mean copy number
- 跑 mtDNA 柱状图 / 线粒体拷贝数

## What it does

1. Reads a raw Ct table (`Target, Sample, Rep1, Rep2, Rep3`).
2. Auto-pairs nuclear references with mtDNA targets:
   - `ND1 Ct` ↔ `B2M Ct`
   - `ND5 Ct` ↔ `POLG Ct`
3. Computes ΔCt, 2^ΔCt, and Mean copy number on the `ND1 Ct` row:
   ```
   Mean copy number = (2^(B2M-ND1) + 2^(POLG-ND5)) / 2
   ```
4. Appends calculation columns to the output CSV.
5. Plots a 300-dpi bar plot from the Mean copy number of the `ND1 Ct` rows.
6. Statistics:
   - 2 groups: independent-samples t-test
   - ≥3 groups: Tukey HSD pairwise comparisons

## Usage

### Single file

```bash
python scripts/run_mtdna.py <input.csv> <output_dir> --name <FigureName> --overwrite
```

Example:

```bash
cd qpcr-mtdna
python scripts/run_mtdna.py \
  examples/input/mtDNA-input.csv \
  examples/output \
  --name Figure18B --overwrite
```

Outputs:
- `Figure18B.csv`: original table + Delta Ct + 2^Delta Ct + Mean copy number
- `Figure18B.png`: bar plot

### Batch mode (a whole experiment directory)

```bash
python scripts/batch_mtdna.py <root_dir> --overwrite
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

- `Target` must include `ND1 Ct`, `ND5 Ct`, `B2M Ct`, `POLG Ct`.
- The `Sample` column defines the x-axis group names; freely customizable.
- Supports 2–6 groups (and more, with an extended layout).

## Output files

- `<name>.csv`: raw Ct + calculation columns
- `<name>.png`: 300-dpi publication-ready bar plot

## Customization

- Y-axis label: `--y-label "your label"`
- DPI: `--dpi 600`
- Output file name: `--name FigureXX`

## Dependencies

Python 3.10+ with:

```bash
pip install pandas numpy scipy matplotlib
```

## Notes

- Never modifies the input CSV; results are written as new files in the **output directory**.
- If an output file already exists and `--overwrite` is not set, the script stops with an error to prevent accidental overwrite.
- Batch mode skips unparseable files and continues with the rest.

> 中文提示：本工具不会修改原始输入 CSV，计算结果写入输出目录；输出已存在时需加 `--overwrite`；批量模式会跳过无法解析的文件继续处理。
