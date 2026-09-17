# REPORT — clinical-table smoke test (2026-09-16)

## What was produced

`clinical_tables.md` — two-cohort baseline characteristics table
(CRE n=67 vs CSE n=72), generated from the de-identified patient-level
example `examples/input/clinical_cohorts.csv` (139 rows × 22 columns).

## Command

```bash
python scripts/clinical_table.py examples/input/clinical_cohorts.csv examples/output/clinical_tables.md
```

## Expected anchors (all reproduced)

| Anchor | Value |
|---|---|
| Cohort sizes | CRE n=67, CSE n=72, Total n=139 |
| Age (years) | 69.16 ± 10.43 vs 63.18 ± 12.56, p = 0.003 |
| Urinary catheterization (Yes) | 54 (80.6) vs 18 (25.0), p < 0.001 |
| Hospital stay ≤7 days (CSE) | 58 (80.6) |
| Diabetes (Yes, CRE) | 61 (91.0) |

## Validation against the authors' revision appendix

Every cell of the 19 categorical + 2 continuous variables was reconciled
against the independent recalculation script shipped in the authors'
revision appendix (State B, 67v72 coding). All values matched, including
the two editorial corrections applied in that appendix (CSE age
63.18 ± 12.56; CSE hospital stay ≤7 days = 58).

Statistical conventions: Pearson chi-square WITHOUT continuity correction
(Fisher's exact when any expected cell < 5); Student's independent t-test
(pooled variance) for continuous variables.

## De-identification record

`examples/input/clinical_cohorts.csv` was produced by
`scripts/prepare_cohorts_example.py` (generic CLI; the two source patient
CSVs stay outside the repository):

- only 21 clinical columns + `cohort` retained;
- ALL identifier and genomic columns dropped (Assembly, Patient_ID,
  Barcode, Kleborate species/genes columns);
- 2 patients genomically re-identified as A. baumannii excluded
  (Patient_ID 4 and 62; cohort n: 69 → 67);
- binary columns normalized to clean "0"/"1" strings.

No direct patient identifiers exist in the example data or anywhere in
this skill directory; residual re-identification risk from the combination
of quasi-identifiers (age, weight, clinical history) is acknowledged and
the dataset is published for method demonstration only, not for secondary
analysis.
