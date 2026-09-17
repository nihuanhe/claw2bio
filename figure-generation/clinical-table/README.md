# clinical-table

Publication-ready clinical three-line tables. Two layers:

1. **Generic engine (Python)** — two-cohort (any two-group) baseline
   comparison: categorical n(%) with Pearson χ² (no continuity correction;
   Fisher's exact when any expected cell < 5), continuous mean±SD with
   Student's t-test. Also: OR (95% CI) summary, correlation matrix,
   univariable/multivariable Cox regression (when survival columns exist).
2. **Manuscript-grade full-table suite (R pipeline)** — 9 R scripts + 1
   Python script that reproduce ALL 10 tables (Tables 1–10 = manuscript
   Table 1/2 + Supplemental S1–S8) of a real CRE/CSE cohort
   study: baseline, Firth penalized
   logistic regression, resistance-gene / sequence-type / plasmid-replicon
   × carbapenemase-group cross tables, univariate analysis, sequencing
   quality table. Verbatim scripts from the authors' reproduction pack —
   every cell reconciled against the authors' independent recalculation.

Read [SKILL.md](SKILL.md) first.

## Layout

```
scripts/
  check_deps.py              # pre-run dependency check (generic engine)
  check_deps.R               # pre-run dependency check (R pipeline: logistf)
  clinical_table.py          # generic engine (Python)
  stats_utils.py             #   shared stats helpers
  prepare_cohorts_example.py #   builds the generic-engine example CSV
  pipeline/                  # manuscript suite (R + one Python)
    table1_baseline.R … table10_plasmid_replicons.R  # fill Table-all.md
    make_table9_sequencing_quality.py  # standalone: Table 9 (sequencing quality)
examples/
  input/clinical_cohorts.csv         # generic-engine example (139 rows × 22 cols)
  input/pipeline/                    # suite inputs: 2 frozen CSVs + Table-all.md skeleton
  output/clinical_tables.md          # generic-engine expected output
  output/pipeline/                   # suite expected outputs + REPORT.md (anchor audit)
```

## Layer 1 — generic engine quick start

```bash
cd figure-generation/clinical-table
python scripts/check_deps.py                        # step 1: verify deps (hints if missing)
pip install pandas numpy scipy statsmodels          # step 2 (online; or see "Offline install")
python scripts/clinical_table.py examples/input/clinical_cohorts.csv examples/output/clinical_tables.md
```

Expected anchors: `CRE n=67, CSE n=72`; Age `69.16±10.43 vs 63.18±12.56`,
p=0.003; Hospital stay >7 days `58 (86.6) vs 14 (19.4)`, p<0.001.

To use your own data: one row per patient with a two-level grouping column,
then edit `DEFAULT_CONFIG` (or pass `--config your.json`).

## Layer 2 — manuscript suite quick start

Inputs (all in `examples/input/pipeline/`, run scripts inside that folder):

- `clinical_data_CRE_67_patients.csv` — CRE cohort, 67 patients after QC
- `clinical_data_CSE_72_patients_clean.csv` — CSE cohort, 72 patients
- `Table-all.md` — 224-line skeleton with empty numeric cells

```bash
cd figure-generation/clinical-table/examples/input/pipeline
Rscript ../../scripts/check_deps.R                          # step 1: verify logistf (hints if missing)
Rscript ../../scripts/pipeline/table1_baseline.R            # baseline: χ²/Fisher + Student t   -> fills Table 1
Rscript ../../scripts/pipeline/table2_firth.R               # Firth penalized logistic (logistf) -> fills Table 2
Rscript ../../scripts/pipeline/table3_esbl_genes.R          # ESBL gene combinations             -> fills Table 3
Rscript ../../scripts/pipeline/table4_sequence_types.R      # species–ST combinations            -> fills Table 4
Rscript ../../scripts/pipeline/table5_sul_genes.R           # sul gene combinations              -> fills Table 5
Rscript ../../scripts/pipeline/table6_disease_genotype.R    # disease × genotype                 -> fills Table 6
Rscript ../../scripts/pipeline/table7_procedures_genotype.R # procedures/albumin/LOS × genotype  -> fills Table 7
Rscript ../../scripts/pipeline/table8_univariate.R          # univariate analysis                -> fills Table 8
Rscript ../../scripts/pipeline/table10_plasmid_replicons.R  # plasmid replicons                  -> fills Table 10
python ../../scripts/pipeline/make_table9_sequencing_quality.py  # Table 9 sequencing quality (standalone CSV)
```

Requires R. The offline bundle zips are R 4.5.x Windows binaries; any R
version works with the online install (`install.packages("logistf")`,
Table 2). Each R script
writes its own `tableN_subtitle.csv` next to the inputs and fills its
block of `Table-all.md`; the filled result matches
`examples/output/pipeline/Table-all_filled.md`. Table numbering:
Table 1/2 = manuscript Table 1/2; Tables 3–10 = manuscript Supplemental
Tables S1–S8 (Table 9 = S7).

Full anchor list and per-cell audit: [examples/output/pipeline/REPORT.md](examples/output/pipeline/REPORT.md).
Headline anchors: Table 1 Sex χ²=1.116 p=0.2907, Age t=3.043 p=0.0028;
Table 2 intubation OR 13.17 (2.08–158.92); Table 4 46 rows; Table 8
30 rows; Table 9 67 rows; Table 10 47 rows.

## Offline install (Windows, no internet)

Bundles live in `cos-staging/clinical-table/deps/` and on Tencent COS (public
read, same file names as the local `deps/` tree / `cos-staging/clinical-table/manifest.csv`):

- COS base URLs:
  - wheels: `https://my-website-1358159656.cos.ap-guangzhou.myqcloud.com/clinical-table/deps/python/`
  - R zips: `https://my-website-1358159656.cos.ap-guangzhou.myqcloud.com/clinical-table/deps/r-win/`
- Example direct link (numpy wheel):
  <https://my-website-1358159656.cos.ap-guangzhou.myqcloud.com/clinical-table/deps/python/numpy-2.5.3-cp313-cp313-win_amd64.whl>

- `deps/python/` — 14 wheels for the generic engine (Python 3.13,
  win_amd64: pandas / numpy / scipy / statsmodels + transitive deps).
  Other Python versions: use the online `pip install` command above instead.
- `deps/r-win/` — 56 binary zips = the full `logistf` dependency closure
  (R 4.5.x Windows; base/recommended packages that ship with R are not
  bundled).

Run from the repo root (the folder that contains `cos-staging/`); from
elsewhere use an absolute path to `deps/python`:

```bash
pip install --no-index --find-links cos-staging/clinical-table/deps/python pandas numpy scipy statsmodels
```

```r
zips <- list.files("<absolute path to>/cos-staging/clinical-table/deps/r-win", full.names = TRUE, pattern = "[.]zip$")
for (i in 1:20) {                    # deep chains need many passes (worst case ~11 on clean R 4.5.x)
  have <- rownames(installed.packages())
  todo <- zips[!sub("_.*$", "", basename(zips)) %in% have]
  if (!length(todo)) break
  try(install.packages(todo, repos = NULL, type = "win.binary"), silent = TRUE)
}
```

Then re-run the check scripts (both expect all-OK):
`python scripts/check_deps.py` and
`Rscript ../../scripts/check_deps.R`.

## Data provenance & de-identification

- **Suite inputs** are the study's **pseudonymized frozen datasets**,
  shipped verbatim (no column edits — the R scripts address columns by
  position). `Patient_ID`/`Sample`/`Barcode` are internal numeric
  pseudonyms (no names, birth dates, or hospital numbers); `Assembly`
  holds GSA public accession numbers. This matches what the study's
  published supplement already discloses; the manuscript is under
  revision.
- **R scripts** are copied verbatim from the authors' reproduction pack;
  the only change is a neutralized header comment (ASCII English — UTF-8
  Chinese comments crash Windows `Rscript` via GBK mis-parsing).
- **Generic-engine example** (`examples/input/clinical_cohorts.csv`) is
  derived from the same study by `scripts/prepare_cohorts_example.py`,
  keeping only the 21 clinical columns + `cohort` label and dropping all
  identifiers — de-identification by construction.

## Troubleshooting

See the table in [SKILL.md](SKILL.md) (χ² vs SPSS, GBK crash, logistf,
float keys, Cox prerequisites, skeleton repair).
