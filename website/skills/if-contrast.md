# Zero-Basics — Batch Contrast Adjustment for Multiplex Immunofluorescence (if-contrast) | Copy & Paste All the Way

This tutorial uses workbuddy as the AI agent and Hy3 as the AI API. For installing and configuring the AI agent itself, see the [AI Agent setup tutorial](/skills/ai-agent-setup).

**Before you start (must read):**

- **If this is your first time doing data analysis with an AI agent, we strongly recommend following the [bulk-RNA-seq differential analysis tutorial](/skills/bulk-RNA-seq) first**, to learn the full "install skill → set up environment → run example → switch to your own data" workflow, then come back to this skill.
- This skill is **standalone** — it does not depend on the output of any other skill. Give it a folder of scanner-exported single-channel TIFFs and it works.
- In one sentence: **calibrate the brightness/contrast of each channel once on a reference field of view, then batch-apply the exact same settings to every FOV** — 16-bit single-channel grayscale TIFFs in, pseudo-color RGB TIFFs plus a 4-channel merged composite out, with a perfectly consistent style across all fields.
- **This skill is different from the others: the macro runs inside Fiji/ImageJ, not on the command line.** The AI agent's job is to *guide* you — prepare the folder structure, adapt the channel configuration, walk you through the calibration dialogs. You are the one who runs the macro and drags the sliders. No Python or R is needed at all.

**Tutorial structure:**

- **Step 1** | Install the if-contrast skill (one time only)
- **Step 2** | Install Fiji/ImageJ (one time only)
- **Step 3** | Run the bundled example data (guided, inside Fiji)
- **Step 4** | Switch to your own data
- **Step 5** | Let the AI explain the outputs & customize the panel
- **More analysis** | Related skills (WB densitometry / brain atlas overlay / image compression)

---

## Step 1 | Install the if-contrast skill

Paste this prompt:

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

When Step 1 finishes, open the file manager and confirm that `D:\claw2bio\if-contrast` exists, with `1_多通道批量对比度调整\scripts\batch_adjust_mif.ijm`, `examples\`, `SKILL.md`, etc. inside.

---

## Step 2 | Install Fiji/ImageJ

Paste this prompt:

```
Please check whether this PC has Fiji or NIH ImageJ 1.x installed:
1. SEARCH THIS PC for an existing Fiji or ImageJ installation. If one is found, tell me
   its version and where it is.
2. Only if neither is installed, download Fiji (the "Fiji is just ImageJ" bundle) for
   Windows from the official imagej.net website and install it with default options.
3. No extra plugins are needed for this skill — the macro uses only built-in ImageJ 1.x
   macro functions. Confirm to me that Fiji/ImageJ can start.
```

---

## Step 3 | Run the bundled example data

Remember: the macro runs **inside Fiji** — the AI agent cannot click the dialogs for you, it guides you through them. Paste this prompt:

```
The skill is installed at D:\claw2bio\if-contrast. Please guide me through running the
bundled example — the macro runs inside Fiji/ImageJ, so walk me through it step by step;
do NOT try to execute the macro yourself:
1. The macro is at D:\claw2bio\if-contrast\1_多通道批量对比度调整\scripts\batch_adjust_mif.ijm.
   The example input is the folder
   D:\claw2bio\if-contrast\1_多通道批量对比度调整\examples\input
   (a small downsampled fixture: 2 samples × 4 channels). If that input folder is missing
   in my copy, tell me and download the full-size example data (181 MB) from
   https://my-website-1358159656.cos.ap-guangzhou.myqcloud.com/if-contrast/data/if-contrast-examples.zip
   instead.
2. Tell me exactly what to click in Fiji: Plugins → Macros → Run... → select the .ijm file,
   then choose the example input folder as the root folder when prompted.
3. For each of the 4 channels a Brightness/Contrast window appears: I drag the Min/Max
   sliders until the reference FOV looks right, then click OK. Remind me clearly: NEVER
   click Apply — Apply would permanently alter the pixels; only the display range is
   recorded and reused.
