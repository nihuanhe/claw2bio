# resources/gmt/

Put MSigDB GMT gene-set files here (download from gsea-msigdb.org after free
registration), e.g.:

- `m2.all.v2025.1.Mm.entrez.gmt` / `m2.all.v2025.1.Mm.symbols.gmt` — mouse C2 curated
- `mh.all.v2025.1.Mm.*.gmt` — mouse Hallmark
- human equivalents (`m2.all.v2025.1.Hs.*`, `h.all...Hs.symbols.gmt`)

ID flavour (Entrez vs symbol) is auto-detected per file; mixed lists are fine.

**License note**: MSigDB requires registration; its files stay local and are
gitignored. The bundled `reactome_demo_mmu.gmt` (built from Reactome's
open-license NCBI2Reactome table) is tracked so the skill runs out of the box.
