---
name: bulk-rnaseq
description: Bulk RNA-seq differential expression and enrichment from a count matrix. Data-driven engine fork — non-integer/normalized input → limma-trend, integer counts with small n → DESeq2, integer counts with large n → edgeR+limma-voom — always printing WHY the engine was chosen. Outputs QC (PCA/correlation), DEG tables, volcano plots, DEG heatmap, and GO/KEGG enrichment.（中文摘要：bulk RNA-seq 从 counts 矩阵到差异表达与富集分析的全流程。按数据自动选择引擎（非整数→limma-trend；整数小样本→DESeq2；整数大样本→edgeR+limma-voom），并强制打印选择理由。输出 QC、DEG 表、火山图、热图、GO/KEGG 富集。）
---

# Skill: bulk-rnaseq

## Trigger phrases

- bulk RNA-seq analysis
- differential expression / DEG
- volcano plot from counts
- GO / KEGG enrichment
- bulk RNA-seq 差异分析 / 火山图 / 富集分析

## What it does

Stage 00 first verifies all R package dependencies and reports anything missing
(you choose: let the agent install via `--install-deps`, or install manually via
miniconda/BiocManager) — the pipeline never starts on a broken environment.

Input: a gene-by-sample count matrix CSV + a sample metadata CSV. Output: full
differential-expression report — QC (PCA, sample correlation), DEG tables per
contrast (with **gene-symbol columns — Ensembl IDs are converted up front**),
volcano plots labelled with gene symbols, DEG heatmap, GO/KEGG enrichment.

**Engine fork (automatic, data-driven; the rationale is ALWAYS printed):**

| Input diagnosis | Engine |
|---|---|
| Non-integer / normalized values (FPKM, TPM, log) | limma-trend |
| Integer counts, min group n < 8 | DESeq2 |
| Integer counts, min group n ≥ 8 | edgeR + limma-voom |

Override with `--engine deseq2|edger-limma|limma`; tune the threshold with `--voom-min-n`.

## Usage

```bash
python scripts/run_rnaseq.py <counts.csv> <metadata.csv> <output_dir> \
  --control Control --organism mouse --overwrite
```

Example (bundled GSE270189, mouse prostate basal cells, 3 groups × 2 replicates):

```bash
cd bioinformatics/bulk-rnaseq
python scripts/run_rnaseq.py \
  examples/input/counts_matrix.csv \
  examples/input/sample_metadata.csv \
  examples/output \
  --control Control --organism mouse --overwrite
```

## Input format

`counts_matrix.csv` — genes as rows, samples as columns, raw integer counts
(normalized matrices are accepted too; they route to limma-trend):

```csv
,CJI1.A,CJI2.B,CJI3.I
ENSMUSG00000000001,2014,2003,2847
ENSMUSG00000000003,13736,19194,...
```

`sample_metadata.csv` — exactly two columns:

```csv
sample,group
CJI1.A,Control
CJI3.I,Mutant
```

The first group in the metadata is the control unless `--control` is given.

## Output files

| File | Content |
|---|---|
| `QC_PCA_plot.png/pdf`, `QC_sample_correlation_heatmap.png/pdf`, `QC_summary.txt` | QC |
| `filtered_counts.csv`, `library_sizes.csv` | preprocessing artefacts |
| `DEG_<treat>_vs_<ref>.csv` | full DEG table per contrast (common schema across engines) |
| `Volcano_<treat>_vs_<ref>.png/pdf` | volcano with top-10 gene labels |
| `DEG_heatmap.png/pdf` | top DEGs, z-scored |
| `GO_DEG_*_{up,down}_{BP,MF,CC}.csv` + dotplots, `KEGG_*.csv` + dotplots | enrichment |

## Parameters

| Flag | Default | Description |
|---|---|---|
| `--control` | first group in metadata | control group name |
| `--engine` | `auto` | force `deseq2` / `edger-limma` / `limma` |
| `--voom-min-n` | 8 | min group size for the voom branch |
| `--organism` | `mouse` | `mouse` (org.Mm.eg.db, mmu) or `human` (org.Hs.eg.db, hsa) |
| `--padj` | 0.05 | adjusted-p significance cutoff |
| `--log2fc` | 1 | |log2FC| cutoff |
| `--skip-enrich` | off | stop after stage 02 |
| `--install-deps` | off | auto-install missing R packages (BiocManager/CRAN) |
| `--rscript` | auto-detect | path to Rscript |
| `--overwrite` | off | allow non-empty output dir |

## Dependencies

- Python 3.10+: `pip install pandas numpy`
- R (≥4.3) with: `DESeq2 edgeR limma clusterProfiler DOSE org.Mm.eg.db org.Hs.eg.db pheatmap ggplot2 ggrepel enrichplot`
- Stage 00 checks these before anything runs; missing packages can be installed by
  the agent (`--install-deps`) or manually (miniconda / BiocManager). The OrgDb
  annotation packages (used for gene-ID conversion) are also mirrored as archives
  on the Download page (COS) for fast domestic installation.
- KEGG enrichment needs network access to rest.kegg.jp; it is skipped gracefully offline.

## Notes

- Never modifies input files; all outputs go to the output directory.
- Contrasts: every group vs control; when ≤4 groups, all pairwise contrasts are added.
- Enrichment maps Ensembl (version suffix stripped) or Symbol IDs to Entrez via the OrgDb.
- DEG tables and figures use converted gene symbols wherever a mapping exists.

> 中文提示：开跑前自动检查 R 依赖，缺包时可选手动安装（miniconda/BiocManager）或加 `--install-deps` 让 agent 代装，装好后还会复检；DEG 表和图默认用转换后的基因名（Symbol）；输入可以是原始整数 counts 或已归一化矩阵（自动分流）；对照组默认取 metadata 第一行分组；KEGG 富集需联网，离线时自动跳过；不改输入文件。
