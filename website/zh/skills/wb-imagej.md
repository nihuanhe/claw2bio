# 零基础——用 AI Agent 做 Western Blot 灰度定量分析（wb-imagej） | 全程复制粘贴

本教程以 workbuddy 作为 AI agent、Hy3 作为 AI API 为例。AI agent 本身的安装与配置请看[AI Agent 安装教程](/zh/skills/ai-agent-setup)。

**在开始之前（必读）：**

- **如果你是第一次用 AI agent 做数据分析，强烈建议先跟一遍 [bulk-RNA-seq 差异分析教程](/zh/skills/bulk-RNA-seq)**，熟悉"装技能 → 配环境 → 跑示例 → 换自己数据"的完整流程，再回来做本技能。
- 本技能是**独立技能**，不依赖任何其他技能的输出——给它一张整理好的灰度值 CSV 就能跑。
- 一句话：**ImageJ 测得的条带灰度 CSV 进，内参归一化 + 统计检验 + 发表级柱状图出**——自动除以 beta-actin 内参，2 组 t 检验、≥3 组 ANOVA + Tukey，300 dpi 带误差线和显著性标注。
- 本技能是**两段式流程**：① 在 ImageJ/Fiji 里框选条带、用宏测灰度（人工操作，AI 引导）→ ② Python 脚本做归一化、统计和作图（AI 直接运行）。
- Python 部分环境配置很轻；ImageJ 部分需要 Fiji 或 NIH ImageJ（无需额外插件）。

**教程结构：**

- **Step 1**｜安装 wb-imagej 技能（只需一次）
- **Step 2**｜配置运行环境（只需一次）
- **Step 3**｜跑通示例数据
- **Step 4**｜换成你自己的数据（含 ImageJ 测灰度）
- **Step 5**｜让 AI 解读结果
- **更多分析**｜相关技能简介（分组柱状图 / 免疫荧光对比度）

---

## Step 1｜Install the wb-imagej skill

输入以下 prompt：

```
Please install the "wb-imagej" skill for me, into the D:\claw2bio folder:
1. Create a folder named claw2bio in the root of the D: drive (if it doesn't exist yet).
2. From the GitHub repository https://github.com/nihuanhe/claw2bio, fetch ONLY the folder
   experiment-data/WB-imageJ-定量 (use sparse checkout — do NOT clone the whole repository),
   and place it at D:\claw2bio\wb-imagej.
3. If downloading from GitHub fails or is too slow, download the zip from this mirror link instead:
   https://claw2bio.site/downloads/wb-imagej.zip
   and extract it to D:\claw2bio\wb-imagej.
4. Read the SKILL.md inside, then confirm to me that the skill is ready and list the contents
   of the folder.
(If my PC has no D: drive, install to C:\claw2bio instead and tell me the actual path.)
```

Step 1 完成后，打开文件管理器确认 `D:\claw2bio\wb-imagej` 文件夹存在，里面有 `scripts/`、`docs/`、`examples/`、`SKILL.md` 等内容。

---

## Step 2｜Set up the runtime environment

输入 prompt：

```
Please set up the runtime environment for the "wb-imagej" skill at D:\claw2bio\wb-imagej:
1. First, SEARCH THIS PC for an existing Python installation. If Python is already installed,
   report its version to me. Only if Python is NOT installed at all, install a recent Python 3
   (Windows), downloaded from the official python.org website, accepting all default options —
   and make sure to check "Add python.exe to PATH" during installation.
2. Install all Python packages this skill needs: pandas, numpy, scipy, matplotlib, statsmodels
   (use pip; if a package fails or is too slow, stop and tell me about it).
3. Also SEARCH THIS PC for an existing Fiji or ImageJ installation and report the path;
   only if NEITHER is found, download Fiji (Windows 64-bit) from the official website
   https://imagej.net/software/fiji/downloads and install/unpack it.
4. When everything is ready, confirm to me that the skill can run.
```

---

## Step 3｜跑通示例数据

输入 prompt：

