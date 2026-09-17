# 系统发育树构建（FASTA → 核心基因组 ML 树）

> 一句话：一目录细菌基因组 FASTA 进，Newick 树文件出——bcgTree 核心基因拼接比对 + IQ-TREE2 最大似然建树（自动选模 + 1000 次超快自举），可选 parsnp 分组子树。

::: info 获取本技能 · Get this skill
**方式 A —— 一键引导 prompt（推荐）**。复制下面这段，粘贴到你的 AI agent IDE：

```
请帮我安装 Claw2Bio 技能库中的 "phylo-tree-build" 技能：
1. 从 GitHub 仓库 https://github.com/nihuanhe/claw2bio 只拉取 bioinformatics/phylo-tree/phylo-tree-build
   这一个文件夹（用 sparse checkout，不要克隆整库）。
2. 阅读其中的 SKILL.md 并注册该技能。
3. 运行 examples/ 里的示例验证环境，把输出的图给我看。
```

**方式 B —— 独立 zip 包**（约 19 MB，本站下载）：<https://claw2bio.site/downloads/phylo-tree-build.zip>

**方式 C —— 全量示例数据**（约 31 MB，本站下载）：<https://claw2bio.site/downloads/phylo-tree-build-examples.zip>
:::

## 它能做什么

输入一个目录的基因组组装文件（`*.fasta`，一个菌株一个文件，文件名主干即样本 ID），脚本来自一项已发表的 67 株 CRE 研究的实战流程，分四步（每步一个模板脚本）：bcgTree 拼接核心基因比对 → IQ-TREE2 `-m MFP -B 1000`（ModelFinder 自动选模 + 1000 次超快自举）建主树 → 可选 parsnp + IQ-TREE2 按组建子树。输出 `main_tree/total_iqtree.treefile`（Newick）及拼接比对文件。

![系统发育树示例](/skills/phylo-tree-build/phylo_tree.png)

说明：建树本身只产树文件，此图是配套技能 [phylo-tree-plot](/zh/skills/phylo-tree-plot) 用本技能对 12 个公开 RefSeq 基因组（4 Escherichia / 4 Klebsiella / 2 Enterobacter / Citrobacter / Serratia）产出的 treefile 绘制的。

## 快速上手（30 秒）

**环境前提**：Windows 上需要 WSL2 + Ubuntu 24.04，按截图教程配置 → [docs/wsl-setup.md](https://github.com/nihuanhe/claw2bio/blob/main/bioinformatics/phylo-tree/phylo-tree-build/docs/wsl-setup.md)。

在 WSL Ubuntu 内按顺序执行：

```bash
cd bioinformatics/phylo-tree/phylo-tree-build/scripts
bash 00_bootstrap_ubuntu.sh        # 一次性：装 iqtree2/mafft + conda 环境 bcgtree
python3 patch_bcgtree_gblocks.py   # 一次性：修 bcgTree↔Gblocks 命名 bug
bash 01_run_bcgtree.sh             # 约 10 分钟 / 12 个基因组
bash 02_iqtree_main.sh             # → main_tree/total_iqtree.treefile
bash 03_parsnp_subtrees.sh         # 可选：分组子树（需两列 SampleID,Group CSV）
```

换自己的数据不用改脚本，用环境变量覆盖路径即可：
`SRC_IN=/path/to/input SRC_OUT=/path/to/output bash 01_run_bcgtree.sh`

## 输入格式

- 一个目录，每个菌株一个 `*.fasta`，文件名主干 = 样本 ID（也是后续注释 CSV 的 SampleID）。
- 可选两列 `SampleID,Group` CSV 用于 parsnp 分组子树。

## 输出文件

| 文件 | 内容 |
|---|---|
| `main_tree/total_iqtree.treefile` | Newick 主树（ML 骨架 + 1000 UFBoot 支持率） |
| `main_tree/full_alignment.concat.fa`（+ `.partition`） | 核心基因拼接比对（供自定义重跑） |
| `subtrees/<Group>.treefile` | 可选的 parsnp 分组子树 |
| `REPORT.md` | 逐文件产出说明 |

## 配置

模板脚本只改头部 EDIT-THIS 变量（`WORK` 工作目录、路径等）。两条黄金规则：

1. **工作目录必须纯 ASCII**——bcgTree/Perl 遇到非 ASCII 路径即崩；脚本默认把基因组复制到 `~/phylo_work` 里跑，结果再拷回。
2. **路径自动定位**——脚本相对自身解析示例输入输出，在任何机器任何目录都能跑。

## 常见问题

- **bcgTree 报 `Fasta::Parser ... .aln-gb`** → 漏跑了一次性的 `patch_bcgtree_gblocks.py`，补跑即可。
- **bcgTree 秒崩、路径报错** → `WORK` 路径含中文/非 ASCII 字符，换 `~/phylo_work` 或 `/mnt/d/...` 纯 ASCII 路径。
- **parsnp 段错误** → 某些 bioconda 构建的已知问题；子树是可选的，跳过第 3 步或换 parsnp 构建版本。
- **IQ-TREE 内存不足** → 降低 `-nt` 或减少基因组数；12 个基因组实测 < 4 GB。
- **国内 apt/conda 很慢** → 换国内镜像（docs/wsl-setup.md 第 4 节）。
- **为什么必须用技能自带脚本，不能让 AI 现写？**
  `scripts/` 里的是经过验证的路径：它们在示例数据上跑过，边界情况有文档记录。AI 现场生成的代码是
  "结果悄悄出错"的最常见来源。遇到没覆盖的情况，先改命令行参数；不够就复制脚本到临时目录做最小改动
  并说明改了什么；只有完全没有对应脚本时才允许新写，且新写后要回沉淀到 `scripts/`。

## 相关链接

- [GitHub 源码与 SKILL.md](https://github.com/nihuanhe/claw2bio/tree/main/bioinformatics/phylo-tree/phylo-tree-build)
- 相关技能：[进化树绘图](/zh/skills/phylo-tree-plot)
