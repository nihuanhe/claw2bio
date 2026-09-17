# scRNA-seq 虚拟敲除（scTenifoldKnk）

> 一句话：不做实验，先在电脑里"敲掉"一个基因——基于单细胞调控网络的 in-silico 敲除，预测下游哪些基因的调控会被扰动。

::: info 获取本技能 · Get this skill
**方式 A —— 一键引导 prompt（推荐）**。复制下面这段，粘贴到你的 AI agent IDE：

```
请帮我安装 Claw2Bio 技能库中的 "scRNA-seq-virtual-ko" 技能：
1. 从 GitHub 仓库 https://github.com/nihuanhe/claw2bio 只拉取 bioinformatics/sc_RNA_seq/scRNA-seq-virtual-ko
   这一个文件夹（用 sparse checkout，不要克隆整库）。
2. 阅读其中的 SKILL.md 并注册该技能。
3. 运行 examples/ 里的示例验证环境，把输出的图给我看。
```

**方式 B —— 独立 zip 包**（约 0.2 MB，本站下载）：<https://claw2bio.site/downloads/scRNA-seq-virtual-ko.zip>

**方式 C —— 全量示例数据**：已包含在方式 B 包内（同一个压缩包）。
:::

## 它能做什么

前提是先跑完 [scRNA-seq 常规流程](/zh/skills/scRNA-seq) 拿到 `annotated_seurat.rds`。指定一个目标基因（`--gene TP53`），scTenifoldKnk（PMID: 35510185）会从 RNA counts 层构建基因调控网络，在计算机中虚拟敲除该基因，输出差异调控表和两张图。内置 smoke 示例敲除 ADIRF：1820 个细胞、500 个网络基因、3 个子采样网络平均，得到 14 个显著差异调控基因（p_adj < 0.05）。

![虚拟敲除 top20 条形图](/skills/scRNA-seq-virtual-ko/ADIRF_barplot_top20.png)

敲除 ADIRF 后 |FC| 最大的 top-20 差异调控基因。

![Z 值散点图](/skills/scRNA-seq-virtual-ko/ADIRF_zscore_scatter.png)

Z 值 vs -log10(p_adj) 散点图，显著基因自动标出名称。

可以先用 `--subset-labels "Epithelial cells"` 圈定目标细胞类型，只在这些细胞上建网络，结果更有针对性。

**注意**：结果是网络扰动的计算预测，需要实验验证。

## 快速上手（30 秒）

```bash
cd bioinformatics/sc_RNA_seq/scRNA-seq-virtual-ko
python scripts/run_virtual_ko.py <annotated_seurat.rds> <output_dir> --gene TP53
```

圈定细胞类型再敲：

```bash
python scripts/run_virtual_ko.py annotated_seurat.rds output --gene TP53 \
  --subset-labels "Epithelial cells"
```

## 输入格式

- 常规流程输出的 `annotated_seurat.rds`（使用 RNA counts 层；按标签子集化需要 `cell_type_final`）。
- 目标基因名区分大小写，用目标物种的写法（人 `TP53`、鼠 `Trp53`）。

## 输出文件

| 文件 | 内容 |
|---|---|
| `<GENE>_diffRegulation.csv` | 完整结果表（Gene, distance, Z, FC, p_value, p_adj） |
| `<GENE>_barplot_top20.png/pdf` | top-20 \|FC\| 基因条形图 |
| `<GENE>_zscore_scatter.png/pdf` | Z 值散点图，显著基因带标签 |
| `virtual_ko_summary.json` / `REPORT.md` | 摘要 + 报告 |

## 参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--gene` | （必填） | 要敲除的基因名（区分大小写） |
| `--subset-labels` | — | 先子集化的 `cell_type_final` 标签，逗号分隔 |
| `--nfeatures` | 2000 | 建网络用的高变基因数 |
| `--all-genes` | 关 | 用全部基因（慢、吃内存） |
| `--nc-nnet` | 10 | 平均的子采样网络数 |
| `--cores` | 自动检测-1 | 并行核数 |

## 常见问题

- **跑得很慢** → 运行时间与 细胞数 × 基因数 × nc_nnet 成正比；smoke 示例（500 基因 × 3 网络 × 1820 细胞）几分钟。
  **全量参数的耗时目前还没有确切数字**：2000 基因 × 10 网络 × 500 细胞在 16 GB / 12 核 Windows 上实测 3.5 h+ 仍未跑完（已中止）；
  请按"数小时"预估，并用 `--nc-nnet` 作为主要的降规模旋钮。
- **能不能中途断了再续？** → **不能**。scTenifoldKnk 是一次不可中断的调用，本技能没有 `--resume`
  （与常规流程、拟时序分析不同）：跑挂了或机器休眠，前面的计算全部作废。长跑前先确认机器不会休眠。
- **目标基因不在高变基因里** → 会被强制纳入网络；若该基因在 <5% 的细胞中表达，会打印警告。
- **结果能直接写进论文吗** → 这是计算预测，应作为候选机制假设，配合实验验证。
- **为什么必须用技能自带脚本，不能让 AI 现写？**
  `scripts/` 里的是经过验证的路径：它们在示例数据上跑过，边界情况有文档记录。AI 现场生成的代码是
  "结果悄悄出错"的最常见来源。遇到没覆盖的情况，先改命令行参数；不够就复制脚本到临时目录做最小改动
  并说明改了什么；只有完全没有对应脚本时才允许新写，且新写后要回沉淀到 `scripts/`。

## 相关链接

- [GitHub 源码与 SKILL.md](https://github.com/nihuanhe/claw2bio/tree/main/bioinformatics/sc_RNA_seq/scRNA-seq-virtual-ko)
- 相关技能：[scRNA-seq 常规流程](/zh/skills/scRNA-seq) · [拟时序分析](/zh/skills/scRNA-seq-pseudotime)
