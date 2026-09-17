# 系统发育树绘图（treefile + 注释 → 发表级图）

> 一句话：Newick 树文件 + 注释 CSV 进，600 dpi 发表级注解进化树出——ggtree 模板：中点生根、枝干按分组着色、任意多环注释自动配色、独立图例网格。

::: info 获取本技能 · Get this skill
**方式 A —— 一键引导 prompt（推荐）**。复制下面这段，粘贴到你的 AI agent IDE：

```
请帮我安装 Claw2Bio 技能库中的 "phylo-tree-plot" 技能：
1. 从 GitHub 仓库 https://github.com/nihuanhe/claw2bio 只拉取 bioinformatics/phylo-tree/phylo-tree-plot
   这一个文件夹（用 sparse checkout，不要克隆整库）。
2. 阅读其中的 SKILL.md 并注册该技能。
3. 运行 examples/ 里的示例验证环境，把输出的图给我看。
```

**方式 B —— 独立 zip 包**（约 0.4 MB，本站下载）：<https://claw2bio.site/downloads/phylo-tree-plot.zip>

**方式 C —— 全量示例数据**：已包含在方式 B 包内（同一个压缩包）。
:::

## 它能做什么

输入一个 Newick 树文件（tip 标签 = 样本 ID，可直接用 [phylo-tree-build](/zh/skills/phylo-tree-build) 的产出）和一张注释 CSV（首列 `SampleID`，其余列任意分类注释），输出：中点生根的树、枝干按分组列着色、每个注释列一圈外环（自动配色渐变）、树下独立图例网格——600 dpi PNG + cairo 内嵌字体 PDF。

![注解进化树示例](/skills/phylo-tree-plot/phylo_tree.png)

示例：phylo-tree-build 对 12 个公开 NCBI 基因组所建的树 + 物种元数据注释（含 contig 数分档环带），控制台锚点 `tips: 12 | ring levels: …`。

**这是模板脚本，不是 CLI**：把 `scripts/plot_tree_template.R` 拷到你的项目里，只改顶部 `CONFIG (EDIT THIS BLOCK)` 块——路径、`GROUP_COL`、`RING_COLS`、配色、布局（`circular` / `rectangular`）、几何尺寸。环数、配色、图例、导出全部自动适配；输入不匹配时 `stopifnot` 当场报错，绝不静默丢 tip。

## 快速上手（30 秒）

```bash
cd bioinformatics/phylo-tree/phylo-tree-plot
Rscript scripts/plot_tree_template.R
```

换自己的数据：拷贝模板，在 CONFIG 块里设 `TREEFILE` 和 `ANN_CSV`，选好 `GROUP_COL` / `RING_COLS`，运行。

需要 Windows R ≥ 4.1（实测 4.5.2）及 ggtree / treeio / ggplot2 / ggnewscale / RColorBrewer / viridis / cowplot / phytools。

## 输入格式

- **树文件**：Newick 格式，tip 标签 = 样本 ID。
- **注释 CSV**：必须有表头；首列 `SampleID` 与 tip 标签一一对应；只收分类值（连续值先分箱——每个不同值占一个配色）；无值的格子填 `-`（画成灰色）。

## 输出文件

| 文件 | 内容 |
|---|---|
| 树图 PNG（600 dpi）+ cairo PDF | 带注释环和图例网格的成品图 |
| 各图例独立 PNG | 单独取用的小图例 |
| `REPORT.md` | 逐文件产出说明 |

## 配置

CONFIG 块主要变量：`TREEFILE` / `ANN_CSV` / `GROUP_COL`（枝干着色列）/ `RING_COLS`（注释环列）/ `LAYOUT`（`circular` / `rectangular`）/ `RING_GAP` / `RING_WIDTH` / `TREE_H_CM` / `FONT`。

## 常见问题

- **`stopifnot: all(tree$tip.label %in% ann$SampleID)`** → SampleID 对不上——检查 FASTA 文件名主干与 CSV 首列。
- **某环一整圈灰** → 该列全是无效值；或 gheatmap 丢了全 NA 的环，检查列名拼写。
- **PDF 字体缺失（Arial）** → cairo_pdf 已处理；非 Windows 系统把 `FONT` 改成 `"sans"`。
- **环太细 / 重叠** → 调大 `RING_GAP` / `RING_WIDTH`，或加大 `TREE_H_CM`。
- **某列取值超过约 30 种** → 配色不可读，先分箱或丢弃该列。
- **为什么必须用技能自带脚本，不能让 AI 现写？**
  `scripts/` 里的是经过验证的路径：它们在示例数据上跑过，边界情况有文档记录。AI 现场生成的代码是
  "结果悄悄出错"的最常见来源。遇到没覆盖的情况，先改命令行参数；不够就复制脚本到临时目录做最小改动
  并说明改了什么；只有完全没有对应脚本时才允许新写，且新写后要回沉淀到 `scripts/`。

## 相关链接

- [GitHub 源码与 SKILL.md](https://github.com/nihuanhe/claw2bio/tree/main/bioinformatics/phylo-tree/phylo-tree-plot)
- 相关技能：[系统发育树构建](/zh/skills/phylo-tree-build)
