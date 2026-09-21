# 零基础——用 AI Agent 做小鼠旷场实验（OFT）分析 | 全程复制粘贴

本教程以 workbuddy 作为 AI agent、Hy3 作为 AI API 为例。AI agent 本身的安装与配置请看[AI Agent 安装教程](/zh/skills/ai-agent-setup)。

**在开始之前（必读）：**

- **如果你是第一次用 AI agent 做数据分析，强烈建议先跟一遍 [bulk-RNA-seq 差异分析教程](/zh/skills/bulk-RNA-seq)**，熟悉"装技能 → 配环境 → 跑示例 → 换自己数据"的完整流程，再回来做本技能。
- 本技能是**独立技能**，不依赖任何其他技能的输出——给它 Tracker 导出的轨迹坐标 CSV 就能跑。
- 一句话：**轨迹坐标 CSV（step,X,Y）进，300 dpi 轨迹图 + 行为学指标报告出**——总距离、中心区进入次数/时间、静止时间、速度分布一键算好，还能批量生成多组汇总表。
- 本技能是**三步流水线**：① 从视频提取轨迹（需视频 + 人工点击）→ ② 统计分析出图（**本教程主线**）→ ③ 像素化展示图（可选）。如果你已有 Tracker 导出的 CSV，直接从步骤 ② 开始即可。
- ⚠️ 步骤 ① 需要视频文件和人工逐帧点击，**AI agent 无法替你自动完成**；本教程以可直接运行的步骤 ② 为主线，步骤 ① 的使用方法见 Step 4 的说明。
- 本技能用的是 **Python**，环境配置很轻（步骤 ② 只需 matplotlib）。

**教程结构：**

- **Step 1**｜安装 OFT 技能（只需一次）
- **Step 2**｜配置运行环境（只需一次）
- **Step 3**｜跑通示例数据
- **Step 4**｜换成你自己的数据
- **Step 5**｜让 AI 解读结果与像素化展示图（可选）
- **更多分析**｜相关技能简介（免疫荧光对比度 / 分组柱状图）

---

## Step 1｜Install the OFT skill

输入以下 prompt：

```
Please install the "OFT" skill for me, into the D:\claw2bio folder:
1. Create a folder named claw2bio in the root of the D: drive (if it doesn't exist yet).
2. From the GitHub repository https://github.com/nihuanhe/claw2bio, fetch ONLY the folder
   experiment-data/OFT (use sparse checkout — do NOT clone the whole repository),
   and place it at D:\claw2bio\OFT.
3. If downloading from GitHub fails or is too slow, download the zip from this mirror link instead:
   https://claw2bio.site/downloads/OFT.zip
   and extract it to D:\claw2bio\OFT.
4. Read the SKILL.md inside, then confirm to me that the skill is ready and list the contents
   of the folder (it should contain three sub-skills: 1_tracker_get_data, 2_oft-analysis,
   3_oft-pixelate).
(If my PC has no D: drive, install to C:\claw2bio instead and tell me the actual path.)
```

Step 1 完成后，打开文件管理器确认 `D:\claw2bio\OFT` 文件夹存在，里面有 `1_tracker_get_data/`、`2_oft-analysis/`、`3_oft-pixelate/` 三个子技能文件夹和 `SKILL.md`。

---

## Step 2｜Set up the runtime environment

输入 prompt：

```
Please set up the runtime environment for the "OFT" skill at D:\claw2bio\OFT:
1. First, SEARCH THIS PC for an existing Python installation. If Python is already installed,
   report its version to me. Only if Python is NOT installed at all, install a recent Python 3
   (Windows), downloaded from the official python.org website, accepting all default options —
   and make sure to check "Add python.exe to PATH" during installation.
2. Install the Python packages this skill needs: matplotlib (required for step 2 analysis),
   and Pillow (for the optional step 3 pixelation). The analysis scripts otherwise use only
   the Python standard library.
3. When everything is installed, confirm to me that the skill can run.
```

> 如果你还需要用步骤 ①（手动录制轨迹，仅 Tracker 失效时），再让 AI 装 `pynput` 即可。

---

## Step 3｜跑通示例数据

输入 prompt：

