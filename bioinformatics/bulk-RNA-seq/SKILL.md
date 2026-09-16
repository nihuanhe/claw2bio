---
name: bulk-RNA-seq
description: Bulk RNA-seq differential expression from a count matrix (regular pipeline — stops at DEG tables). Data-driven engine fork — non-integer/normalized input → limma-trend, integer counts with small n → DESeq2, integer counts with large n → edgeR+limma-voom — always printing WHY the engine was chosen. Outputs QC (PCA/correlation), DEG tables, volcano plots, DEG heatmap. Follow-up personalized skills consume its outputs — RNA-seq-enrichment (GO/KEGG/Reactome), RNA-seq-gene-plot (gene-of-interest bar charts), RNA-seq-GSEA (GSEA).（中文摘要：bulk RNA-seq 从 counts 矩阵到差异表达的常规流程（到 DEG 为止）。按数据自动选择引擎并强制打印理由。富集、指定基因柱状图、GSEA 是三个独立的后续个性化 skill，都吃本流程的产出。）
---

# Skill: bulk-RNA-seq (regular pipeline: counts → DEG)

## Trigger phrases

- bulk RNA-seq analysis
- differential expression / DEG
- volcano plot from counts
- bulk RNA-seq 差异分析 / 火山图

(Follow-ups — enrichment / gene plots / GSEA — are separate skills:
`RNA-seq-enrichment`, `RNA-seq-gene-plot`, `RNA-seq-GSEA`.)

## What it does

Stage 00 first verifies all R package dependencies and reports anything missing
(you choose: let the agent install via `--install-deps`, or install manually via
miniconda/BiocManager) — the pipeline never starts on a broken environment.

Input: a gene-by-sample count matrix CSV + a sample metadata CSV. Output: the
differential-expression result set — QC (PCA, sample correlation), DEG tables per
contrast (with **gene-symbol columns — Ensembl IDs are converted up front**),
volcano plots labelled with gene symbols, DEG heatmap. **The regular pipeline
stops at DEG**; personalized analyses (enrichment, gene-of-interest plots, GSEA)
are separate skills that consume these outputs.

**Engine fork (automatic, data-driven; the rationale is ALWAYS printed):**

| Input diagnosis | Engine |
|---|---|
| Non-integer / normalized values (FPKM, TPM, log) | limma-trend |
| Integer counts, min group n < 8 | DESeq2 |
| Integer counts, min group n ≥ 8 | edgeR + limma-voom |

Override with `--engine deseq2|edger-limma|limma`; tune the threshold with `--voom-min-n`.

## Usage

```bash
python scripts/run_rnaseq.py <counts.csv> <metadata.csv> <output_dir> \
  --control Control --organism mouse --overwrite
```

Example (bundled GSE270189, mouse prostate basal cells, 3 groups × 2 replicates):

```bash
cd bioinformatics/bulk-RNA-seq
python scripts/run_rnaseq.py \
  examples/1_example_GSE270189_clean-mouse-3groups/input/counts_matrix.csv \
  examples/1_example_GSE270189_clean-mouse-3groups/input/sample_metadata.csv \
  examples/1_example_GSE270189_clean-mouse-3groups/output \
  --control Control --organism mouse --overwrite
```

## 特殊情况速查 / special situations

**先直接跑**：stage 00.5（输入体检）会无损自动修复常见格式坑并逐条打印
`[fixed]`（混合矩阵拆列、后缀剥离、转置、毁名匹配、重复 symbol 聚合、负值归零、
metadata 列名归一化、series_matrix 解析……）。其余情况查
**[docs/decision-tree.md](docs/decision-tree.md)**（症状 → 诊断 → 参数 → 对应 example）。

| 情况 | 入口 |
|---|---|
| paired / 重复测量 | `--paired-by <subject列>`（强制 limma + duplicateCorrelation），example 3 |
| 批次效应 | `--batch <批次列>`（进 design + QC 着色），docs/paired-and-batch.md |
| 每组 n=1 | 自动降级探索模式（REPORT 显著警告），docs/no-replicates.md |
| 多组全配对 / 只比子集 | `--pairwise-max N` / `--contrasts "A vs B, C vs D"`，example 4 |
| 大鼠/其它物种/无 OrgDb | `--organism rat` / `--orgdb <包>` / `--gene-map <两列CSV>` |
| outlier 样本 | QC 只标记不剔除；确认后 `--exclude-samples s1,s2` |

