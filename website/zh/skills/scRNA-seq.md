# 零基础——用 AI Agent 做 scRNA-seq 单细胞常规流程 | 全程复制粘贴

本教程以 workbuddy 作为 AI agent、Hy3 作为 AI API 为例。AI agent 本身的安装与配置请看[AI Agent 安装教程](/zh/skills/ai-agent-setup)。

**在开始之前（必读）：**

- **如果你是第一次用 AI agent 做生信分析，强烈建议先跟一遍 [bulk-RNA-seq 差异分析教程](/zh/skills/bulk-RNA-seq)**，熟悉"装技能 → 配环境 → 跑示例 → 换自己数据"的完整流程，再回来做本技能。
- **⚠️ 硬件要求（单细胞技能通用）：请使用内存 ≥16 GB、多核 CPU 的电脑。** 官方实测：约 6 万细胞的数据集内存峰值约 5.7 GB；约 9.7 万细胞峰值约 11.9 GB——已是 16 GB 机器的上限。更大的数据请先降采样探索，或换内存更大的机器。
- 一句话：**从各种格式的原始矩阵进，到注释好的 Seurat 对象出**——QC、Harmony 多样本整合、聚类、UMAP、marker、SingleR 注释一条龙；10X mtx / h5 / h5ad / rds / 文本矩阵 / 华大 BGI 都能自动识别，stage 00.5 自动体检并修复 9 类格式坑；每个阶段自动存 checkpoint，支持断点续跑。
- **本流程只到自动注释为止**——拟时序、虚拟敲除是独立技能，都吃本流程产出的 `annotated_seurat.rds`（见文末"更多分析"）。

**教程结构：**

- **Step 1**｜安装 scRNA-seq 技能（只需一次）
- **Step 2**｜配置运行环境（只需一次）
- **Step 3**｜跑通示例数据
- **Step 4**｜换成你自己的数据
- **Step 5**｜读懂 REPORT.md
- **更多分析**｜下游技能简介（拟时序 / 虚拟敲除）

---

## Step 1｜Install the scRNA-seq skill

注意：本技能包较大（约 102 MB），且**示例数据是独立的 zip 包**（约 102 MB），与技能包分开。输入以下 prompt：

```
Please install the "scRNA-seq" skill for me, into the D:\claw2bio folder:
1. Create a folder named claw2bio in the root of the D: drive (if it doesn't exist yet).
2. From the GitHub repository https://github.com/nihuanhe/claw2bio, fetch ONLY the folder
   bioinformatics/sc_RNA_seq/scRNA-seq (use sparse checkout — do NOT clone the whole
   repository), and place it at D:\claw2bio\scRNA-seq.
3. If downloading from GitHub fails or is too slow, download the skill zip from this mirror
   link instead:
   https://my-website-1358159656.cos.ap-guangzhou.myqcloud.com/scRNA-seq/zip/scRNA-seq.zip
   and extract it to D:\claw2bio\scRNA-seq. The example data is a SEPARATE zip:
   https://my-website-1358159656.cos.ap-guangzhou.myqcloud.com/scRNA-seq/data/scRNA-seq-examples.zip
   — download it too and merge its contents into the examples/ folder of the skill.
4. Read the SKILL.md inside, then confirm to me that the skill is ready and list the contents
   of the folder (including whether examples/ has input data).
(If my PC has no D: drive, install to C:\claw2bio instead and tell me the actual path.)
```

Step 1 完成后，打开文件管理器确认 `D:\claw2bio\scRNA-seq` 文件夹存在，里面有 `scripts/`、`examples/`、`SKILL.md` 等内容。

---

## Step 2｜Set up the runtime environment

本技能同时用 **R（≥4.5，Seurat / harmony / SingleR 等）** 和 **Python（pandas / numpy / scipy）**。如果你已经按 bulk-RNA-seq 教程装好了 R，这一步主要是补装 Seurat 系列大包（首次安装可能需要 20–60 分钟，耐心等）。输入 prompt：

```
Please set up the runtime environment for the "scRNA-seq" skill at D:\claw2bio\scRNA-seq:
1. R should already be installed from the bulk-RNA-seq tutorial — verify that R is installed
   and report its version to me (it must be 4.5 or above). If R is missing, stop and tell me.
2. Also check for a Python installation; if Python is NOT installed, install a recent Python 3
   from python.org (check "Add python.exe to PATH"), then pip install pandas numpy scipy.
3. Install all R packages this skill needs (Seurat, harmony, SingleR and their dependencies):
   try CRAN / Bioconductor online first; if any package fails or is too slow, stop and tell
   me about it. These packages are LARGE — the first install may take 20–60 minutes, which
   is normal.
4. The skill's stage 00 checks dependencies automatically and supports an --install-deps flag.
   When everything is installed, run the dependency check and show me the result.
5. Reminder: this machine should have at least 16 GB RAM and a multi-core CPU for single-cell
   work — tell me my RAM size and CPU core count, and warn me if they are below that.
```

---

## Step 3｜跑通示例数据

输入 prompt：

