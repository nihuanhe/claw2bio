# scRNA-seq-virtual-ko REPORT

- input rds: D:\single_cell_1\GSE234527_output\annotated_seurat.rds
- knocked-out gene: **ACTA2** (expression rank in data: 23)
- cells used: 10859 | genes in network: 2000 | networks averaged: 5
- significant differentially regulated (p_adj<0.05): 54

## 注意

> 虚拟敲除是**计算预测**（基于基因调控网络的扰动模拟），结果需实验验证；目标基因表达太低时结果不可靠（见上行 rank）。

## Output files

| file | content |
|---|---|
| `<GENE>_diffRegulation.csv` | full scTenifoldKnk result table |
| `<GENE>_barplot_top20.png/pdf` | top-20 |FC| genes |
| `<GENE>_zscore_scatter.png/pdf` | Z-score vs -log10(p_adj) |
| `virtual_ko_summary.json` | machine-readable summary |