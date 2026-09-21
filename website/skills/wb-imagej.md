# Zero-Basics — Western Blot Band Densitometry (wb-imagej) with an AI Agent | Copy & Paste All the Way

This tutorial uses workbuddy as the AI agent and Hy3 as the AI API. For installing and configuring the AI agent itself, see the [AI Agent setup tutorial](/skills/ai-agent-setup).

**Before you start (must read):**

- **If this is your first time doing data analysis with an AI agent, we strongly recommend following the [bulk-RNA-seq differential analysis tutorial](/skills/bulk-RNA-seq) first**, to learn the full "install skill → set up environment → run example → switch to your own data" workflow, then come back to this skill.
- This skill is **standalone** — it does not depend on the output of any other skill. Give it a gray-value CSV and it runs.
- In one sentence: **Western Blot band densitometry, two stages — measure band gray values in ImageJ (guided, with the bundled macro), then one Python command does β-actin normalization + statistics + a publication-grade 300 dpi barplot** (t-test for 2 groups; ANOVA + Tukey HSD for ≥3 groups).
- Stage 1 runs **inside ImageJ/Fiji** (the AI agent guides you; it cannot draw the band boxes for you). Stage 2 is a regular Python script the agent runs for you. Environment setup is light.

**Tutorial structure:**

- **Step 1** | Install the wb-imagej skill (one time only)
- **Step 2** | Set up the runtime environment (Python + ImageJ, one time only)
- **Step 3** | Run the bundled example data
- **Step 4** | Switch to your own data (ImageJ measurement → CSV → pipeline)
- **Step 5** | Let the AI interpret the results & customize
- **More analysis** | Related skills (qPCR / grouped barplot / IF contrast)

---

## Step 1 | Install the wb-imagej skill

Paste this prompt:

```
Please install the "wb-imagej" skill for me, into the D:\claw2bio folder:
1. Create a folder named claw2bio in the root of the D: drive (if it doesn't exist yet).
2. From the GitHub repository https://github.com/nihuanhe/claw2bio, fetch ONLY the folder
   experiment-data/WB-imageJ-定量 (use sparse checkout — do NOT clone the whole repository),
   and place it at D:\claw2bio\wb-imagej.
3. If downloading from GitHub fails or is too slow, download the zip from this mirror link instead:
   https://claw2bio.site/downloads/wb-imagej.zip
   and extract it to D:\claw2bio\wb-imagej.
4. Read the SKILL.md inside, then confirm to me that the skill is ready and list the contents
   of the folder.
(If my PC has no D: drive, install to C:\claw2bio instead and tell me the actual path.)
```

When Step 1 finishes, open the file manager and confirm that `D:\claw2bio\wb-imagej` exists, with `scripts\wb_pipeline.py`, `docs\wb_quantify_imageJ.ijm`, `examples\`, `SKILL.md`, etc. inside.

---

## Step 2 | Set up the runtime environment

Paste this prompt:

```
Please set up the runtime environment for the "wb-imagej" skill at D:\claw2bio\wb-imagej:
1. First, SEARCH THIS PC for an existing Python installation. If Python is already installed,
   report its version to me. Only if Python is NOT installed at all, install a recent Python 3
   (Windows), downloaded from the official python.org website, accepting all default options —
   and make sure to check "Add python.exe to PATH" during installation.
2. Install all Python packages this skill needs: pandas, numpy, scipy, matplotlib, statsmodels
   (use pip; if a package fails or is too slow, stop and tell me about it).
3. Also SEARCH THIS PC for ImageJ or Fiji (needed for the band-measurement stage). Only if
   neither is installed, download Fiji from the official imagej.net website with default
   options. No extra ImageJ plugins are needed.
4. When everything is installed, confirm to me that the skill can run.
```

---

## Step 3 | Run the bundled example data

The example starts from stage 2 (the gray values have already been measured and arranged into a CSV). Paste this prompt:

```
The skill is installed at D:\claw2bio\wb-imagej. Please run the bundled example:
1. Example input is at D:\claw2bio\wb-imagej\examples\input\FigureR3.csv — 1 protein (NOXA)
   × 4 groups (Ctrl-BD-sEV / Stress-BD-sEV / Stress-BD-sEV+ProtK / Stress-BD-sEV+RNase)
   × 3 replicates, so it exercises the ANOVA + Tukey HSD branch.
