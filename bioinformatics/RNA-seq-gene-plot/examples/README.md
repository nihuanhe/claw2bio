# Examples — RNA-seq-gene-plot

`input/` holds products of the **bulk-RNA-seq** skill's example run (GSE270189,
DESeq2 branch): the vst-normalized matrix, the sample metadata, and one DEG
table (for symbol mapping). `output/` is the real result of:

```bash
Rscript scripts/gene_expression.R \
  examples/input/vst_normalized_counts.csv \
  examples/input/sample_metadata.csv \
  --genes Trp53,Gapdh --control Control --outdir examples/output
```

Contents: `GeneExpr_Trp53_by_group.png/pdf` + values CSV,
`GeneExpr_Gapdh_by_group.png/pdf` + values CSV, and
`GeneExpr_compare_Trp53_vs_Gapdh_within_group.png/pdf` + values CSV
(paired t-test per group).
