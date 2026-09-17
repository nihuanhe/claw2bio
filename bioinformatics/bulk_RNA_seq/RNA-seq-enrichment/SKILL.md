---
name: RNA-seq-enrichment
description: GO / KEGG / Reactome enrichment analysis from bulk RNA-seq DEG tables (clusterProfiler, offline-capable). Use after the bulk-RNA-seq regular pipeline has produced DEG_*.csv files — when the user asks for 富集分析, GO/KEGG pathway analysis, dotplots of enriched terms. Works fully offline via local pathway caches.
---

# Bulk RNA-seq Enrichment (GO / KEGG / Reactome)

Personalized follow-up to the **bulk-RNA-seq** skill. It consumes the DEG result
tables produced by that pipeline (`DEG_*.csv` with `gene`, `log2fc`, `padj`
columns) and runs clusterProfiler enrichment — GO (BP/MF/CC) always offline via
OrgDb, KEGG online-first with local-cache fallback, Reactome always offline.

**Prerequisite / 前提**: run `bioinformatics/bulk_RNA_seq/bulk-RNA-seq` first (counts → DEG).
Point this skill at the pipeline's output directory (or any folder containing
`DEG_*.csv` files).

## Quick start

```bash
cd bioinformatics/bulk_RNA_seq/RNA-seq-enrichment
Rscript scripts/00_check_deps.R --organism mouse        # dependency gate
Rscript scripts/enrich.R examples/input examples/output --organism mouse
```

## Usage

```
Rscript scripts/enrich.R <deg_dir> <outdir> [--organism mouse|human]
                         [--padj 0.05] [--log2fc 1] [--offline]
```

- Every `DEG_<A>_vs_<B>.csv` in `<deg_dir>` yields up/down gene sets → per-set
  GO tables + dotplots, KEGG table + dotplot, Reactome table + dotplot.
- `--offline`: skip the KEGG online attempt, use the local cache directly.
- Every run also writes **`REPORT.md`** into the output dir — a file-by-file guide
  (which step produced it, what it is for / 产出文件说明).

## Pathway caches (offline mode)

`resources/pathway_cache/` holds TERM2GENE tables. Rebuild or extend with:

```bash
Rscript scripts/build_pathway_cache.R --organism both   # mmu + hsa
```

- KEGG cache: downloaded once from rest.kegg.jp — **local use only** (KEGG
  license forbids redistribution).
- Reactome cache: open-license, redistributable (not mirrored online yet).

## Dependencies

- R: clusterProfiler, DOSE, enrichplot, ggplot2, org.Mm.eg.db (mouse) /
  org.Hs.eg.db (human). `00_check_deps.R [--install]` verifies / installs.
- The OrgDb packages are archived in the bulk-RNA-seq skill's `resources/`
  (not mirrored online yet) — one OrgDb install serves both skills.

## Notes

- DEG tables from any engine branch work (DESeq2 `log2FoldChange`, edgeR/limma
  `logFC` — the reader normalizes column names).
- 中文提示：必须先跑 bulk-RNA-seq 常规管线拿到 DEG_*.csv；GO 永远离线，
  KEGG 联网失败自动用本地缓存（缓存因版权不上 COS，新机器跑一次
  build_pathway_cache.R 即可），Reactome 永远离线；输出全部写入指定目录，
  不改输入文件。
