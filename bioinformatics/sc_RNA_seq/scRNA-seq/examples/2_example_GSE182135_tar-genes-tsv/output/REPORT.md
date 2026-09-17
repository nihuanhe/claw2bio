# scRNA-seq pipeline REPORT

- date: 2026-09-17T18:21:05.339674
- mode: **multi** (grouped)
- samples: 10 | cells after QC: 54484 | clusters: 21


## Memory notes / 内存提示

> merge/integration (and downstream pseudotime) are the memory-peak steps. All checkpoints live in `.checkpoints/`; rerun with `--resume` after a crash. 大数据量时合并/整合（以及后续拟时序）可能爆内存——崩了用 --resume 续跑，或加 --downsample N 先探索。


## Stage 00.5 — input inspection / 输入体检

- **GSM5519136_E9_5_rep1_2018JULY18.tar** (10x_mtx, group=E9.5)
  - [fixed] mitochondrial prefix looks like ^mt- (13 genes); will auto-select unless --mt-pattern overrides
  - [fixed] metadata sample 'GSM5519136_E9_5_rep1_2018JULY18' matched to 'GSM5519136_E9_5_rep1_2018JULY18.tar'
- **GSM5519137_E9_5_rep2_2018AUG07.tar** (10x_mtx, group=E9.5)
  - [fixed] mitochondrial prefix looks like ^mt- (13 genes); will auto-select unless --mt-pattern overrides
  - [fixed] metadata sample 'GSM5519137_E9_5_rep2_2018AUG07' matched to 'GSM5519137_E9_5_rep2_2018AUG07.tar'
- **GSM5519138_E10_5_rep5_2018AUG16.tar** (10x_mtx, group=E10.5)
  - [fixed] mitochondrial prefix looks like ^mt- (13 genes); will auto-select unless --mt-pattern overrides
  - [fixed] metadata sample 'GSM5519138_E10_5_rep5_2018AUG16' matched to 'GSM5519138_E10_5_rep5_2018AUG16.tar'
- **GSM5519139_E10_5_rep6_2018SEP22.tar** (10x_mtx, group=E10.5)
  - [fixed] mitochondrial prefix looks like ^mt- (13 genes); will auto-select unless --mt-pattern overrides
  - [fixed] metadata sample 'GSM5519139_E10_5_rep6_2018SEP22' matched to 'GSM5519139_E10_5_rep6_2018SEP22.tar'
- **GSM5519140_E10_5_rep7_2018AUG16.tar** (10x_mtx, group=E10.5)
  - [fixed] mitochondrial prefix looks like ^mt- (13 genes); will auto-select unless --mt-pattern overrides
  - [fixed] metadata sample 'GSM5519140_E10_5_rep7_2018AUG16' matched to 'GSM5519140_E10_5_rep7_2018AUG16.tar'
- **GSM5519141_E11_5_rep2_2018JUNE26.tar** (10x_mtx, group=E11.5)
  - [fixed] mitochondrial prefix looks like ^mt- (13 genes); will auto-select unless --mt-pattern overrides
  - [fixed] metadata sample 'GSM5519141_E11_5_rep2_2018JUNE26' matched to 'GSM5519141_E11_5_rep2_2018JUNE26.tar'
- **GSM5519142_E11_5_rep2B_2018JULY27.tar** (10x_mtx, group=E11.5)
  - [fixed] mitochondrial prefix looks like ^mt- (13 genes); will auto-select unless --mt-pattern overrides
  - [fixed] metadata sample 'GSM5519142_E11_5_rep2B_2018JULY27' matched to 'GSM5519142_E11_5_rep2B_2018JULY27.tar'
- **GSM5519143_E11_5_rep3_2018SEP22.tar** (10x_mtx, group=E11.5)
  - [fixed] mitochondrial prefix looks like ^mt- (13 genes); will auto-select unless --mt-pattern overrides
  - [fixed] metadata sample 'GSM5519143_E11_5_rep3_2018SEP22' matched to 'GSM5519143_E11_5_rep3_2018SEP22.tar'
- **GSM5519144_E12_5_rep1_2018JUNE28.tar** (10x_mtx, group=E12.5)
  - [fixed] mitochondrial prefix looks like ^mt- (13 genes); will auto-select unless --mt-pattern overrides
  - [fixed] metadata sample 'GSM5519144_E12_5_rep1_2018JUNE28' matched to 'GSM5519144_E12_5_rep1_2018JUNE28.tar'
