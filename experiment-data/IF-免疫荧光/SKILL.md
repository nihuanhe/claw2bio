---
name: if-contrast
description: Batch contrast adjustment for multiplex immunofluorescence (mIF) images via an ImageJ/Fiji macro — interactively calibrate min/max per channel once, then batch-convert 16-bit single-channel grayscale TIFFs to pseudo-color RGB plus a merged composite.（中文摘要：Fiji/ImageJ 宏技能——多通道免疫荧光图批量对比度调整；先交互校准一次各通道亮度，再批量把 16-bit 单通道灰度 TIFF 转伪彩 RGB 并合成 Merge 图，保证所有视野风格统一。）
---

# Skill: if-contrast

## Execution rule / 执行铁律

**This is a Fiji/ImageJ macro skill — the macro runs inside Fiji/ImageJ, not on the command line.**
The AI agent's job is to **guide** the user (prepare the folder structure, adapt the
`CHANNELS` array, walk through the calibration dialogs), **not to execute the macro
itself**. Do not rewrite the macro from memory; the tested macro is
`1_多通道批量对比度调整/scripts/batch_adjust_mif.ijm`.

Allowed changes, in order of preference:

1. Edit the `CHANNELS` / `LUTS` arrays at the top of the macro to match the user's
   panel (this is the designed configuration point).
2. Copy the macro to a scratch dir and make a **minimal** edit for a case the
   config arrays cannot express — keep the change small and report exactly what
   changed.
3. Only if no macro covers the task at all: write new code, and then **fold it
   back** next to the existing macro so the next run reuses it.

（中文摘要：本技能是 Fiji/ImageJ 宏技能。AI agent 负责**引导**用户在 Fiji/ImageJ 中运行宏，
而非自己执行；优先只改宏顶部的 `CHANNELS`/`LUTS` 配置数组；确需改代码时复制到临时目录做
**最小改动**并说明改了什么。禁止"凭印象重写一遍"。）

## Trigger phrases

- immunofluorescence contrast / IF contrast adjustment
- multiplex IF / mIF batch processing
- pseudo-color / merge channels ImageJ
- 免疫荧光调对比度 / 多通道免疫荧光 / 伪彩合成 / Merge 图

## What it does

Batch-adjusts brightness/contrast of multiplex immunofluorescence (mIF) scans:
the user calibrates the display min/max of each channel **once** on a reference
FOV via the ImageJ Brightness/Contrast dialog, then the macro applies the same
parameters to every FOV, converts each 16-bit single-channel grayscale TIFF to a
pseudo-color RGB TIFF (`*-adjusted.tif`), and writes a 4-channel merged composite
(`FOV <sample>-Merge-adjusted.tif`). Original files are never modified.

## Sub-skills

| Sub-skill | Path | What it does |
|---|---|---|
| 多通道批量对比度调整 | `1_多通道批量对比度调整/README.md` | Full step-by-step manual for the `batch_adjust_mif.ijm` macro (calibration dialogs, folder naming rules, panel switching) |

## Usage (guided, in Fiji/ImageJ)

1. Organize the input as `{root}/{sample}/{channel}/*.tif` — channel folder names
   must exactly match the macro's `CHANNELS` array
   (default: `DAPI`, `CD8-AF488`, `PDL1-AF594`, `PD1-AF647`).
2. In Fiji/ImageJ: **Plugins → Macros → Run...** → select
   `1_多通道批量对比度调整/scripts/batch_adjust_mif.ijm`.
3. Choose the root folder when prompted.
4. For each of the 4 channels, drag the Min/Max sliders in the
   Brightness/Contrast window (do **not** click Apply), then click OK.
5. The macro batch-processes all samples and saves `*-adjusted.tif` next to the
   originals plus one `*-Merge-adjusted.tif` per sample.

## Input

16-bit single-channel grayscale TIFFs (scanner raw data), organized as:

```
{root}/
├── sample1/
│   ├── DAPI/xxx_TG440.tif
│   ├── CD8-AF488/xxx_TG520.tif
│   ├── PDL1-AF594/xxx_TG570.tif
│   └── PD1-AF647/xxx_TG650.tif
└── sample2/ ...（同样 4 通道结构）
```

A flat layout (`{root}/{channel}/*.tif`, no sample level) is also supported.

## Output

- Per channel: `*-adjusted.tif` — pseudo-color RGB TIFF (DAPI→blue, AF488→green,
  AF594→red, AF647→magenta), saved next to the source file
- Per sample: `FOV <sample>-Merge-adjusted.tif` — 4-channel merged RGB composite
- All FOVs of the same channel share identical min/max → consistent style

## Example

`1_多通道批量对比度调整/examples/` contains a small downsampled (×4) fixture
(2 samples × 4 channels, 4.1 MB total) with simulated pseudo-color output PNGs
for visual reference. The full-size example data (181 MB: 16-bit inputs + actual
macro outputs) is distributed via COS:

```
https://my-website-1358159656.cos.ap-guangzhou.myqcloud.com/if-contrast/data/if-contrast-examples.zip
```

Run the macro in Fiji/ImageJ on `examples/input/` and select it as the root
folder; compare the resulting `*-adjusted.tif` files with `examples/output/`.

## Dependencies

- Fiji or NIH ImageJ 1.x (macro language, no extra plugins required)
- No Python/R needed

## Verification / 验证方式

The macro cannot be executed by the AI agent on this machine (no headless
ImageJ). It has been **statically syntax-reviewed** (2026-09-21): all functions
are complete, braces balanced, no mojibake/truncation; macro API calls
(`getFileList`, `setMinAndMax`, `run("Merge Channels...", ...)`,
`File.getNameWithoutExtension`, `setBatchMode`, `waitForUser`) are valid ImageJ
1.x macro functions. Known cosmetic issues (do not affect execution):

- Header/LUT comments still mention the old Panel-2 channels (FOXP3/NOXA/CD4)
  while `CHANNELS` is the Panel-1 array (CD8/PDL1/PD1) — comments only.
- The merge uses the `c5` slot (cyan) for the AF647 channel while the
  single-channel output uses the Magenta LUT; the composite shows this channel
  in cyan. Change `c5=` to `c6=` in the merge command if magenta is preferred.
- The macro body contains Chinese comments; ImageJ 1.x handles UTF-8 comments
  in practice, but if the macro editor shows garbled text, open the file as
  UTF-8 — execution is unaffected (comments are stripped by the parser).

End-to-end validation requires opening Fiji/ImageJ and running the macro on
`examples/input/` as described above.

## Notes

- Never click **Apply** in the Brightness/Contrast dialog during calibration —
  only the display range is recorded; Apply would permanently alter pixels.
- To switch antibody panels, edit only the `CHANNELS` line (and keep folder
  names identical to it); `LUTS` maps colors by array index.
- Original files are never overwritten; to re-calibrate, delete all
  `*-adjusted.tif` and rerun.

> 中文提示：本技能需在 Fiji/ImageJ 中人工运行宏，AI agent 只负责准备目录结构、
> 改 `CHANNELS` 配置和引导校准流程；校准时只拖 Min/Max 滑块、绝不点 Apply。
