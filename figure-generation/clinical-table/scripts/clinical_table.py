"""
Clinical statistical table generator.

Reads a patient-level CSV and produces publication-ready Markdown tables:
1. Two-cohort baseline characteristics (categorical chi-square/Fisher +
   continuous mean±SD / Student's t; legacy marker high/low layout supported)
2. Correlation matrix (Pearson + Spearman) for continuous variables
3. Univariable / multivariable Cox regression tables (if survival columns present)
4. Odds ratio summary for Fisher's exact 2x2 tests

Output is Markdown formatted as a three-line table suitable for Pandoc → DOCX.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from stats_utils import (
    AssocResult,
    build_baseline_table,
    build_correlation_table,
    build_cox_tables,
    fmt_pvalue,
    render_baseline_markdown,
    render_correlation_markdown,
    render_cox_markdown,
    render_or_markdown,
    stars,
    test_association,
)


# ---------------------------------------------------------------------------
# Default configuration: two-cohort baseline comparison (CRE vs CSE example)
# Variable coding follows the de-identified examples/input/clinical_cohorts.csv
# produced by scripts/prepare_cohorts_example.py.
# ---------------------------------------------------------------------------

_BINARY_YES_NO = {"0": "No", "1": "Yes"}

DEFAULT_CONFIG: Dict = {
    "group_cols": ["cohort"],
    "group_labels": {"cohort": "Cohort"},
    "clinical_vars": [
        "Gender", "Smoking", "Surgery", "Urinary_catheterization",
        "Endotracheal_intubation", "Puncture_drainage", "Tracheotomy",
        "Hemodialysis", "Gastric_tube", "Diabetes", "Hypertension",
        "Coronary_artery_disease", "Cerebrovascular_disease",
        "Renal_insufficiency", "Pulmonary_disease",
        "Antibiotic_multiple_therapy", "Albumin_gt35", "Prealbumin_gt280",
        "Hospital_stay_gt7d",
    ],
    "var_labels": {
        "cohort": "Cohort (CRE vs CSE)",
        "Gender": "Gender (male)",
        "Smoking": "Smoking",
        "Surgery": "Surgery",
        "Urinary_catheterization": "Urinary catheterization",
        "Endotracheal_intubation": "Endotracheal intubation",
        "Puncture_drainage": "Puncture drainage",
        "Tracheotomy": "Tracheotomy",
        "Hemodialysis": "Hemodialysis",
        "Gastric_tube": "Gastric tube",
        "Diabetes": "Diabetes",
        "Hypertension": "Hypertension",
        "Coronary_artery_disease": "Coronary artery disease",
        "Cerebrovascular_disease": "Cerebrovascular disease",
        "Renal_insufficiency": "Renal insufficiency",
        "Pulmonary_disease": "Pulmonary disease",
        "Antibiotic_multiple_therapy": "Antibiotic multiple therapy",
        "Albumin_gt35": "Albumin ≤35 g/L",
        "Prealbumin_gt280": "Prealbumin ≤280 mg/L",
        "Hospital_stay_gt7d": "Hospital stay >7 days",
    },
    "level_maps": {
        "Gender": {"0": "Male", "1": "Female"},
        "Smoking": _BINARY_YES_NO,
        "Surgery": _BINARY_YES_NO,
        "Urinary_catheterization": _BINARY_YES_NO,
        "Endotracheal_intubation": _BINARY_YES_NO,
        "Puncture_drainage": _BINARY_YES_NO,
        "Tracheotomy": _BINARY_YES_NO,
        "Hemodialysis": _BINARY_YES_NO,
        "Gastric_tube": _BINARY_YES_NO,
        "Diabetes": _BINARY_YES_NO,
        "Hypertension": _BINARY_YES_NO,
        "Coronary_artery_disease": _BINARY_YES_NO,
        "Cerebrovascular_disease": _BINARY_YES_NO,
        "Renal_insufficiency": _BINARY_YES_NO,
        "Pulmonary_disease": _BINARY_YES_NO,
        "Antibiotic_multiple_therapy": _BINARY_YES_NO,
        # exposure = LOW level (code 0), per the source-study Table-1 coding
        "Albumin_gt35": {"0": "≤35 g/L", "1": ">35 g/L"},
        "Prealbumin_gt280": {"0": "≤280 mg/L", "1": ">280 mg/L"},
        "Hospital_stay_gt7d": {"0": "≤7 days", "1": ">7 days"},
    },
    "baseline_continuous_vars": ["Age_years", "Weight_kg"],
    "baseline_continuous_labels": {
        "Age_years": "Age (years)",
        "Weight_kg": "Weight (kg)",
    },
    "continuous_vars": [],          # correlation matrix: none in this example
    "continuous_labels": {},
    "survival": {},                 # no survival columns in this example
}


# ---------------------------------------------------------------------------
# Data preprocessing helpers
# ---------------------------------------------------------------------------

def clean_prospective_df(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the prospective cohort CSV into analysis-ready format."""
    df = df.copy()
    # Drop trailing unnamed columns
    unnamed = [c for c in df.columns if str(c).startswith("Unnamed:")]
    df = df.drop(columns=unnamed)

    # Standardize column names
    rename_map = {}
    for c in df.columns:
        s = str(c).strip()
        if s == "Age":
            rename_map[c] = "Age_cat"
        elif s == "Age-":
            rename_map[c] = "Age_num"
        elif s == "BMI-":
            rename_map[c] = "BMI_num"
        elif s == "BMI":
            rename_map[c] = "BMI_cat"
        elif s in ("Sex",):
            rename_map[c] = "Sex"
        elif "Tumor differentiation" in s:
            rename_map[c] = "Tumor differentiation"
        elif s == "Cancer stage":
            rename_map[c] = "Cancer_stage_cat"
        elif s == "Cancer stage--":
            rename_map[c] = "Cancer_stage_raw"
        elif s in ("HAMA",):
            rename_map[c] = "HAMA"
        elif s in ("FOXP3",):
            rename_map[c] = "FOXP3"
        elif s in ("NOXA",):
            rename_map[c] = "NOXA"
        elif s in ("HAMA--",):
            rename_map[c] = "HAMA--"
        elif s in ("FOXP3--",):
            rename_map[c] = "FOXP3--"
        elif s in ("NOXA--",):
            rename_map[c] = "NOXA--"
    df = df.rename(columns=rename_map)

    # Normalize categorical labels
    if "Age_cat" in df.columns:
        df["Age_cat"] = (
            df["Age_cat"]
            .astype(str)
            .str.replace("＜", "<", regex=False)
            .str.replace("≥", ">=", regex=False)
            .str.strip()
        )
        df["Age_cat"] = df["Age_cat"].replace(
            {
                ">=60 years": "≥60 years",
                "<60 years": "< 60 years",
                ">=60": "≥60 years",
                "<60": "< 60 years",
            }
        )
    if "BMI_cat" in df.columns:
        df["BMI_cat"] = (
            df["BMI_cat"]
            .astype(str)
            .str.replace("＜", "<", regex=False)
            .str.replace("≥", ">=", regex=False)
            .str.strip()
        )
        df["BMI_cat"] = df["BMI_cat"].replace(
            {
                ">=24": "≥24",
                "<24": "< 24",
            }
        )
    if "Sex" in df.columns:
        df["Sex"] = df["Sex"].astype(str).str.strip()
    if "Tumor differentiation" in df.columns:
        df["Tumor differentiation"] = (
            df["Tumor differentiation"].astype(str).str.strip()
        )
    if "Cancer_stage_cat" in df.columns:
        df["Cancer_stage_cat"] = df["Cancer_stage_cat"].astype(str).str.strip()

    # Convert continuous vars to numeric
    for col in ["HAMA", "FOXP3", "NOXA"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def auto_group_by_median(
    df: pd.DataFrame, col: str, labels: Optional[List[str]] = None
) -> pd.Series:
    """Create high/low group based on median split."""
    labels = labels or ["low", "high"]
    median = df[col].median()
    return pd.cut(df[col], bins=[-float("inf"), median, float("inf")], labels=labels)


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def collect_or_rows(
    df: pd.DataFrame,
    group_cols: List[str],
    clinical_vars: List[str],
    group_labels: Dict[str, str],
    var_labels: Dict[str, str],
) -> List[Dict]:
    """Collect OR rows for all 2x2 Fisher tables."""
    or_rows = []
    for grp in group_cols:
        if grp not in df.columns:
            continue
        sub = df.dropna(subset=[grp])
        for var in clinical_vars:
            if var not in sub.columns:
                continue
            res = test_association(sub[grp], sub[var])
            if res.method == "Fisher's exact test" and res.or_val is not None:
                # Get level labels from first level of the clinical var
                level = str(sorted(sub[var].dropna().unique())[0])
                or_rows.append(
                    {
                        "group": group_labels.get(grp, grp),
                        "variable": var_labels.get(var, var),
                        "level": level,
                        "or": res.or_val,
                        "ci": res.ci,
                        "pvalue": res.pvalue,
                    }
                )
    return or_rows


def run_pipeline(
    input_csv: Path,
    output_md: Path,
    config: Dict,
    auto_group: bool = False,
    group_cutoffs: Optional[Dict[str, float]] = None,
) -> None:
    """Run the full clinical table pipeline."""
    df = pd.read_csv(input_csv, dtype=str)  # keep 0/1 codings as strings
    # legacy HAMA-style cleaning only applies to the old prospective-cohort layout
    if "cohort" not in df.columns:
        df = clean_prospective_df(df)

    group_cols = config["group_cols"]
    group_labels = config.get("group_labels", {})
    clinical_vars = config["clinical_vars"]
    var_labels = config.get("var_labels", {})
    level_maps = config.get("level_maps", {})
    continuous_vars = config.get("continuous_vars", [])
    continuous_labels = config.get("continuous_labels", {})

    # Handle auto-grouping if requested
    if auto_group:
        group_cutoffs = group_cutoffs or {}
        for col in group_cols:
            base = col.replace("--", "")
            if base in df.columns:
                if base in group_cutoffs:
                    cutoff = group_cutoffs[base]
                    df[col] = (
                        df[base].apply(lambda x: "high" if x >= cutoff else "low")
                        .astype(str)
                    )
                else:
                    df[col] = auto_group_by_median(df, base, labels=["low", "high"]).astype(str)

    # Ensure group columns are strings
    for col in group_cols:
        if col in df.columns:
            df[col] = df[col].astype(str)

    # Baseline tables (categorical + optional continuous mean±SD / t-test)
    baseline_tables = build_baseline_table(
        df,
        group_cols=group_cols,
        clinical_vars=clinical_vars,
        var_labels=var_labels,
        level_maps=level_maps,
        continuous_vars=config.get("baseline_continuous_vars", []),
        continuous_labels=config.get("baseline_continuous_labels", {}),
    )
    baseline_md = render_baseline_markdown(baseline_tables)

    # OR summary
    or_rows = collect_or_rows(
        df, group_cols, clinical_vars, group_labels, var_labels
    )
    or_md = render_or_markdown(or_rows)

    # Correlation matrix
    corr_results = build_correlation_table(
        df,
        continuous_vars=[c for c in continuous_vars if c in df.columns],
        var_labels=continuous_labels,
    )
    corr_md = render_correlation_markdown(corr_results)

    # Cox regression (only if survival columns exist)
    surv = config.get("survival", {})
    time_col = surv.get("time_col")
    event_col = surv.get("event_col")
    cox_md = ""
    if time_col in df.columns and event_col in df.columns:
        uni, multi, cox_footer = build_cox_tables(
            df,
            time_col=time_col,
            event_col=event_col,
            candidate_predictors=[
                c for c in surv.get("candidate_predictors", []) if c in df.columns
            ],
            multivar_predictors=[
                c for c in surv.get("multivar_predictors", []) if c in df.columns
            ],
            alpha=surv.get("alpha", 0.10),
        )
        cox_md = render_cox_markdown(uni, multi, cox_footer)

    # Assemble final Markdown document
    out = []
    out.append("# Clinical statistical tables")
    out.append("")
    out.append(
        "*Generated by clinical-table. "
        "Categorical variables: Pearson chi-square without continuity correction "
        "(Fisher's exact test when any expected cell < 5). "
        "Continuous variables: Student's independent t-test. "
        "Significance: * p<0.05, ** p<0.01, *** p<0.001.*"
    )
    out.append("")
    out.append("## Baseline characteristics")
    out.append("")
    out.append(baseline_md)
    if or_md:
        out.append(or_md)
    if corr_md:
        out.append("## Correlation analysis")
        out.append("")
        out.append(corr_md)
    if cox_md:
        out.append("## Survival analysis")
        out.append("")
        out.append(cox_md)

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote {output_md}")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate clinical statistical tables in Markdown."
    )
    parser.add_argument("input_csv", type=Path, help="Input patient-level CSV")
    parser.add_argument("output_md", type=Path, help="Output Markdown file")
    parser.add_argument(
        "--config",
        type=Path,
        help="JSON config file overriding defaults",
    )
    parser.add_argument(
        "--auto-group",
        action="store_true",
        help="Automatically create high/low groups by median split if --group-col labels are missing",
    )
    parser.add_argument(
        "--group-cutoffs",
        type=str,
        help='JSON dict of cutoff values for auto-grouping, e.g. {"Marker":29}',
    )
    args = parser.parse_args(argv)

    config = DEFAULT_CONFIG.copy()
    if args.config:
        with open(args.config, "r", encoding="utf-8") as fh:
            override = json.load(fh)
            config.update(override)

    group_cutoffs = None
    if args.group_cutoffs:
        group_cutoffs = json.loads(args.group_cutoffs)

    run_pipeline(
        args.input_csv,
        args.output_md,
        config,
        auto_group=args.auto_group,
        group_cutoffs=group_cutoffs,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
