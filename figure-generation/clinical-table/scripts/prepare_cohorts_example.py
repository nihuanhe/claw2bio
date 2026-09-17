# prepare_cohorts_example.py — build the DE-IDENTIFIED two-cohort clinical
# example dataset for the clinical-table skill.
#
# Generic CLI (no private paths hardcoded):
#   python scripts/prepare_cohorts_example.py --cre <cre.csv> --cse <cse.csv> \
#       --out examples/input/clinical_cohorts.csv
#
# What it does:
#   1. keeps ONLY the clinical columns (drops Assembly / Patient_ID / Barcode /
#      all genomic & Kleborate columns) — de-identification by construction;
#   2. excludes the two genomically re-identified A. baumannii patients
#      (Patient_ID 4 and 62) from the CRE cohort -> n = 67;
#   3. standardizes column names (the source files mix full/half-width parens);
#   4. adds the `cohort` column (CRE / CSE) and stacks both cohorts.
import argparse
import sys

import pandas as pd

# canonical name -> candidate source columns (CRE uses full-width parens for Gender)
CLINICAL_COLS = {
    "Gender": ["Gender(M=0,F=1）", "Gender(M=0,F=1)"],
    "Age_years": ["Age (years)"],
    "Weight_kg": ["Weight (kg)"],
    "Smoking": ["Smoking(NO=0,YES=1)"],
    "Surgery": ["Surgery(NO=0,YES=1)"],
    "Urinary_catheterization": ["Urinary catheterization(NO=0,YES=1)"],
    "Endotracheal_intubation": ["Endotracheal intubation"],
    "Puncture_drainage": ["Puncture drainage"],
    "Tracheotomy": ["Tracheotomy"],
    "Hemodialysis": ["Hemodialysis"],
    "Gastric_tube": ["Gastric tube"],
    "Diabetes": ["Diabetes"],
    "Hypertension": ["Hypertension"],
    "Coronary_artery_disease": ["Coronary artery disease"],
    "Cerebrovascular_disease": ["Cerebrovascular disease"],
    "Renal_insufficiency": ["Renal insufficiency"],
    "Pulmonary_disease": ["Pulmonary disease"],
    "Antibiotic_multiple_therapy": ["Antibiotic usage(Multiple therapy=1)"],
    "Prealbumin_gt280": ["Prealbumin level(>280 mg/L)"],
    "Albumin_gt35": ["Albumin level(>35 g/L)"],
    "Hospital_stay_gt7d": ["Hospital length of stay"],
}
EXCLUDE_PIDS = {4.0, 62.0}  # A. baumannii re-identified patients (CRE side)


def load(path: str, cohort: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    out = pd.DataFrame()
    for canon, candidates in CLINICAL_COLS.items():
        hit = next((c for c in candidates if c in df.columns), None)
        if hit is None:
            sys.exit(f"ERROR: column for {canon} not found in {path} (tried {candidates})")
        out[canon] = df[hit]
    if cohort == "CRE":
        keep_cols = [c for c in ("Assembly", "Patient_ID") if c in df.columns]
        if not keep_cols:
            sys.exit("ERROR: CRE file needs Assembly/Patient_ID for row validity + exclusion")
        asm = df["Assembly"].astype(str).str.strip()
        valid = df["Assembly"].notna() & asm.ne("") & asm.str.lower().ne("nan")
        out = out[valid]
        # Patient_ID may parse as float when empty rows exist -> compare numerically
        pids = pd.to_numeric(df.loc[valid, "Patient_ID"], errors="coerce")
        out = out[~pids.isin(EXCLUDE_PIDS).values]
    out["cohort"] = cohort
    return out.reset_index(drop=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cre", required=True)
    ap.add_argument("--cse", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    cre = load(a.cre, "CRE")
    cse = load(a.cse, "CSE")
    df = pd.concat([cre, cse], ignore_index=True)
    # binary clinical columns as clean "0"/"1" strings (float NaN upstream
    # would otherwise render as 0.0/1.0); continuous stay numeric
    for col in df.columns:
        if col in ("Age_years", "Weight_kg", "cohort"):
            continue
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64").astype(str)
    df.to_csv(a.out, index=False, encoding="utf-8")
    print(f"ANCHOR: CRE n={len(cre)} (expect 67) | CSE n={len(cse)} (expect 72) | total={len(df)}")
    print(f"ANCHOR: columns={len(df.columns)} (21 clinical + cohort)")
    print(f"written: {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