- **GSM5519145_E12_5_rep2_2018JUNE28.tar** (10x_mtx, group=E12.5)
  - [fixed] mitochondrial prefix looks like ^mt- (13 genes); will auto-select unless --mt-pattern overrides
  - [fixed] metadata sample 'GSM5519145_E12_5_rep2_2018JUNE28' matched to 'GSM5519145_E12_5_rep2_2018JUNE28.tar'
- WARNING: samples without group (exploratory): ['E10_5_pbmc', 'E11_5_pbmc', 'E12_5_pbmc', 'E9_5_pbmc', 'combined_pbmc']
- WARNING: user-excluded samples: E10_5_pbmc, E11_5_pbmc, E12_5_pbmc, E9_5_pbmc, combined_pbmc

## Stage 02 — QC

- thresholds: percent.mt < 20%, 200 < nFeature < 6000
- GSM5519136_E9_5_rep1_2018JULY18.tar: 5901 -> 5901 cells (100%)
  - **advice**: retention 100% > 95%: consider lowering --mt-max (e.g. 15) and tightening nFeature range
- GSM5519137_E9_5_rep2_2018AUG07.tar: 7760 -> 7754 cells (99.9%)
  - **advice**: retention 100% > 95%: consider lowering --mt-max (e.g. 15) and tightening nFeature range
- GSM5519138_E10_5_rep5_2018AUG16.tar: 5045 -> 4995 cells (99%)
  - **advice**: retention 99% > 95%: consider lowering --mt-max (e.g. 15) and tightening nFeature range
- GSM5519139_E10_5_rep6_2018SEP22.tar: 4324 -> 4242 cells (98.1%)
  - **advice**: retention 98% > 95%: consider lowering --mt-max (e.g. 15) and tightening nFeature range
- GSM5519140_E10_5_rep7_2018AUG16.tar: 4382 -> 4354 cells (99.4%)
  - **advice**: retention 99% > 95%: consider lowering --mt-max (e.g. 15) and tightening nFeature range
- GSM5519141_E11_5_rep2_2018JUNE26.tar: 5878 -> 5872 cells (99.9%)
  - **advice**: retention 100% > 95%: consider lowering --mt-max (e.g. 15) and tightening nFeature range
- GSM5519142_E11_5_rep2B_2018JULY27.tar: 3268 -> 3263 cells (99.8%)
  - **advice**: retention 100% > 95%: consider lowering --mt-max (e.g. 15) and tightening nFeature range
- GSM5519143_E11_5_rep3_2018SEP22.tar: 9413 -> 9407 cells (99.9%)
  - **advice**: retention 100% > 95%: consider lowering --mt-max (e.g. 15) and tightening nFeature range
- GSM5519144_E12_5_rep1_2018JUNE28.tar: 5146 -> 5137 cells (99.8%)
  - **advice**: retention 100% > 95%: consider lowering --mt-max (e.g. 15) and tightening nFeature range
- GSM5519145_E12_5_rep2_2018JUNE28.tar: 6732 -> 6727 cells (99.9%)
  - **advice**: retention 100% > 95%: consider lowering --mt-max (e.g. 15) and tightening nFeature range
- doublet rate per sample (%): {'GSM5519136_E9_5_rep1_2018JULY18.tar': 3.76, 'GSM5519137_E9_5_rep2_2018AUG07.tar': 5.48, 'GSM5519138_E10_5_rep5_2018AUG16.tar': 5.37, 'GSM5519139_E10_5_rep6_2018SEP22.tar': 4.86, 'GSM5519140_E10_5_rep7_2018AUG16.tar': 3.67, 'GSM5519141_E11_5_rep2_2018JUNE26.tar': 6.86, 'GSM5519142_E11_5_rep2B_2018JULY27.tar': 3.74, 'GSM5519143_E11_5_rep3_2018SEP22.tar': 6.72, 'GSM5519144_E12_5_rep1_2018JUNE28.tar': 4.83, 'GSM5519145_E12_5_rep2_2018JUNE28.tar': 7.17}

## Stage 03 — clustering

- normalization: LogNormalize | integration: harmony | resolution: 0.5
- see `clustree_resolution_scan.png` to tune `--resolution`

## Stage 04 — annotation

- SingleR references: M, o, u, s, e, R, N, A, s, e, q, D, a, t, a

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