2. Run the skill's own script:
   python scripts/wb_pipeline.py examples/input/FigureR3.csv --control "Ctrl-BD-sEV" --output-dir examples/output
   (--control sets the reference group for Tukey; --output-dir keeps the results separate
   from the input).
3. Prefer the skill's own scripts in scripts/ — do NOT write new analysis code from scratch.
4. When the run succeeds, show me the output CSV and the FigureR3.png barplot, and explain both.
```

When the run succeeds, `examples/output/` contains the normalized `FigureR3.csv` (with `Normalized_Mean/SD/SEM`, `ANOVA_F/ANOVA_p`, `p_value`, `Significance` appended) and a 300 dpi `FigureR3.png` (mean bars + SD error bars + jittered points + significance labels). Anchor results: normalized means **Ctrl = 0.7000, Stress = 1.4000, +ProtK = 1.1272, +RNase = 1.0000; ANOVA F = 38.0612, P < 0.001**; Tukey vs control: `***` / `***` (P = 0.0009) / `**` (P = 0.0086). If your numbers match, the environment and pipeline are working correctly.

---

## Step 4 | Switch to your own data

Two parts: measure your bands in ImageJ (guided), arrange the gray values into a CSV, then run the pipeline. Paste this prompt:

```
I want to quantify my own Western Blot. My blot image is at: <paste the image path here>.
PART A — guide me through measuring band gray values in ImageJ/Fiji (the macro runs inside
ImageJ; walk me through it, do NOT try to execute it yourself):
1. Use the skill's macro docs\wb_quantify_imageJ.ijm (see docs\ImageJ操作说明.md for the
   detailed manual). I draw a box around the first band and the macro handles 8-bit
   conversion, Rolling Ball background subtraction, inversion and sorting, then exports a
   CSV with IntDen values.
PART B — arrange the gray values into the pipeline's input format and run it:
1. Build my input CSV with EXACTLY these columns: Protein,Sample,Mean_Rep1,Mean_Rep2,
   Mean_Rep3,beta_actin_mean (more/fewer Mean_RepN columns are auto-detected; Protein =
   target protein name; Sample = group name, 2–6 groups; beta_actin_mean = loading-control
   gray value, shared by all proteins within the same Sample).
2. My control group is <the group name as it appears in the Sample column>.
3. Run the skill's own wb_pipeline.py with --control "<control group>" and --output-dir
   <a separate output folder>. IMPORTANT: without --output-dir the script overwrites the
   input CSV in place — keep my raw gray values safe.
4. Show me the normalized CSV and the barplot PNG, and explain the statistics.
```

---

## Step 5 | Let the AI interpret the results & customize

Paste this prompt:

```
Please explain my wb-imagej results in detail:
1. What each appended column means (Normalized_RepX = Mean_RepX / beta_actin_mean;
   Normalized_Mean/SD/SEM; p_value and the ns/*/**/*** Significance labels).
2. Which statistical test was used and why (Student's t-test for 2 groups; one-way ANOVA +
   Tukey HSD vs my --control group for ≥3 groups).
3. Anything to watch (small replicate counts, outlier points visible in the jitter).

Then help me with follow-ups:
1. I have several more blots saved as FigureR*/FigureR*.csv under one folder — run the
   batch mode: python scripts/wb_pipeline.py --batch <that folder>.
2. If I rerun the pipeline on an already-normalized CSV, confirm the normalization step is
   skipped automatically (idempotent) and only the figure/stats are regenerated.
```

After reading the AI's explanation, if anything is unclear, just ask it directly.

---

## More analysis

This skill only does WB densitometry → normalized barplot. The skills below are related and installed in exactly the same way (one-click prompt or zip download):

### qPCR mRNA (ΔΔCt) — qpcr-mrna

**One sentence: raw qPCR Ct tables in, ΔΔCt relative-expression barplots out.** The classic companion to a WB figure — mRNA and protein of the same target, analyzed with the same one-command workflow.

Details & download: /skills/qpcr-mrna

### Grouped barplot — barplot

**One sentence: any 2–6 group experimental data → barplot with statistics in one shot.** If you already have normalized values from elsewhere (ELISA, cell counts), this plots them directly.

Details & download: /skills/barplot

### Multiplex IF contrast — if-contrast

**One sentence: calibrate contrast once, then batch-apply to every FOV and merge channels** — the ImageJ-macro companion skill for the immunofluorescence side of your experiment.

Details & download: /skills/if-contrast
