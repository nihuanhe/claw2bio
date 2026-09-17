# Example 1 (smoke) — pseudotime on the main pipeline's example 1 output

输入 = `../../../scRNA-seq/examples/1_example_GSE234527_downsampled-10x-mtx/output/annotated_seurat.rds`
（主流程 example 1 的真实产出，人 PBMC 样降采样数据）。

## 运行

```bash
python scripts/run_pseudotime.py \
  ../scRNA-seq/examples/1_example_GSE234527_downsampled-10x-mtx/output/annotated_seurat.rds \
  examples/1_smoke/output --root-cluster 0 --overwrite
```

预期：9 cluster 的轨迹图（拟时序/cluster/group/样本 4 套着色）、
`pseudotime_genes.csv`（graph_test）、top 基因轨迹表达图。
起点 cluster 0 仅为演示——真实分析按生物学问题选根（不给 root 会打印
cluster→标签对照表后退出）。

> 完整数据（GSE234527 全量 / 25057A 等）的拟时序案例上线前补跑，
> slim annotated rds 可从 COS 下载直接复现（见主 skill examples/manifest.csv）。
