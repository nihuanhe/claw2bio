# Downloading data from GEO (knowing the GSExxxx accession)

> 中文摘要：知道 GSE 编号后，首选 **GEOquery**（`getGEO` + `getGEOSuppFiles`）。
> 先诊断类型：能拿到 ExpressionSet → 芯片/归一化矩阵直接用；拿不到 → RNA-seq，
> counts 在 Supplementary files 里，`getGEOSuppFiles` 下载后合并。

## Recommended package: GEOquery

`GEOquery` is still the standard, most-used R package for GEO. Two functions cover
everything:

| Function | What it fetches |
|---|---|
| `getGEO("GSExxxx", GSEMatrix = TRUE)` | Series matrix → ExpressionSet (expression + phenotype). Works when GEO hosts a processed matrix (microarray, some RNA-seq). |
| `getGEOSuppFiles("GSExxxx")` | The **supplementary files** — this is where RNA-seq count matrices actually live (~90% of RNA-seq series). |

## Step 1 — diagnose the series type

```r
library(GEOquery)

gset <- getGEO("GSExxxx", GSEMatrix = TRUE)

if (length(gset) > 0) {
  # Case A: processed matrix available (microarray / normalized RNA-seq)
  exp_matrix <- exprs(gset[[1]])
  pheno      <- pData(gset[[1]])   # grouping info lives here
} else {
  # Case B: RNA-seq raw counts — go to supplementary files
  message("No series matrix: download supplementary files instead")
}
```

## Step 2 — supplementary files (the usual RNA-seq path)

```r
getGEOSuppFiles("GSExxxx")   # downloads into ./GSExxxx/
# Then find the counts file, e.g.:
f <- list.files("GSExxxx", pattern = "count|tsv|csv|txt", full.names = TRUE,
                recursive = TRUE, ignore.case = TRUE)[1]
```

**Reading whatever comes down** — GEO files arrive as `.csv` / `.tsv` / `.txt`,
very often gzipped (`.gz`) or as tar/zip bundles:

- `.gz`: read directly — `read.csv("x.csv.gz")` and `read.delim("x.tsv.gz")` handle
  gzip natively; or in Python `pd.read_csv(path, sep=None, engine="python",
  compression="infer")`. **Do not assume the delimiter** — sniff the first line
  (tab / comma / space) before parsing.
- `.tar` / `.zip` bundles: unpack first (`untar()` / `unzip()`), then inspect the
  per-sample files; merge per-sample count files into one genes × samples matrix
  before handing it to the skill.
- This skill's own reader (`read_table_smart` in `scripts/rnaseq_utils.R` and the
  Python driver) already auto-detects delimiter and gzip for the final matrix.

## Step 3 — shape it for bulk-RNA-seq

The skill needs two files:

1. `counts_matrix.csv` — genes × samples, raw integer counts preferred
   (normalized matrices work too; they route to limma-trend automatically).
2. `sample_metadata.csv` — two columns `sample,group`; build `group` from the
   phenotype table (`pData`) or the series description.

## Useful alternatives

- **recount3** (`recount3` R package): uniformly reprocessed raw counts for a huge
  share of GEO/SRA — best when the series has no count matrix at all.
- **GEOquery `getGEO(., GSEMatrix = FALSE)`**: full SOFT metadata when you need the
  experimental design text.
