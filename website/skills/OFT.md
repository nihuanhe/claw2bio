# Zero-Basics — Open Field Test (OFT) Analysis with an AI Agent | Copy & Paste All the Way

This tutorial uses workbuddy as the AI agent and Hy3 as the AI API. For installing and configuring the AI agent itself, see the [AI Agent setup tutorial](/skills/ai-agent-setup).

**Before you start (must read):**

- **If this is your first time doing data analysis with an AI agent, we strongly recommend following the [bulk-RNA-seq differential analysis tutorial](/skills/bulk-RNA-seq) first**, to learn the full "install skill → set up environment → run example → switch to your own data" workflow, then come back to this skill.
- This skill is **standalone** — it does not depend on the output of any other skill. Give it a coordinate CSV and it runs.
- In one sentence: **mouse open-field-test analysis — a Tracker-exported coordinate CSV (step,X,Y) in, a 300 dpi trajectory plot + behavior metrics (total distance, center entries / center time, rest time) + a multi-group summary table out**, with an optional pixelation step for presentation figures.
- **Honest note about the full pipeline:** the skill covers three steps — (1) extracting coordinates from video, (2) analysis & plotting, (3) optional pixelation. Step 1 needs the actual video file and manual frame-by-frame clicking, so the AI agent **cannot do that part for you**. Most users already have Tracker-exported CSVs and start directly at Step 2 — that is the main line of this tutorial. If your Tracker software works, just export from it and skip step 1 entirely.
- This skill uses **Python** — environment setup is light (matplotlib for analysis; pynput / Pillow only if you need steps 1 or 3).

**Tutorial structure:**

- **Step 1** | Install the OFT skill (one time only)
- **Step 2** | Set up the runtime environment (one time only)
- **Step 3** | Run the bundled example data
- **Step 4** | Switch to your own data
- **Step 5** | Let the AI interpret the results (+ optional pixelation)
- **More analysis** | Related skills (grouped barplot / brain atlas overlay)

---

## Step 1 | Install the OFT skill

Paste this prompt:

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
   of the folder (it should contain the three step folders 1_tracker_get_data,
   2_oft-analysis, 3_oft-pixelate).
(If my PC has no D: drive, install to C:\claw2bio instead and tell me the actual path.)
```

When Step 1 finishes, open the file manager and confirm that `D:\claw2bio\OFT` exists, with the three step subfolders, each having its own `SKILL.md`.

---

## Step 2 | Set up the runtime environment

Paste this prompt:

```
Please set up the runtime environment for the "OFT" skill at D:\claw2bio\OFT:
1. First, SEARCH THIS PC for an existing Python installation. If Python is already installed,
   report its version to me. Only if Python is NOT installed at all, install a recent Python 3
   (Windows), downloaded from the official python.org website, accepting all default options —
   and make sure to check "Add python.exe to PATH" during installation.
2. Install the Python packages this skill needs: matplotlib (required for step 2 analysis).
   Also install pynput (only used by step 1 manual recording) and Pillow (only used by
   step 3 pixelation) so all three steps are ready (use pip; if a package fails or is too
   slow, stop and tell me about it).
3. When everything is installed, confirm to me that the skill can run.
```

---

## Step 3 | Run the bundled example data

Paste this prompt:

```
The skill is installed at D:\claw2bio\OFT. Please run the bundled analysis example:
1. Example input is at D:\claw2bio\OFT\2_oft-analysis\examples\input\6.csv — a
   Tracker-exported step,X,Y coordinate file (344 frames, 2 minutes of recording).
2. From the folder D:\claw2bio\OFT\2_oft-analysis, run the skill's own script:
   python scripts/plot_oft.py examples/input/6.csv
   (outputs arena_6.png and arena_6.csv into the current directory).
3. Prefer the skill's own scripts in scripts/ — do NOT write new analysis code from scratch.
4. When the run succeeds, show me the trajectory figure and the metrics report, and explain both.
```

When the run succeeds, `arena_6.png` shows the arena with the mouse trajectory as a black line, the center zone (40%) as a green dashed square, the arena boundary (50 cm × 50 cm) in red, and four behavior metrics along the bottom. Anchor results for the example data: **total distance 1159.4 cm, 13 center entries, rest time 19.2 s, time in center 15.74%** — if your numbers match, the environment and pipeline are working correctly.

---

## Step 4 | Switch to your own data

Hand over your own Tracker-exported CSVs (`step,X,Y`, one file per animal/session). Paste this prompt:

```
My own OFT coordinate CSV files are at: <paste the path to your folder here>.
1. First check my files: each should be a Tracker export with columns step,X,Y (one file
   per animal). If some files came from the step-1 manual recorder (record.csv), that
   format is fine too.
2. IMPORTANT calibration check: the default arena bounds (908,384,1270,745), 50 cm side
   length and 120 s duration are specific to the example recording setup. My arena side
   length is <e.g., 50> cm and my recording duration is <e.g., 300> s; my camera/setup is
   <the same as the example / different>. If different, help me recalibrate px-per-cm
   (step 1 of the skill shows how: click two arena corners, pixel span ÷ real side length),
   then pass --px-per-cm and --total-duration to plot_oft.py.
3. Run the skill's own script plot_oft.py on each of my files — do NOT write new analysis
   code. Then run scripts/generate_summary.py on the results folder to produce one summary
   table for all animals.
4. Show me the trajectory figures, the per-animal metric CSVs, and the summary table.
```

If your Tracker software does not work at all, step 1 (`1_tracker_get_data/tracker.py`) is the fallback: you play the video, press **F2** to start recording, click the mouse's nose/body center frame by frame, press **F2** to pause and **Esc** to save `record.csv`. This needs you at the keyboard with the video — the AI agent prepares and guides, but cannot click for you.

---

## Step 5 | Let the AI interpret the results (+ optional pixelation)

Paste this prompt:

```
Please explain my OFT results in detail:
1. What each metric means (total distance = locomotor activity; center entries / time in
   center = anxiety-like behavior; rest time), and how my groups compare in the summary
   table.
2. Any WARNING lines in the metric CSVs — I understand they are data-quality self-checks
   (e.g., implausible speeds) that do not block the run; tell me if any of my animals look
   problematic. For reference, a C57BL/6 mouse typically moves at 3–8 cm/s.
3. Which figures and tables can go directly into a paper or presentation.

Then, if I want presentation-style figures: pixelate my arena_*.png trajectory plots with
the skill's own step-3 script:
   python 3_oft-pixelate/scripts/batch_pixelate.py <input_dir> <output_dir>
(350 px wide, NEAREST sampling, pixel-art style, keeps my folder structure). This is pure
cosmetic post-processing and does not change any analysis result.
```

After reading the AI's explanation, if anything is unclear, just ask it directly.

---

## More analysis

This skill only does OFT coordinate analysis and visualization. The skills below are related and installed in exactly the same way (one-click prompt or zip download):

### Grouped barplot — barplot

**One sentence: the per-group OFT metrics from your summary table (or any 2–6 group data) → barplot with statistics in one shot.** Wide-format CSV in; t-test / ANOVA + Tukey chosen automatically.

Details & download: /skills/barplot

### Brain atlas overlay annotation — brain-if-atlas-annotate

**One sentence: 100 ready-made mouse brain atlas line-art PNGs to overlay on fluorescence sections for brain-region annotation.** A natural next step if your behavioral study also looks at c-Fos or other brain-region readouts.

Details & download: /skills/brain-if-atlas-annotate
