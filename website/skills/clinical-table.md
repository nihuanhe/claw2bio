# Zero-Basics — Clinical Statistics Tables with an AI Agent (clinical-table) | Copy & Paste All the Way

This tutorial uses workbuddy as the AI agent and Hy3 as the AI API. For installing and configuring the AI agent itself, see the [AI Agent setup tutorial](/skills/ai-agent-setup).

**Before you start (must read):**

- **If this is your first time doing data analysis with an AI agent, we strongly recommend following the [bulk-RNA-seq differential analysis tutorial](/skills/bulk-RNA-seq) first**, to learn the full "install skill → set up environment → run example → switch to your own data" workflow, then come back to this skill.
- This skill is **standalone** — it does not depend on the output of any other skill. Give it a patient-level CSV and it runs.
- In one sentence: **patient-level CSV in, a paper-style Table 1 baseline-characteristics table out** — n (%) + χ² for categorical variables (automatic Fisher when expected counts <5) + mean±SD + Student t for continuous ones; correlation matrix, Cox regression, and OR summaries are also supported. Output is Markdown three-line tables, convertible to DOCX with Pandoc in one command.
- This skill has **two modes**: this tutorial's main line covers the **general engine** (Python, works out of the box); the "Advanced" section at the end introduces the **manuscript-grade R pipeline** (9 R scripts + 1 Python script that reproduce a paper's full Table 1–10 from patient-level CSVs).
- **Note**: this skill's χ² does **NOT** apply the Yates continuity correction (the publication convention for Table 1), so p values may differ slightly from SPSS — this is a feature, not a bug.

**Tutorial structure:**

- **Step 1** | Install the clinical-table skill (one time only)
- **Step 2** | Set up the runtime environment (one time only)
- **Step 3** | Run the bundled example data (general engine)
- **Step 4** | Switch to your own data
- **Step 5** | Let the AI interpret the results
- **Advanced** | The manuscript-grade R pipeline
- **More analysis** | Related skills (survival curve / grouped barplot)

---

## Step 1 | Install the clinical-table skill

Paste this prompt:

```
Please install the "clinical-table" skill for me, into the D:\claw2bio folder:
1. Create a folder named claw2bio in the root of the D: drive (if it doesn't exist yet).
2. From the GitHub repository https://github.com/nihuanhe/claw2bio, fetch ONLY the folder
   figure-generation/clinical-table (use sparse checkout — do NOT clone the whole repository),
   and place it at D:\claw2bio\clinical-table.
3. If downloading from GitHub fails or is too slow, download the zip from this mirror link instead:
   https://claw2bio.site/downloads/clinical-table.zip
   and extract it to D:\claw2bio\clinical-table.
4. Read the SKILL.md inside, then confirm to me that the skill is ready and list the contents
   of the folder.
(If my PC has no D: drive, install to C:\claw2bio instead and tell me the actual path.)
```

When Step 1 finishes, open the file manager and confirm that `D:\claw2bio\clinical-table` exists, with `scripts/`, `examples/`, `SKILL.md`, etc. inside.

---

## Step 2 | Set up the runtime environment

The general engine only needs Python (the advanced R pipeline additionally needs R + the logistf package). Paste this prompt:

```
Please set up the runtime environment for the "clinical-table" skill at
D:\claw2bio\clinical-table:
1. First, SEARCH THIS PC for an existing Python installation. If Python is already installed,
   report its version to me. Only if Python is NOT installed at all, install a recent Python 3
   (Windows), downloaded from the official python.org website, accepting all default options —
   and make sure to check "Add python.exe to PATH" during installation.
2. Install all Python packages this skill needs: pandas, numpy, scipy, statsmodels
   (use pip; if a package fails or is too slow, stop and tell me about it).
3. The general engine is Python-only. The advanced R pipeline additionally needs R with the
   logistf package — check whether R is installed; if yes, also install logistf; if no,
   just tell me that the R pipeline won't be available (I can still use the general engine).
4. When everything is installed, confirm to me what is ready.
```

---

## Step 3 | Run the bundled example data (general engine)

Paste this prompt:

```
The skill is installed at D:\claw2bio\clinical-table. Please run the bundled example with the
GENERAL ENGINE:
1. Example input is at D:\claw2bio\clinical-table\examples\input\clinical_cohorts.csv
2. Run: python scripts/clinical_table.py examples/input/clinical_cohorts.csv
   examples/output/clinical_tables.md
3. Prefer the skill's own scripts in scripts/ — do NOT write new analysis code from scratch.
4. When the run succeeds, show me the generated clinical_tables.md and explain it table by
   table.
```

