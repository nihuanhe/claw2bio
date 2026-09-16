# RNA-seq-gene-plot

Gene-of-interest expression bar charts from bulk RNA-seq results — a personalized
follow-up skill for [bulk-RNA-seq](../bulk-RNA-seq).

**Prerequisite**: run the bulk-RNA-seq regular pipeline first
(`counts → QC → DEG`); this skill consumes its normalized matrix
(`normalized_expression.csv`; legacy names `vst_normalized_counts.csv` /
`voom_normalized_logcpm.csv` / `log_expression_used.csv` also work),
the sample metadata, and optionally a `DEG_*.csv` for symbol mapping.

```
RNA-seq-gene-plot/
├── SKILL.md
├── scripts/
│   └── gene_expression.R   # per-gene group bars + within-group two-gene comparison
└── examples/
    ├── input/              # normalized matrix + metadata + one DEG table (GSE270189)
    └── output/             # real plots: Trp53/Gapdh across groups + within-group comparison
```

## Quick start

```bash
Rscript scripts/gene_expression.R \
  examples/input/normalized_expression.csv \
  examples/input/sample_metadata.csv \
  --genes Trp53,Gapdh --control Control --outdir examples/output
```

Expected: `GeneExpr_Trp53_by_group.png` (ANOVA p = 0.02 with Tukey pairs in the
caption), `GeneExpr_Gapdh_by_group.png`, and
`GeneExpr_compare_Trp53_vs_Gapdh_within_group.png` (paired t-test per group:
Control ns / Mutant * / Mutant_Rap **) plus the underlying value CSVs.