编号 example 各覆盖一类特殊情况（兼作回归测试），见 `examples/README.md`。

## Personalized follow-ups (separate skills, all consume this pipeline's outputs)

| Skill | Input from this pipeline | What it adds |
|---|---|---|
| `../RNA-seq-enrichment` | `DEG_*.csv` | GO / KEGG / Reactome enrichment (offline-capable) |
| `../RNA-seq-gene-plot` | normalized matrix + metadata (+ DEG for symbols) | gene-of-interest bar charts (cross-group; within-group two-gene) |
| `../RNA-seq-GSEA` | `DEG_*.csv` | GSEA (fgsea + MSigDB GMT) |

## Input format

**File formats are flexible**: the count matrix and metadata may be `.csv`, `.tsv`
or `.txt`, and may be gzipped (`.gz`) — the pipeline auto-detects delimiter and
compression (both the Python driver and the R stages). Zip/tar bundles must be
unpacked first (the agent should do this before calling the skill). For GEO-derived
data see `docs/downloading-from-GEO.md`.

`counts_matrix.csv` — genes as rows, samples as columns, raw integer counts
(normalized matrices are accepted too; they route to limma-trend):

```csv
,CJI1.A,CJI2.B,CJI3.I
ENSMUSG00000000001,2014,2003,2847
ENSMUSG00000000003,13736,19194,...
```

`sample_metadata.csv` — required columns `sample,group`; optional columns
`batch` / a subject column enable `--batch` / `--paired-by`:

```csv
sample,group,subject
S1_pre,pre,Subject1
S1_post,post,Subject1
```

The first group in the metadata is the control unless `--control` is given.
Non-standard column names (`sample_id`, `condition`, ...) are auto-renamed by the
inspection stage.

## Input resources: gene-ID conversion packages

DEG tables/figures use gene symbols converted via the Bioconductor OrgDb annotation
packages — treat them as part of the skill's input assets:

| Organism | Package | Size | Where to get |
|---|---|---|---|
| mouse | `org.Mm.eg.db` | ~380 MB installed | `BiocManager::install("org.Mm.eg.db")`, or the prebuilt archive on the Download page (COS) |
| human | `org.Hs.eg.db` | ~100 MB download | `BiocManager::install("org.Hs.eg.db")`, or the prebuilt archive on the Download page (COS) |
| rat | `org.Rn.eg.db` | ~100 MB download | `BiocManager::install("org.Rn.eg.db")` (`--organism rat`) |
| other | any OrgDb | — | `--orgdb <package>`; no OrgDb available → `--gene-map` two-column CSV |

Install a downloaded archive (same R major.minor version, Windows):
`install.packages("org.Mm.eg.db.zip", repos = NULL, type = "win.binary")`.
Stage 00 verifies the package matching `--organism` before anything runs.
(The same OrgDb install also serves the RNA-seq-enrichment and RNA-seq-GSEA skills.)

**Fully offline route**: `resources/r-deps/` is a Windows-binary mini-repo of the
entire R dependency closure (139 packages incl. the enrichment/GSEA skills'
packages, exact tested versions, R 4.5) — point
`install.packages(..., repos = "file:///<path>/r-deps", type = "win.binary")` at it
when Bioconductor/CRAN is slow or unreachable. Also mirrored on COS at launch.

## Output files

