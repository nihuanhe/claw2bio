# 零基础——用 AI Agent 做 qPCR mRNA 相对表达量分析（ΔΔCt） | 全程复制粘贴

本教程以 workbuddy 作为 AI agent、Hy3 作为 AI API 为例。AI agent 本身的安装与配置请看[AI Agent 安装教程](/zh/skills/ai-agent-setup)。

**在开始之前（必读）：**

- **如果你是第一次用 AI agent 做数据分析，强烈建议先跟一遍 [bulk-RNA-seq 差异分析教程](/zh/skills/bulk-RNA-seq)**，熟悉"装技能 → 配环境 → 跑示例 → 换自己数据"的完整流程，再回来做本技能。
- 本技能是**独立技能**，不依赖任何其他技能的输出——给它一张原始 qPCR Ct 表就能跑。
- 一句话：**ΔΔCt 法相对表达量分析，从原始 Ct 表直接产出每个靶基因一张发表级柱状图**——自动以内参基因归一化，自动选统计方法（2 组 t 检验；≥3 组 ANOVA + Dunnett）。
- 本技能用的是 **Python**（不是 R），环境配置比 RNA-seq 系列轻得多。

**教程结构：**

- **Step 1**｜安装 qpcr-mrna 技能（只需一次）
- **Step 2**｜配置运行环境（只需一次）
- **Step 3**｜跑通示例数据
- **Step 4**｜换成你自己的数据
- **Step 5**｜让 AI 解读结果
- **更多分析**｜相关技能简介（qPCR mtDNA / 分组柱状图）

---

## Step 1｜Install the qpcr-mrna skill

输入以下 prompt：

```
Please install the "qpcr-mrna" skill for me, into the D:\claw2bio folder:
1. Create a folder named claw2bio in the root of the D: drive (if it doesn't exist yet).
2. From the GitHub repository https://github.com/nihuanhe/claw2bio, fetch ONLY the folder
   experiment-data/qpcr-mrna (use sparse checkout — do NOT clone the whole repository),
   and place it at D:\claw2bio\qpcr-mrna.
3. If downloading from GitHub fails or is too slow, download the zip from this mirror link instead:
   https://claw2bio.site/downloads/qpcr-mrna.zip
   and extract it to D:\claw2bio\qpcr-mrna.
4. Read the SKILL.md inside, then confirm to me that the skill is ready and list the contents
   of the folder.
(If my PC has no D: drive, install to C:\claw2bio instead and tell me the actual path.)
```

Step 1 完成后，打开文件管理器确认 `D:\claw2bio\qpcr-mrna` 文件夹存在，里面有 `scripts/`、`examples/`、`SKILL.md` 等内容。

---

## Step 2｜Set up the runtime environment

输入 prompt：

```
Please set up the runtime environment for the "qpcr-mrna" skill at D:\claw2bio\qpcr-mrna:
1. First, SEARCH THIS PC for an existing Python installation. If Python is already installed,
   report its version to me. Only if Python is NOT installed at all, install a recent Python 3
   (Windows), downloaded from the official python.org website, accepting all default options —
   and make sure to check "Add python.exe to PATH" during installation.
2. Install all Python packages this skill needs: pandas, numpy, scipy, matplotlib
   (use pip; if a package fails or is too slow, stop and tell me about it).
3. When everything is installed, confirm to me that the skill can run.
```

Step 2 结束后，AI agent 会告诉你本机的 Python 版本和依赖安装结果。

---

## Step 3｜跑通示例数据

输入 prompt：

```
The skill is installed at D:\claw2bio\qpcr-mrna. Please run the bundled example:
1. Example input is at D:\claw2bio\qpcr-mrna\examples\input\mrna-input.csv
2. Write results to D:\claw2bio\qpcr-mrna\examples\output\ with the output name "Figure1".
3. Prefer the skill's own scripts in scripts/ — do NOT write new analysis code from scratch.
4. When the run succeeds, show me the result barplot for each target gene, and the Figure1.csv
   table; explain both to me.
```

运行成功后，每个靶基因会得到一张 300 dpi 柱状图。示例数据的锚点结果：**IL6 上调约 6.8 倍，P<0.001**——如果你的结果与此一致，说明环境和流程都没问题。

![qPCR mRNA 示例结果](/skills/qpcr-mrna/Figure1_IL6_barplot.png)

---

## Step 4｜换成你自己的数据

把你自己的原始 Ct 表交给它。输入格式很简单（Target, Sample, Rep1, Rep2, Rep3 五列；内参行如 GAPDH 与靶标行格式相同；第一个出现的 Sample 默认作为对照组；支持 2–6 组）。输入 prompt：

```
My own qPCR Ct table is at: <paste the path to your CSV file here>.
1. First check whether my table has any format problems (required columns: Target, Sample,
   Rep1, Rep2, Rep3; the reference gene row — default GAPDH — must be present and spelled
   correctly); if so, fix them and tell me what you did.
2. My reference gene is <GAPDH / write your own>, and my control group is <the group name as
   it appears in the Sample column>.
3. Once the data checks out, run the full ΔΔCt analysis with the output name <e.g., Figure2>,
   and show me the barplot for each target gene plus the result CSV.
4. Prefer the skill's own scripts in scripts/; if anything needs adapting, make the smallest
   possible change — do NOT write large amounts of new code.
```

等候 AI agent 运行结束：每个靶基因出一张带统计标注的 300 dpi 柱状图（2 组 t 检验；≥3 组 ANOVA + Dunnett），外加一张含 ΔCt、Fold change、P 值、显著性的结果 CSV。

---

## Step 5｜让 AI 解读结果

输入 prompt：

```
Please explain the result CSV and the barplots in my output folder line by line:
1. What each column in the CSV means (raw Ct, ΔCt, ΔΔCt, Fold change, P value, significance);
2. For each target gene: how much it is up- or down-regulated relative to my control group,
   and whether the change is statistically significant;
3. Which statistical test was used for each gene, and why;
4. Any warnings or things I should pay attention to (e.g., high Ct replicate variation,
   reference-gene stability).
After explaining, tell me which figures can be used directly in a paper or presentation.
```

阅读完 AI 的解释，如果有不懂的直接问它。

---

## 更多分析

本技能只做 mRNA 的 ΔΔCt 相对表达量分析。下面两个技能与它相关，安装方式完全相同（一键 prompt 或网站下载 zip 包）：

### qPCR mtDNA 拷贝数 —— qpcr-mtdna

**一句话：从 ND1 / ND5 / B2M / POLG 四个 Ct 值算线粒体 DNA 相对拷贝数。** 自动按公式 Mean copy number = (2^(B2M-ND1) + 2^(POLG-ND5)) / 2 计算，自动统计并出 300 dpi 柱状图。

详细介绍与下载：/zh/skills/qpcr-mtdna

### 分组柱状图 —— barplot

**一句话：任何 2–6 组的实验数据（ELISA、WB 灰度、细胞计数……）一键出带统计标注的柱状图。** 给一张宽表 CSV 就行，自动选统计方法。

详细介绍与下载：/zh/skills/barplot
