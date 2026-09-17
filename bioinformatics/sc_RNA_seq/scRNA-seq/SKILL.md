---
name: scRNA-seq
description: Single-cell RNA-seq regular pipeline from raw matrices to an annotated Seurat object (read → QC → normalize → integrate → cluster → UMAP/t-SNE → markers → SingleR annotation), hardened for real-world messy inputs. Stage-00 dependency check; stage-00.5 input inspection auto-repairs the input zoo — 10X mtx (features.tsv vs old genes.tsv), tar/tar.gz bundles with nested mm10 dirs, 10X h5, h5ad (via anndata export, no SeuratDisk), rds/RData (Seurat object validation + v4 upgrade), txt/csv.gz text matrices (orientation auto-detected), BGI exports (gene.column=1 + MT. mitochondrial prefix), multi-sample mixtures. Multi-sample runs default to Harmony integration with before/after UMAPs; doublets via scDblFinder (default on); per-sample QC threshold advice printed; every stage checkpoints an rds for --resume (memory blow-ups are ROUTINE — merge/integration is the peak, all inputs are staged before it). The pipeline stops at annotation; personalized follow-ups are separate skills consuming annotated_seurat.rds — scRNA-seq-pseudotime (monocle3), scRNA-seq-virtual-ko (scTenifoldKnk), scRNA-seq-compare (planned). Manual annotation channel: hand-written cluster→cell_type CSV + apply_manual_annotation.R.（中文摘要：单细胞常规流程 skill，从各种格式的原始矩阵到注释好的 Seurat 对象为止。输入体检自动识别并修复 9 类格式坑（10X 新旧版/tar 嵌套/h5/h5ad/rds/文本矩阵/华大 BGI/多样本混杂）；多样本默认 Harmony 整合并出前后对照图；双细胞默认开；每步自动存 checkpoint 支持断点续跑（爆内存是常态，合并/整合是高峰，所有输入就绪后才进合并）；组间比较、拟时序、虚拟敲除是独立后续 skill，都吃本流程的 annotated_seurat.rds；支持手动注释 CSV 一键回写。）
---

# Skill: scRNA-seq (regular pipeline: raw matrices → annotated Seurat object)

## Trigger phrases

- scRNA-seq analysis / 单细胞测序分析
- read 10X / h5 / h5ad / BGI single-cell data / 读取单细胞数据
- Seurat clustering / cell annotation / SingleR / 细胞聚类注释

(Follow-ups — pseudotime / virtual knockout / group comparison — are separate
skills: `scRNA-seq-pseudotime`, `scRNA-seq-virtual-ko`, `scRNA-seq-compare`.
They ALL consume this pipeline's `annotated_seurat.rds` — run this pipeline
FIRST.)

## What it does

Stage 00 verifies R package dependencies (missing → `--install-deps` or manual
install; the pipeline never starts on a broken environment).

Stage 00.5 inspects every input, auto-repairs common format traps and prints
each repair as `[fixed]` (see "特殊情况速查" below). **All inputs are fully
unpacked and repaired before any heavy step runs** — merge/integration is the
memory-peak stage.

Input: a directory (one 10X dir / a dir of per-sample dirs or files / mixed)
or a single file; plus an OPTIONAL `--metadata sample_metadata.csv`
(`sample,group`). Output: `annotated_seurat.rds` (Seurat v5, meta.data has
`orig.ident / group / seurat_clusters / SingleR_* / cell_type_final`), QC
violins before/after, UMAP+t-SNE sets (by cluster/sample/group; integration
before/after for multi-sample), marker tables (presto-accelerated), per-cluster
annotation table, `REPORT.md`, `run_metadata.json`. **The regular pipeline
stops at annotation.**

## Usage

```bash
python scripts/run_scrnaseq.py <input_dir> <output_dir> \
  [--metadata sample_metadata.csv] [--organism human] --overwrite
```

Bundled runnable example (downsampled GSE234527, 5 samples × 400 cells):

