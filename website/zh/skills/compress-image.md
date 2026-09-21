# 零基础——用 AI Agent 压缩科研大图（compress-image） | 全程复制粘贴

本教程以 workbuddy 作为 AI agent、Hy3 作为 AI API 为例。AI agent 本身的安装与配置请看[AI Agent 安装教程](/zh/skills/ai-agent-setup)。

**在开始之前（必读）：**

- **如果你是第一次用 AI agent 做数据分析，强烈建议先跟一遍 [bulk-RNA-seq 差异分析教程](/zh/skills/bulk-RNA-seq)**，熟悉"装技能 → 配环境 → 跑示例 → 换自己数据"的完整流程，再回来做本技能。
- 本技能是**独立技能**，不依赖任何其他技能的输出——给一张大图就能跑。
- 一句话：**几百 MB 的无压缩 TIFF 进，几 MB 的小图出**——默认 JPEG 85% 质量，肉眼基本无损，并保留 300 dpi 元数据；也支持无损 TIFF LZW/ZIP 和 PNG。
- 本技能用的是 **Python**，环境配置极轻（只需 Pillow）。

**教程结构：**

- **Step 1**｜安装 compress-image 技能（只需一次）
- **Step 2**｜配置运行环境（只需一次）
- **Step 3**｜跑通示例数据
- **Step 4**｜换成你自己的数据
- **Step 5**｜让 AI 解读结果与选择格式
- **更多分析**｜相关技能简介（脑 atlas 标注 / 免疫荧光对比度）

---

## Step 1｜Install the compress-image skill

输入以下 prompt：

```
Please install the "compress-image" skill for me, into the D:\claw2bio folder:
1. Create a folder named claw2bio in the root of the D: drive (if it doesn't exist yet).
2. From the GitHub repository https://github.com/nihuanhe/claw2bio, fetch ONLY the folder
   figure-generation/compress-image (use sparse checkout — do NOT clone the whole
   repository), and place it at D:\claw2bio\compress-image.
3. If downloading from GitHub fails or is too slow, download the zip from this mirror link instead:
   https://claw2bio.site/downloads/compress-image.zip
   and extract it to D:\claw2bio\compress-image.
4. Read the SKILL.md inside, then confirm to me that the skill is ready and list the contents
   of the folder.
(If my PC has no D: drive, install to C:\claw2bio instead and tell me the actual path.)
```

Step 1 完成后，打开文件管理器确认 `D:\claw2bio\compress-image` 文件夹存在，里面有 `scripts/`、`examples/`、`SKILL.md` 等内容。

---

## Step 2｜Set up the runtime environment

输入 prompt：

```
Please set up the runtime environment for the "compress-image" skill at D:\claw2bio\compress-image:
1. First, SEARCH THIS PC for an existing Python installation. If Python is already installed,
   report its version to me. Only if Python is NOT installed at all, install a recent Python 3
   (Windows), downloaded from the official python.org website, accepting all default options —
   and make sure to check "Add python.exe to PATH" during installation.
2. Install the Python package this skill needs: Pillow
   (use pip; if the package fails or is too slow, stop and tell me about it).
3. When everything is installed, confirm to me that the skill can run.
```

---

## Step 3｜跑通示例数据

输入 prompt：

```
The skill is installed at D:\claw2bio\compress-image. Please run the bundled example:
1. Example input is at D:\claw2bio\compress-image\examples\input\sample_small.png
2. Run the skill's own script:
   python scripts/compress_image.py examples/input/sample_small.png examples/output/sample_small_JPEG_85pct.jpeg
3. Prefer the skill's own scripts in scripts/ — do NOT write new analysis code from scratch.
4. When the run succeeds, report the console output to me: sizes before/after, compression
   ratio, and space saved.
```

运行成功后，控制台会打印压缩前后大小与压缩比例。示例数据的锚点结果：输入为 1200×1200 RGB 降采样示例图（约 0.83 MB），输出 JPEG 85% 约 **0.08 MB**（约 1/10 体积），肉眼与原版无区别。

想试全尺寸真实示例，可下载 187.49 MB 的 7903×7903 尼康扫描 RGB 无压缩 TIFF（转 JPEG 85% 后约 2.62 MB）：`https://my-website-1358159656.cos.ap-guangzhou.myqcloud.com/compress-image/data/PRV_0001_RGB.tif`，下载后同样交给 AI 跑一遍即可。

---

## Step 4｜换成你自己的数据

输入 prompt：

```
My own image file(s) are at: <paste the path to your image file or folder here>.
1. Run the skill's own script scripts/compress_image.py on my file(s) with the DEFAULT
   settings first (JPEG quality 85, dpi inherited from input or 300) — do NOT write new
   code from scratch.
2. If I need a different output, use the script's own CLI parameters instead:
   --quality 1-100 (JPEG quality, default 85),
   --format jpeg / tiff_lzw / tiff_zip / png (default jpeg),
   --dpi <number> (default: inherit input or 300).
3. Report the before/after sizes and compression ratio for each file.
```

---

## Step 5｜让 AI 解读结果与选择格式

输入 prompt：

```
Please explain the compression results and help me choose the right format:
1. Explain the console output: original size, compressed size, ratio, space saved;
2. Confirm the output keeps 300 dpi metadata (important for journal figure submission);
3. Advise me on format choice: JPEG 85% for presentation/sharing; but if the image is
   raw data for later quantitative analysis, JPEG is NOT appropriate — re-compress with
   --format tiff_zip (lossless) instead;
4. Note: if my input is already a compressed TIFF, further compression gains are limited —
   tell me if that is the case.
```

阅读完 AI 的解释，如果有不懂的直接问它。

---

## 更多分析

本技能只做图像压缩。下面几个技能与它相关，安装方式完全相同（一键 prompt 或网站下载 zip 包）：

### 脑 atlas 叠加标注 —— brain-if-atlas-annotate

**一句话：100 张小鼠脑 atlas 冠状面线图（黑线/白线两版），按 Bregma 坐标选图叠加到荧光/脑片图上标注脑区。** 全脑扫描的大图先用 compress-image 瘦身，再叠加标注更流畅。

详细介绍与下载：/zh/skills/brain-if-atlas-annotate

### 多通道免疫荧光批量对比度调整 —— if-contrast

**一句话：16-bit 单通道灰度 TIFF 批量转伪彩 RGB + Merge 合成图。** 免疫荧光扫描原图既大又灰，先用 if-contrast 调对比度出图，再用 compress-image 控制成品图体积。

详细介绍与下载：/zh/skills/if-contrast
