# Skills

All skills are lab-validated fixed scripts packaged in the standard `SKILL.md` format.
Each skill page is a zero-basics, copy-paste tutorial in English and Chinese.

> **First time here? Start with [Set up your first AI Agent](/skills/ai-agent-setup)** — install an AI agent from scratch, then come back to pick a skill.

## 🧪 Experiment Data Processing

| Skill | What it does |
|---|---|
| [qPCR mRNA (ΔΔCt)](/skills/qpcr-mrna) | Relative expression from raw Ct tables, one plot per target |
| [qPCR mtDNA copy number](/skills/qpcr-mtdna) | ND1/ND5 + B2M/POLG pairing, mean copy number |
| [mIF contrast (ImageJ)](/skills/if-contrast) | mIF multi-channel batch contrast adjustment (Fiji/ImageJ macro) |
| [Open-field test](/skills/OFT) | Tracker trajectory → analysis plots → pixelated heatmaps |
| [WB densitometry](/skills/wb-imagej) | WB band densitometry: ImageJ macro → Python normalization + stats + bar plot |

## 🧬 Bioinformatics Analysis {#bioinformatics}

| Skill | What it does |
|---|---|
| [Single-cell RNA-seq](/skills/scRNA-seq) | Raw matrices → QC → Harmony → clustering → UMAP → markers → SingleR annotation |
| [scRNA-seq pseudotime](/skills/scRNA-seq-pseudotime) | monocle3 trajectory on the regular pipeline's annotated rds |
| [scRNA-seq virtual KO](/skills/scRNA-seq-virtual-ko) | scTenifoldKnk in-silico gene knockout |
| [Bulk RNA-seq DEG](/skills/bulk-RNA-seq) | Counts → QC → DEG, auto engine fork (limma-trend / DESeq2 / edgeR+voom) |
| [Enrichment (GO/KEGG/Reactome)](/skills/RNA-seq-enrichment) | GO/Reactome offline, KEGG online + cache fallback |
| [Gene expression plots](/skills/RNA-seq-gene-plot) | One gene across groups / two genes within group |
| [GSEA](/skills/RNA-seq-GSEA) | fgsea + MSigDB GMT, auto Entrez/symbol conversion |
| [Phylo tree — build](/skills/phylo-tree-build) | Genome FASTAs → bcgTree → IQ-TREE2 treefile (WSL2) |
| [Phylo tree — plot](/skills/phylo-tree-plot) | Treefile + annotation CSV → publication-ready ggtree figure |

## 📈 Figure & Table Generation

| Skill | What it does |
|---|---|
| [Grouped bar plot](/skills/barplot) | Wide-format CSV → 300-dpi annotated bar plot |
| [Clinical tables](/skills/clinical-table) | One pipeline reproducing all 10 tables of a paper: baseline / Firth / genotype cross-tabs / univariate |
| [Survival curve](/skills/survival-curve) | Optimal-cutoff KM curve + risk table + Cox forest plot |
| [Brain atlas annotate](/skills/brain-if-atlas-annotate) | Mouse brain atlas line-art overlays (100 plates ×2 versions) for IF brain-region annotation |
| [Compress images](/skills/compress-image) | Batch image compression (huge scanner TIFF → shareable JPEG) |
