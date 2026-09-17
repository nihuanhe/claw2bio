# scRNA-seq-pseudotime REPORT

- input rds: ../scRNA-seq/examples/1_example_GSE234527_downsampled-10x-mtx/output/annotated_seurat.rds
- cells: 1820 | root: cluster 0
- pseudotime genes (q<0.05): 2227

## Memory / 内存

> learn_graph/graph_test 是内存高峰；崩了检查点后 `--resume` 思路同主流程。

## Output files

| file | content |
|---|---|
| `pseudotime_cds.rds` | monocle3 cell_data_set with pseudotime |
| `trajectory_by_pseudotime/cluster/group.*` | trajectory plots |
| `pseudotime_genes.csv` | graph_test result (q<0.05 significant) |
| `pseudotime_summary.json` | machine-readable summary |

## Root choice / 起点

Root was chosen by the user (biological decision). To redo with another root, rerun with a different --root-cluster/--root-label.