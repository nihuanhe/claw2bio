# Pipeline inputs — reproduce the full manuscript table suite

Contents:

- `clinical_data_CRE_67_patients.csv` — pseudonymized frozen dataset,
  CRE arm (815 cols: clinical + WGS features; 71 raw rows, the pipeline
  filters to the 67-isolate analysis set by dropping the 2 empty-species
  rows and the 2 A. baumannii re-identified isolates)
- `clinical_data_CSE_72_patients_clean.csv` — pseudonymized frozen dataset,
  CSE arm (23 cols, 72 rows)
- `Table-all.md` — the empty skeleton the R scripts fill (224 lines)

Patient identifiers are internal numeric pseudonyms; Assembly IDs are
public GSA deposit identifiers (same as the study's published supplement).

Gotcha when adapting by column NAME: the CRE CSV header contains a
full-width closing paren in `Gender(M=0,F=1）` and other mixed-width
characters; the R scripts therefore address columns by POSITION
(`d[,4:25]` / `d[,2:23]`) and rename them. Keep your columns in the same
order instead of renaming headers.

## Run (from this folder)

```bash
Rscript ../../scripts/pipeline/table1_baseline.R
Rscript ../../scripts/pipeline/table2_firth.R     # needs the R package "logistf"
Rscript ../../scripts/pipeline/table3_esbl_genes.R
Rscript ../../scripts/pipeline/table4_sequence_types.R
Rscript ../../scripts/pipeline/table5_sul_genes.R
Rscript ../../scripts/pipeline/table6_disease_genotype.R
Rscript ../../scripts/pipeline/table7_procedures_genotype.R
Rscript ../../scripts/pipeline/table8_univariate.R
Rscript ../../scripts/pipeline/table10_plasmid_replicons.R
python ../../scripts/pipeline/make_table9_sequencing_quality.py
```

Each script fills its block of `Table-all.md` (in this folder) and writes
a standalone CSV. Table numbering: Table 1/2 = manuscript Table 1/2;
Tables 3–10 = manuscript Supplemental Tables S1–S8 (Table 9 = S7).
Expected anchors: see
`examples/output/pipeline/REPORT.md`, where the maintainer's verified run
ships as `examples/output/pipeline/Table-all_filled.md`.

To re-run from scratch: restore `Table-all.md` from this folder (the R
pipeline overwrites the copy in the run folder — keep inputs pristine by
copying them to a scratch directory first).
