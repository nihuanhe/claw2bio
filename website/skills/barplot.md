# Zero-Basics — Grouped Barplots with an AI Agent (barplot) | Copy & Paste All the Way

This tutorial uses workbuddy as the AI agent and Hy3 as the AI API. For installing and configuring the AI agent itself, see the [AI Agent setup tutorial](/skills/ai-agent-setup).

**Before you start (must read):**

- **If this is your first time doing data analysis with an AI agent, we strongly recommend following the [bulk-RNA-seq differential analysis tutorial](/skills/bulk-RNA-seq) first**, to learn the full "install skill → set up environment → run example → switch to your own data" workflow, then come back to this skill.
- This skill is **standalone** — it does not depend on the output of any other skill. Give it a wide-format CSV and it runs.
- In one sentence: **wide-format CSV in, publication-grade grouped barplot out** — auto-detects 2–6 groups, with means, SD error bars, jittered points, and statistics (t-test for 2 groups; ANOVA + Tukey HSD for ≥3 groups), 300 dpi. ELISA, WB densitometry, cell counts… any grouped experimental data works.
- This skill uses **Python** — environment setup is light.

**Tutorial structure:**

- **Step 1** | Install the barplot skill (one time only)
- **Step 2** | Set up the runtime environment (one time only)
- **Step 3** | Run the bundled example data
- **Step 4** | Switch to your own data
- **Step 5** | Let the AI interpret the results & customize the style
- **More analysis** | Related skills (qPCR / clinical table / survival curve)

---

## Step 1 | Install the barplot skill

Paste this prompt:

```
Please install the "barplot" skill for me, into the D:\claw2bio folder:
1. Create a folder named claw2bio in the root of the D: drive (if it doesn't exist yet).
2. From the GitHub repository https://github.com/nihuanhe/claw2bio, fetch ONLY the folder
   figure-generation/barplot (use sparse checkout — do NOT clone the whole repository),
   and place it at D:\claw2bio\barplot.
3. If downloading from GitHub fails or is too slow, download the zip from this mirror link instead:
   https://claw2bio.site/downloads/barplot.zip
   and extract it to D:\claw2bio\barplot.
4. Read the SKILL.md inside, then confirm to me that the skill is ready and list the contents
   of the folder.
(If my PC has no D: drive, install to C:\claw2bio instead and tell me the actual path.)
```

When Step 1 finishes, open the file manager and confirm that `D:\claw2bio\barplot` exists, with `scripts/`, `examples/`, `SKILL.md`, etc. inside.

---

## Step 2 | Set up the runtime environment

Paste this prompt:

```
Please set up the runtime environment for the "barplot" skill at D:\claw2bio\barplot:
1. First, SEARCH THIS PC for an existing Python installation. If Python is already installed,
   report its version to me. Only if Python is NOT installed at all, install a recent Python 3
   (Windows), downloaded from the official python.org website, accepting all default options —
   and make sure to check "Add python.exe to PATH" during installation.
2. Install all Python packages this skill needs: pandas, numpy, scipy, matplotlib, statsmodels
   (use pip; if a package fails or is too slow, stop and tell me about it).
3. When everything is installed, confirm to me that the skill can run.
```

---

## Step 3 | Run the bundled example data

Paste this prompt:

```
The skill is installed at D:\claw2bio\barplot. Please run the bundled example:
1. Example input is at D:\claw2bio\barplot\examples\input\data.csv
2. Run the skill's own script: python scripts/run_barplot.py examples/input/data.csv
   (the figure is saved NEXT TO the input CSV as data_barplot.png).
3. Prefer the skill's own scripts in scripts/ — do NOT write new analysis code from scratch.
4. When the run succeeds, show me the output figure and explain it: how many groups were
   detected, which statistical test was used, and what the significance labels mean.
```

When the run succeeds, `data_barplot.png` appears next to the example CSV: mean bars + SD error bars + jittered points + significance labels.

[Image placeholder: grouped barplot example result — no result screenshot on the skill webpage yet, to be added]

---

## Step 4 | Switch to your own data

Prepare a **wide-format** CSV: one column per group, one row per biological replicate (column names are group names; non-numeric columns are ignored automatically). Paste this prompt:

```
My own data table is at: <paste the path to your CSV file here>.
1. First check my table: it should be WIDE format — one column per group, one row per
   biological replicate, column names are group names. Non-numeric columns are ignored
   automatically, but if there are unexpected non-numeric columns the skill may pick the
   wrong script — check for that and tell me what you found.
2. Tell me how many groups you detected (the skill auto-selects the 2/3/4/5/6-group script),
   and confirm the group names match my intention before plotting.
3. Run the skill's own script — do NOT write new analysis code from scratch. The figure is
   saved next to my input CSV as <input>_barplot.png.
4. Show me the figure and explain the statistics (t-test for 2 groups; ANOVA + Tukey HSD
   for ≥3 groups).
```

---

## Step 5 | Let the AI interpret the results & customize the style

Paste this prompt:

```
Please explain my barplot figure in detail:
1. Which groups differ significantly and at what level (the meaning of the stars / letters);
2. Which statistical test was used and why it is appropriate for my group count;
3. Any warnings (e.g., very small sample sizes, outliers visible in the jittered points).

Then help me CUSTOMIZE the figure for my paper:
1. This skill's scripts are configured by editing the TOP of the selected script
   (FIGURE_NAME, Y_LABEL, bar_colors). Copy the script to a new file next to my data first,
   then edit ONLY that config block — my figure title should be <e.g., "ELISA"> and my Y-axis
   label should be <e.g., "IFNβ (pg/mL)">. Do NOT change anything else in the script.
2. The default colors are the Wong 2011 colorblind-safe palette; if I want the alternative
   palettes, use the barplot_2col_green_pink.py / barplot_3col_light.py variants (identical
   statistics).
3. Re-run and show me the customized figure.
```

After reading the AI's explanation, if anything is unclear, just ask it directly.

---

## More analysis

This skill only draws grouped barplots. The skills below are related and installed in exactly the same way (one-click prompt or zip download):

### qPCR mRNA (ΔΔCt) — qpcr-mrna | qPCR mtDNA copy number — qpcr-mtdna

**One sentence: raw qPCR Ct tables in, ΔΔCt relative-expression / mtDNA copy-number barplots out** — if your data is qPCR, these two skills save you a step (they compute ΔΔCt / copy number before plotting).

/skills/qpcr-mrna | /skills/qpcr-mtdna

### Clinical table — clinical-table

**One sentence: patient-level CSV in, a paper-style Table 1 baseline-characteristics table out.** χ²/Fisher for categorical variables + t-test for continuous ones; Markdown three-line tables convert to DOCX in one command.

Details & download: /skills/clinical-table

### Survival curve — survival-curve

**One sentence: a follow-up table in, KM survival curves + risk table + Cox forest plot out.** Automatic maxstat optimal cutoff, 600 dpi publication-grade.

Details & download: /skills/survival-curve
