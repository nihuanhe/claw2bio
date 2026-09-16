# RNA-seq-enrichment

GO / KEGG / Reactome enrichment from bulk RNA-seq DEG tables — a personalized
follow-up skill for [bulk-RNA-seq](../bulk-RNA-seq).

**Prerequisite**: run the bulk-RNA-seq regular pipeline first
(`counts → QC → DEG`); this skill consumes its `DEG_*.csv` outputs.

```
RNA-seq-enrichment/
├── SKILL.md
├── scripts/
│   ├── 00_check_deps.R        # dependency gate (clusterProfiler/DOSE/enrichplot/OrgDb)
│   ├── enrich.R               # GO (offline) + KEGG (online→cache) + Reactome (offline)
│   └── build_pathway_cache.R  # one-time download of KEGG/Reactome TERM2GENE tables
├── resources/
│   └── pathway_cache/         # local caches (gitignored; KEGG local-only by license)
└── examples/
    ├── input/                 # DEG tables from the bulk-RNA-seq example (GSE270189)
    └── output/                # real enrichment output for the bundled example
```

## Quick start

```bash
Rscript scripts/00_check_deps.R --organism mouse
Rscript scripts/enrich.R examples/input examples/output --organism mouse
```

Expected for the bundled example (Mutant vs Control etc., padj<0.05, |log2FC|>1):
GO dotplots per contrast/ontology, KEGG pathways (e.g. `mmu04820 Cytoskeleton in
muscle cells` for the Mutant-down set), Reactome pathways — all from a fully
offline run.
