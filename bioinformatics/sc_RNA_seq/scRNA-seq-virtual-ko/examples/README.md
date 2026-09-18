# Examples — scRNA-seq-virtual-ko

## 1_smoke — 主流程 example 1 产出的冒烟测试

输入 = 主流程 example 1 的 `annotated_seurat.rds`（降采样 fixture 的真实产出）。
目标基因 ADIRF（fixture 里 86% 细胞表达的高丰度基因）。

```bash
python scripts/run_virtual_ko.py \
  ../scRNA-seq/examples/1_example_GSE234527_downsampled-10x-mtx/output/annotated_seurat.rds \
  examples/1_smoke/output --gene ADIRF --nfeatures 500 --nc-nnet 3 --overwrite
```

预期：`ADIRF_diffRegulation.csv`（Z/FC/p_adj 全表）、top20 条形图、
Z 值散点图、REPORT.md。本 fixture 是随机子集，生物学结论无意义——
仅验证流程跑通。

## 2_real_GSE234527 — 真实全量数据（已跑通归档）

输入 = GSE234527 全量 `annotated_seurat.rds`（10,859 细胞，**不随仓库/zip 分发**；
slim 版可从 COS 下载，见主 skill `examples/manifest.csv`）。目标基因 ACTA2。

```bash
python scripts/run_virtual_ko.py <annotated_seurat.rds> examples/2_real_GSE234527/output \
  --gene ACTA2 --nc-nnet 5
```

实测（16 GB / 12 核 Windows，2000 高变基因 × 每网 500 细胞）：
`--nc-nnet 3` = 90 min → 58 个显著基因；`--nc-nnet 5` = 约 2 h → 54 个显著基因
（两者重合 41 个，top hits MYLK/TPM1/TPM2/TAGLN/CNN1/DES 均为平滑肌程序基因）。
**建议 `--nc-nnet` ≤ 5**：包默认的 10 在本数据上张量分解不收敛（norm explained
21.8%），manifoldAlignment 内部数值退化报错，2 小时建网结果全部作废。
归档内容 = 图 + csv + summary + REPORT。
