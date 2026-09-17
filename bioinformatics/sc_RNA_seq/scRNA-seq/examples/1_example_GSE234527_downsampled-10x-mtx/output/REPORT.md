# scRNA-seq pipeline REPORT

- date: 2026-09-16T17:56:40.612688
- mode: **multi** (grouped)
- samples: 5 | cells after QC: 1820 | clusters: 9


## Memory notes / 内存提示

> merge/integration (and downstream pseudotime) are the memory-peak steps. All checkpoints live in `.checkpoints/`; rerun with `--resume` after a crash. 大数据量时合并/整合（以及后续拟时序）可能爆内存——崩了用 --resume 续跑，或加 --downsample N 先探索。


## Stage 00.5 — input inspection / 输入体检

- **GSM7470392_352** (10x_mtx, group=Control)
- **GSM7470393_354** (10x_mtx, group=Control)
- **GSM7470394_356** (10x_mtx, group=Treatment)
- **GSM7470395_363** (10x_mtx, group=Treatment)
- **GSM7470396_365** (10x_mtx, group=Treatment)

## Stage 02 — QC

- thresholds: percent.mt < 20%, 200 < nFeature < 6000
- GSM7470392_352: 400 -> 383 cells (95.8%)
  - **advice**: retention 96% > 95%: consider lowering --mt-max (e.g. 15) and tightening nFeature range
- GSM7470393_354: 400 -> 388 cells (97%)
  - **advice**: retention 97% > 95%: consider lowering --mt-max (e.g. 15) and tightening nFeature range
- GSM7470394_356: 400 -> 392 cells (98%)
  - **advice**: retention 98% > 95%: consider lowering --mt-max (e.g. 15) and tightening nFeature range
- GSM7470395_363: 400 -> 393 cells (98.2%)
  - **advice**: retention 98% > 95%: consider lowering --mt-max (e.g. 15) and tightening nFeature range
- GSM7470396_365: 400 -> 375 cells (93.8%)
- doublet rate per sample (%): {'GSM7470392_352': 3.66, 'GSM7470393_354': 4.12, 'GSM7470394_356': 6.63, 'GSM7470395_363': 7.38, 'GSM7470396_365': 6.93}

## Stage 03 — clustering

- normalization: LogNormalize | integration: harmony | resolution: 0.5
- see `clustree_resolution_scan.png` to tune `--resolution`

## Stage 04 — annotation

- SingleR references: HPCA, BlueprintEncode
- **clusters where the two references disagree (manual review advised)**: 0, 1, 2, 3, 4, 5, 6, 7, 8

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
