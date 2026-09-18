# scRNA-seq-pseudotime REPORT

- input rds: D:\single_cell_1\GSE234527_output\annotated_seurat.rds
- cells: 10859 | root: cluster 0
- pseudotime genes (q<0.05): 13790

## Memory / 内存

> learn_graph/graph_test 是内存高峰。learn_graph 后自动写 `.checkpoint_cds_learned.rds`；崩溃后用 `--resume` 复用该检查点（跳过建 cds 与 learn_graph，成功结束时检查点会自动删除）。

## Output files

| file | content |
|---|---|
| `pseudotime_cds.rds` | monocle3 cell_data_set with pseudotime |
| `trajectory_by_pseudotime/cluster/group.*` | trajectory plots |
| `pseudotime_genes.csv` | graph_test result (q<0.05 significant) |
| `pseudotime_summary.json` | machine-readable summary |

## Root choice / 起点

Root was chosen by the user (biological decision). To redo with another root, rerun with a different --root-cluster/--root-label.