```bash
cd sc_RNA_seq/scRNA-seq
python scripts/run_scrnaseq.py \
  examples/1_example_GSE234527_downsampled-10x-mtx/input \
  examples/1_example_GSE234527_downsampled-10x-mtx/output \
  --metadata examples/1_example_GSE234527_downsampled-10x-mtx/input/sample_metadata.csv \
  --overwrite
```

BGI auto-detection example (synthetic fixture):

```bash
python scripts/run_scrnaseq.py \
  examples/4_example_synthetic-BGI/input \
  examples/4_example_synthetic-BGI/output \
  --min-features 5 --mt-max 50 --max-features-qc 50 --no-tsne --overwrite
```

## 特殊情况速查 / special situations

Stage 00.5 auto-fixes and prints `[fixed]` for: genes.tsv vs features.tsv,
swapped feature columns (BGI → `gene.column=1`), mitochondrial prefix variants
(`MT-`/`Mt-`/`mt-`/`MT.`), tar bundles with nested `mm10/` dirs, h5ad (anndata
export), transposed text matrices, metadata↔sample name mismatches (fuzzy
matching, GSM prefixes / `.tar` suffixes tolerated). Full symptom table:
**[docs/decision-tree.md](docs/decision-tree.md)**.

| Situation | Entry |
|---|---|
| memory blow-up (routine!) | crash → rerun with `--resume`; big data → `--downsample N` first |
| batch separation on UMAP | multi-sample runs default to `--integrate harmony` (before/after UMAPs written); `--integrate cca\|rpca\|none` |
| wrong cluster count | check `clustree_resolution_scan.png`, rerun `--resolution` (with `--resume`) |
| percent.mt all zeros | mt prefix sniffed automatically; override `--mt-pattern "^MT-"` |
| retention <50% or >95% | per-sample advice printed in REPORT; adjust `--mt-max` / feature range |
| blood contamination | `percent.hb` flagged, never auto-removed |
| old rds (v4 Seurat) | auto `JoinLayers`/validation in stage 01 |
| manual annotation | copy `top10_markers.csv` → two-column `cluster,cell_type` CSV → `Rscript scripts/apply_manual_annotation.R <rds> <csv> <outdir>` (also documented in every REPORT.md) |

## Input formats (stage 00.5 zoo)

| # | format | handling |
|---|---|---|
| 1 | 10X dir, features.tsv[.gz] (3 col) | `Read10X(gene.column=2)` |
| 2 | 10X dir, genes.tsv (2 col, old) | `Read10X(gene.column=2)` |
| 3 | .tar/.tar.gz with nested triplet | unpacked to `.staging/`, triplet dir auto-found |
| 4 | 10X h5 | `Read10X_h5` |
| 5 | h5ad | anndata export → triplet in `.staging/` (features written without index) |
| 6 | rds/RData | Seurat object → validated/upgraded; bare matrix → CreateSeuratObject |
| 7 | txt/tsv/csv(.gz) matrix | delimiter + orientation auto-detected, transposed if needed |
| 8 | BGI (10X-like, symbol in col1) | `gene.column=1` + `MT.` mt prefix auto-selected |
| 9 | multi-sample mixture of the above | per-sample classification, then merge |

`sample_metadata.csv` (optional): columns `sample,group`. Sample names are
fuzzy-matched (extensions / GSM prefixes tolerated). No metadata →
single-sample exploratory mode (group column absent, noted in REPORT).

## Output files

| file | content |
|---|---|
| `annotated_seurat.rds` | THE deliverable — also written to `.checkpoints/04_annotated.rds` |
| `markers_all.csv`, `top10_markers.csv` | presto wilcoxauc per cluster |
| `annotation_per_cluster.csv` | per-cluster label per reference + `refs_agree` flag |
| `QC_violin_before/after.png/pdf` | nFeature/nCount/percent.mt per sample |
| `UMAP_by_{seurat_clusters,orig.ident,group}.*`, `TSNE_by_*` | embeddings |
| `UMAP_before/after_integration.*` | integration sanity check (multi-sample) |
| `clustree_resolution_scan.png/pdf` | resolution 0.1–1.2 scan (if clustree installed) |
| `marker_heatmap.*`, `marker_dotplot.*` | top-5 markers per cluster |
| `run_metadata.json` | params, input diagnostics, per-sample stats, versions |
| `REPORT.md` | human-readable run report + manual-annotation how-to |
| `.checkpoints/` | per-stage rds + `.done_*` flags for `--resume` |