```
The skill is installed at D:\claw2bio\scRNA-seq. Please run the bundled example
(downsampled GSE234527, 5 samples × 400 cells, 10X mtx format):
1. Example input is at D:\claw2bio\scRNA-seq\examples\1_example_GSE234527_downsampled-10x-mtx\input\
2. Write results to D:\claw2bio\scRNA-seq\examples\1_example_GSE234527_downsampled-10x-mtx\output\
   with the metadata file at ...\input\sample_metadata.csv, and use --overwrite.
3. Prefer the skill's own scripts in scripts/ — do NOT write new analysis code from scratch.
4. When the run succeeds, show me the key result figures in this order: the QC violin plot
   (after QC), the UMAP colored by cell-type annotation, the UMAP colored by sample group,
   and the marker dotplot + heatmap; then explain the generated REPORT.md line by line.
```

运行成功后的**锚点结果**：QC 后保留约 **1820 个细胞**（各样本保留率 93.8%–98.2%），聚成 **9 个 cluster**。你的结果与此一致即说明环境和流程正常。示例效果（你的网站实跑结果会替换成自己的截图）：

QC 后每个样本的 nFeature / nCount / percent.mt 分布：

![QC 小提琴图示例](/skills/scRNA-seq/QC_violin_after.png)

按细胞类型注释着色的 UMAP（SingleR 自动注释）：

![UMAP 注释示例](/skills/scRNA-seq/UMAP_by_annotation.png)

按样本分组着色的 UMAP（检查组间分布与批次混杂）：

![UMAP 分组示例](/skills/scRNA-seq/UMAP_by_group.png)

每个 cluster 的 top-5 marker 点图与热图：

![marker 点图示例](/skills/scRNA-seq/marker_dotplot.png)

![marker 热图示例](/skills/scRNA-seq/marker_heatmap.png)

---

## Step 4｜换成你自己的数据

把你自己数据所在的文件夹交给它（10X mtx / h5 / h5ad / rds / 文本矩阵 / 华大 BGI / 多样本混杂均可；输入文件永不被修改，解包导出都进 `<output>/.staging/`）。如有分组信息，准备一张两列 `sample,group` 的 CSV。输入 prompt：

```
My own single-cell data is at: <paste the path to your data folder here>.
<Optional: my metadata table (two columns: sample,group) is at: <path>.>
My organism is <human / mouse>.
1. First run the skill's built-in input check (stage 00.5 auto-detects and fixes common format
   problems — 10X mtx / h5 / h5ad / rds / text matrices / BGI). Show me what it detected and
   fixed; if anything needs my decision, ask me before proceeding.
2. IMPORTANT metadata pitfall: the "sample" column in my metadata CSV must contain the FULL
   sample names (e.g., GSM6045825_wt_filtered_gene_bc_matrices_h5_1), not just the GSM number —
   otherwise samples silently fail to match and the run degrades to exploration mode. Verify
   that every metadata row matched a real sample before continuing, and show me the match table.
3. If my data is compressed as .h5ad.gz / .RDS.gz, decompress it first (some files are even
   double-gzipped — decompress again if R still reports "unknown input format").
4. If my dataset is large (tens of thousands of cells or more), ask me whether to first run a
   downsampled exploration pass (--downsample) before the full run — full runs can take tens
   of minutes to an hour and need most of my 16 GB RAM.
5. Run the full pipeline with the skill's own scripts in scripts/ — do NOT write new analysis
   code from scratch. If the run crashes midway, use --resume to continue from the last
   checkpoint instead of starting over.
6. When the run succeeds, show me the QC plots, UMAPs, marker dotplot/heatmap, and explain
   the REPORT.md line by line.
```

等候 AI agent 运行结束，核心交付物是 **`annotated_seurat.rds`**（QC 后、聚类、注释好的 Seurat v5 对象）——保存好它，拟时序和虚拟敲除都要用它。

---

## Step 5｜读懂 REPORT.md

输入 prompt：

```
Please explain the REPORT.md in my scRNA-seq results folder line by line:
1. What each output file is and what it contains (annotated_seurat.rds, the marker tables,
   annotation_per_cluster.csv, the QC/UMAP/marker figures, the checkpoints);
2. How many cells passed QC per sample, how many clusters were found, and how each cluster
   was annotated — do the SingleR annotations agree with the marker genes? Flag any cluster
   whose identity looks doubtful;
3. If my run used Harmony integration: does the before/after integration UMAP comparison show
   good batch mixing without over-correction?
4. Any warnings or things I should pay attention to.
After explaining, tell me which figures can be used directly in a paper or presentation, and
remind me that pseudotime analysis and virtual knockout are separate skills that both consume
my annotated_seurat.rds.
```

阅读完 AI 的解释，如果有不懂的直接问它。

---

## 更多分析

下面两个下游技能都吃本流程的 `annotated_seurat.rds`，安装方式与本技能完全相同（一键 prompt 或网站下载 zip 包）。**同样需要 ≥16 GB 内存 + 多核 CPU**：

### 单细胞拟时序 —— scRNA-seq-pseudotime

**一句话：从注释好的 Seurat 对象出发，用 monocle3 学轨迹、排拟时序、找拟时序相关基因。** 起点（root cluster / 细胞类型）由你指定——这是生物学决策，技能会打印 cluster → 标签对照表帮你选。

详细介绍与下载：/zh/skills/scRNA-seq-pseudotime

### 单细胞虚拟敲除 —— scRNA-seq-virtual-ko

**一句话：指定一个基因，用 scTenifoldKnk 在计算机里"敲除"它，看调控网络怎么变。** 输出差异调控基因表和两张图，是产生候选机制假设的利器（计算预测，需实验验证）。

详细介绍与下载：/zh/skills/scRNA-seq-virtual-ko
