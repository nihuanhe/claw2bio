---
name: scRNA-seq-virtual-ko
description: Virtual gene knockout (in-silico perturbation) with scTenifoldKnk on the scRNA-seq regular pipeline's annotated_seurat.rds. Builds gene-regulatory networks from the RNA counts layer (optionally pre-subset to cell types via --subset-labels), virtually knocks out a user-given gene, and outputs the differential-regulation table + top-20 barplot + Z-score scatter. Handles scTenifoldKnk version differences (function/argument/column renames across releases). Slow on big objects — tune --nfeatures/--nc-nnet.（中文摘要：虚拟敲除 skill（scTenifoldKnk，PMID:35510185）。前提：先跑 scRNA-seq 常规流程拿 annotated_seurat.rds。指定目标基因即可（--gene TP53），可先用 --subset-labels 圈定细胞类型再建调控网络；产出差异调控表 + top20 条形图 + Z 值散点图。大对象跑得慢，用 --nfeatures/--nc-nnet 控制规模。结果是计算预测，需实验验证。）
---

# Skill: scRNA-seq-virtual-ko (scTenifoldKnk in-silico knockout)

## Trigger phrases

- 虚拟敲除 / virtual knockout / in-silico knockout
- scTenifoldKnk / 计算敲除某基因

## Prerequisite / 前提

**Run the `../scRNA-seq` regular pipeline FIRST** — this skill consumes its
`annotated_seurat.rds` (RNA counts layer + `cell_type_final` for subsetting).
必须先用常规流程跑出 annotated_seurat.rds；本 skill 不做 QC/聚类。

## Usage

```bash
python scripts/run_virtual_ko.py <annotated_seurat.rds> <output_dir> \
  --gene TP53
```

Subset to the relevant cell type first (network is built from those cells):

```bash
python scripts/run_virtual_ko.py annotated_seurat.rds output --gene TP53 \
  --subset-labels "Epithelial cells"
```

## Parameters

| flag | default | description |
|---|---|---|
| `--gene` | (required) | gene symbol to knock out (case-sensitive) |
| `--subset-labels` | — | comma-separated cell_type_final labels to subset first |
| `--nfeatures` | 2000 | variable genes for network construction |
| `--all-genes` | off | use all genes (slow, memory-heavy) |
| `--nc-nnet` | 10 | subsampled networks to average |
| `--nc-ncells` | 500 | cells per subsampled network; 0 = all cells (**runtime ~quadratic — all-cells with thousands of genes stalled >8 h in testing**) |
| `--cores` | detect-1 | parallel cores |
| `--overwrite` / `--rscript` | — | usual |

## Outputs

| file | content |
|---|---|
| `<GENE>_diffRegulation.csv` | full result (Gene, distance, Z, FC, p_value, p_adj) |
| `<GENE>_barplot_top20.png/pdf` | top-20 \|FC\| genes |
| `<GENE>_zscore_scatter.png/pdf` | Z vs -log10(p_adj), significant labelled |
| `virtual_ko_summary.json`, `REPORT.md` | summary + report |

## Notes

- The target gene is force-included in the network gene set even if not
  variable; a warning prints when it is expressed in <5% of cells.
- Results are computational predictions from network perturbation — validate
  experimentally.
- Runtime scales ~quadratically with genes and per-network cells; the smoke
  example (500 genes x 3 nets) takes minutes. **Runtime on full-size settings is
  not yet characterised**: a 2000-gene x 10-net run with the default 500-cell
  subsampling was measured at >3.5 h without finishing on a 16 GB / 12-core
  Windows machine (killed). Budget hours, and use `--nc-nnet` as the main knob.
  **never combine all-cells with thousands of genes** (see `--nc-ncells`).
- **No checkpoint / not resumable.** scTenifoldKnk is a single non-interruptible
  call, so unlike the main pipeline and `scRNA-seq-pseudotime` this skill has no
  `--resume`: if the run dies or the machine sleeps, all work is lost. Confirm
  the machine will not sleep before starting a long run.
- Version drift handled internally: scTenifoldKnk ≤1.0.3 exports
  `scTenifoldKnk()` (not `sctenifoldknk()`) with args `gKO/qc/nc_nNet/nCores`
  and result columns `gene/p.adj`; the stage script harmonises to
  Gene/p_value/p_adj.

## Dependencies

R (≥4.5): `scTenifoldKnk Seurat dplyr ggplot2 ggrepel parallel jsonlite`.
scTenifoldKnk is distributed as a Windows binary zip (see COS / resources).
Tested: scTenifoldKnk 1.0.3. Python driver: stdlib only.
