# REPORT — full table suite (Tables 1–10) via the R pipeline (renamed rerun 2026-09-17; numbers originally validated 2026-09-16)

## What was produced

`Table-all_filled.md` — the complete table set (Tables 1–10) filled by
the 9-script R pipeline, plus `table9_sequencing_quality.csv` generated
by `make_table9_sequencing_quality.py`.
Ten tables in total; every numeric cell reconciled against the
verification anchors of the reproduction pack (its §9.2 table).

## Run order (scratch folder with the two pseudonymized CSVs + skeleton)

```
Rscript table1_baseline.R -> table2_firth.R -> table3_esbl_genes.R ...
table8_univariate.R -> table10_plasmid_replicons.R
python make_table9_sequencing_quality.py

Table numbering: Tables 1/2 = manuscript Table 1/2; Tables 3-10 =
manuscript Supplemental Tables S1-S8 (Table 9 = S7).
```

R note: the bundled scripts keep comments ASCII/English on purpose —
UTF-8 CJK comments crash Windows Rscript (GB  parser); if you re-add
comments, save UTF-8 without BOM or run `Rscript --encoding=utf-8`.

## Verified anchors (all reproduced)

| Table | Anchor |
|---|---|
| Table 1 | Sex χ²=1.116, P=0.2907; Age t=3.043, P=0.0028; 69.16 ± 10.43 / 63.18 ± 12.56 |
| Table 2 | Endotracheal intubation coef 2.578, OR 13.17 (2.08–158.92) |
| Table 3 | column sums 13/18/22/1/13, Total = 67 |
| Table 4 | 46 body rows; *C. freundii* ST116 present |
| Table 5 | column sums 13/18/22/1/13, Total = 67 |
| Table 6 | Diabetes: 9 (69.2) \| 18 (100.0) \| 20 (90.9) \| 1 (100.0) \| 13 (100.0) |
| Table 7 | Urinary catheterization: 9 (69.2) \| 16 (88.9) \| 16 (72.7) \| 1 (100.0) \| 12 (92.3) |
| Table 8 | Urinary catheterization χ²=42.965; Gastric tube χ²=30.121; 30 rows |
| Table 9 | 67 rows; depth 332–1540x (median 949x); N50 64.8–750.5 kb (median 191.2 kb) |
| Table 10 | IncX3: – \| 11/18 (61%) \| 11/22 (50%) \| 1/1 (100%) \| – \| 23/67 (34%); 47 rows |

## Verification evidence

- Anchor audit: the table above was checked line-by-line against the
  reproduction pack's §9.2 verification table in the maintainer's run
  (2026-09-16); the renaming to Tables 1–10 re-ran the whole pipeline
  on 2026-09-17 with all stopifnot guards passing and reproduced every
  anchor — the filled `Table-all_filled.md` and the 10 per-table CSVs
  in this folder ARE that renamed rerun's outputs (shipped as-is).
- Website rendering check: `website_check.png` — live screenshot of
  `zh/skills/clinical-table` with the Table 2 picker tab active
  (OR 13.17 (2.08–158.92) visible in the rendered PNG); re-captured
  2026-09-17 under the Table 1–10 renaming (new tab labels + PNGs).

## Data provenance & de-identification

- Inputs: `examples/input/pipeline/clinical_data_CRE_67_patients.csv` and
  `clinical_data_CSE_72_patients_clean.csv` — the pseudonymized frozen
  datasets of a CRE/CSE cohort study (manuscript under review).
- All patient-level fields are internal numeric pseudonyms (Patient_ID,
  Sample, Barcode are integers with no name/DOB/hospital-number linkage);
  Assembly IDs are public GSA deposit identifiers. The same information is
  disclosed by the study's own published supplemental tables (e.g. S7).
- No name, date-of-birth, or free-text identifier exists anywhere in the
  example data; the dataset is published for method demonstration only,
  not for secondary analysis.
- Dependencies: R with `logistf` (Table 2 Firth penalized regression);
  Python 3 stdlib for S7.
