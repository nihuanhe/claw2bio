# Zero-Basics — Mouse Brain Atlas Overlay Annotation (brain-if-atlas-annotate) | Copy & Paste All the Way

This tutorial uses workbuddy as the AI agent and Hy3 as the AI API. For installing and configuring the AI agent itself, see the [AI Agent setup tutorial](/skills/ai-agent-setup).

**Before you start (must read):**

- **If this is your first time doing data analysis with an AI agent, we strongly recommend following the [bulk-RNA-seq differential analysis tutorial](/skills/bulk-RNA-seq) first**, to learn the full "install skill → set up environment → run example → switch to your own data" workflow, then come back to this skill.
- This skill is **standalone** — it does not depend on the output of any other skill.
- In one sentence: **100 ready-made mouse brain atlas coronal line-art PNGs (Bregma +1.97 mm to −8.15 mm), in two versions — black lines on white for bright backgrounds and white lines on transparent for dark fluorescence images — so you can pick the plate matching your section's Bregma coordinate, overlay it, and annotate brain regions** without any atlas software or registration pipeline.
- This is a **resource skill**: the main use (pick plate → overlay → annotate) needs **no code at all** — ImageJ, Photoshop or Illustrator all work. Only the optional converter script (black-line → transparent white-line PNG) needs Python.

**Tutorial structure:**

- **Step 1** | Install the brain-if-atlas-annotate skill (one time only)
- **Step 2** | (Optional) Set up Python — only needed for the converter script
- **Step 3** | Try the pick-and-overlay workflow (guided, no code)
- **Step 4** | Annotate your own sections
- **Step 5** | (Optional) Convert black-line plates to transparent white-line PNGs
- **More analysis** | Related skills (IF contrast / image compression)

---

## Step 1 | Install the brain-if-atlas-annotate skill

Paste this prompt:

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
   of the folder.
(If my PC has no D: drive, install to C:\claw2bio instead and tell me the actual path.)
```

When Step 1 finishes, open the file manager and confirm that `D:\claw2bio\brain-if-atlas-annotate` exists, with `black_lines_only\` and `white_lines_only\` (100 PNGs each, identical filenames `Bregma_±X.XXmm.png` matched one-to-one by coordinate), plus `scripts\` and `SKILL.md`.

---

## Step 2 | (Optional) Set up Python — only needed for the converter script

The pick-and-overlay main workflow needs no environment at all. Only if you plan to convert black-line plates into transparent white-line PNGs (Step 5), paste this prompt:

```
Please set up Python for the converter script of the "brain-if-atlas-annotate" skill at
D:\claw2bio\brain-if-atlas-annotate:
1. First, SEARCH THIS PC for an existing Python installation. If Python is already installed,
   report its version to me. Only if Python is NOT installed at all, install a recent Python 3
   (Windows), downloaded from the official python.org website, accepting all default options —
   and make sure to check "Add python.exe to PATH" during installation.
2. Install the packages the converter needs: numpy, pillow (use pip).
3. Confirm to me when done.
```

---

## Step 3 | Try the pick-and-overlay workflow (guided, no code)

Paste this prompt:

```
The skill is installed at D:\claw2bio\brain-if-atlas-annotate. Guide me through the atlas
overlay workflow with a practice run — no coding needed:
1. Suppose my coronal section is at Bregma -1.55 mm. Show me the matching plate file
   (white_lines_only\Bregma_-1.55mm.png for a dark fluorescence image, or
   black_lines_only\Bregma_-1.55mm.png for a bright-field / light-background image) and
   explain the two versions.
2. Walk me through overlaying it in ImageJ: open my section image and the atlas plate,
   stack them, and align by anatomical landmarks (midline, ventricles, hippocampus shape).
3. Once aligned, explain how I read brain-region boundaries off the line art and label
   them on my figure.
4. Remind me of the golden rule: the atlas is a REFERENCE line drawing — I must verify
   region boundaries against my own histology before finalizing labels.
```

After this walkthrough you will have an annotated practice figure: your section image with the matching atlas plate aligned on top, region boundaries traced and labeled.

---

## Step 4 | Annotate your own sections

Paste this prompt:

```
My own brain section images are at: <paste the path to your folder here>.
1. For each image I tell you the Bregma coordinate of the section: <e.g., -1.55 mm, -2.03
   mm, +0.49 mm>. For each one, find the matching plate in white_lines_only\ or
   black_lines_only\ (the two folders have identical filenames, one per coordinate —
   pick white lines for my dark fluorescence scans, black lines for bright images) and
   tell me the exact file path to use.
2. Guide me through the overlay + landmark alignment in ImageJ (or Photoshop/Illustrator)
   for each section, like the practice run.
3. For each aligned overlay, list the major brain regions visible at that coordinate so I
   can label them, and remind me to verify every boundary against my own histology.
```

---

## Step 5 | (Optional) Convert black-line plates to transparent white-line PNGs

Only needed when you want to re-derive the white-line version or convert your own atlas pages. Paste this prompt:

```
Please run the skill's converter script (do NOT write new code):
1. Single plate:
   python scripts/convert_bregma_to_white_lines.py black_lines_only/Bregma_+0.01mm.png <output_dir>
2. Or batch-convert all 100 plates:
   python scripts/convert_bregma_to_white_lines.py --batch black_lines_only <output_dir>
3. Show me the outputs: each input produces an atlas_<coord>_white_lines_only.png
   (transparent background, white lines) plus a _preview_on_black_<coord>.png for a quick
   visual check.
4. If I convert my OWN atlas pages and the background gray level differs, copy the script
   to a scratch folder and adjust ONLY the GRAY_MAX threshold (default 169; black lines
   are ~≤64, gray fill ~128–169) — tell me exactly what you changed.
```

---

## More analysis

This skill only provides atlas line-art overlays and the converter. The skills below are related and installed in exactly the same way (one-click prompt or zip download):

### Multiplex IF contrast — if-contrast

**One sentence: calibrate contrast once, then batch-apply to every FOV and merge channels.** Prepares consistent-style fluorescence images before you overlay atlas plates on them.

Details & download: /skills/if-contrast

### Compress large images — compress-image

**One sentence: giant uncompressed TIFF brain scans in, small visually-lossless files out** — JPEG 85% by default with 300 dpi metadata preserved. Whole-slide brain scans are exactly what it was built for.

Details & download: /skills/compress-image