`cell_type_final` priority: **manual annotation > SingleR cluster consensus >
Cluster_N**. Downstream skills read ONLY this column.

## Parameters

| flag | default | description |
|---|---|---|
| `--metadata` | — | sample,group CSV (absent → exploratory mode) |
| `--organism` | `human` | `human`/`mouse` (references + mt/hb prefixes) |
| `--mt-pattern` | auto-sniffed | regex for mitochondrial genes |
| `--min-cells` / `--min-features` | 3 / 200 | CreateSeuratObject + QC low bound |
| `--mt-max` | 20 | percent.mt QC threshold (%) |
| `--max-features-qc` | 6000 | nFeature upper bound |
| `--no-doublets` | off | skip scDblFinder |
| `--integrate` | `harmony` | `harmony`/`cca`/`rpca`/`none` (multi-sample only) |
| `--sct` | off | SCTransform instead of LogNormalize |
| `--resolution` | 0.5 | clustering resolution (see clustree plot) |
| `--no-tsne` | off | skip t-SNE |
| `--downsample N` | 0 | subsample N cells/sample (exploratory) |
| `--reference` / `--custom-ref` | — | SingleR celldex reference / custom rds |
| `--marker-file` | — | supplementary marker CSV |
| `--no-annotation` | off | skip SingleR (labels = Cluster_N) |
| `--install-deps` | off | auto-install missing R packages / anndata |
| `--rscript` | auto-detect | path to Rscript (PATH → Windows registry) |
| `--resume` | off | skip completed stages (checkpoints) |
| `--export-slim` | off | also write `annotated_seurat.slim.rds` (DietSeurat: keeps counts/data + pca/umap; for COS distribution & sharing) |
| `--overwrite` | off | allow non-empty output dir |

## Dependencies

- Python 3.10+: `pandas numpy scipy`; `anndata` ONLY when an h5ad input exists.
- R (≥4.5) with: `Seurat harmony SingleR celldex scDblFinder clustree presto
  hdf5r Matrix ggplot2 dplyr patchwork data.table jsonlite`
  (scDblFinder / clustree are optional — stages degrade gracefully).
- Tested version matrix: R 4.5.2, Seurat 5.4.0, SeuratObject 5.3.0,
  Matrix 1.7.5, harmony 1.2.4, SingleR 2.12.0, celldex 1.20.0, presto 1.0.0,
  hdf5r 1.3.12. **Known trap: Matrix/SeuratObject ABI mismatch → segfault in
  readMM/Read10X; reinstall both from the same CRAN snapshot** (see
  docs/decision-tree.md #17).
- The shared Windows-binary R mini-repo `resources/r-deps` (bulk-RNA-seq
  family) is being extended with this closure; celldex references + presto are
  distributed via COS (see examples/manifest.csv / website Download page).

## Notes

- Never modifies input files; unpacks/exports go to `<output>/.staging/`.
- Every stage checkpoints (`<output>/.checkpoints/`); `--resume` after crashes.
- merge + integration are the memory-peak steps and run only after ALL inputs
  are staged; README/REPORT carry the warning. Downstream pseudotime inherits
  this convention.
- presto is called on the matrix directly (the CRAN presto 1.0.0 Seurat method
  uses the defunct `slot=` argument).

> 中文提示：本 skill 只到"自动注释"为止；拟时序（scRNA-seq-pseudotime）、虚拟敲除
> （scRNA-seq-virtual-ko）、组间比较（scRNA-seq-compare，规划中）是独立 skill，都吃本
> 流程的 `annotated_seurat.rds`。手动注释：把 `top10_markers.csv` 改成 `cluster,cell_type`
> 两列 CSV，跑 `apply_manual_annotation.R`（REPORT.md 里有同样指引）。爆内存是常态：
> 崩了 `--resume` 续跑，大样本先 `--downsample`。h5ad 需要 `pip install anndata`。