4. When the batch run finishes, show me where the outputs were saved and explain them.
```

When the run finishes, next to every source TIFF you get a `*-adjusted.tif` pseudo-color RGB image (DAPI→blue, AF488→green, AF594→red, AF647→magenta), plus one `FOV <sample>-Merge-adjusted.tif` 4-channel merged composite per sample. Every FOV of the same channel shares identical min/max, so all fields look consistent. Original files are never modified. The bundled `examples\output\` folder also contains simulated pseudo-color PNGs you can compare your result against.

---

## Step 4 | Switch to your own data

Organize your scanner-exported 16-bit single-channel grayscale TIFFs as `{root}/{sample}/{channel}/*.tif` — the channel folder names must **exactly** match the macro's `CHANNELS` array (default: `DAPI`, `CD8-AF488`, `PDL1-AF594`, `PD1-AF647`). A flat layout (`{root}/{channel}/*.tif`, no sample level) is also supported. Paste this prompt:

```
My own multiplex IF images are at: <paste the path to your root folder here>.
1. Check my folder structure first: it should be {root}/{sample}/{channel}/*.tif (a flat
   {root}/{channel}/*.tif layout is also OK). My channels are <e.g., DAPI, CD8-AF488,
   PDL1-AF594, PD1-AF647 / write your own>.
2. The macro's channel list is the CHANNELS array at the top of batch_adjust_mif.ijm —
   if my panel differs from the default, edit ONLY the CHANNELS line (and keep my channel
   folder names identical to it); LUTS maps colors by array index. Do NOT rewrite the macro.
3. Then guide me through the run in Fiji exactly like the example: Plugins → Macros →
   Run..., pick the root folder, and remind me to only drag the Min/Max sliders and never
   click Apply during calibration.
4. When it finishes, confirm that every channel of every sample has a *-adjusted.tif and
   that each sample has a *-Merge-adjusted.tif, and that my original files are untouched.
```

---

## Step 5 | Let the AI explain the outputs & customize the panel

Paste this prompt:

```
Please explain the batch results to me:
1. What each output file is (per-channel *-adjusted.tif pseudo-color RGB; per-sample
   *-Merge-adjusted.tif 4-channel composite), and why all FOVs of a channel now share a
   consistent style.
2. I want to re-calibrate one channel with a different display range — tell me the correct
   procedure (delete all *-adjusted.tif, then rerun the macro; originals are never
   overwritten).
3. In my merged composite the AF647 channel shows in cyan while the single-channel output
   uses magenta — explain why (the merge command uses the c5/cyan slot) and, if I prefer
   magenta in the merge, make the minimal change (c5= → c6=) in a copy of the macro and
   tell me exactly what changed.
4. For my next experiment I use a different antibody panel: <list your channels>. Adapt
   the CHANNELS/LUTS arrays for it and remind me how to name the channel folders.
```

After reading the AI's explanation, if anything is unclear, just ask it directly.

---

## More analysis

This skill only does batch contrast adjustment and merging for multiplex IF images. The skills below are related and installed in exactly the same way (one-click prompt or zip download):

### Western Blot densitometry — wb-imagej

**One sentence: WB band gray values measured in ImageJ → β-actin normalization → statistics + publication-grade barplot.** Another ImageJ + Python combo skill — if your experiment has both IF and WB readouts, they share the same guided workflow style.

Details & download: /skills/wb-imagej

### Brain atlas overlay annotation — brain-if-atlas-annotate

**One sentence: 100 ready-made mouse brain atlas coronal line-art PNGs (Bregma +1.97 to -8.15 mm, black-line and white-line versions) to overlay on your fluorescence sections for brain-region annotation** — no atlas software or registration pipeline needed.

Details & download: /skills/brain-if-atlas-annotate

### Compress large images — compress-image

**One sentence: giant uncompressed TIFF scans in, small visually-lossless files out** — JPEG 85% by default with 300 dpi metadata preserved; lossless TIFF/PNG also supported. Ideal for archiving the huge scanner files this skill produces.

Details & download: /skills/compress-image
