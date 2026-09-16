---
name: RNA-seq-gsea
description: GSEA (gene set enrichment analysis) on bulk RNA-seq DEG tables using fgsea and MSigDB-format GMT gene sets. Use after the bulk-RNA-seq pipeline — when the user asks for GSEA, 基因集富集分析, pathway enrichment of the full ranked gene list (not just significant DEGs), NES plots, enrichment curves. Fully offline once GMT files are in place.
---

# RNA-seq GSEA (fgsea + MSigDB GMT)

Personalized follow-up to the **bulk-RNA-seq** skill. Unlike the threshold-based
enrichment in `RNA-seq-enrichment`, GSEA uses the **entire ranked gene list** (all
genes by signed metric: `sign(log2FC) × -log10(pvalue)`), which detects
subtle but coordinated pathway shifts.

**Prerequisite / 前提**: run `bioinformatics/bulk-RNA-seq` first; this skill
consumes a `DEG_*.csv` table (`gene`, `log2fc`/`log2FoldChange`/`logFC`,
`pvalue`, `padj`).

## Quick start

```bash
cd bioinformatics/RNA-seq-gsea
Rscript scripts/00_check_deps.R --organism mouse
Rscript scripts/gsea.R examples/input/DEG_Mutant_vs_Control.csv \
  --gmt resources/gmt/reactome_demo_mmu.gmt --organism mouse \
  --outdir examples/output
```

## Usage

```
Rscript scripts/gsea.R <DEG_table.csv>
        [--gmt file1.gmt[,file2.gmt]]   # default: all *.gmt in resources/gmt/
        [--organism mouse|human] [--rank auto|log2fc|stat] [--outdir DIR]
```

- **Gene-set files**: MSigDB GMT format. Put your MSigDB downloads (e.g.
  `m2.all.v2025.1.Mm.entrez.gmt`, `m2.all.v2025.1.Mm.symbols.gmt`, `mh.all...`
  Hallmark) into `resources/gmt/` — ID type (Entrez vs symbol) is auto-detected
  **per GMT** and our IDs are converted accordingly via OrgDb. Mixed GMT lists
  are fine.
- A bundled `reactome_demo_mmu.gmt` (open-license, built from the Reactome
  cache) makes the skill runnable out of the box; MSigDB files stay local
  (registration/download terms).
- Outputs per GMT: `GSEA_<label>_<gmt>.csv` (NES/padj/leadingEdge), a top-15
  NES dotplot, and the classic enrichment curve of the top significant set.

## Dependencies

- R: fgsea, ggplot2, org.Mm.eg.db / org.Hs.eg.db (ID conversion).
  `00_check_deps.R [--install]` verifies / installs.

## Notes

- MSigDB mouse C2 (m2.all) contains Reactome/BioCarta/WikiPathways + curated
  published sets, but **no KEGG** (licensing) — for KEGG use RNA-seq-enrichment.
- 中文提示：必须先跑 bulk-RNA-seq 常规管线拿到 DEG 表；GSEA 用全部基因的
  排序列表，不是只用显著基因；MSigDB 的 .gmt 文件拷进 resources/gmt/ 即可
  （Entrez/symbol 自动识别，可混用）；fgsea 强制串行（并行 socket 在部分
  Windows 环境打不开端口会卡死）；不改输入文件。
