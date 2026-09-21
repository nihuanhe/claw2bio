# 零基础——用 AI Agent 给脑片免疫荧光图叠加脑 atlas 标注（brain-if-atlas-annotate） | 全程复制粘贴

本教程以 workbuddy 作为 AI agent、Hy3 作为 AI API 为例。AI agent 本身的安装与配置请看[AI Agent 安装教程](/zh/skills/ai-agent-setup)。

**在开始之前（必读）：**

- **如果你是第一次用 AI agent 做数据分析，强烈建议先跟一遍 [bulk-RNA-seq 差异分析教程](/zh/skills/bulk-RNA-seq)**，熟悉"装技能 → 配环境 → 跑示例 → 换自己数据"的完整流程，再回来做本技能。
- 本技能是**资源型技能**：它自带 100 张小鼠脑 atlas 冠状面线图（Paxinos 风格，Bregma +1.97 ~ -8.15 mm，黑线/白线两版），主用途是**按坐标选图 → 叠加到你的荧光/脑片图上 → 标注脑区**，不需要跑任何分析代码，也不需要 atlas 软件或配准流程。
- 一句话：**查 Bregma 坐标 → 取同名线图 → ImageJ 里叠加对齐 → 脑区标注完成。** 黑线版适合亮场/浅色背景，白线版适合暗背景荧光图。
- 附带的转换脚本（黑线图 → 透明底白线图）是**可选**的，只有需要自定义图谱页时才用，需要 Python（numpy + pillow）。

**教程结构：**

- **Step 1**｜安装 brain-if-atlas-annotate 技能（只需一次）
- **Step 2**｜确定你脑片的 Bregma 坐标
- **Step 3**｜选图并在 ImageJ 里叠加标注（AI 引导）
- **Step 4**｜自定义：黑线图转透明底白线图（可选）
- **更多分析**｜相关技能简介（图片压缩 / 免疫荧光对比度）

---

## Step 1｜Install the brain-if-atlas-annotate skill

输入以下 prompt：

```
Please install the "brain-if-atlas-annotate" skill for me, into the D:\claw2bio folder:
1. Create a folder named claw2bio in the root of the D: drive (if it doesn't exist yet).
2. From the GitHub repository https://github.com/nihuanhe/claw2bio, fetch ONLY the folder
   figure-generation/brain-if-atlas-annotate (use sparse checkout — do NOT clone the whole
   repository), and place it at D:\claw2bio\brain-if-atlas-annotate.
3. If downloading from GitHub fails or is too slow, download the zip from this mirror link instead:
   https://claw2bio.site/downloads/brain-if-atlas-annotate.zip
   and extract it to D:\claw2bio\brain-if-atlas-annotate.
4. Read the SKILL.md inside, then confirm to me that the skill is ready and list the contents
   of the folder (it should contain black_lines_only/ and white_lines_only/ with 100 atlas
   PNGs each, plus scripts/).
(If my PC has no D: drive, install to C:\claw2bio instead and tell me the actual path.)
```

Step 1 完成后，打开文件管理器确认 `D:\claw2bio\brain-if-atlas-annotate` 文件夹存在，里面有 `black_lines_only/`、`white_lines_only/`（各 100 张 `Bregma_±X.XXmm.png`，两版文件名完全一致、按坐标一一对应）、`scripts/` 和 `SKILL.md`。

---

## Step 2｜确定你脑片的 Bregma 坐标

这一步不跑代码，是让 AI 帮你把坐标定准。输入 prompt：

```
The skill is installed at D:\claw2bio\brain-if-atlas-annotate. Before picking an atlas
plate, help me determine the Bregma coordinate of my brain section:
1. My sectioning info is: <e.g., the coronal level you targeted when sectioning, the
   brain region of interest, or landmarks visible in my image>.
2. Based on that, tell me the most likely Bregma coordinate(s), and list which
   Bregma_±X.XXmm.png files in black_lines_only/ and white_lines_only/ match them
   (the atlas covers Bregma +1.97 to -8.15 mm, 100 coronal plates).
3. If I am unsure between two adjacent plates, tell me both file names so I can try each.
```

