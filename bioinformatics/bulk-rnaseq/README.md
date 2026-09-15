# bulk-rnaseq

Bulk RNA-seq differential expression + enrichment pipeline with a data-driven
engine fork. Refactored from lab-validated R scripts.

bulk RNA-seq 差异表达与富集分析流程，引擎按数据自动分叉；由实验室实战脚本重构而来。

## Features

1. **QC** — library sizes, `filterByExpr` filtering, PCA, sample-correlation heatmap.
2. **Differential expression** — three engines, auto-selected by data diagnosis
   (rationale always printed):
   - non-integer / normalized input → **limma-trend**
   - integer counts, min group n < 8 → **DESeq2**
   - integer counts, min group n ≥ 8 → **edgeR + limma-voom**
3. **Visualization** — volcano plots (top-10 labels), z-scored DEG heatmap.
4. **Enrichment** — clusterProfiler GO (BP/MF/CC) + KEGG, up/down separately per contrast.

## Installation

```bash
pip install pandas numpy
```

```r
# in R (>= 4.3):
if (!require("BiocManager", quietly = TRUE)) install.packages("BiocManager")
BiocManager::install(c("DESeq2", "edgeR", "limma", "clusterProfiler", "DOSE",
                       "org.Mm.eg.db", "org.Hs.eg.db", "enrichplot"))
install.packages(c("pheatmap", "ggplot2", "ggrepel"))
```

## Quick start

```bash
cd bioinformatics/bulk-rnaseq
python scripts/run_rnaseq.py \
  examples/input/counts_matrix.csv \
  examples/input/sample_metadata.csv \
  examples/output \
  --control Control --organism mouse --overwrite
```

## Input

- `counts_matrix.csv`: genes × samples integer counts (or a normalized matrix —
  auto-routed to limma-trend).
- `sample_metadata.csv`: columns `sample,group`. First group = control unless
  `--control` is passed.

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
bulk-rnaseq/
├── SKILL.md
├── README.md
├── scripts/
│   ├── run_rnaseq.py        # diagnosis + engine fork + stage driver
│   ├── 01_qc.R              # filtering, logCPM, PCA, correlation heatmap
│   ├── 02_de_deseq2.R       # DESeq2 branch
│   ├── 02_de_edger_limma.R  # edgeR+limma-voom branch / limma-trend (--mode trend)
│   ├── 03_enrich.R          # clusterProfiler GO/KEGG
│   └── rnaseq_utils.R       # shared helpers (contrasts, volcano, heatmap)
└── examples/
    ├── input/               # GSE270189: mouse prostate basal, Control/Mutant/Mutant_Rap (n=2 each)
    └── output/              # real pipeline output for the bundled example
```

## Statistical notes

- DESeq2 branch: standard `DESeq()` Wald tests; contrasts via `results(contrast=...)`.
- voom branch: TMM normalization → `voom` precision weights → `lmFit` → `eBayes(robust=TRUE)`.
- trend branch: log-transform if max > 50, then `lmFit` + `eBayes(trend=TRUE, robust=TRUE)`.
- Multiple testing: BH adjusted p values everywhere.
- Enrichment: Ensembl IDs (version-stripped) or Symbols → Entrez via OrgDb; GO with
  `readable=TRUE`; KEGG via KEGG REST (skipped gracefully when offline).

## Notes

- Inputs are never modified; everything lands in the output directory.
- With ≤4 groups, all pairwise contrasts are produced; otherwise every group vs control.
