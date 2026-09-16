---
name: RNA-seq-gene-plot
description: Gene-of-interest expression plots from bulk RNA-seq results — per-gene abundance across groups and within-group two-gene comparison, as bar charts with SD error bars, jittered points, and statistics (t-test / ANOVA+Tukey / paired t-test). Use after the bulk-RNA-seq pipeline — when the user asks 某基因在不同分组的表达柱状图, 比较同组内两个基因表达量, e.g. TP53 abundance, TP53 vs GAPDH.
---

# RNA-seq Gene-of-Interest Expression Plots

Personalized follow-up to the **bulk-RNA-seq** skill. Consumes the pipeline's
normalized expression matrix + sample metadata (and optionally a DEG table for
symbol→ID mapping) and produces publication-style bar charts:

- **Per gene across groups** — bar + SD error bars + jittered sample points;
  t-test (2 groups) or ANOVA + Tukey (≥3 groups) annotated in the caption.
  (For 3-vs-3 or any n≥2 design you get the bar-with-error-bar plot.)
- **Two genes within each group** (e.g. TP53 vs GAPDH) — dodged bars + SD +
  points, with a **paired** t-test per group (same samples, two genes).

**Prerequisite / 前提**: run `bioinformatics/bulk-RNA-seq` first; then hand this
skill its `vst_normalized_counts.csv` (or `voom_normalized_logcpm.csv` /
`log_expression_used.csv`), the `sample_metadata.csv`, and any `DEG_*.csv`.

## Quick start

```bash
cd bioinformatics/RNA-seq-gene-plot
Rscript scripts/gene_expression.R \
  examples/input/vst_normalized_counts.csv \
  examples/input/sample_metadata.csv \
  --genes Trp53,Gapdh --control Control --outdir examples/output
```

## Usage

```
Rscript scripts/gene_expression.R <norm_matrix.csv> <metadata.csv>
        --genes GENE1[,GENE2,...] [--deg DEG_xxx.csv] [--control NAME]
        [--outdir DIR]
```

- Gene queries: Ensembl ID or symbol, case-insensitive. Symbols are resolved via
  the `--deg` table's `symbol` column (if omitted, any `DEG_*.csv` next to the
  matrix is used). **Use the target species' symbols** — `TP53` for human,
  `Trp53` for mouse.
- Outputs: `GeneExpr_<GENE>_by_group.png/pdf` + values CSV per gene; with ≥2
  genes also `GeneExpr_compare_<G1>_vs_<G2>_within_group.png/pdf` + values CSV.
- Every run also writes **`REPORT.md`** into the output dir — a file-by-file guide
  (which step produced it, what it is for / 产出文件说明).

## Dependencies

- R: **ggplot2 only** (stats from base R). Matrix/metadata readers handle
  csv/tsv/txt and `.gz`.

## Notes

- 中文提示：必须先跑 bulk-RNA-seq 常规管线；输入是它的归一化表达矩阵
  （vst/voom/log 自动识别）+ 分组表；单基因出跨组丰度柱状图（均值±SD+散点+
  t 检验/ANOVA+Tukey），两个基因出同组内对比柱状图（配对 t 检验）；基因名
  用目标物种写法（人 TP53、鼠 Trp53）；不改输入文件。