```
The skill is installed at D:\claw2bio\wb-imagej. Please run the bundled example:
1. Example input is at D:\claw2bio\wb-imagej\examples\input\FigureR3.csv
   (4 groups, 1 target protein, 3 replicates each).
2. Run the skill's own script:
   python scripts/wb_pipeline.py examples/input/FigureR3.csv --control "Ctrl-BD-sEV" --output-dir examples/output
3. Prefer the skill's own scripts in scripts/ — do NOT write new analysis code from scratch.
4. When the run succeeds, show me the output figure and the normalized CSV, and explain
   both to me.
```

运行成功后，在 `examples\output` 得到 `FigureR3.png`（300 dpi 柱状图：均值柱 + SD 误差线 + 散点 + 显著性标注）和 `FigureR3.csv`（追加归一化数值、ANOVA/Tukey p 值与显著性）。示例是 4 组数据，脚本自动走单因素 ANOVA + Tukey HSD（对照组 Ctrl-BD-sEV）。

---

## Step 4｜换成你自己的数据

**第①段：在 ImageJ 里测灰度（人工操作，AI 引导）。** 输入 prompt：

```
I need to measure band gray values from my Western Blot scan first.
1. The skill at D:\claw2bio\wb-imagej has an ImageJ macro at docs/wb_quantify_imageJ.ijm
   and an operation manual at docs/ImageJ操作说明.md — read them first.
2. My WB scan image is at: <paste the path to your image here>.
3. GUIDE me through the manual in ImageJ/Fiji: I draw the band ROIs, and the macro does
   8-bit conversion, Rolling Ball background subtraction, inversion and sorting, then
   exports a CSV with IntDen values. Do NOT try to run the macro yourself — it runs
   inside ImageJ with my manual ROI selection.
```

**第②段：整理 CSV 并跑 Python 分析。** 把 ImageJ 导出的灰度值整理成列名严格为 `Protein,Sample,Mean_Rep1,Mean_Rep2,Mean_Rep3,beta_actin_mean` 的 CSV（重复次数不限于 3 次；同一 Sample 下所有 Protein 共享同一个 beta_actin_mean）。输入 prompt：

```
My organized gray-value CSV is at: <paste the path to your CSV file here>.
1. First check my table format: column names must be exactly
   Protein, Sample, Mean_Rep1..N, beta_actin_mean; Sample supports 2-6 groups.
   Report any problems.
2. My control group is <the group name as it appears in the Sample column> — pass it via
   --control so the Tukey p values are computed against it.
3. Run the skill's own wb_pipeline.py with --output-dir pointing to a separate output
   folder (the default OVERWRITES my input CSV — I want to keep the original).
   Do NOT write new analysis code from scratch.
4. Show me the bar plot and the normalized CSV, and explain the statistics.
```

---

## Step 5｜让 AI 解读结果

输入 prompt：

```
Please explain my WB quantification results in detail:
1. How the normalization works (each replicate divided by beta-actin mean of the same
   sample) and what Normalized_Mean / SD / SEM mean;
2. Which statistical test was used and why (Student's t-test for 2 groups;
   one-way ANOVA + Tukey HSD vs my control for >=3 groups), and what the significance
   labels (ns/*/**/***) mean for each comparison;
3. Any warnings (e.g., large replicate variation, unusual loading-control values).
After explaining, tell me whether the figure can be used directly in a paper.
```

阅读完 AI 的解释，如果有不懂的直接问它。更多计算背景（完整流程推导、宏参数说明）在技能文件夹的 `docs/WB计算完整流程.md` 和 `docs/ImageJ操作说明.md`。

---

## 更多分析

本技能只做 WB 灰度的归一化、统计与柱状图。下面几个技能与它相关，安装方式完全相同（一键 prompt 或网站下载 zip 包）：

### 分组柱状图 —— barplot

**一句话：任何 2–6 组的实验数据一键出带统计标注的分组柱状图。** 如果你的数据不需要内参归一化（ELISA、细胞计数等），或者想换配色风格，直接用 barplot 更省事。

详细介绍与下载：/zh/skills/barplot

### 多通道免疫荧光批量对比度调整 —— if-contrast

**一句话：16-bit 单通道灰度 TIFF 批量转伪彩 RGB + Merge 合成图。** 同属 ImageJ 工作流家族，WB 之外的免疫荧光图处理用它。

详细介绍与下载：/zh/skills/if-contrast
