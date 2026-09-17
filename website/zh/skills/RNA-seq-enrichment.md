# RNA-seq 富集分析（GO / KEGG / Reactome）

> 一句话：DEG 表进，GO / KEGG / Reactome 富集表和点图出——GO 与 Reactome 全程离线，KEGG 联网失败自动用本地缓存。

::: info 获取本技能 · Get this skill
**方式 A —— 一键引导 prompt（推荐）**。复制下面这段，粘贴到你的 AI agent IDE：

```
请帮我安装 Claw2Bio 技能库中的 "RNA-seq-enrichment" 技能：
1. 从 GitHub 仓库 https://github.com/nihuanhe/claw2bio 只拉取 bioinformatics/bulk_RNA_seq/RNA-seq-enrichment
   这一个文件夹（用 sparse checkout，不要克隆整库）。
2. 阅读其中的 SKILL.md 并注册该技能。
3. 运行 examples/ 里的示例验证环境，把输出的图给我看。
```

**方式 B —— 独立 zip 包**（约 11 MB，本站下载）：<https://claw2bio.site/downloads/RNA-seq-enrichment.zip>

**方式 C —— 全量示例数据**：已包含在方式 B 包内（同一个压缩包）。
:::

## 它能做什么

前提是先跑完 [bulk-RNA-seq 常规流程](/zh/skills/bulk-RNA-seq)。指向它的输出目录（或任何含 `DEG_*.csv` 的文件夹），每个 contrast 拆出上调 / 下调两个基因集，用 clusterProfiler 分别做 GO（BP/MF/CC，永远离线走 OrgDb）、KEGG（在线优先，失败自动回退本地缓存）、Reactome（永远离线）富集，每个方向 × 通路库出一张表和一张点图：

![GO BP 富集点图](/skills/RNA-seq-enrichment/GO_BP_dotplot.png)

GO Biological Process 富集点图——点大小为基因数，颜色为校正后 P 值。

![KEGG 富集点图](/skills/RNA-seq-enrichment/KEGG_dotplot.png)

KEGG 通路富集点图（离线缓存兜底，断网也能出图）。

![Reactome 富集点图](/skills/RNA-seq-enrichment/Reactome_dotplot.png)

Reactome 通路富集点图（开放许可，缓存可随技能分发）。

## 快速上手（30 秒）

```bash
cd bioinformatics/bulk_RNA_seq/RNA-seq-enrichment
Rscript scripts/00_check_deps.R --organism mouse        # 依赖检查
Rscript scripts/enrich.R examples/input examples/output --organism mouse
```

## 输入格式

- 一个目录，里面有 bulk-RNA-seq 流程产出的 `DEG_*.csv`（含 `gene`、`log2fc`、`padj` 列；DESeq2 的 `log2FoldChange`、edgeR/limma 的 `logFC` 列名会自动归一化）。

## 输出文件

| 文件 | 内容 |
|---|---|
| `GO_<contrast>_<up\|down>_<BP\|MF\|CC>.csv` + `_dotplot.png` | 每个 contrast × 方向 × 本体论的 GO 表和点图 |
| `KEGG_<contrast>_<up\|down>.csv` + `_dotplot.png` | KEGG 富集表和点图 |
| `Reactome_<contrast>_<up\|down>.csv` + `_dotplot.png` | Reactome 富集表和点图 |
| `REPORT.md` | 逐文件产出说明 |

## 参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--organism` | `mouse` | `mouse` / `human` |
| `--padj` | 0.05 | 校正 P 值阈值 |
| `--log2fc` | 1 | \|log2FC\| 阈值 |
| `--offline` | 关 | 跳过 KEGG 在线尝试，直接用本地缓存 |

## 常见问题

- **断网 / KEGG 接口超时** → 自动回退本地缓存；新机器先跑一次 `Rscript scripts/build_pathway_cache.R --organism both` 建缓存（KEGG 缓存因版权只存本地，不上 COS）。
- **没有 OrgDb 包** → 用 bulk-RNA-seq 技能 `resources/` 里的预编译包（COS 镜像），一次安装两个技能共用。
- **DEG 表不是本流程出的** → 只要有 `gene` / `log2fc`(或 `logFC` / `log2FoldChange`) / `padj` 列即可读入。
- **为什么必须用技能自带脚本，不能让 AI 现写？**
  `scripts/` 里的是经过验证的路径：它们在示例数据上跑过，边界情况有文档记录。AI 现场生成的代码是
  "结果悄悄出错"的最常见来源。遇到没覆盖的情况，先改命令行参数；不够就复制脚本到临时目录做最小改动
  并说明改了什么；只有完全没有对应脚本时才允许新写，且新写后要回沉淀到 `scripts/`。

## 相关链接

- [GitHub 源码与 SKILL.md](https://github.com/nihuanhe/claw2bio/tree/main/bioinformatics/bulk_RNA_seq/RNA-seq-enrichment)
- 相关技能：[bulk RNA-seq 差异分析](/zh/skills/bulk-RNA-seq) · [指定基因柱状图](/zh/skills/RNA-seq-gene-plot) · [GSEA](/zh/skills/RNA-seq-GSEA)