```
The skill is installed at D:\claw2bio\OFT. Please run the bundled example of step 2
(2_oft-analysis):
1. Example input is at D:\claw2bio\OFT\2_oft-analysis\examples\input\6.csv
   (a Tracker-exported trajectory CSV with columns step,X,Y).
2. Run the skill's own script: python scripts/plot_oft.py examples/input/6.csv
   from inside the 2_oft-analysis folder (outputs arena_6.png and arena_6.csv
   next to the input file).
3. Prefer the skill's own scripts in scripts/ — do NOT write new analysis code from scratch.
4. When the run succeeds, show me the trajectory figure and the metrics CSV, and explain
   every metric to me.
```

运行成功后得到 `arena_6.png`（300 dpi 轨迹图，含中心区框线）和 `arena_6.csv`（结构化指标报告）。示例数据的锚点结果：**总距离 1159.4 cm、中心区进入 13 次、中心时间占比 15.74%**——如果你的结果与此一致，说明环境和流程都没问题。

---

## Step 4｜换成你自己的数据

**情况 A：你已有 Tracker 导出的 CSV（最常见）。** 输入格式很简单：`step,X,Y` 三列像素坐标。输入 prompt：

```
My own OFT trajectory CSV files are at: <paste the path to your file or folder here>.
1. First check my data format (required columns: step,X,Y, pixel coordinates exported
   from Tracker). Report any problems.
2. IMPORTANT — calibration: the skill's default arena bounds (908,384,1270,745) and
   px_per_cm ≈ 7.24 correspond to a specific recording setup (50 cm arena, 120 s
   duration). Ask me whether my recording setup matches; if not, help me recalibrate
   px_per_cm (pixel span of the arena / real side length in cm) and pass it via
   --px-per-cm, and adjust --total-duration to my actual recording length.
3. Run the skill's own plot_oft.py on each of my CSV files — do NOT write new analysis
   code from scratch.
4. If I have multiple animals, also run generate_summary.py on the results folder to
   produce one summary table.
5. Show me the trajectory figures and explain the metrics.
```

**情况 B：你只有视频、还没有轨迹 CSV。** 如实说明：这一步需要人工参与，AI 无法自动完成——

- **Tracker 软件正常**：直接用 Tracker 自动追踪并导出 `step,X,Y` CSV，然后回到情况 A；
- **Tracker 失效**：用技能自带的补救工具 `1_tracker_get_data/tracker.py` 手动录制——运行后打开视频暂停到起始帧，按 **F2** 开始录制，逐帧点击小鼠鼻子/身体中心，再按 **F2** 暂停、**Esc** 保存 `record.csv`。Arena 校准方法（点击场地两角算像素跨度 ÷ 真实边长 50 cm = px_per_cm）与操作演示 PPT 都在 `1_tracker_get_data/` 文件夹里，AI 可以照着 SKILL.md 引导你完成。

---

## Step 5｜让 AI 解读结果与像素化展示图（可选）

输入 prompt：

```
Please explain my OFT results in detail:
1. What each metric in arena_*.csv means: total distance, center entries, center time
   ratio, rest time, and the speed-distribution check;
2. Whether my animals' behavior looks reasonable (e.g., typical C57BL/6 moving speed is
   about 3-8 cm/s — flag anything abnormal, which may indicate a calibration problem);
3. Any WARNING messages in the output and whether I should worry about them.

Then, for figure presentation: run the skill's step 3 script
(3_oft-pixelate/scripts/batch_pixelate.py) to pixelate my arena_*.png figures to 350 px
width (NEAREST sampling) for assembling multi-panel paper figures. Keep the original
300 dpi versions for the record.
```

像素化是纯美化步骤（把高清轨迹图缩成 350 px 像素风小图，方便论文拼图），不影响任何分析结果。阅读完 AI 的解释，如果有不懂的直接问它。

---

## 更多分析

本技能只做旷场实验的轨迹分析与展示图。下面几个技能与它相关，安装方式完全相同（一键 prompt 或网站下载 zip 包）：

### 分组柱状图 —— barplot

**一句话：多组动物的行为学指标（总距离、中心时间……）一键出带统计标注的分组柱状图。** 把 `generate_summary.py` 汇总表整理成宽表 CSV 就能直接画，2 组 t 检验、≥3 组 ANOVA + Tukey。

详细介绍与下载：/zh/skills/barplot

### 多通道免疫荧光批量对比度调整 —— if-contrast

**一句话：16-bit 单通道灰度 TIFF 批量转伪彩 RGB + Merge 合成图。** Fiji/ImageJ 宏技能，一次校准、整批统一风格——做完行为学再做免疫荧光时用得上。

详细介绍与下载：/zh/skills/if-contrast
