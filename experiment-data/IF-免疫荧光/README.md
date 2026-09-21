# IF-免疫荧光 (if-contrast)

Batch contrast adjustment for multiplex immunofluorescence (mIF) images, driven
by a Fiji/ImageJ macro.

多色免疫荧光（mIF）批量对比度调整——在 Fiji/ImageJ 中运行宏，交互校准一次各通道亮度，
批量将 16-bit 单通道灰度 TIFF 转伪彩 RGB 并合成 Merge 图，保证所有视野风格统一。

## Features

- Interactive one-time calibration of per-channel display min/max (Brightness/Contrast dialog)
- Batch conversion of 16-bit single-channel grayscale TIFFs to pseudo-color RGB
- 4-channel merged composite per sample (`FOV <sample>-Merge-adjusted.tif`)
- Uniform parameters across all FOVs → consistent figure style
- Original files never modified; supports nested (`sample/channel/`) and flat (`channel/`) layouts

## Requirements

Fiji or NIH ImageJ 1.x. No extra plugins, no Python/R.

> 注意：宏需在 Fiji/ImageJ 中由用户运行；AI agent 负责引导流程与改配置，不直接执行。

## Quick start

1. Organize input as `{root}/{sample}/{channel}/*.tif` (channel folder names must
   match the macro's `CHANNELS` array).
2. Fiji/ImageJ → **Plugins → Macros → Run...** →
   `1_多通道批量对比度调整/scripts/batch_adjust_mif.ijm`.
3. Select the root folder, calibrate the 4 channels (drag Min/Max, never click
   Apply), wait for batch processing to finish.

Full step-by-step manual: [`1_多通道批量对比度调整/README.md`](1_多通道批量对比度调整/README.md).

## Example data

- `1_多通道批量对比度调整/examples/` — small downsampled (×4) fixture,
  2 samples × 4 channels, ~4.1 MB, with simulated pseudo-color output PNGs.
- Full-size data (181 MB: 16-bit inputs + real macro outputs) via COS:
  `https://my-website-1358159656.cos.ap-guangzhou.myqcloud.com/if-contrast/data/if-contrast-examples.zip`

## File structure

```
IF-免疫荧光/
├── README.md
├── SKILL.md
└── 1_多通道批量对比度调整/
    ├── README.md                     # 完整操作手册（校准、命名规则、换 panel）
    ├── scripts/
    │   └── batch_adjust_mif.ijm      # ImageJ 宏（核心脚本）
    └── examples/
        ├── input/                    # 小 fixture：2 样本 × 4 通道 16-bit tif（×4 降采样）
        └── output/                   # 模拟伪彩输出 PNG + 说明（真机输出为 *-adjusted.tif）
```
