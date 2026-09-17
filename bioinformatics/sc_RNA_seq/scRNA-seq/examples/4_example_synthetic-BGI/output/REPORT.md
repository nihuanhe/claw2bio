# scRNA-seq pipeline REPORT

- date: 2026-09-16T17:21:39.555671
- mode: **single** (exploratory, no group info)
- samples: 1 | cells after QC: 34 | clusters: 1


## Memory notes / 内存提示

> merge/integration (and downstream pseudotime) are the memory-peak steps. All checkpoints live in `.checkpoints/`; rerun with `--resume` after a crash. 大数据量时合并/整合（以及后续拟时序）可能爆内存——崩了用 --resume 续跑，或加 --downsample N 先探索。


## Stage 00.5 — input inspection / 输入体检

- **BGI_sampleA** (10x_mtx)
  - [fixed] no Ensembl IDs detected in feature file; assuming col1=symbol (gene.column=1) (features.tsv.gz)
  - [fixed] mitochondrial prefix looks like ^MT\. (6 genes); will auto-select unless --mt-pattern overrides
- WARNING: single-sample exploratory mode (no metadata given)

## Stage 02 — QC

- thresholds: percent.mt < 50%, 5 < nFeature < 50
- BGI_sampleA: 38 -> 34 cells (89.5%)

## Stage 03 — clustering

- normalization: LogNormalize | integration: none (single sample) | resolution: 0.5
- see `clustree_resolution_scan.png` to tune `--resolution`

## Stage 04 — annotation

- annotation skipped; `cell_type_final` falls back to `Cluster_N` labels

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
