# rnaseq-gsea

GSEA on bulk RNA-seq DEG tables (fgsea + MSigDB GMT) — a personalized follow-up
skill for [bulk-RNA-seq](../bulk-RNA-seq).

**Prerequisite**: run the bulk-RNA-seq regular pipeline first
(`counts → QC → DEG`); this skill consumes a `DEG_*.csv` table.

```
rnaseq-gsea/
├── SKILL.md
├── scripts/
│   ├── 00_check_deps.R   # dependency gate (fgsea/OrgDb/ggplot2)
│   └── gsea.R            # ranked-list GSEA, per-GMT auto ID conversion
├── resources/
│   └── gmt/              # MSigDB .gmt files go here (gitignored);
│                         # reactome_demo_mmu.gmt bundled (open license)
└── examples/
    ├── input/            # DEG table from the bulk-RNA-seq example (GSE270189)
    └── output/           # real GSEA output against the bundled Reactome GMT
```

## Quick start

```bash
Rscript scripts/00_check_deps.R --organism mouse
Rscript scripts/gsea.R examples/input/DEG_Mutant_vs_Control.csv \
  --gmt resources/gmt/reactome_demo_mmu.gmt --organism mouse \
  --outdir examples/output
```

Expected for the bundled example: ~89/701 significant Reactome gene sets
(padj<0.05), a NES dotplot, and the top-set enrichment curve.

To use MSigDB: copy e.g. `m2.all.v2025.1.Mm.entrez.gmt` /
`m2.all.v2025.1.Mm.symbols.gmt` / Hallmark into `resources/gmt/` and pass them
via `--gmt` (or drop the flag to use everything in that folder). Verified:
166–188/2017 significant sets on the example data with both ID flavours.
