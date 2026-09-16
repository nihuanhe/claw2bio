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
  --control Control --organism mouse --overwrite
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

The regular pipeline stops here. Personalized follow-ups on these outputs:
`../../RNA-seq-enrichment` (GO/KEGG/Reactome), `../../RNA-seq-gene-plot`
(Trp53/Gapdh bar charts), `../../RNA-seq-GSEA` (GSEA).

## Output committed here

The complete real output of the command above: QC plots + summary, all DEG
tables (with symbol columns), volcano plots, DEG heatmap, and the preprocessing
artefacts (`filtered_counts.csv`, `vst_normalized_counts.csv`,
`library_sizes.csv`) consumed by the follow-up skills.
