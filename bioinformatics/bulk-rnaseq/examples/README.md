# bulk-rnaseq example — GSE270189

## Input

Real public dataset [GSE270189](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE270189):
mouse prostate basal cells, 3 groups × 2 replicates (integer gene counts, Ensembl IDs).

- `input/counts_matrix.csv` — 18,975 genes × 6 samples (filtered integer counts)
- `input/sample_metadata.csv` — Control / Mutant / Mutant_Rap groups

Groups: `Control` (CD1, EtOH), `Mutant` (PTEN-Pik3ca double mutant, EtOH),
`Mutant_Rap` (double mutant + rapamycin).

## Run

```bash
cd bioinformatics/bulk-rnaseq
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
3. **DEGs** (padj < 0.05, |log2FC| > 1):
   - Mutant vs Control: **1380 up / 1688 down**
   - Mutant_Rap vs Control: **517 up / 763 down**
   - Mutant vs Mutant_Rap: **855 up / 578 down**
4. **Volcano plots** per contrast + `DEG_heatmap.png`.
5. **GO enrichment** tables + dotplots per contrast (up/down × BP/MF/CC).
   KEGG requires network access to rest.kegg.jp and is skipped gracefully offline.

## Output committed here

A representative subset (≈5 MB): QC plots + summary, the Mutant-vs-Control DEG table
and volcano, the DEG heatmap, and one GO dotplot. The complete output set (all
contrasts, all ontologies) is hosted on COS — see the Download page.
