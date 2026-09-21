# Zero-Basics — qPCR mRNA Relative Expression Analysis (ΔΔCt) with an AI Agent | Copy & Paste All the Way

This tutorial uses workbuddy as the AI agent and Hy3 as the AI API. For installing and configuring the AI agent itself, see the [AI Agent setup tutorial](/skills/ai-agent-setup).

**Before you start (must read):**

- **If this is your first time doing data analysis with an AI agent, we strongly recommend following the [bulk-RNA-seq differential analysis tutorial](/skills/bulk-RNA-seq) first**, to learn the full "install skill → set up environment → run example → switch to your own data" workflow, then come back to this skill.
- This skill is **standalone** — it does not depend on the output of any other skill. Give it a raw qPCR Ct table and it runs.
- In one sentence: **ΔΔCt relative-expression analysis — from a raw Ct table straight to one publication-grade barplot per target gene** — automatic normalization against the reference gene, automatic statistics (t-test for 2 groups; ANOVA + Dunnett for ≥3 groups).
- This skill uses **Python** (not R) — environment setup is much lighter than the RNA-seq family.

**Tutorial structure:**

- **Step 1** | Install the qpcr-mrna skill (one time only)
- **Step 2** | Set up the runtime environment (one time only)
- **Step 3** | Run the bundled example data
- **Step 4** | Switch to your own data
- **Step 5** | Let the AI interpret the results
- **More analysis** | Related skills (qPCR mtDNA / grouped barplot)

---

## Step 1 | Install the qpcr-mrna skill

Paste this prompt:

```
Please install the "qpcr-mrna" skill for me, into the D:\claw2bio folder:
1. Create a folder named claw2bio in the root of the D: drive (if it doesn't exist yet).
2. From the GitHub repository https://github.com/nihuanhe/claw2bio, fetch ONLY the folder
   experiment-data/qpcr-mrna (use sparse checkout — do NOT clone the whole repository),
   and place it at D:\claw2bio\qpcr-mrna.
3. If downloading from GitHub fails or is too slow, download the zip from this mirror link instead:
   https://claw2bio.site/downloads/qpcr-mrna.zip
   and extract it to D:\claw2bio\qpcr-mrna.
4. Read the SKILL.md inside, then confirm to me that the skill is ready and list the contents
   of the folder.
(If my PC has no D: drive, install to C:\claw2bio instead and tell me the actual path.)
```

When Step 1 finishes, open the file manager and confirm that `D:\claw2bio\qpcr-mrna` exists, with `scripts/`, `examples/`, `SKILL.md`, etc. inside.

---

## Step 2 | Set up the runtime environment

Paste this prompt:

```
Please set up the runtime environment for the "qpcr-mrna" skill at D:\claw2bio\qpcr-mrna:
1. First, SEARCH THIS PC for an existing Python installation. If Python is already installed,
   report its version to me. Only if Python is NOT installed at all, install a recent Python 3
   (Windows), downloaded from the official python.org website, accepting all default options —
   and make sure to check "Add python.exe to PATH" during installation.
2. Install all Python packages this skill needs: pandas, numpy, scipy, matplotlib
   (use pip; if a package fails or is too slow, stop and tell me about it).
3. When everything is installed, confirm to me that the skill can run.
```

When Step 2 finishes, the AI agent will tell you your Python version and the dependency installation result.

---

## Step 3 | Run the bundled example data

Paste this prompt:

```
The skill is installed at D:\claw2bio\qpcr-mrna. Please run the bundled example:
1. Example input is at D:\claw2bio\qpcr-mrna\examples\input\mrna-input.csv
2. Write results to D:\claw2bio\qpcr-mrna\examples\output\ with the output name "Figure1".
3. Prefer the skill's own scripts in scripts/ — do NOT write new analysis code from scratch.
4. When the run succeeds, show me the result barplot for each target gene, and the Figure1.csv
   table; explain both to me.
```

When the run succeeds, each target gene gets a 300 dpi barplot. Anchor result for the example data: **IL6 is up-regulated ~6.8-fold, P<0.001** — if your result matches, the environment and pipeline are working correctly.

[Image placeholder: qPCR mRNA example result barplot — no result screenshot on the skill webpage yet, to be added]

---

## Step 4 | Switch to your own data

Hand over your own raw Ct table. The input format is simple (five columns: Target, Sample, Rep1, Rep2, Rep3; reference-gene rows like GAPDH have the same format as target rows; the first Sample that appears is treated as the control group by default; 2–6 groups supported). Paste this prompt:

```
My own qPCR Ct table is at: <paste the path to your CSV file here>.
1. First check whether my table has any format problems (required columns: Target, Sample,
   Rep1, Rep2, Rep3; the reference gene row — default GAPDH — must be present and spelled
   correctly); if so, fix them and tell me what you did.
2. My reference gene is <GAPDH / write your own>, and my control group is <the group name as
   it appears in the Sample column>.
3. Once the data checks out, run the full ΔΔCt analysis with the output name <e.g., Figure2>,
   and show me the barplot for each target gene plus the result CSV.
4. Prefer the skill's own scripts in scripts/; if anything needs adapting, make the smallest
   possible change — do NOT write large amounts of new code.
```

Wait for the AI agent to finish: one 300 dpi barplot with statistics per target gene (t-test for 2 groups; ANOVA + Dunnett for ≥3 groups), plus a result CSV with ΔCt, Fold change, P values, and significance.

---

## Step 5 | Let the AI interpret the results

Paste this prompt:

```
Please explain the result CSV and the barplots in my output folder line by line:
1. What each column in the CSV means (raw Ct, ΔCt, ΔΔCt, Fold change, P value, significance);
2. For each target gene: how much it is up- or down-regulated relative to my control group,
   and whether the change is statistically significant;
3. Which statistical test was used for each gene, and why;
4. Any warnings or things I should pay attention to (e.g., high Ct replicate variation,
   reference-gene stability).
After explaining, tell me which figures can be used directly in a paper or presentation.
```

After reading the AI's explanation, if anything is unclear, just ask it directly.

---

## More analysis

This skill only does ΔΔCt relative-expression analysis for mRNA. The two skills below are related and installed in exactly the same way (one-click prompt or zip download from the website):

### qPCR mtDNA copy number — qpcr-mtdna

**One sentence: compute relative mitochondrial DNA copy number from four Ct values (ND1 / ND5 / B2M / POLG).** Automatically applies Mean copy number = (2^(B2M-ND1) + 2^(POLG-ND5)) / 2, with automatic statistics and a 300 dpi barplot.

Details & download: /skills/qpcr-mtdna

### Grouped barplot — barplot

**One sentence: any 2–6 group experimental data (ELISA, WB densitometry, cell counts…) → barplot with statistics in one shot.** Just give it a wide-format CSV; the statistical method is chosen automatically.

Details & download: /skills/barplot
