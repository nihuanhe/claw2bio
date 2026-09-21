# Zero-Basics — Compress Large Scientific Images (compress-image) with an AI Agent | Copy & Paste All the Way

This tutorial uses workbuddy as the AI agent and Hy3 as the AI API. For installing and configuring the AI agent itself, see the [AI Agent setup tutorial](/skills/ai-agent-setup).

**Before you start (must read):**

- **If this is your first time doing data analysis with an AI agent, we strongly recommend following the [bulk-RNA-seq differential analysis tutorial](/skills/bulk-RNA-seq) first**, to learn the full "install skill → set up environment → run example → switch to your own data" workflow, then come back to this skill.
- This skill is **standalone** — it does not depend on the output of any other skill. Give it an image file and it runs.
- In one sentence: **huge uncompressed TIFF scans in, small visually-lossless files out** — JPEG at 85% quality by default (indistinguishable by eye) with 300 dpi metadata preserved; lossless TIFF LZW/ZIP and PNG are also supported.
- This skill uses **Python with a single dependency (Pillow)** — the lightest environment setup of all skills.

**Tutorial structure:**

- **Step 1** | Install the compress-image skill (one time only)
- **Step 2** | Set up the runtime environment (one time only)
- **Step 3** | Run the bundled example data
- **Step 4** | Switch to your own data
- **Step 5** | Let the AI help you pick the right format & verify quality
- **More analysis** | Related skills (IF contrast / brain atlas overlay)

---

## Step 1 | Install the compress-image skill

Paste this prompt:

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

When Step 1 finishes, open the file manager and confirm that `D:\claw2bio\compress-image` exists, with `scripts\compress_image.py`, `examples\`, `SKILL.md`, etc. inside.

---

## Step 2 | Set up the runtime environment

Paste this prompt:

```
Please set up the runtime environment for the "compress-image" skill at D:\claw2bio\compress-image:
1. First, SEARCH THIS PC for an existing Python installation. If Python is already installed,
   report its version to me. Only if Python is NOT installed at all, install a recent Python 3
   (Windows), downloaded from the official python.org website, accepting all default options —
   and make sure to check "Add python.exe to PATH" during installation.
2. Install the only package this skill needs: Pillow (use pip; if it fails or is too slow,
   stop and tell me about it).
3. When everything is installed, confirm to me that the skill can run.
```

---

## Step 3 | Run the bundled example data

Paste this prompt:

```
The skill is installed at D:\claw2bio\compress-image. Please run the bundled example:
1. Example input is at D:\claw2bio\compress-image\examples\input\sample_small.png
   (a 1200×1200 RGB downsampled example image, about 0.83 MB).
2. Run the skill's own script:
   python scripts/compress_image.py examples/input/sample_small.png examples/output/sample_small_JPEG_85pct.jpeg
3. Prefer the skill's own scripts in scripts/ — do NOT write new analysis code from scratch.
4. When the run succeeds, show me the console output (size before / after, compression
   ratio, space saved) and open both images side by side so I can check the visual quality.
```

When the run succeeds, the console prints the compression report: the ~0.83 MB PNG becomes a ~0.08 MB JPEG (about 90% smaller) with no visible difference. Want a stress test on a real scan? A full-size example (187.49 MB, 7903×7903 uncompressed Nikon scanner RGB TIFF, compresses to ~2.62 MB at JPEG 85%) is distributed separately — download it from `https://my-website-1358159656.cos.ap-guangzhou.myqcloud.com/compress-image/data/PRV_0001_RGB.tif` and run the same command on it.

---

## Step 4 | Switch to your own data

Paste this prompt:

```
My own large image files are at: <paste the path to your file or folder here>.
1. Compress each image with the skill's own script compress_image.py — do NOT write new
   code. Default mode is TIFF → JPEG 85% with the dpi metadata preserved (inherits the
   input dpi, or 300):
   python scripts/compress_image.py <input.tif> <output.jpg>
2. Use the script's CLI options as needed — nothing else:
   --quality <1-100, default 85>   JPEG quality
   --format <jpeg / tiff_lzw / tiff_zip / png>   output format
   --dpi <e.g., 300>   output DPI
3. IMPORTANT: ask me about the downstream use first. If these images will be used for
   quantitative analysis later, JPEG is NOT appropriate for the analysis originals — use
   --format tiff_zip (lossless) for those, and JPEG only for presentation/sharing copies.
4. Show me the size report for every file and confirm the dpi metadata is preserved.
```

Note: if an input TIFF is already compressed, compressing it again yields little — the script will still run, but expect modest savings.

---

## Step 5 | Let the AI help you pick the right format & verify quality

Paste this prompt:

```
Please help me decide and verify:
1. For each of my use cases, recommend the right settings: (a) figures for a paper
   submission, (b) archiving raw scans, (c) images that still need densitometry / IF
   quantification later, (d) quick sharing by email or chat. Base the recommendation on
   the script's options only (JPEG quality, tiff_lzw / tiff_zip, png, dpi).
2. Verify the results: open the original and the compressed version side by side at 100%
   zoom and confirm there is no visible quality loss; check that the output file carries
   the correct dpi metadata.
3. Summarize the total space saved across all my files.
```

After reading the AI's explanation, if anything is unclear, just ask it directly.

---

## More analysis

This skill only compresses images. The skills below are related and installed in exactly the same way (one-click prompt or zip download):

### Multiplex IF contrast — if-contrast

**One sentence: calibrate contrast once, then batch-apply to every FOV and merge channels.** Compress the raw scans for archiving, then adjust the working copies for your figures.

Details & download: /skills/if-contrast

### Brain atlas overlay annotation — brain-if-atlas-annotate

**One sentence: 100 ready-made mouse brain atlas line-art PNGs (Bregma +1.97 to −8.15 mm, two versions) to overlay on your sections for brain-region annotation** — pairs naturally with compressed whole-slide brain scans.

Details & download: /skills/brain-if-atlas-annotate
