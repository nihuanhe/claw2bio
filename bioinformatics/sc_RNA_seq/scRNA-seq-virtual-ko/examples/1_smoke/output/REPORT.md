# scRNA-seq-virtual-ko REPORT

- input rds: ../scRNA-seq/examples/1_example_GSE234527_downsampled-10x-mtx/output/annotated_seurat.rds
- knocked-out gene: **ADIRF** (expression rank in data: 60)
- cells used: 1820 | genes in network: 500 | networks averaged: 3
- significant differentially regulated (p_adj<0.05): 14

## 注意

> 虚拟敲除是**计算预测**（基于基因调控网络的扰动模拟），结果需实验验证；目标基因表达太低时结果不可靠（见上行 rank）。

## Output files

| file | content |
|---|---|
| `<GENE>_diffRegulation.csv` | full scTenifoldKnk result table |
| `<GENE>_barplot_top20.png/pdf` | top-20 |FC| genes |
| `<GENE>_zscore_scatter.png/pdf` | Z-score vs -log10(p_adj) |
| `virtual_ko_summary.json` | machine-readable summary |