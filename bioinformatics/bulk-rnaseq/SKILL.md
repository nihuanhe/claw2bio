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

**File formats are flexible**: the count matrix and metadata may be `.csv`, `.tsv`
or `.txt`, and may be gzipped (`.gz`) — the pipeline auto-detects delimiter and
compression (both the Python driver and the R stages). Zip/tar bundles must be
unpacked first (the agent should do this before calling the skill). For GEO-derived
data see `docs/downloading-from-GEO.md`.

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

## Input resources: gene-ID conversion packages

DEG tables/figures use gene symbols converted via the Bioconductor OrgDb annotation
packages — treat them as part of the skill's input assets:

| Organism | Package | Size | Where to get |
|---|---|---|---|
| mouse | `org.Mm.eg.db` | ~380 MB installed | `BiocManager::install("org.Mm.eg.db")`, or the prebuilt archive on the Download page (COS) |
| human | `org.Hs.eg.db` | ~100 MB download | `BiocManager::install("org.Hs.eg.db")`, or the prebuilt archive on the Download page (COS) |

Install a downloaded archive (same R major.minor version, Windows):
`install.packages("org.Mm.eg.db.zip", repos = NULL, type = "win.binary")`.
Stage 00 verifies the package matching `--organism` before anything runs.

**Fully offline route**: `resources/r-deps/` is a Windows-binary mini-repo of the
entire R dependency closure (139 packages, exact tested versions, R 4.5) — point
`install.packages(..., repos = "file:///<path>/r-deps", type = "win.binary")` at it
when Bioconductor/CRAN is slow or unreachable. Also mirrored on COS at launch.

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

> 中文提示：输入可以是 csv/tsv/txt 及 .gz 压缩（自动识别分隔符与压缩；zip/tar 需先解压）；GEO 数据获取见 docs/downloading-from-GEO.md；基因 ID 转换包（org.Mm.eg.db / org.Hs.eg.db）属于本技能输入资源，体积大故随 COS 分发（见 Download 页）；开跑前自动检查 R 依赖，缺包时可选手动安装（miniconda/BiocManager）或加 `--install-deps` 让 agent 代装，装好后还会复检；DEG 表和图默认用转换后的基因名（Symbol）；KEGG 富集需联网，离线自动跳过；不改输入文件。
