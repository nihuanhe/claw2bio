---
name: scRNA-seq-pseudotime
description: Monocle3 pseudotime / trajectory analysis on the scRNA-seq regular pipeline's annotated_seurat.rds. Reuses the Seurat UMAP and cluster IDs (no re-embedding), learns the trajectory graph, orders cells from a user-chosen root cluster or cell-type label, runs graph_test for pseudotime-associated genes, and plots top genes on the trajectory. Root selection is a biological decision — the skill refuses to run without --root-cluster or --root-label and prints the cluster→label table to help you choose. Optional --subset-labels pre-subsets cell types. Checkpoints before the memory-heavy steps.（中文摘要：拟时序分析 skill。前提：先跑 scRNA-seq 常规流程拿到 annotated_seurat.rds。复用 Seurat 的 UMAP 和聚类 ID，monocle3 学轨迹、定起点（必须用户指定 root cluster 或细胞类型标签，会打印 cluster→标签对照表帮你选）、graph_test 找拟时序相关基因、出轨迹图和基因趋势图。learn_graph/graph_test 是内存高峰，有 checkpoint 兜底。）
---

# Skill: scRNA-seq-pseudotime (monocle3 trajectory on annotated rds)

## Trigger phrases

- 拟时序分析 / pseudotime / trajectory analysis
- monocle3 / 细胞分化轨迹

## Prerequisite / 前提

**Run the `../scRNA-seq` regular pipeline FIRST** — this skill consumes its
`annotated_seurat.rds` (needs `seurat_clusters`, UMAP reduction; uses
`cell_type_final` for root-by-label). 必须先用常规流程跑出注释好的
annotated_seurat.rds，本 skill 不做 QC/聚类。

## Usage

```bash
python scripts/run_pseudotime.py <annotated_seurat.rds> <output_dir> \
  --root-cluster 3            # 或 --root-label "Naive CD4 T"
```

Root choice is YOUR biological decision. Run once without a root to get the
cluster → label table printed (the skill exits with the table), or check
`annotation_per_cluster.csv` from the main pipeline.

## Parameters

| flag | default | description |
|---|---|---|
| `--root-cluster` | — | cluster id as trajectory root (required¹) |
| `--root-label` | — | cell_type_final label as root (required¹) |
| `--subset-labels` | — | comma-separated labels to subset cells first |
| `--no-graph-test` | off | skip the slow graph_test step |
| `--cores` | 4 | cores for graph_test |
| `--resume` / `--overwrite` | off | `--resume` reuses `.checkpoint_cds_learned.rds` (skips cds build + learn_graph); `--overwrite` allows a non-empty output dir |
| `--rscript` | auto | path to Rscript |

¹ exactly one of the two root options is required.

## Outputs

| file | content |
|---|---|
| `pseudotime_cds.rds` | monocle3 cell_data_set with pseudotime |
| `trajectory_by_pseudotime/cluster/group/sample.png+pdf` | trajectory plots |
| `pseudotime_genes.csv` | graph_test full table (q_value < 0.05 significant) |
| `gene_<X>_on_trajectory.png+pdf` | top-4 pseudotime genes on the trajectory |
| `REPORT.md`, `pseudotime_summary.json` | report + machine-readable summary |

## Memory / 内存

learn_graph and graph_test are the memory-peak steps (same league as merge/
integration in the main pipeline). A checkpoint cds
(`.checkpoint_cds_learned.rds`) is written right after learn_graph; rerun with
`--resume` after a crash and the cds build + learn_graph are skipped. The
checkpoint is deleted once the run completes; `--resume` without a checkpoint
simply runs from scratch.

## Dependencies

R (≥4.5): `monocle3 Seurat dplyr ggplot2 jsonlite`. Tested: monocle3 1.4.26,
Seurat 5.4.0. Python driver: stdlib only.
