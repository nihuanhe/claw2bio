# Examples — RNA-seq-enrichment

`input/` holds the three `DEG_*.csv` tables produced by the **bulk-RNA-seq**
skill's example run (GSE270189, mouse prostate basal cells, DESeq2 branch).
`output/` is the real result of:

```bash
Rscript scripts/enrich.R examples/input examples/output --organism mouse --offline
```

Contents: GO enrichment tables + dotplots per contrast × up/down × BP/MF/CC,
KEGG tables + dotplots (via local cache), Reactome tables + dotplots
(all offline).