**Anchor results** for a successful run: CRE n=67, CSE n=72; Age 69.16±10.43 vs 63.18±12.56, p=0.003. If your results match, the environment is working. The skill webpage shows the full 10-table suite produced by the R pipeline on real cohort data (Table 1 baseline shown below; replace with your own screenshots later):

![Table 1 baseline example](/skills/clinical-table/table1_baseline.png)

**Converting three-line tables to Word**: Markdown tables convert to DOCX with Pandoc in one command — ask the AI to run `pandoc output.md -o output.docx` (if Pandoc is not installed, ask the AI to install it).

---

## Step 4 | Switch to your own data

Prepare a **patient-level CSV** (one row per patient): a two-level grouping column (default name `cohort`) + several 0/1 binary columns + several continuous columns. Paste this prompt:

```
My own patient-level CSV is at: <paste the path to your CSV file here>.
My grouping column is <cohort / your column name> with the two groups <group A> and <group B>.
1. First check my table: one row per patient; a two-level grouping column; 0/1 binary columns
   for categorical variables; numeric columns for continuous variables. If anything is wrong,
   fix it and tell me what you did.
2. The variable list is configured in DEFAULT_CONFIG or via --config your.json — list the
   variables you detected in my data, ask me which ones to include in the baseline table,
   and put the continuous variables into baseline_continuous_vars.
3. If my data has survival_time and survival_event columns, tell me — the skill will then
   also generate a Cox table.
4. Run the general engine with the skill's own script — do NOT write new analysis code from
   scratch. Show me the resulting clinical_tables.md and convert it to DOCX with Pandoc.
```

Wait for the AI agent to finish: a Markdown three-line table suite (baseline / correlation / Cox / OR) + optional DOCX.

---

## Step 5 | Let the AI interpret the results

Paste this prompt:

```
Please explain the tables in my clinical_tables.md line by line:
1. For each variable: which statistical test was used (χ², Fisher exact, or Student t) and
   why — remind me that χ² here does NOT use the Yates continuity correction, so p values
   may differ slightly from SPSS, which is the Table 1 publication convention;
2. Which baseline variables differ significantly between my two cohorts, and what that means
   for interpreting downstream comparisons (potential confounders);
3. If a Cox or OR table was generated: walk me through the effect sizes and confidence
   intervals;
4. Any warnings or things I should pay attention to.
After explaining, tell me how to cite/report these tables in a manuscript.
```

After reading the AI's explanation, if anything is unclear, just ask it directly.

---

## Advanced | The manuscript-grade R pipeline

If you need to reproduce a full manuscript table suite (baseline, Firth penalized logistic regression, gene/sequence-type cross-tables, univariate analysis… 10 tables in total), the skill ships 9 R scripts + 1 Python script under `scripts/pipeline/` that fill a `Table-all.md` skeleton in order. Paste this prompt:

```
I want to use the ADVANCED R pipeline of the clinical-table skill at D:\claw2bio\clinical-table
to reproduce a full manuscript table suite:
1. Look at examples/input/pipeline/ — two patient-level CSVs plus the Table-all.md skeleton
   live there. First run the pipeline on the EXAMPLE data: run the scripts in scripts/pipeline/
   in order (table1_baseline.R, table2_firth.R, table3_esbl_genes.R, and so on; Table 9 is
   generated by the Python script make_table9_sequencing_quality.py). Each script reads the
   CSVs, computes, fills its section of Table-all.md, and writes a standalone CSV.
2. Use the skill's own scripts unchanged — do NOT write new analysis code from scratch.
   IMPORTANT on Windows: use the English-comment script versions as shipped in the repo;
   if any script is edited, save it as UTF-8 WITHOUT BOM, or R may crash.
3. Verify the run against the anchors in examples/output/pipeline/REPORT.md.
4. After the example works, ask me for my own two-cohort CSVs (prepared with the same column
   structure) and repeat the pipeline on them.
```

The skill webpage shows the real 10-table output (Tables 1–10; every number cross-checked cell-by-cell against the authors' independent review scripts) for reference: /skills/clinical-table

---

## More analysis

The two skills below are related and installed in exactly the same way (one-click prompt or zip download):

### Survival curve — survival-curve

**One sentence: a follow-up table in, KM survival curves + risk table + Cox forest plot out.** If your patient data includes follow-up time and outcome events, a KM curve usually goes alongside the baseline table.

Details & download: /skills/survival-curve

### Grouped barplot — barplot

**One sentence: any 2–6 group experimental data → barplot with statistics in one shot.** For experimental data beyond the clinic (ELISA, WB densitometry…), use this one.

Details & download: /skills/barplot
