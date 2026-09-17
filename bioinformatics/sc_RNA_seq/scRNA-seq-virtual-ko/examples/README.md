# Example 1 (smoke) — virtual knockout on the main pipeline's example 1 output

输入 = 主流程 example 1 的 `annotated_seurat.rds`（降采样 fixture 的真实产出）。
目标基因 ADIRF（fixture 里 86% 细胞表达的高丰度基因）。

## 运行

```bash
python scripts/run_virtual_ko.py \
  ../scRNA-seq/examples/1_example_GSE234527_downsampled-10x-mtx/output/annotated_seurat.rds \
  examples/1_smoke/output --gene ADIRF --nfeatures 500 --nc-nnet 3 --overwrite
```

（冒烟用缩小参数 500 基因 × 3 网络，分钟级；真实分析默认 2000 × 10，
小时级。）

预期：`ADIRF_diffRegulation.csv`（Z/FC/p_adj 全表）、top20 条形图、
Z 值散点图、REPORT.md。本 fixture 是随机子集，生物学结论无意义——
仅验证流程跑通。
