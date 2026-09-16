# Analysis Report — RNA-seq-enrichment (GO / KEGG / Reactome)

- Input: DEG tables in `input` (produced by the bulk-RNA-seq regular pipeline)
- Organism: mouse; cutoffs: padj < 0.05, |log2FC| > 1
- Gene sets: up/down per contrast, analyzed separately / 每个对比的上下调分开做

| File | Produced by | What it is / use |
|---|---|---|
| `GO_DEG_Mutant_Rap_vs_Control_down_BP.csv` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment table for one contrast x direction x ontology (BP/MF/CC) / GO 富集结果表 |
| `GO_DEG_Mutant_Rap_vs_Control_down_BP_dotplot.png` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment dotplot (top terms, one ontology per file) / GO 富集气泡图 |
| `GO_DEG_Mutant_Rap_vs_Control_down_CC.csv` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment table for one contrast x direction x ontology (BP/MF/CC) / GO 富集结果表 |
| `GO_DEG_Mutant_Rap_vs_Control_down_CC_dotplot.png` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment dotplot (top terms, one ontology per file) / GO 富集气泡图 |
| `GO_DEG_Mutant_Rap_vs_Control_down_MF.csv` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment table for one contrast x direction x ontology (BP/MF/CC) / GO 富集结果表 |
| `GO_DEG_Mutant_Rap_vs_Control_down_MF_dotplot.png` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment dotplot (top terms, one ontology per file) / GO 富集气泡图 |
| `GO_DEG_Mutant_Rap_vs_Control_up_BP.csv` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment table for one contrast x direction x ontology (BP/MF/CC) / GO 富集结果表 |
| `GO_DEG_Mutant_Rap_vs_Control_up_BP_dotplot.png` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment dotplot (top terms, one ontology per file) / GO 富集气泡图 |
| `GO_DEG_Mutant_Rap_vs_Control_up_CC.csv` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment table for one contrast x direction x ontology (BP/MF/CC) / GO 富集结果表 |
| `GO_DEG_Mutant_Rap_vs_Control_up_CC_dotplot.png` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment dotplot (top terms, one ontology per file) / GO 富集气泡图 |
| `GO_DEG_Mutant_Rap_vs_Control_up_MF.csv` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment table for one contrast x direction x ontology (BP/MF/CC) / GO 富集结果表 |
| `GO_DEG_Mutant_Rap_vs_Control_up_MF_dotplot.png` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment dotplot (top terms, one ontology per file) / GO 富集气泡图 |
| `GO_DEG_Mutant_vs_Control_down_BP.csv` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment table for one contrast x direction x ontology (BP/MF/CC) / GO 富集结果表 |
| `GO_DEG_Mutant_vs_Control_down_BP_dotplot.png` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment dotplot (top terms, one ontology per file) / GO 富集气泡图 |
| `GO_DEG_Mutant_vs_Control_down_CC.csv` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment table for one contrast x direction x ontology (BP/MF/CC) / GO 富集结果表 |
| `GO_DEG_Mutant_vs_Control_down_CC_dotplot.png` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment dotplot (top terms, one ontology per file) / GO 富集气泡图 |
| `GO_DEG_Mutant_vs_Control_down_MF.csv` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment table for one contrast x direction x ontology (BP/MF/CC) / GO 富集结果表 |
| `GO_DEG_Mutant_vs_Control_down_MF_dotplot.png` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment dotplot (top terms, one ontology per file) / GO 富集气泡图 |
| `GO_DEG_Mutant_vs_Control_up_BP.csv` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment table for one contrast x direction x ontology (BP/MF/CC) / GO 富集结果表 |
| `GO_DEG_Mutant_vs_Control_up_BP_dotplot.png` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment dotplot (top terms, one ontology per file) / GO 富集气泡图 |
| `GO_DEG_Mutant_vs_Control_up_CC.csv` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment table for one contrast x direction x ontology (BP/MF/CC) / GO 富集结果表 |
| `GO_DEG_Mutant_vs_Control_up_CC_dotplot.png` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment dotplot (top terms, one ontology per file) / GO 富集气泡图 |
| `GO_DEG_Mutant_vs_Control_up_MF.csv` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment table for one contrast x direction x ontology (BP/MF/CC) / GO 富集结果表 |
| `GO_DEG_Mutant_vs_Control_up_MF_dotplot.png` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment dotplot (top terms, one ontology per file) / GO 富集气泡图 |
| `GO_DEG_Mutant_vs_Mutant_Rap_down_BP.csv` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment table for one contrast x direction x ontology (BP/MF/CC) / GO 富集结果表 |
| `GO_DEG_Mutant_vs_Mutant_Rap_down_BP_dotplot.png` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment dotplot (top terms, one ontology per file) / GO 富集气泡图 |
| `GO_DEG_Mutant_vs_Mutant_Rap_down_CC.csv` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment table for one contrast x direction x ontology (BP/MF/CC) / GO 富集结果表 |
| `GO_DEG_Mutant_vs_Mutant_Rap_down_CC_dotplot.png` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment dotplot (top terms, one ontology per file) / GO 富集气泡图 |
| `GO_DEG_Mutant_vs_Mutant_Rap_down_MF.csv` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment table for one contrast x direction x ontology (BP/MF/CC) / GO 富集结果表 |
| `GO_DEG_Mutant_vs_Mutant_Rap_down_MF_dotplot.png` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment dotplot (top terms, one ontology per file) / GO 富集气泡图 |
| `GO_DEG_Mutant_vs_Mutant_Rap_up_BP.csv` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment table for one contrast x direction x ontology (BP/MF/CC) / GO 富集结果表 |
| `GO_DEG_Mutant_vs_Mutant_Rap_up_BP_dotplot.png` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment dotplot (top terms, one ontology per file) / GO 富集气泡图 |
| `GO_DEG_Mutant_vs_Mutant_Rap_up_CC.csv` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment table for one contrast x direction x ontology (BP/MF/CC) / GO 富集结果表 |
| `GO_DEG_Mutant_vs_Mutant_Rap_up_CC_dotplot.png` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment dotplot (top terms, one ontology per file) / GO 富集气泡图 |
| `GO_DEG_Mutant_vs_Mutant_Rap_up_MF.csv` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment table for one contrast x direction x ontology (BP/MF/CC) / GO 富集结果表 |
| `GO_DEG_Mutant_vs_Mutant_Rap_up_MF_dotplot.png` | enrich.R (GO, clusterProfiler, offline via OrgDb) | GO enrichment dotplot (top terms, one ontology per file) / GO 富集气泡图 |
| `KEGG_DEG_Mutant_Rap_vs_Control_down.csv` | enrich.R (KEGG, online REST or local cache) | KEGG pathway enrichment table / KEGG 富集结果表 |
| `KEGG_DEG_Mutant_Rap_vs_Control_down_dotplot.png` | enrich.R (KEGG, online REST or local cache) | KEGG pathway dotplot / KEGG 气泡图 |
| `KEGG_DEG_Mutant_Rap_vs_Control_up.csv` | enrich.R (KEGG, online REST or local cache) | KEGG pathway enrichment table / KEGG 富集结果表 |
| `KEGG_DEG_Mutant_Rap_vs_Control_up_dotplot.png` | enrich.R (KEGG, online REST or local cache) | KEGG pathway dotplot / KEGG 气泡图 |
| `KEGG_DEG_Mutant_vs_Control_down.csv` | enrich.R (KEGG, online REST or local cache) | KEGG pathway enrichment table / KEGG 富集结果表 |
| `KEGG_DEG_Mutant_vs_Control_down_dotplot.png` | enrich.R (KEGG, online REST or local cache) | KEGG pathway dotplot / KEGG 气泡图 |
| `KEGG_DEG_Mutant_vs_Control_up.csv` | enrich.R (KEGG, online REST or local cache) | KEGG pathway enrichment table / KEGG 富集结果表 |
| `KEGG_DEG_Mutant_vs_Control_up_dotplot.png` | enrich.R (KEGG, online REST or local cache) | KEGG pathway dotplot / KEGG 气泡图 |
| `KEGG_DEG_Mutant_vs_Mutant_Rap_down.csv` | enrich.R (KEGG, online REST or local cache) | KEGG pathway enrichment table / KEGG 富集结果表 |
| `KEGG_DEG_Mutant_vs_Mutant_Rap_down_dotplot.png` | enrich.R (KEGG, online REST or local cache) | KEGG pathway dotplot / KEGG 气泡图 |
| `KEGG_DEG_Mutant_vs_Mutant_Rap_up.csv` | enrich.R (KEGG, online REST or local cache) | KEGG pathway enrichment table / KEGG 富集结果表 |
| `KEGG_DEG_Mutant_vs_Mutant_Rap_up_dotplot.png` | enrich.R (KEGG, online REST or local cache) | KEGG pathway dotplot / KEGG 气泡图 |
| `Reactome_DEG_Mutant_Rap_vs_Control_down.csv` | enrich.R (Reactome, offline cache) | Reactome pathway enrichment table / Reactome 富集结果表 |
| `Reactome_DEG_Mutant_Rap_vs_Control_down_dotplot.png` | enrich.R (Reactome, offline cache) | Reactome pathway dotplot / Reactome 气泡图 |
| `Reactome_DEG_Mutant_Rap_vs_Control_up.csv` | enrich.R (Reactome, offline cache) | Reactome pathway enrichment table / Reactome 富集结果表 |
| `Reactome_DEG_Mutant_Rap_vs_Control_up_dotplot.png` | enrich.R (Reactome, offline cache) | Reactome pathway dotplot / Reactome 气泡图 |
| `Reactome_DEG_Mutant_vs_Control_down.csv` | enrich.R (Reactome, offline cache) | Reactome pathway enrichment table / Reactome 富集结果表 |
| `Reactome_DEG_Mutant_vs_Control_down_dotplot.png` | enrich.R (Reactome, offline cache) | Reactome pathway dotplot / Reactome 气泡图 |
| `Reactome_DEG_Mutant_vs_Control_up.csv` | enrich.R (Reactome, offline cache) | Reactome pathway enrichment table / Reactome 富集结果表 |
| `Reactome_DEG_Mutant_vs_Control_up_dotplot.png` | enrich.R (Reactome, offline cache) | Reactome pathway dotplot / Reactome 气泡图 |
| `Reactome_DEG_Mutant_vs_Mutant_Rap_down.csv` | enrich.R (Reactome, offline cache) | Reactome pathway enrichment table / Reactome 富集结果表 |
| `Reactome_DEG_Mutant_vs_Mutant_Rap_down_dotplot.png` | enrich.R (Reactome, offline cache) | Reactome pathway dotplot / Reactome 气泡图 |
| `Reactome_DEG_Mutant_vs_Mutant_Rap_up.csv` | enrich.R (Reactome, offline cache) | Reactome pathway enrichment table / Reactome 富集结果表 |
| `Reactome_DEG_Mutant_vs_Mutant_Rap_up_dotplot.png` | enrich.R (Reactome, offline cache) | Reactome pathway dotplot / Reactome 气泡图 |

_This file is auto-generated by `enrich.R` at the end of every run._

