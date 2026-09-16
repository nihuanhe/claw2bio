# bulk-RNA-seq

Bulk RNA-seq differential expression pipeline with a data-driven engine fork —
the **regular** stage (counts → QC → DEG). Refactored from lab-validated R scripts.
Personalized follow-ups are separate skills that consume this pipeline's outputs:
[RNA-seq-enrichment](../RNA-seq-enrichment) (GO/KEGG/Reactome),
[RNA-seq-gene-plot](../RNA-seq-gene-plot) (gene-of-interest bar charts),
[RNA-seq-gsea](../RNA-seq-gsea) (GSEA).

bulk RNA-seq 差异表达常规流程（到 DEG 为止），引擎按数据自动分叉；富集 / 指定基因柱状图 / GSEA 是三个独立的后续个性化 skill。

## Features

1. **QC** — library sizes, `filterByExpr` filtering, PCA, sample-correlation heatmap.
2. **Differential expression** — three engines, auto-selected by data diagnosis
   (rationale always printed):
   - non-integer / normalized input → **limma-trend**
   - integer counts, min group n < 8 → **DESeq2**
   - integer counts, min group n ≥ 8 → **edgeR + limma-voom**
3. **Visualization** — volcano plots (top-10 labels), z-scored DEG heatmap.

The pipeline **stops at DEG tables**. Personalized follow-ups (separate skills):
`RNA-seq-enrichment` (GO/KEGG/Reactome), `RNA-seq-gene-plot` (gene-of-interest
bar charts), `RNA-seq-gsea` (GSEA).

**Gene ID conversion is built into the DEG step**: Ensembl IDs (version-stripped)
or Symbols are mapped to gene Symbols via the OrgDb; DEG tables gain a `symbol`
column and volcano/heatmap figures label genes by symbol.

## Installation

```bash
pip install pandas numpy
```

```r
# in R (>= 4.3):
if (!require("BiocManager", quietly = TRUE)) install.packages("BiocManager")
BiocManager::install(c("DESeq2", "edgeR", "limma", "org.Mm.eg.db", "org.Hs.eg.db"))
install.packages(c("pheatmap", "ggplot2", "ggrepel"))
```

**You don't have to do this by hand**: stage 00 checks every dependency before the
analysis starts. If anything is missing you pick the route — let the agent install
(`--install-deps`) or install manually (miniconda / BiocManager) — and the pipeline
re-verifies before running. OrgDb annotation archives are also mirrored on the
Download page (COS) for fast domestic installation.

## Quick start

```bash
cd bioinformatics/bulk-RNA-seq
python scripts/run_rnaseq.py \
  examples/input/counts_matrix.csv \
  examples/input/sample_metadata.csv \
  examples/output \
  --control Control --organism mouse --overwrite
```

## Input

- **Flexible file formats**: `.csv` / `.tsv` / `.txt`, optionally gzipped (`.gz`) —
  delimiter and compression are auto-detected in both the Python driver and the R
  stages. Zip/tar bundles must be unpacked first (the agent should handle that).
  GEO download walkthrough: [`docs/downloading-from-GEO.md`](docs/downloading-from-GEO.md).
- `counts_matrix.csv`: genes × samples integer counts (or a normalized matrix —
  auto-routed to limma-trend).
- `sample_metadata.csv`: columns `sample,group`. First group = control unless
  `--control` is passed.

### Input resource: gene-ID conversion packages

DEG outputs use gene symbols converted through Bioconductor OrgDb packages:
`org.Mm.eg.db` (mouse) / `org.Hs.eg.db` (human). They are large (100–380 MB), so
we mirror prebuilt Windows-binary archives in `resources/` (and on COS at launch)
for offline/fast installation: `install.packages("<archive>.zip", repos = NULL,
type = "win.binary")`. Stage 00 verifies the right one is present.

## How the engine is chosen

The Python entry diagnoses the matrix (integer check + per-group replicate counts)
and prints a boxed rationale before any R stage runs:

```
>>> SELECTED ENGINE: deseq2
>>> WHY: Integer counts with small replication (min group n = 2 < 8).
    DESeq2 gives the most robust dispersion/shrinkage estimates at small n.
```

Force with `--engine`, tune the switch point with `--voom-min-n`.

## File structure

```
bulk-RNA-seq/
├── SKILL.md
├── README.md
├── scripts/
│   ├── run_rnaseq.py        # diagnosis + engine fork + stage driver
│   ├── 00_check_deps.R      # dependency gate (install / verify)
│   ├── 01_qc.R              # filtering, logCPM, PCA, correlation heatmap
│   ├── 02_de_deseq2.R       # DESeq2 branch
│   ├── 02_de_edger_limma.R  # edgeR+limma-voom branch / limma-trend (--mode trend)
│   └── rnaseq_utils.R       # shared helpers (smart reader, contrasts, volcano, heatmap)
└── examples/
    ├── input/               # GSE270189: mouse prostate basal, Control/Mutant/Mutant_Rap (n=2 each)
    └── output/              # real pipeline output for the bundled example
```

## Statistical notes

- DESeq2 branch: standard `DESeq()` Wald tests; contrasts via `results(contrast=...)`.
- voom branch: TMM normalization → `voom` precision weights → `lmFit` → `eBayes(robust=TRUE)`.
- trend branch: log-transform if max > 50, then `lmFit` + `eBayes(trend=TRUE, robust=TRUE)`.
- Multiple testing: BH adjusted p values everywhere.
- Gene IDs: Ensembl (version-stripped) or Symbols → Entrez/Symbol via OrgDb.

## Notes

- Inputs are never modified; everything lands in the output directory.
- With ≤4 groups, all pairwise contrasts are produced; otherwise every group vs control.
