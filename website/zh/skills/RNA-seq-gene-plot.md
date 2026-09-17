# RNA-seq 指定基因表达柱状图

> 一句话：从 RNA-seq 归一化矩阵里把某个基因单独拎出来——跨组丰度柱状图，或同组内两个基因的配对比较，带误差线、散点和统计标注。

::: info 获取本技能 · Get this skill
**方式 A —— 一键引导 prompt（推荐）**。复制下面这段，粘贴到你的 AI agent IDE：

```
请帮我安装 Claw2Bio 技能库中的 "RNA-seq-gene-plot" 技能：
1. 从 GitHub 仓库 https://github.com/nihuanhe/claw2bio 只拉取 bioinformatics/bulk_RNA_seq/RNA-seq-gene-plot
   这一个文件夹（用 sparse checkout，不要克隆整库）。
2. 阅读其中的 SKILL.md 并注册该技能。
3. 运行 examples/ 里的示例验证环境，把输出的图给我看。
```

**方式 B —— 独立 zip 包**（约 2.0 MB，本站下载）：<https://claw2bio.site/downloads/RNA-seq-gene-plot.zip>

**方式 C —— 全量示例数据**：已包含在方式 B 包内（同一个压缩包）。
:::

## 它能做什么

前提是先跑完 [bulk-RNA-seq 常规流程](/zh/skills/bulk-RNA-seq)。给它归一化表达矩阵 + 分组表，它就能回答两类问题：

1. **某基因在各组表达多少**——柱状图 + SD 误差线 + 抖动散点，2 组 t 检验、≥3 组 ANOVA + Tukey，统计方法标在图注里；
2. **同组内两个基因谁高谁低**（如 TP53 vs GAPDH）——并列柱 + SD + 散点，每组内做配对 t 检验（同一批样本、两个基因）。

![Trp53 跨组表达柱状图](/skills/RNA-seq-gene-plot/GeneExpr_Trp53_by_group.png)

示例：Trp53 在各组的表达丰度（均值 ± SD + 抖动散点 + 显著性标注）。

![同组内两基因比较](/skills/RNA-seq-gene-plot/GeneExpr_compare_within_group.png)

示例：同组内两个基因的配对比较柱状图（配对 t 检验）。

基因查询支持 Ensembl ID 或 Symbol，不区分大小写；Symbol 通过 DEG 表的 `symbol` 列解析。**依赖只有 ggplot2**（统计用 base R），是全库最轻量的技能之一。

## 快速上手（30 秒）

```bash
cd bioinformatics/bulk_RNA_seq/RNA-seq-gene-plot
Rscript scripts/gene_expression.R \
  examples/input/normalized_expression.csv \
  examples/input/sample_metadata.csv \
  --genes Trp53,Gapdh --control Control --outdir examples/output
```

## 输入格式

- 归一化表达矩阵（流程的 `normalized_expression.csv`；旧版 `vst_normalized_counts.csv` / `voom_normalized_logcpm.csv` / `log_expression_used.csv` 也认；csv/tsv/txt 及 `.gz` 均可）+ `sample_metadata.csv`。
- 基因名用目标物种写法：人 `TP53`、鼠 `Trp53`。

## 输出文件

| 文件 | 内容 |
|---|---|
| `GeneExpr_<GENE>_by_group.png/pdf` + 数值 CSV | 每个基因的跨组丰度图 |
| `GeneExpr_compare_<G1>_vs_<G2>_within_group.png/pdf` + 数值 CSV | ≥2 个基因时的同组内对比图 |
| `REPORT.md` | 逐文件产出说明 |

## 参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--genes` | （必填） | 基因列表，逗号分隔 |
| `--deg` | 矩阵旁的任一 `DEG_*.csv` | 用于 Symbol → ID 解析 |
| `--control` | — | 对照组名（影响组排序） |
| `--outdir` | — | 输出目录 |

## 常见问题

- **基因找不到** → 检查物种写法（人全大写、鼠首字母大写）；或确认该基因在低表达过滤中没被滤掉。
- **只有 1 个基因怎么没有对比图** → 同组内对比图需要 `--genes` 至少给 2 个。
- **矩阵列名和 metadata 对不上** → 先用 bulk-RNA-seq 流程的产出（两边命名天然一致）。
- **为什么必须用技能自带脚本，不能让 AI 现写？**
  `scripts/` 里的是经过验证的路径：它们在示例数据上跑过，边界情况有文档记录。AI 现场生成的代码是
  "结果悄悄出错"的最常见来源。遇到没覆盖的情况，先改命令行参数；不够就复制脚本到临时目录做最小改动
  并说明改了什么；只有完全没有对应脚本时才允许新写，且新写后要回沉淀到 `scripts/`。

## 相关链接

- [GitHub 源码与 SKILL.md](https://github.com/nihuanhe/claw2bio/tree/main/bioinformatics/bulk_RNA_seq/RNA-seq-gene-plot)
- 相关技能：[bulk RNA-seq 差异分析](/zh/skills/bulk-RNA-seq) · [富集分析](/zh/skills/RNA-seq-enrichment) · [GSEA](/zh/skills/RNA-seq-GSEA)
