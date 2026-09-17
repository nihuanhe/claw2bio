# bulk RNA-seq 差异分析（counts → DEG）

> 一句话：counts 矩阵 + 分组表进，差异表达全套出——输入体检自动修复格式坑，按数据自动选择 DESeq2 / edgeR+voom / limma 引擎并打印理由。

::: info 获取本技能 · Get this skill
**方式 A —— 一键引导 prompt（推荐）**。复制下面这段，粘贴到你的 AI agent IDE：

```
请帮我安装 Claw2Bio 技能库中的 "bulk-RNA-seq" 技能：
1. 从 GitHub 仓库 https://github.com/nihuanhe/claw2bio 只拉取 bioinformatics/bulk_RNA_seq/bulk-RNA-seq
   这一个文件夹（用 sparse checkout，不要克隆整库）。
2. 阅读其中的 SKILL.md 并注册该技能。
3. 运行 examples/ 里的示例验证环境，把输出的图给我看。
```

**方式 B —— 独立 zip 包**（约 76 MB，腾讯 COS 直链）：<https://my-website-1358159656.cos.ap-guangzhou.myqcloud.com/bulk-RNA-seq/zip/bulk-RNA-seq.zip>

**方式 C —— 全量示例数据**（约 87 MB，腾讯 COS 直链）：<https://my-website-1358159656.cos.ap-guangzhou.myqcloud.com/bulk-RNA-seq/data/bulk-RNA-seq-examples.zip>
:::

## 它能做什么

输入基因 × 样本的 counts 矩阵和样本分组表，stage 00.5 输入体检自动修复混合矩阵 / GEO series_matrix 表头 / 转置 / 毁名 / 重复 symbol 等常见坑，然后按数据自动分叉引擎（理由强制打印）：

| 输入诊断 | 引擎 |
|---|---|
| 非整数 / 已归一化（FPKM、TPM、log） | limma-trend |
| 整数 counts，最小组 n < 8 | DESeq2 |
| 整数 counts，最小组 n ≥ 8 | edgeR + limma-voom |
| 声明 `--paired-by`（以上任意） | 强制 limma + duplicateCorrelation |
| 任一组 n = 1 | 探索模式：limma-trend 只算 fold change，REPORT 显著警告 |

内置示例为 GSE270189（小鼠前列腺基底细胞，3 组 × 2 重复），自动走 DESeq2 分支，输出 QC、每个 contrast 的 DEG 表、火山图、MA 图和 DEG 热图：

![QC PCA 图](/skills/bulk-RNA-seq/QC_PCA.png)

样本 PCA——检查组间分离与离群样本（离群只标记，绝不自动剔除）。

![样本相关性热图](/skills/bulk-RNA-seq/QC_correlation_heatmap.png)

样本间表达相关性热图，批次效应在此一览无余。

![火山图](/skills/bulk-RNA-seq/Volcano.png)

每个 contrast 一张火山图，top-10 基因自动标注（默认阈值 padj < 0.05 且 |log2FC| ≥ 1）。

![MA 图](/skills/bulk-RNA-seq/MA.png)

MA 图——检查归一化是否成功、logFC 与表达量是否脱钩。

![DEG 热图](/skills/bulk-RNA-seq/DEG_heatmap.png)

显著 DEG 并集的 z-score 热图。

**本流程只到 DEG 为止**——富集分析、指定基因柱状图、GSEA 是三个独立技能，都吃本流程的产出。

## 快速上手（30 秒）

技能装好后，直接对 agent 说：

> 运行 bulk-RNA-seq 的示例，把火山图给我看。

或手动执行：

```bash
cd bioinformatics/bulk_RNA_seq/bulk-RNA-seq
pip install pandas numpy
python scripts/run_rnaseq.py \
  examples/1_example_GSE270189_clean-mouse-3groups/input/counts_matrix.csv \
  examples/1_example_GSE270189_clean-mouse-3groups/input/sample_metadata.csv \
  examples/1_example_GSE270189_clean-mouse-3groups/output \
  --control Control --organism mouse --overwrite
```

需要 R（≥4.3）及 DESeq2 / edgeR / limma / OrgDb 等包；stage 00 先查依赖，缺包可加 `--install-deps` 让 agent 代装。

