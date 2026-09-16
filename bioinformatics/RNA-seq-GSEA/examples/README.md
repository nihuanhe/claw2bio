# Examples — RNA-seq-GSEA

`input/` holds one `DEG_*.csv` table from the **bulk-RNA-seq** skill's example
run (GSE270189, Mutant vs Control, DESeq2 branch). `output/` is the real result
of running against the bundled open-license Reactome demo GMT:

```bash
Rscript scripts/gsea.R examples/input/DEG_Mutant_vs_Control.csv \
  --gmt resources/gmt/reactome_demo_mmu.gmt --organism mouse \
  --outdir examples/output
```

Contents: `GSEA_...csv` (89/701 significant sets at padj<0.05), NES dotplot,
top-set enrichment curve. MSigDB runs (user's own GMTs in `resources/gmt/`)
give 166–188/2017 significant m2 sets on this table.
