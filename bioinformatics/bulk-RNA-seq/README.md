# bulk-RNA-seq

Bulk RNA-seq differential expression pipeline with a data-driven engine fork —
the **regular** stage (counts → QC → DEG). Refactored from lab-validated R scripts.
Personalized follow-ups are separate skills that consume this pipeline's outputs:
[RNA-seq-enrichment](../RNA-seq-enrichment) (GO/KEGG/Reactome),
[RNA-seq-gene-plot](../RNA-seq-gene-plot) (gene-of-interest bar charts),
[RNA-seq-GSEA](../RNA-seq-GSEA) (GSEA).

bulk RNA-seq 差异表达常规流程（到 DEG 为止），引擎按数据自动分叉；富集 / 指定基因柱状图 / GSEA 是三个独立的后续个性化 skill。

## Features

0. **Input inspection (stage 00.5)** — lossless auto-repair of the usual GEO/input mess,
   every repair printed: mixed count/FPKM/annotation matrices, GEO series_matrix headers,
   transposed matrices, `_count`-style suffixes, R-mangled sample names (`check.names` /
   `make.names`), duplicate gene symbols, negative values, non-standard metadata columns.
1. **QC** — library sizes, `filterByExpr` filtering, PCA (batch-aware shapes), sample-correlation
   heatmap, suspected-outlier flagging (report only, never auto-excluded).
2. **Differential expression** — three engines, auto-selected by data diagnosis
   (rationale always printed):
   - non-integer / normalized input → **limma-trend**
   - integer counts, min group n < 8 → **DESeq2**
   - integer counts, min group n ≥ 8 → **edgeR + limma-voom**
   - paired/repeated-measures declared (`--paired-by`) → forced **limma family + duplicateCorrelation**;
     n = 1 per group → forced limma-trend **exploratory mode** (fold change only, REPORT banner)
   - batch supported in every engine via `--batch` (design formula)
3. **Visualization** — volcano plots (top-10 labels), MA plots per contrast,
   z-scored DEG heatmap.

The pipeline **stops at DEG tables**. Personalized follow-ups (separate skills):
`RNA-seq-enrichment` (GO/KEGG/Reactome), `RNA-seq-gene-plot` (gene-of-interest
bar charts), `RNA-seq-GSEA` (GSEA).

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
  examples/1_example_GSE270189_clean-mouse-3groups/input/counts_matrix.csv \
  examples/1_example_GSE270189_clean-mouse-3groups/input/sample_metadata.csv \
  examples/1_example_GSE270189_clean-mouse-3groups/output \
  --control Control --organism mouse --overwrite
```

Special situations (paired / batch / no replicates / multi-group / species & IDs /
dirty inputs): **[docs/decision-tree.md](docs/decision-tree.md)** — symptom-driven,
points at flags and the numbered `examples/N_example_*` cases.

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
│   ├── run_rnaseq.py        # stage-00.5 input inspection + diagnosis + engine fork + driver
│   ├── 00_check_deps.R      # dependency gate (install / verify)
│   ├── 01_qc.R              # filtering, logCPM, PCA, correlation heatmap, outlier flags
│   ├── 02_de_deseq2.R       # DESeq2 branch (batch/subject-aware design formula)
│   ├── 02_de_edger_limma.R  # edgeR+limma-voom / limma-trend (--mode trend; duplicateCorrelation)
│   └── rnaseq_utils.R       # shared helpers (reader, contrasts, ID conversion, plots)
├── docs/
│   ├── decision-tree.md     # symptom -> diagnosis -> flag/example (special situations)
│   ├── input-formats.md     # auto-repair inventory, series_matrix, CEL refusal
│   ├── paired-and-batch.md
│   ├── no-replicates.md
│   ├── multi-group-and-contrasts.md
│   └── downloading-from-GEO.md
└── examples/
    ├── 1_example_GSE270189_clean-mouse-3groups/          # clean baseline (regression)
    ├── 2_example_GSE255223_mixed-count-FPKM-annotation/  # mixed matrix surgery
    ├── 3_example_GSE167882_paired-symbol-logcpm-human/   # paired + duplicateCorrelation
    ├── 4_example_GSE214514_multi-group-circadian/        # 4 groups, all-pairwise
    └── 5_example_synthetic_dirty-and-series-matrix/      # inspection-stage stress tests
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
- The normalized matrix always lands at `normalized_expression.csv` regardless of
  engine; group names in output file names are sanitised; every run also writes a
  machine-readable `run_metadata.json` (engine, parameters, versions, timestamp).
