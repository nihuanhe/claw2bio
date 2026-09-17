# scRNA-seq pipeline REPORT

- date: 2026-09-17T19:01:17.307261
- mode: **single** (exploratory, no group info)
- samples: 1 | cells after QC: 46059 | clusters: 27


## Memory notes / 内存提示

> merge/integration (and downstream pseudotime) are the memory-peak steps. All checkpoints live in `.checkpoints/`; rerun with `--resume` after a crash. 大数据量时合并/整合（以及后续拟时序）可能爆内存——崩了用 --resume 续跑，或加 --downsample N 先探索。


## Stage 00.5 — input inspection / 输入体检

- **GSM6923183_MC_scRNA** (10x_mtx)
  - [fixed] h5ad: X was not counts -> exported raw counts from layers['counts']
  - [fixed] h5ad exported via anndata -> E:\工作\博士后阶段\课题\课题-AI-Openclaw\内容整理\bioinformatics\sc_RNA_seq\scRNA-seq\examples\5_example_GSM6923183_h5ad\output\.staging\h5ad_GSM6923183_MC_scRNA (features written WITHOUT index, gene ids kept in col1)
- WARNING: single-sample exploratory mode (no metadata given)

## Stage 02 — QC

- thresholds: percent.mt < 20%, 200 < nFeature < 6000
- GSM6923183_MC_scRNA: 53748 -> 53748 cells (100%)
  - **advice**: retention 100% > 95%: consider lowering --mt-max (e.g. 15) and tightening nFeature range
- doublet rate per sample (%): [14.31]

## Stage 03 — clustering

- normalization: LogNormalize | integration: none (single sample) | resolution: 0.5
- see `clustree_resolution_scan.png` to tune `--resolution`

## Stage 04 — annotation

- SingleR references: HPCA, BlueprintEncode
- **clusters where the two references disagree (manual review advised)**: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26

## Manual annotation / 手动注释

SingleR is a baseline. To apply your own labels:
1. copy `top10_markers.csv` -> `manual_annotation.csv`, keep/make two columns: `cluster,cell_type` (one row per cluster, your expert call per cluster).
2. run: `Rscript scripts/apply_manual_annotation.R <output>/annotated_seurat.rds manual_annotation.csv <output>`
   (or ask your AI agent: "用 apply_manual_annotation.R 把我的手动注释 CSV 应用到 annotated_seurat.rds")
3. `cell_type_final` will be overwritten and the annotated UMAP regenerated. 优先级：手动注释 > SingleR consensus > Cluster_N。

## Output files / 产出文件

| file | content |
|---|---|
| `annotated_seurat.rds` | THE deliverable: QC'd, clustered, annotated Seurat v5 object (meta.data: orig.ident/group/seurat_clusters/SingleR_*/cell_type_final) |
| `markers_all.csv`, `top10_markers.csv` | marker tables (presto) |
| `annotation_per_cluster.csv` | per-cluster labels from each reference + agreement flag |
| `QC_violin_before/after.png/pdf` | QC violins |
| `UMAP_*.png/pdf`, `TSNE_*.png/pdf` | embeddings by cluster/sample/group |
| `UMAP_before/after_integration.*` | integration sanity check (multi-sample) |
| `marker_heatmap/dotplot.*` | top markers |
| `run_metadata.json` | machine-readable run record |
| `.checkpoints/` | per-stage rds for `--resume` |

## Next steps / 下游 skill

- `scRNA-seq-pseudotime` (monocle3): input = `annotated_seurat.rds`
- `scRNA-seq-virtual-ko` (scTenifoldKnk): input = `annotated_seurat.rds` + target gene
- `scRNA-seq-compare` (planned): group comparison on `annotated_seurat.rds`
