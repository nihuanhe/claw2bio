# scRNA-seq

单细胞常规流程：从各种格式的原始矩阵 → 注释好的 Seurat 对象（annotated_seurat.rds）。

The regular single-cell RNA-seq pipeline: read (any common format) → QC →
normalize → integrate (multi-sample) → cluster → UMAP/t-SNE → markers → SingleR
annotation. Everything the follow-up skills (pseudotime, virtual knockout,
group comparison) need starts from this pipeline's `annotated_seurat.rds`.

## Quick start

```bash
python scripts/run_scrnaseq.py <input_dir> <output_dir> \
  --metadata sample_metadata.csv --overwrite
```

- `<input_dir>`: a 10X directory, a folder of per-sample subdirectories, a
  folder of files (`.h5` / `.h5ad` / `.rds` / `.tar(.gz)` / `.txt.gz` /
  `.csv.gz`), or a single file. Mixed formats are fine.
- `--metadata` (optional): CSV with `sample,group`. Without it the run is a
  single-sample exploratory analysis.
- Stage 00 checks dependencies first (`--install-deps` to auto-install).
- Stage 00.5 inspects and auto-repairs inputs, printing every fix as `[fixed]`.

See `SKILL.md` for the full input zoo, parameters and special situations;
`docs/decision-tree.md` for symptom → diagnosis → parameter; `examples/` for
runnable fixtures and the per-dataset case files.

## Memory / 内存（重要）

爆内存是**常态**不是意外：

- 每个 stage 自动把中间对象存进 `<output>/.checkpoints/`，崩了之后
  `--resume` 从断点续跑；
- 合并（merge）与整合（integration）是内存最高峰，流程保证所有输入文件
  就绪后才进入这一步；下游拟时序（monocle3）同样吃内存；
- 机器扛不住时先加 `--downsample N`（每样本抽 N 细胞）做探索性聚类，
  再全量跑。

## Manual annotation / 手动注释

SingleR 是基线，专家判断是终裁。手动注释流程（同样写在每份 REPORT.md 里）：

1. 复制输出目录的 `top10_markers.csv` → `manual_annotation.csv`，整理成两列
   `cluster,cell_type`（每群一行，填你的专家判断）；
2. 让 AI agent 执行（或自己跑）：
   ```bash
   Rscript scripts/apply_manual_annotation.R \
     <output>/annotated_seurat.rds manual_annotation.csv <output>
   ```
3. `cell_type_final` 被手动标签覆盖、注释 UMAP 重画。优先级：
   手动注释 > SingleR consensus > Cluster_N。

## Downstream skills / 下游

| skill | input |
|---|---|
| `../scRNA-seq-pseudotime` | `annotated_seurat.rds`（先跑本流程） |
| `../scRNA-seq-virtual-ko` | `annotated_seurat.rds` + 目标基因 |
| `../scRNA-seq-compare`（规划中） | `annotated_seurat.rds` + 用户指定对比组 |

Example data availability: see `examples/manifest.csv` (repo fixture / GEO
link / COS link per example). Full-dataset slim annotated rds files are
served via COS so downstream skills can be tried without re-running this
pipeline.
