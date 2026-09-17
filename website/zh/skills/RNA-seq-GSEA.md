# RNA-seq GSEA 基因集富集分析

> 一句话：不只盯着显著差异基因——用全基因排序列表做 GSEA，捕捉微弱但协调的通路变化。

::: info 获取本技能 · Get this skill
**方式 A —— 一键引导 prompt（推荐）**。复制下面这段，粘贴到你的 AI agent IDE：

```
请帮我安装 Claw2Bio 技能库中的 "RNA-seq-GSEA" 技能：
1. 从 GitHub 仓库 https://github.com/nihuanhe/claw2bio 只拉取 bioinformatics/bulk_RNA_seq/RNA-seq-GSEA
   这一个文件夹（用 sparse checkout，不要克隆整库）。
2. 阅读其中的 SKILL.md 并注册该技能。
3. 运行 examples/ 里的示例验证环境，把输出的图给我看。
```

**方式 B —— 独立 zip 包**（约 2.5 MB，本站下载）：<https://claw2bio.site/downloads/RNA-seq-GSEA.zip>

**方式 C —— 全量示例数据**：已包含在方式 B 包内（同一个压缩包）。
:::

## 它能做什么

前提是先跑完 [bulk-RNA-seq 常规流程](/zh/skills/bulk-RNA-seq)。与基于阈值的[富集分析](/zh/skills/RNA-seq-enrichment)不同，GSEA 使用**全基因排序列表**（排序指标：`sign(log2FC) × -log10(pvalue)`），对 MSigDB 格式的 GMT 基因集做 fgsea 富集。内置 `reactome_demo_mmu.gmt`（开放许可，由 Reactome 缓存构建）开箱即用；把自己的 MSigDB `.gmt` 拷进 `resources/gmt/` 即可，Entrez / symbol ID 类型逐文件自动识别、可混用。

![GSEA NES 点图](/skills/RNA-seq-GSEA/GSEA_dotplot.png)

按 padj 取 top-15 基因集的 NES 点图——x 轴为 NES（上调红 / 下调蓝），点大小为 -log10(padj)。

![GSEA 富集曲线](/skills/RNA-seq-GSEA/GSEA_top_curve.png)

最显著基因集的经典 enrichment running-score 曲线。

**注意**：MSigDB 小鼠 C2（m2.all）含 Reactome/BioCarta/WikiPathways 等，但**不含 KEGG**（许可原因）——要做 KEGG 请用 [RNA-seq-enrichment](/zh/skills/RNA-seq-enrichment)。

## 快速上手（30 秒）

```bash
cd bioinformatics/bulk_RNA_seq/RNA-seq-GSEA
Rscript scripts/00_check_deps.R --organism mouse
Rscript scripts/gsea.R examples/input/DEG_Mutant_vs_Control.csv \
  --gmt resources/gmt/reactome_demo_mmu.gmt --organism mouse \
  --outdir examples/output
```

## 输入格式

- bulk-RNA-seq 流程产出的 `DEG_*.csv`（含 `gene`、log2FC 列、`pvalue`、`padj`）。
- 基因集：MSigDB GMT 格式文件，放入 `resources/gmt/`；不给 `--gmt` 时默认用该目录下全部 `.gmt`。

## 输出文件

| 文件 | 内容 |
|---|---|
| `GSEA_<label>_<gmt>.csv` | 每个 GMT 的结果表（pathway, NES, pvalue, padj, leadingEdge） |
| `GSEA_<label>_<gmt>_dotplot.png` | top-15 NES 点图 |
| `GSEA_<label>_<gmt>_top_curve.png` | 最显著基因集的富集曲线 |
| `REPORT.md` | 逐文件产出说明 |

## 参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--gmt` | `resources/gmt/` 下全部 | GMT 文件，逗号分隔可多个 |
| `--organism` | `mouse` | `mouse` / `human`（用于 ID 转换） |
| `--rank` | `auto` | 排序指标：`auto` / `log2fc` / `stat` |
| `--outdir` | — | 输出目录 |

## 常见问题

- **MSigDB 文件哪里来** → MSigDB 官网注册下载（许可要求自行下载，技能不代发）；拷进 `resources/gmt/` 即可。
- **想做 KEGG 的 GSEA** → MSigDB 无 KEGG 基因集；用 [RNA-seq-enrichment](/zh/skills/RNA-seq-enrichment) 的 KEGG 富集替代。
- **在 Windows 上卡住不动** → fgsea 被强制串行（并行 socket 在部分 Windows 环境打不开端口），耐心等即可，不是死机。

## 相关链接

- [GitHub 源码与 SKILL.md](https://github.com/nihuanhe/claw2bio/tree/main/bioinformatics/bulk_RNA_seq/RNA-seq-GSEA)
- 相关技能：[bulk RNA-seq 差异分析](/zh/skills/bulk-RNA-seq) · [富集分析](/zh/skills/RNA-seq-enrichment) · [指定基因柱状图](/zh/skills/RNA-seq-gene-plot)
