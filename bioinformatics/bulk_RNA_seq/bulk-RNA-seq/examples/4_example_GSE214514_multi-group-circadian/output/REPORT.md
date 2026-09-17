# Analysis Report — bulk-RNA-seq (regular pipeline: counts → DEG)

- Input counts: `GSE214514_counts_all.tsv.gz` (20362 genes × 25 samples)
- Metadata: `sample_metadata.csv` (control group: `WT_Young`)
- Engine: **deseq2** (rationale was printed at run time)
- Personalized follow-ups on these outputs: `../RNA-seq-enrichment` (GO/KEGG/Reactome), `../RNA-seq-gene-plot` (gene bar charts), `../RNA-seq-GSEA` (GSEA)

## Input grouping

- **KO_Young** (n=6): Bmal1601, Bmal1602, Bmal1621, Bmal1631, Bmal1632, Bmal1633
- **WT_Young** (n=6): Bmal1634, Bmal1641, Bmal1642, Bmal1643, Bmal1644, Bmal1645
- **WT_Aged** (n=6): Bmal121, Bmal122, Bmal131, Bmal132, Bmal133, Bmal171
- **KO_Aged** (n=7): Bmal141, Bmal142, Bmal151, Bmal191, Bmal192, Bmal193, Bmal1211

| File | Produced by | What it is / use |
|---|---|---|
| `DEG_KO_Aged_vs_KO_Young.csv` | 02_de (deseq2) | Full differential-expression table for one contrast (log2FC, p, padj, symbol) — input for the RNA-seq-enrichment and RNA-seq-GSEA skills |
| `DEG_KO_Aged_vs_WT_Aged.csv` | 02_de (deseq2) | Full differential-expression table for one contrast (log2FC, p, padj, symbol) — input for the RNA-seq-enrichment and RNA-seq-GSEA skills |
| `DEG_KO_Aged_vs_WT_Young.csv` | 02_de (deseq2) | Full differential-expression table for one contrast (log2FC, p, padj, symbol) — input for the RNA-seq-enrichment and RNA-seq-GSEA skills |
| `DEG_KO_Young_vs_WT_Aged.csv` | 02_de (deseq2) | Full differential-expression table for one contrast (log2FC, p, padj, symbol) — input for the RNA-seq-enrichment and RNA-seq-GSEA skills |
| `DEG_KO_Young_vs_WT_Young.csv` | 02_de (deseq2) | Full differential-expression table for one contrast (log2FC, p, padj, symbol) — input for the RNA-seq-enrichment and RNA-seq-GSEA skills |
| `DEG_WT_Aged_vs_WT_Young.csv` | 02_de (deseq2) | Full differential-expression table for one contrast (log2FC, p, padj, symbol) — input for the RNA-seq-enrichment and RNA-seq-GSEA skills |
| `DEG_heatmap.pdf` | 02_de (deseq2) | Z-scored heatmap of the union of significant DEGs |
| `DEG_heatmap.png` | 02_de (deseq2) | Z-scored heatmap of the union of significant DEGs |
| `MA_KO_Aged_vs_KO_Young.pdf` | 02_de (deseq2) | MA plot of one contrast — sanity check that normalisation worked and logFC is expression-independent |
| `MA_KO_Aged_vs_KO_Young.png` | 02_de (deseq2) | MA plot of one contrast — sanity check that normalisation worked and logFC is expression-independent |
| `MA_KO_Aged_vs_WT_Aged.pdf` | 02_de (deseq2) | MA plot of one contrast — sanity check that normalisation worked and logFC is expression-independent |
| `MA_KO_Aged_vs_WT_Aged.png` | 02_de (deseq2) | MA plot of one contrast — sanity check that normalisation worked and logFC is expression-independent |
| `MA_KO_Aged_vs_WT_Young.pdf` | 02_de (deseq2) | MA plot of one contrast — sanity check that normalisation worked and logFC is expression-independent |
| `MA_KO_Aged_vs_WT_Young.png` | 02_de (deseq2) | MA plot of one contrast — sanity check that normalisation worked and logFC is expression-independent |
| `MA_KO_Young_vs_WT_Aged.pdf` | 02_de (deseq2) | MA plot of one contrast — sanity check that normalisation worked and logFC is expression-independent |
| `MA_KO_Young_vs_WT_Aged.png` | 02_de (deseq2) | MA plot of one contrast — sanity check that normalisation worked and logFC is expression-independent |
| `MA_KO_Young_vs_WT_Young.pdf` | 02_de (deseq2) | MA plot of one contrast — sanity check that normalisation worked and logFC is expression-independent |
| `MA_KO_Young_vs_WT_Young.png` | 02_de (deseq2) | MA plot of one contrast — sanity check that normalisation worked and logFC is expression-independent |
| `MA_WT_Aged_vs_WT_Young.pdf` | 02_de (deseq2) | MA plot of one contrast — sanity check that normalisation worked and logFC is expression-independent |
| `MA_WT_Aged_vs_WT_Young.png` | 02_de (deseq2) | MA plot of one contrast — sanity check that normalisation worked and logFC is expression-independent |
| `QC_PCA_plot.pdf` | 01_qc.R | PCA of logCPM expression — check group separation and outlier/batch samples |
| `QC_PCA_plot.png` | 01_qc.R | PCA of logCPM expression — check group separation and outlier/batch samples |
| `QC_sample_correlation_heatmap.pdf` | 01_qc.R | Sample-sample correlation heatmap — replicates should cluster together |
| `QC_sample_correlation_heatmap.png` | 01_qc.R | Sample-sample correlation heatmap — replicates should cluster together |
| `QC_summary.txt` | 01_qc.R | Filtering stats (genes kept, library sizes) |
| `Volcano_KO_Aged_vs_KO_Young.pdf` | 02_de (deseq2) | Volcano plot of one contrast, top-10 gene labels |
| `Volcano_KO_Aged_vs_KO_Young.png` | 02_de (deseq2) | Volcano plot of one contrast, top-10 gene labels |
| `Volcano_KO_Aged_vs_WT_Aged.pdf` | 02_de (deseq2) | Volcano plot of one contrast, top-10 gene labels |
| `Volcano_KO_Aged_vs_WT_Aged.png` | 02_de (deseq2) | Volcano plot of one contrast, top-10 gene labels |
| `Volcano_KO_Aged_vs_WT_Young.pdf` | 02_de (deseq2) | Volcano plot of one contrast, top-10 gene labels |
| `Volcano_KO_Aged_vs_WT_Young.png` | 02_de (deseq2) | Volcano plot of one contrast, top-10 gene labels |
| `Volcano_KO_Young_vs_WT_Aged.pdf` | 02_de (deseq2) | Volcano plot of one contrast, top-10 gene labels |
| `Volcano_KO_Young_vs_WT_Aged.png` | 02_de (deseq2) | Volcano plot of one contrast, top-10 gene labels |
| `Volcano_KO_Young_vs_WT_Young.pdf` | 02_de (deseq2) | Volcano plot of one contrast, top-10 gene labels |
| `Volcano_KO_Young_vs_WT_Young.png` | 02_de (deseq2) | Volcano plot of one contrast, top-10 gene labels |
| `Volcano_WT_Aged_vs_WT_Young.pdf` | 02_de (deseq2) | Volcano plot of one contrast, top-10 gene labels |
| `Volcano_WT_Aged_vs_WT_Young.png` | 02_de (deseq2) | Volcano plot of one contrast, top-10 gene labels |
| `filtered_counts.csv` | 01_qc.R | Count matrix after filterByExpr — input to the DE stage |
| `library_sizes.csv` | 01_qc.R | Per-sample library sizes before/after filtering |
| `normalized_expression.csv` | 02_de (deseq2) | Normalised expression matrix (vst / voom logCPM / log-expression, engine-dependent) — input for the RNA-seq-gene-plot skill |
| `run_metadata.json` | run_rnaseq.py | Machine-readable run record: engine, parameters, input stats, software versions, timestamp |

_This file is auto-generated by `run_rnaseq.py` at the end of every run._
