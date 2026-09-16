# bulk-RNA-seq example — GSE270189

## Input

Real public dataset [GSE270189](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE270189):
mouse prostate basal cells, 3 groups × 2 replicates (integer gene counts, Ensembl IDs).

- `input/counts_matrix.csv` — 18,975 genes × 6 samples (filtered integer counts)
- `input/sample_metadata.csv` — Control / Mutant / Mutant_Rap groups

Groups: `Control` (CD1, EtOH), `Mutant` (PTEN-Pik3ca double mutant, EtOH),
`Mutant_Rap` (double mutant + rapamycin).

## Run

```bash
cd bioinformatics/bulk-RNA-seq
python scripts/run_rnaseq.py \
  examples/input/counts_matrix.csv \
  examples/input/sample_metadata.csv \
  examples/output \
  --control Control --organism mouse --genes Trp53,Gapdh --overwrite
```

## What you should see

1. **Engine diagnosis box**: integer counts + min group n = 2 → **DESeq2** selected,
   with the printed rationale.
2. **QC**: `QC_PCA_plot.png` (groups separate cleanly), `QC_sample_correlation_heatmap.png`.
3. **DEGs** (padj < 0.05, |log2FC| > 1), tables include converted gene symbols:
   - Mutant vs Control: **1380 up / 1688 down**
   - Mutant_Rap vs Control: **517 up / 763 down**
   - Mutant vs Mutant_Rap: **855 up / 578 down**
4. **Volcano plots** per contrast (symbol-labelled) + `DEG_heatmap.png`.
5. **Gene-of-interest plots**: `GeneExpr_Trp53_by_group.png` (ANOVA p = 0.02),
   `GeneExpr_Gapdh_by_group.png`, and `GeneExpr_compare_Trp53_vs_Gapdh_within_group.png`
   (paired test per group: Control ns / Mutant * / Mutant_Rap **).
6. **GO enrichment** tables + dotplots per contrast (up/down × BP/MF/CC) and
   **KEGG enrichment** (e.g. `mmu04820 Cytoskeleton in muscle cells` for the
   Mutant-down set). KEGG needs network access to rest.kegg.jp and is skipped
   gracefully offline.

## Output committed here

The complete real output of the command above (~23 MB): QC, all DEG tables and
volcano plots, DEG heatmap, gene-of-interest plots + value CSVs, and all GO/KEGG
enrichment tables + dotplots.
