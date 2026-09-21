# 零基础——用 AI Agent 做多通道免疫荧光批量对比度调整（if-contrast） | 全程复制粘贴

本教程以 workbuddy 作为 AI agent、Hy3 作为 AI API 为例。AI agent 本身的安装与配置请看[AI Agent 安装教程](/zh/skills/ai-agent-setup)。

**在开始之前（必读）：**

- **如果你是第一次用 AI agent 做数据分析，强烈建议先跟一遍 [bulk-RNA-seq 差异分析教程](/zh/skills/bulk-RNA-seq)**，熟悉"装技能 → 配环境 → 跑示例 → 换自己数据"的完整流程，再回来做本技能。
- 本技能是**独立技能**，不依赖任何其他技能的输出——给它一批扫描仪导出的单通道灰度 TIFF 就能用。
- 一句话：**16-bit 单通道灰度 TIFF 进，伪彩 RGB 图 + 四通道 Merge 合成图出**——先在一个参考视野上交互校准一次各通道亮度，宏把同一套参数应用到所有视野，保证整批图风格统一。
- ⚠️ **本技能是 Fiji/ImageJ 宏技能**：宏必须在 Fiji/ImageJ 里由你亲手运行，AI agent 的角色是**引导你操作**（准备目录结构、改通道配置、带你走校准对话框），而不是替你在命令行执行。
- 本技能**不需要 Python/R**，只需要 Fiji 或 NIH ImageJ 1.x（无需额外插件）。

**教程结构：**

- **Step 1**｜安装 if-contrast 技能（只需一次）
- **Step 2**｜安装 Fiji/ImageJ（只需一次）
- **Step 3**｜在 Fiji 里跑通示例（AI 全程引导）
- **Step 4**｜换成你自己的数据
- **Step 5**｜结果说明与重新校准
- **更多分析**｜相关技能简介（图片压缩 / 旷场实验）

---

## Step 1｜Install the if-contrast skill

输入以下 prompt：

```
Please install the "if-contrast" skill for me, into the D:\claw2bio folder:
1. Create a folder named claw2bio in the root of the D: drive (if it doesn't exist yet).
2. From the GitHub repository https://github.com/nihuanhe/claw2bio, fetch ONLY the folder
   experiment-data/IF-免疫荧光 (use sparse checkout — do NOT clone the whole repository),
   and place it at D:\claw2bio\if-contrast.
3. If downloading from GitHub fails or is too slow, download the zip from this mirror link instead:
   https://claw2bio.site/downloads/if-contrast.zip
   and extract it to D:\claw2bio\if-contrast.
4. Read the SKILL.md inside, then confirm to me that the skill is ready and list the contents
   of the folder.
(If my PC has no D: drive, install to C:\claw2bio instead and tell me the actual path.)
```

Step 1 完成后，打开文件管理器确认 `D:\claw2bio\if-contrast` 文件夹存在，里面有 `1_多通道批量对比度调整/`（含 `scripts/`、`examples/`）和 `SKILL.md` 等内容。

---

## Step 2｜安装 Fiji/ImageJ

宏必须在 Fiji 或 NIH ImageJ 1.x 中运行。输入 prompt：

```
The "if-contrast" skill at D:\claw2bio\if-contrast runs as a macro inside Fiji/ImageJ.
1. First, SEARCH THIS PC for an existing Fiji or ImageJ installation (e.g., Fiji.app,
   ImageJ.exe). If found, tell me the exact path to the executable.
2. Only if NEITHER is installed, download Fiji (Windows 64-bit) from the official website
   https://imagej.net/software/fiji/downloads and install/unpack it, then tell me the
   path to the executable.
3. Do NOT try to run the macro yourself — it must be run by me inside Fiji/ImageJ.
   Your job in this skill is to GUIDE me through the process.
```

Step 2 结束后，AI agent 会告诉你 Fiji/ImageJ 可执行文件的位置。

---

## Step 3｜在 Fiji 里跑通示例（AI 全程引导）

输入 prompt：

```
The skill is installed at D:\claw2bio\if-contrast. Please GUIDE me through running the
bundled example in Fiji/ImageJ (you guide, I click):
1. The macro is at D:\claw2bio\if-contrast\1_多通道批量对比度调整\scripts\batch_adjust_mif.ijm
   and the example input root folder is
   D:\claw2bio\if-contrast\1_多通道批量对比度调整\examples\input
   (2 samples × 4 channels: DAPI, CD8-AF488, PDL1-AF594, PD1-AF647).
2. Walk me through it step by step: Plugins → Macros → Run... → select the macro →
   choose the example input folder as the root folder.
3. For each of the 4 calibration dialogs, remind me: drag ONLY the Min/Max sliders in
   the Brightness/Contrast window, NEVER click Apply, then click OK.
4. When the "Done" dialog appears, help me verify the outputs: *-adjusted.tif files next
   to the originals and one FOV <sample>-Merge-adjusted.tif per sample.
5. Do NOT rewrite the macro; if anything needs adapting, edit only the CHANNELS/LUTS
   arrays at the top of the macro and tell me exactly what you changed.
```