## 输入格式

`counts_matrix.csv`——基因行 × 样本列的原始整数 counts（归一化矩阵也收，自动走 limma-trend；csv/tsv/txt 及 `.gz` 均可，分隔符与压缩自动识别）：

```csv
,CJI1.A,CJI2.B,CJI3.I
ENSMUSG00000000001,2014,2003,2847
ENSMUSG00000000003,13736,19194,...
```

`sample_metadata.csv`——必需列 `sample,group`；可选 `batch` / 个体列配合 `--batch` / `--paired-by`：

```csv
sample,group,subject
S1_pre,pre,Subject1
S1_post,post,Subject1
```

第一个 group 默认为对照，除非 `--control` 指定；非标准列名自动归一化。

## 输出文件

| 文件 | 内容 |
|---|---|
| `DEG_<treat>_vs_<ref>.csv` | 每个 contrast 的完整 DEG 表（Ensembl 已转成 Symbol） |
| `Volcano_<treat>_vs_<ref>.png/pdf` | 火山图（top-10 基因标注） |
| `MA_<treat>_vs_<ref>.png/pdf` | MA 图 |
| `DEG_heatmap.png/pdf` | 显著 DEG 并集 z-score 热图 |
| `QC_PCA_plot.*` / `QC_sample_correlation_heatmap.*` / `QC_summary.txt` | QC 三件套 |
| `normalized_expression.csv` | 归一化矩阵（供 RNA-seq-gene-plot 使用） |
| `cleaned_counts.csv` / `cleaned_metadata.csv` | 仅当输入被修复时输出（原文件不动） |
| `REPORT.md` / `run_metadata.json` | 产出说明报告 + 机器可读运行记录 |

## 参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--control` | metadata 第一个组 | 对照组名 |
| `--engine` | `auto` | 强制 `deseq2` / `edger-limma` / `limma` |
| `--voom-min-n` | 8 | voom 分支的最小组样本数阈值 |
| `--organism` | `mouse` | `mouse` / `human` / `rat` OrgDb 快捷方式 |
| `--orgdb` / `--gene-map` | — | 任意 OrgDb 包 / 两列 ID 转换 CSV |
| `--batch` | — | 批次列（进 design 公式 + QC 着色） |
| `--paired-by` | — | 个体列（强制 limma + duplicateCorrelation） |
| `--contrasts` | — | 显式 contrast，如 `'A vs B, C vs D'` |
| `--padj` / `--log2fc` | 0.05 / 1 | 显著性阈值 |
| `--exclude-samples` | — | 显式剔除样本（绝不自动） |
| `--overwrite` | 关 | 允许非空输出目录 |

## 常见问题

- **数据是 FPKM 怎么办** → 直接给，自动走 limma-trend 并打印理由；无需自己转换。
- **有批次效应** → metadata 加一列批次，跑时加 `--batch <列名>`。
- **配对样本 / 重复测量** → 加 `--paired-by <个体列>`，自动强制 limma + duplicateCorrelation。
- **OrgDb 包装不上** → 可用预编译压缩包（Download 页 COS 镜像），或 `--gene-map` 两列 CSV 免 OrgDb；`resources/r-deps/` 还有 139 个 Windows 二进制包的离线小仓库。
- **输入文件被改了吗** → 没有，修复后的副本写入输出目录，原件不动。
- **为什么必须用技能自带脚本，不能让 AI 现写？**
  `scripts/` 里的是经过验证的路径：它们在示例数据上跑过，边界情况有文档记录。AI 现场生成的代码是
  "结果悄悄出错"的最常见来源。遇到没覆盖的情况，先改命令行参数；不够就复制脚本到临时目录做最小改动
  并说明改了什么；只有完全没有对应脚本时才允许新写，且新写后要回沉淀到 `scripts/`。

## 相关链接

- [GitHub 源码与 SKILL.md](https://github.com/nihuanhe/claw2bio/tree/main/bioinformatics/bulk_RNA_seq/bulk-RNA-seq)
- 相关技能：[富集分析](/zh/skills/RNA-seq-enrichment) · [指定基因柱状图](/zh/skills/RNA-seq-gene-plot) · [GSEA](/zh/skills/RNA-seq-GSEA)
