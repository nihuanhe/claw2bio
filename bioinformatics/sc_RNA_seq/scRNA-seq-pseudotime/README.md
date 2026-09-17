# scRNA-seq-pseudotime

拟时序分析（monocle3）。**前提：先跑 `../scRNA-seq` 常规流程**，拿到
`annotated_seurat.rds` 后再来本 skill。

```bash
python scripts/run_pseudotime.py <annotated_seurat.rds> <output_dir> \
  --root-cluster 3     # 起点是生物学决策，必须你定；不给会打印 cluster→标签对照表
```

- 复用 Seurat 的 UMAP 坐标和聚类 ID，不重新降维；
- 产出轨迹图（按拟时序/cluster/分组/样本着色）、`pseudotime_genes.csv`
  （graph_test）、top 基因轨迹表达图；
- learn_graph / graph_test 是内存高峰；learn_graph 后写 `.checkpoint_cds_learned.rds`，
  崩溃后加 `--resume` 复用（跳过建 cds 与 learn_graph）；
- 详见 `SKILL.md`；示例见 `examples/1_smoke/`（吃主流程 example 1 的产出）。