AI 会给出候选坐标和对应的线图文件名（例如 `Bregma_-1.55mm.png`）。

---

## Step 3｜选图并在 ImageJ 里叠加标注（AI 引导）

主用途不需要跑脚本，在 ImageJ（或 Photoshop/Illustrator）里叠加即可。输入 prompt：

```
Please GUIDE me through overlaying the atlas line art on my fluorescence image in
ImageJ (you guide, I click):
1. My fluorescence image is at: <paste the path to your image here>.
   The matching atlas plate is D:\claw2bio\brain-if-atlas-annotate\white_lines_only\Bregma_<X.XX>mm.png
   (white-line version, since my image has a dark fluorescence background; if my image
   were bright-field/light background, use the same file name from black_lines_only/
   instead).
2. Walk me through it step by step in ImageJ: open my fluorescence image, then bring in
   the atlas PNG as an overlay/second layer (e.g., Image → Overlay → Add Image..., or
   open both and use Image → Color → Merge Channels...), scale and position the line
   art to match my section.
3. Remind me to align using anatomical landmarks: midline, ventricles, and the outline
   of the hippocampus.
4. Once aligned, guide me to flatten/export the composite (e.g., Image → Overlay →
   Flatten, then File → Save As) so I can annotate brain regions on it.
5. Finally remind me: the atlas is a reference line art — I should double-check region
   boundaries against my own histological judgment before finalizing labels.
```

按 AI 的引导操作，预期结果：荧光图上叠好一层透明底白线 atlas，中线、脑室、海马外形与你的脑片对齐，之后即可按线图轮廓标注目标脑区并导出成品图。

---

## Step 4｜自定义：黑线图转透明底白线图（可选）

只有当你需要重新生成白线版（例如自有 atlas 页）时才跑脚本。先让 AI 装好 Python 与 `numpy pillow`，然后输入 prompt：

```
I need to convert black-line atlas page(s) to transparent-background white-line PNGs
using the skill's own script at D:\claw2bio\brain-if-atlas-annotate:
1. Single file: python scripts/convert_bregma_to_white_lines.py black_lines_only/Bregma_+0.01mm.png <output dir>
2. Batch mode: python scripts/convert_bregma_to_white_lines.py --batch black_lines_only [output dir]
   (defaults to <input dir>/white_lines_only/).
3. Prefer the skill's own scripts in scripts/ — do NOT write new code from scratch.
   If my own atlas pages have a different background gray level, copy the script to a
   scratch folder and adjust ONLY the GRAY_MAX threshold (default 169), and tell me
   exactly what you changed.
4. Show me both outputs per plate: atlas_<coord>_white_lines_only.png (transparent white
   lines) and _preview_on_black_<coord>.png (black-background preview for quick check).
```

每张输入产出两个文件：透明底白线图和黑底预览图（供快速目检）。

---

## 更多分析

本技能只提供脑 atlas 线图资源与叠加标注流程。下面几个技能与它相关，安装方式完全相同（一键 prompt 或网站下载 zip 包）：

### 大图压缩 —— compress-image

**一句话：几百 MB 的无压缩 TIFF 脑片扫描图一键压到几 MB。** 默认 JPEG 85% 肉眼无损、保留 300 dpi 元数据——全脑切片扫描的大图先瘦身再叠加标注，操作更流畅。

详细介绍与下载：/zh/skills/compress-image

### 多通道免疫荧光批量对比度调整 —— if-contrast

**一句话：16-bit 单通道灰度 TIFF 批量转伪彩 RGB + Merge 合成图。** 叠加 atlas 之前，先用它把免疫荧光图的对比度统一调好。

详细介绍与下载：/zh/skills/if-contrast