| File | Content |
|---|---|
| `cleaned_counts.csv`, `cleaned_metadata.csv` | only when stage 00.5 repaired something — the actual analysed copies (originals untouched) |
| `gene_annotation.csv` | annotation columns split off a mixed input matrix; reusable as `--gene-map` |
| `QC_PCA_plot.png/pdf`, `QC_sample_correlation_heatmap.png/pdf`, `QC_summary.txt` | QC (outlier samples are flagged, never excluded) |
| `filtered_counts.csv`, `library_sizes.csv`, `normalized_expression.csv` | preprocessing artefacts consumed by follow-up skills (one canonical normalized-matrix name across all engines) |
| `DEG_<treat>_vs_<ref>.csv` | full DEG table per contrast (common schema across engines) |
| `Volcano_<treat>_vs_<ref>.png/pdf` | volcano with top-10 gene labels |
| `MA_<treat>_vs_<ref>.png/pdf` | MA plot per contrast — checks normalization success and logFC-vs-expression independence |
| `DEG_heatmap.png/pdf` | top DEGs, z-scored |
| `run_metadata.json` | machine-readable run record: engine, parameters, input stats, software versions, timestamp |
| `REPORT.md` | auto-written into the output dir every run: which stage produced each file and what it is for / 产出文件说明（自动写入输出目录） |

## Parameters

| Flag | Default | Description |
|---|---|---|
| `--control` | first group in metadata | control group name |
| `--engine` | `auto` | force `deseq2` / `edger-limma` / `limma` |
| `--voom-min-n` | 8 | min group size for the voom branch |
| `--organism` | `mouse` | `mouse` / `human` / `rat` OrgDb shortcut |
| `--orgdb` | — | any Bioconductor OrgDb package (overrides `--organism`) |
| `--gene-map` | — | two-column CSV (id,symbol); OrgDb-free ID conversion |
| `--batch` | — | metadata column with batch info (design formula + QC colouring) |
| `--paired-by` | — | subject column for paired/repeated measures (forces limma + duplicateCorrelation) |
| `--pairwise-max` | 4 | add all pairwise contrasts when #groups ≤ this |
| `--contrasts` | — | explicit contrasts `'A vs B, C vs D'` (overrides auto) |
| `--exclude-samples` | — | comma-separated samples to exclude explicitly (never automatic) |
| `--padj` | 0.05 | adjusted-p significance cutoff |
| `--log2fc` | 1 | \|log2FC\| cutoff |
| `--install-deps` | off | auto-install missing R packages (BiocManager/CRAN) |
| `--rscript` | auto-detect | path to Rscript |
| `--overwrite` | off | allow non-empty output dir |

## Dependencies

- Python 3.10+: `pip install pandas numpy`
- R (≥4.3) with: `DESeq2 edgeR limma org.Mm.eg.db org.Hs.eg.db pheatmap ggplot2 ggrepel`
  (clusterProfiler/fgsea belong to the follow-up skills' own dependency gates).
- Stage 00 checks these before anything runs; missing packages can be installed by
  the agent (`--install-deps`) or manually (miniconda / BiocManager). The OrgDb
  annotation packages (used for gene-ID conversion) are also mirrored as archives
  on the Download page (COS) for fast domestic installation.

## Notes

- Never modifies input files; all outputs go to the output directory.
- Contrasts: every group vs control; when ≤4 groups, all pairwise contrasts are added.
- Group names inside output **file names** are sanitised (spaces/special/non-ASCII
  characters → `_`), so odd group names never produce odd file names.
- DEG tables map Ensembl (version suffix stripped) or Symbol IDs to Entrez/Symbol
  via the OrgDb; tables and figures use converted gene symbols wherever a mapping exists.

> 中文提示：本 skill 只跑到 DEG（常规步骤）；富集（GO/KEGG/Reactome）、指定基因柱状图、GSEA 是三个独立 skill（RNA-seq-enrichment / RNA-seq-gene-plot / RNA-seq-GSEA），都用本流程的产出作为输入。输入可以是 csv/tsv/txt 及 .gz 压缩（自动识别分隔符与压缩；zip/tar 需先解压）；GEO 数据获取见 docs/downloading-from-GEO.md；基因 ID 转换包（org.Mm.eg.db / org.Hs.eg.db）属于本技能输入资源，体积大故随 COS 分发（见 Download 页）；开跑前自动检查 R 依赖，缺包时可选手动安装（miniconda/BiocManager）或加 `--install-deps` 让 agent 代装，装好后还会复检；DEG 表和图默认用转换后的基因名（Symbol）；不改输入文件。