按 AI 的引导操作，预期流程如下：

1. 宏弹出文件夹选择框，选择示例的 `examples\input` 目录；
2. 宏依次弹出 **4 次校准对话框**（DAPI→蓝、CD8-AF488→绿、PDL1-AF594→红、PD1-AF647→紫红），每次只拖 Min/Max 滑块调好显示效果后点 OK——**绝不点 Apply**（Apply 会永久修改像素值）；
3. 宏自动批量处理，结束后弹出 "Done" 提示。

运行成功后，每个通道的原始 TIFF 旁边会多出 `*-adjusted.tif`（伪彩 RGB），每个样本多出一张 `FOV sample1-Merge-adjusted.tif`（四通道合成图）。同一通道的所有视野共用同一套 min/max 参数，风格完全一致。仓库自带的示例是 ×4 降采样小 fixture（约 4 MB）；想看 181 MB 全尺寸示例（含宏真实输出）可从镜像下载：`https://my-website-1358159656.cos.ap-guangzhou.myqcloud.com/if-contrast/data/if-contrast-examples.zip`。

---

## Step 4｜换成你自己的数据

把扫描仪导出的 16-bit 单通道灰度 TIFF 按 `{root}/{样本}/{通道}/*.tif` 组织好（通道文件夹名必须与宏的 `CHANNELS` 数组**完全一致**，默认 `DAPI`、`CD8-AF488`、`PDL1-AF594`、`PD1-AF647`；也支持无样本层的扁平结构 `{root}/{通道}/*.tif`）。输入 prompt：

```
My own multiplex IF scans are at: <paste the path to your root folder here>.
1. First check my folder structure: it should be {root}/{sample}/{channel}/*.tif, and the
   channel folder names must EXACTLY match the macro's CHANNELS array (default: DAPI,
   CD8-AF488, PDL1-AF594, PD1-AF647 — case and hyphens must match). Report any mismatches.
2. My antibody panel is <e.g., DAPI + your markers and dyes>. If it differs from the default
   panel, edit ONLY the CHANNELS line at the top of the macro to match my panel (LUTS maps
   colors by array index), and tell me exactly what you changed.
3. Then GUIDE me through running the macro in Fiji/ImageJ on my root folder, same as the
   example run: 4 calibration dialogs, Min/Max sliders only, never Apply.
```

AI 会先核对你的目录命名，必要时只改宏顶部的 `CHANNELS` 数组适配你的抗体 panel，然后引导你在 Fiji 里完成校准和批量处理。

---

## Step 5｜结果说明与重新校准

跑完后按以下清单自查（AI 可以陪你逐项核对）：

- **单通道颜色**：DAPI→蓝、AF488→绿、AF594→红、AF647→紫红，`*-adjusted.tif` 与原图同目录；
- **Merge 图**：每个样本一张 `FOV {样本名}-Merge-adjusted.tif`，四通道叠加清晰、无明显过曝/欠曝；
- **一致性**：不同样本的同一通道亮度风格一致（因为共用同一套校准参数）；
- **原始文件**：不会被修改，所有输出都带 `-adjusted` 后缀。

如果对校准效果不满意：删除所有 `*-adjusted.tif` 和 `*-Merge-adjusted.tif`，重新运行宏再校准一次即可。有不懂的直接问 AI。

---

## 更多分析

本技能只做免疫荧光图的批量对比度调整与伪彩合成。下面几个技能与它相关，安装方式完全相同（一键 prompt 或网站下载 zip 包）：

### 大图压缩 —— compress-image

**一句话：几百 MB 的无压缩 TIFF 扫描图一键压到几 MB。** 默认 JPEG 85% 肉眼无损、保留 300 dpi 元数据；需要存档或后续定量分析时可选无损 TIFF LZW/ZIP。免疫荧光扫出来的大图正好用它瘦身。

详细介绍与下载：/zh/skills/compress-image

### 旷场实验（OFT）—— OFT

**一句话：小鼠旷场实验从轨迹 CSV 到发表级轨迹图与行为指标。** 总距离、中心区进入次数/时间、静止时间一键出，另有像素化展示图工具。

详细介绍与下载：/zh/skills/OFT
