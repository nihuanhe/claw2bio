# 技能总览

所有技能都是实验室实战验证的固定脚本，采用标准 `SKILL.md` 格式封装。
点击任意技能查看中文教程与一键安装 prompt（英文教程筹备中）。

> **第一次用？先看 [安装你的第一个 AI Agent](/zh/skills/ai-agent-setup)**——零基础装好 AI agent，再回到本页挑技能。

## 🧪 实验数据处理

| 技能 | 功能 |
|---|---|
| [qPCR mRNA（ΔΔCt）](/zh/skills/qpcr-mrna) | 原始 Ct 表 → 相对表达量，每个靶标一张图 |
| [qPCR mtDNA 拷贝数](/zh/skills/qpcr-mtdna) | ND1/ND5 + B2M/POLG 配对，Mean copy number |

## 🧬 生信数据分析 {#bioinformatics}

### 进化树

| 技能 | 功能 |
|---|---|
| [进化树 · 建树](/zh/skills/phylo-tree-build) | 基因组 FASTA → bcgTree → IQ-TREE2 树文件（WSL2） |
| [进化树 · 绘图](/zh/skills/phylo-tree-plot) | 树文件 + 注解表 → 发表级 ggtree 图 |

### 单细胞测序

| 技能 | 功能 |
|---|---|
| [单细胞 RNA-seq](/zh/skills/scRNA-seq) | 原始矩阵 → QC → Harmony → 聚类 → UMAP → marker → SingleR 注释 |
| [单细胞拟时序](/zh/skills/scRNA-seq-pseudotime) | monocle3 轨迹/拟时序（需常规管线的 annotated_seurat.rds） |
| [单细胞虚拟敲除](/zh/skills/scRNA-seq-virtual-ko) | scTenifoldKnk 计算机模拟基因敲除 |

### RNA-seq分析

| 技能 | 功能 |
|---|---|
| [Bulk RNA-seq 差异分析](/zh/skills/bulk-RNA-seq) | counts → QC → DEG，引擎自动分叉（limma-trend/DESeq2/edgeR+voom） |
| [富集分析（GO/KEGG/Reactome）](/zh/skills/RNA-seq-enrichment) | GO/Reactome 离线，KEGG 在线+缓存兜底 |
| [基因表达对比图](/zh/skills/RNA-seq-gene-plot) | 单基因跨组 / 组内两基因，t-test / ANOVA+Tukey |
| [GSEA](/zh/skills/RNA-seq-GSEA) | fgsea + MSigDB GMT，Entrez/symbol 自动转换 |

## 📈 图表生成

| 技能 | 功能 |
|---|---|
| [分组柱状图](/zh/skills/barplot) | 宽表 CSV → 300 dpi 带统计标注柱状图 |
| [临床统计表](/zh/skills/clinical-table) | 一套管线复现论文全套 10 张表：基线 / Firth / 基因型交叉 / 单因素 |
| [生存分析曲线](/zh/skills/survival-curve) | 最优截点 KM 曲线 + 风险表 + Cox 森林图 |
