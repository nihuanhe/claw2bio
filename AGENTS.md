# AGENTS.md — Claw2Bio skill index

This file is the entry point for command-line agents (Codex, OpenCode, pi, etc.).
Each skill below has a standard `SKILL.md` (agent-facing definition, English with
Chinese summary), a `README.md`, `scripts/`, and `examples/` with minimal runnable
input and expected output.

## Stage 1 — Experiment data processing (`experiment-data/`)

| Skill | Path | What it does |
|---|---|---|
| qpcr-mrna | `experiment-data/qpcr-mrna/SKILL.md` | mRNA qPCR ΔΔCt analysis + publication-ready bar plots (t-test / ANOVA + Dunnett) |
| qpcr-mtdna | `experiment-data/qpcr-mtdna/SKILL.md` | mtDNA qPCR (ND1/ND5/B2M/POLG) ΔCt + Mean copy number + bar plots |
| if-contrast | `experiment-data/IF-免疫荧光/SKILL.md` | mIF multi-channel batch contrast adjustment (Fiji/ImageJ macro) |
| OFT | `experiment-data/OFT/SKILL.md` | Open-field test pipeline: Tracker trajectory → analysis plots → pixelated heatmaps |
| wb-imagej | `experiment-data/WB-imageJ-定量/SKILL.md` | WB band densitometry: ImageJ macro → Python normalization + stats + bar plot |

## Stage 2 — Bioinformatics analysis (`bioinformatics/`)

| Skill | Path | What it does |
|---|---|---|
| scRNA-seq | `bioinformatics/sc_RNA_seq/scRNA-seq/SKILL.md` | Single-cell regular pipeline: raw matrices → QC → Harmony → clustering → UMAP → markers → SingleR annotation |
| scRNA-seq-pseudotime | `bioinformatics/sc_RNA_seq/scRNA-seq-pseudotime/SKILL.md` | monocle3 pseudotime/trajectory on the regular pipeline's annotated_seurat.rds (root cluster/label required) |
| scRNA-seq-virtual-ko | `bioinformatics/sc_RNA_seq/scRNA-seq-virtual-ko/SKILL.md` | scTenifoldKnk in-silico gene knockout on the regular pipeline's annotated_seurat.rds |
| bulk-RNA-seq | `bioinformatics/bulk_RNA_seq/bulk-RNA-seq/SKILL.md` | Bulk RNA-seq counts → QC → DEG (auto engine fork: limma-trend / DESeq2 / edgeR+voom; paired/batch/exploratory modes) |
| RNA-seq-enrichment | `bioinformatics/bulk_RNA_seq/RNA-seq-enrichment/SKILL.md` | GO (offline) / KEGG (online+cache) / Reactome (offline) enrichment |
| RNA-seq-gene-plot | `bioinformatics/bulk_RNA_seq/RNA-seq-gene-plot/SKILL.md` | Gene-of-interest bar plots across groups (t-test / ANOVA+Tukey) |
| RNA-seq-GSEA | `bioinformatics/bulk_RNA_seq/RNA-seq-GSEA/SKILL.md` | GSEA via fgsea + MSigDB GMT (auto Entrez/symbol conversion) |
| phylo-tree-build | `bioinformatics/phylo-tree/phylo-tree-build/SKILL.md` | Genome FASTAs → core-genome ML tree (bcgTree→IQ-TREE2 on WSL2; optional parsnp subtrees) |
| phylo-tree-plot | `bioinformatics/phylo-tree/phylo-tree-plot/SKILL.md` | Newick treefile + annotation CSV → publication-ready annotated tree figure (ggtree template) |

## Stage 3 — Figure & table generation (`figure-generation/`)

| Skill | Path | What it does |
|---|---|---|
| barplot | `figure-generation/barplot/SKILL.md` | Grouped bar plots from wide-format CSV, auto-selects 2–6 group script |
| clinical-table | `figure-generation/clinical-table/SKILL.md` | Clinical three-line tables: generic 2-cohort baseline (χ²/Fisher + t, OR, Cox) + R suite reproducing all 10 tables (Tables 1–10 = manuscript Table 1/2 + S1–S8: Firth, genotype crosses, univariate) — real CRE vs CSE example, cell-reconciled |
| survival-curve | `figure-generation/survival-curve/SKILL.md` | KM survival curve + univariate Cox (surv_cutpoint cutoff, risk table, HR forest plot, 600 dpi) |
| brain-if-atlas-annotate | `figure-generation/brain-if-atlas-annotate/SKILL.md` | Mouse brain atlas line-art overlays (100 plates ×2 versions) for IF brain-region annotation |
| compress-image | `figure-generation/compress-image/SKILL.md` | Batch image compression (huge scanner TIFF → shareable JPEG) |

## Conventions

- All skills follow the design rules in `ARCHITECTURE.md` (script reuse, examples
  smoke-test convention, adapter pattern).
- Scripts run locally; no data leaves the user's machine.
- Python skills expect Python 3.10+ with `pip install pandas numpy scipy matplotlib statsmodels`.
- **Execution rule / 执行铁律**: run the scripts in `scripts/` — never write your own.
  Preferred order: (1) run the script as-is, changing CLI arguments only; (2) copy
  it to a scratch dir and make a minimal edit for a case the CLI cannot express,
  reporting exactly what changed; (3) only if no script covers the task at all,
  write new code and then fold it back into `scripts/` so the next run reuses it.
  **AI agents must not write replacement scripts on the fly.**
