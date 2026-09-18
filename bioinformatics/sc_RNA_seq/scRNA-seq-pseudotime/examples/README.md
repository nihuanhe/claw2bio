# Examples — scRNA-seq-pseudotime

## 1_smoke — 主流程 example 1 产出的冒烟测试

输入 = `../../../scRNA-seq/examples/1_example_GSE234527_downsampled-10x-mtx/output/annotated_seurat.rds`
（主流程 example 1 的真实产出，人 PBMC 样降采样数据）。

```bash
python scripts/run_pseudotime.py \
  ../scRNA-seq/examples/1_example_GSE234527_downsampled-10x-mtx/output/annotated_seurat.rds \
  examples/1_smoke/output --root-cluster 0 --overwrite
```

预期：9 cluster 的轨迹图（拟时序/cluster/group/样本 4 套着色）、
`pseudotime_genes.csv`（graph_test）、top 基因轨迹表达图。
起点 cluster 0 仅为演示——真实分析按生物学问题选根（不给 root 会打印
cluster→标签对照表后退出）。

## 2_real_GSE234527 — 真实全量数据（已跑通归档）

输入 = GSE234527 全量 `annotated_seurat.rds`（10,859 细胞，**不随仓库/zip 分发**；
slim 版可从 COS 下载，见主 skill `examples/manifest.csv`）。

```bash
python scripts/run_pseudotime.py <annotated_seurat.rds> examples/2_real_GSE234527/output \
  --root-cluster 0
```

实测（16 GB / 12 核 Windows，R 4.5.2）：全程约 11 min，其中 graph_test 约 9 min
（8 核）；`pseudotime_genes.csv` 17,655 行，13,790 个基因 q < 0.05。
已覆盖参数分支：无 root 拒绝+打印对照表、`--root-cluster`、`--root-label`、
`--subset-labels`、`--no-graph-test`（80 s）、`--resume` 断点续跑。
归档内容 = 图 + csv + summary + REPORT；`pseudotime_cds.rds`（26.8 MB）按约定不进 git。
