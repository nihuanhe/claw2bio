"""
Clinical table statistics utilities.

Implements:
- Baseline characteristic tables with automatic Fisher's exact / chi-square test selection
- Odds ratio (OR) and 95% CI for 2x2 tables
- Spearman and Pearson correlation matrices
- Univariable and multivariable Cox proportional hazards regression via statsmodels PHReg
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact, pearsonr, spearmanr
from statsmodels.duration.hazard_regression import PHReg


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def fmt_pvalue(p: float) -> str:
    """Format p-value for tables."""
    if pd.isna(p):
        return "NA"
    if p < 0.001:
        return "<0.001"
    return f"{p:.3f}"


def stars(p: float) -> str:
    """Return significance stars."""
    if pd.isna(p):
        return ""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return ""


def fmt_pct(n: int, total: int) -> str:
    """Format n (%) with one decimal."""
    if total == 0:
        return f"{n} (0.0)"
    return f"{n} ({100 * n / total:.1f})"


def fmt_or(a: int, b: int, c: int, d: int) -> Tuple[str, str]:
    """
    Compute sample odds ratio and Woolf 95% CI for a 2x2 table:
        a  b
        c  d
    Returns (or_str, ci_str).
    """
    if b == 0 or c == 0 or a == 0 or d == 0:
        # Add 0.5 continuity correction
        a_, b_, c_, d_ = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    else:
        a_, b_, c_, d_ = a, b, c, d
    or_val = (a_ * d_) / (b_ * c_)
    log_or = np.log(or_val)
    se_log_or = np.sqrt(1 / a_ + 1 / b_ + 1 / c_ + 1 / d_)
    ci_low = np.exp(log_or - 1.96 * se_log_or)
    ci_high = np.exp(log_or + 1.96 * se_log_or)
    return f"{or_val:.2f}", f"{ci_low:.2f}–{ci_high:.2f}"


# ---------------------------------------------------------------------------
# Categorical association tests
# ---------------------------------------------------------------------------

@dataclass
class AssocResult:
    method: str
    pvalue: float
    or_val: Optional[str] = None
    ci: Optional[str] = None


def test_association(group: pd.Series, var: pd.Series) -> AssocResult:
    """
    Run chi-square test or Fisher's exact test on two categorical variables.
    Returns method, p-value, and OR with 95% CI for 2x2 tables when Fisher is used.
    """
    df = pd.crosstab(group, var)
    # Drop all-NA rows/cols
    df = df.loc[(df.sum(axis=1) > 0), (df.sum(axis=0) > 0)]
    if df.shape != (2, 2):
        chi2, p, dof, expected = chi2_contingency(df)
        return AssocResult(method="Chi-square test", pvalue=p)
    # 2x2 table: decide Fisher vs chi-square
    expected = chi2_contingency(df)[3]
    use_fisher = (expected < 5).any()
    if use_fisher:
        a, b = df.iloc[0, 0], df.iloc[0, 1]
        c, d = df.iloc[1, 0], df.iloc[1, 1]
        or_val, ci = fmt_or(a, b, c, d)
        _, p = fisher_exact(df)
        return AssocResult(method="Fisher's exact test", pvalue=p, or_val=or_val, ci=ci)
    chi2, p, _, _ = chi2_contingency(df)
    return AssocResult(method="Chi-square test", pvalue=p)


# ---------------------------------------------------------------------------
# Baseline table
# ---------------------------------------------------------------------------

@dataclass
class BaselineRow:
    variable: str
    level: str
    is_header: bool = False
    counts: Dict[str, str] = None
    pvalue: str = ""
    stars: str = ""
    method: str = ""


def build_baseline_table(
    df: pd.DataFrame,
    group_cols: Sequence[str],
    clinical_vars: Sequence[str],
    var_labels: Optional[Dict[str, str]] = None,
    level_maps: Optional[Dict[str, Dict[str, str]]] = None,
) -> List[Tuple[str, List[BaselineRow], str, str]]:
    """
    Build baseline characteristic table for each grouping variable.

    Returns a list of tuples:
        (group_label, rows, overall_n, footer_note)
    """
    var_labels = var_labels or {}
    level_maps = level_maps or {}
    tables = []

    for grp in group_cols:
        if grp not in df.columns:
            continue
        sub = df.dropna(subset=[grp])
        groups = sorted(sub[grp].dropna().unique().tolist())
        if len(groups) != 2:
            continue
        n_total = len(sub)
        n_g1 = (sub[grp] == groups[0]).sum()
        n_g2 = (sub[grp] == groups[1]).sum()
        header = f"{var_labels.get(grp, grp)} high/low"
        rows = []
        footer_methods = set()

        for var in clinical_vars:
            if var not in sub.columns:
                continue
            label = var_labels.get(var, var)
            rows.append(BaselineRow(variable=label, level="", is_header=True))
            levels = sorted(sub[var].dropna().unique().tolist())
            res = test_association(sub[grp], sub[var])
            footer_methods.add(res.method)
            p_str = fmt_pvalue(res.pvalue)
            s_str = stars(res.pvalue)

            for lvl in levels:
                lvl_label = level_maps.get(var, {}).get(str(lvl), str(lvl))
                counts = {}
                for g, n_g in [(groups[0], n_g1), (groups[1], n_g2)]:
                    cnt = ((sub[grp] == g) & (sub[var] == lvl)).sum()
                    counts[str(g)] = fmt_pct(int(cnt), int(n_g))
                counts["Total"] = fmt_pct(int((sub[var] == lvl).sum()), int(n_total))
                rows.append(
                    BaselineRow(
                        variable="",
                        level=lvl_label,
                        counts=counts,
                        pvalue=p_str if lvl == levels[0] else "",
                        stars=s_str if lvl == levels[0] else "",
                        method=res.method if lvl == levels[0] else "",
                    )
                )

        footer = (
            f"Group sizes: {groups[0]} n={n_g1}, {groups[1]} n={n_g2}; "
            f"Total n={n_total}. "
            f"Methods used: {', '.join(sorted(footer_methods))}. "
            "Fisher's exact test applied when any expected cell count < 5; otherwise chi-square test. "
            "OR (95% CI) reported separately for 2x2 tables analyzed by Fisher's exact test."
        )
        tables.append((header, rows, f"n={n_total}", footer))
    return tables


# ---------------------------------------------------------------------------
# Correlation matrix
# ---------------------------------------------------------------------------

@dataclass
class CorrResult:
    var1: str
    var2: str
    pearson_r: float
    pearson_p: float
    spearman_r: float
    spearman_p: float


def build_correlation_table(
    df: pd.DataFrame,
    continuous_vars: Sequence[str],
    var_labels: Optional[Dict[str, str]] = None,
) -> List[CorrResult]:
    """Build pairwise correlation results."""
    var_labels = var_labels or {}
    results = []
    sub = df[list(continuous_vars)].apply(pd.to_numeric, errors="coerce")
    for i, v1 in enumerate(continuous_vars):
        for v2 in continuous_vars[i + 1 :]:
            x = sub[v1].dropna()
            y = sub[v2].reindex(x.index).dropna()
            x = x.reindex(y.index)
            if len(x) < 3:
                continue
            pr, pp = pearsonr(x, y)
            sr, sp = spearmanr(x, y)
            results.append(
                CorrResult(
                    var1=var_labels.get(v1, v1),
                    var2=var_labels.get(v2, v2),
                    pearson_r=pr,
                    pearson_p=pp,
                    spearman_r=sr,
                    spearman_p=sp,
                )
            )
    return results


# ---------------------------------------------------------------------------
# Cox regression
# ---------------------------------------------------------------------------

@dataclass
class CoxResult:
    variable: str
    level: str
    hr: float
    ci_low: float
    ci_high: float
    pvalue: float
    model: str  # univariable or multivariable


def _safe_cox(
    df: pd.DataFrame,
    time_col: str,
    event_col: str,
    predictors: List[str],
    model_name: str,
) -> List[CoxResult]:
    """Fit Cox PH regression using statsmodels PHReg."""
    results = []
    sub = df[[time_col, event_col] + predictors].dropna().copy()
    sub[time_col] = pd.to_numeric(sub[time_col], errors="coerce")
    sub[event_col] = pd.to_numeric(sub[event_col], errors="coerce")
    sub = sub.dropna()
    if len(sub) < 5:
        return results

    # Convert categorical predictors to dummy variables
    X_parts = []
    var_info = []  # (original_var, level_label, dummy_col_name)
    for var in predictors:
        if sub[var].dtype == object or sub[var].dtype.name == "category":
            dummies = pd.get_dummies(sub[var], prefix=var, drop_first=True)
            for col in dummies.columns:
                level_label = col.split("_", 1)[1]
                var_info.append((var, level_label, col))
            X_parts.append(dummies.astype(float))
        else:
            X_parts.append(sub[[var]].astype(float))
            var_info.append((var, "", var))

    X = pd.concat(X_parts, axis=1)
    X = X.loc[:, (X.std() > 0)]  # drop constant columns
    if X.shape[1] == 0:
        return results

    # Align
    valid_idx = X.index
    time_vals = sub.loc[valid_idx, time_col].astype(float).values
    event_vals = sub.loc[valid_idx, event_col].astype(float).values
    X_arr = X.values

    try:
        model = PHReg(time_vals, X_arr, status=event_vals, ties="efron")
        fit = model.fit()
        params = fit.params
        se = fit.bse
        pvalues = fit.pvalues
        for (orig_var, level_label, col_name), idx in zip(
            var_info, range(X.shape[1])
        ):
            if col_name not in X.columns:
                continue
            col_idx = X.columns.get_loc(col_name)
            hr = np.exp(params[col_idx])
            ci_low = np.exp(params[col_idx] - 1.96 * se[col_idx])
            ci_high = np.exp(params[col_idx] + 1.96 * se[col_idx])
            results.append(
                CoxResult(
                    variable=orig_var,
                    level=level_label,
                    hr=hr,
                    ci_low=ci_low,
                    ci_high=ci_high,
                    pvalue=pvalues[col_idx],
                    model=model_name,
                )
            )
    except Exception as exc:  # noqa: BLE001
        print(f"Cox PH fit failed for {model_name}: {exc}")
    return results


def build_cox_tables(
    df: pd.DataFrame,
    time_col: str,
    event_col: str,
    candidate_predictors: List[str],
    multivar_predictors: Optional[List[str]] = None,
    var_labels: Optional[Dict[str, str]] = None,
    alpha: float = 0.10,
) -> Tuple[List[CoxResult], List[CoxResult], str]:
    """
    Build univariable and multivariable Cox regression tables.

    Multivariable model includes candidate predictors that are significant at
    alpha in univariable analysis, plus any predictors in multivar_predictors.
    """
    var_labels = var_labels or {}
    uni = _safe_cox(df, time_col, event_col, candidate_predictors, "Univariable")
    selected = set()
    for r in uni:
        if r.pvalue < alpha:
            selected.add(r.variable)
    if multivar_predictors:
        selected.update(multivar_predictors)
    selected = [p for p in candidate_predictors if p in selected]
    multi: List[CoxResult] = []
    if selected:
        multi = _safe_cox(df, time_col, event_col, selected, "Multivariable")

    footer = (
        f"Cox proportional hazards regression. "
        f"Multivariable model includes variables with univariable p < {alpha} "
        f"plus prespecified variables. "
        f"HR = hazard ratio; CI = confidence interval. "
        f"Event: {event_col}; Time: {time_col}."
    )
    return uni, multi, footer


# ---------------------------------------------------------------------------
# Markdown renderers
# ---------------------------------------------------------------------------

def render_baseline_markdown(
    tables: List[Tuple[str, List[BaselineRow], str, str]]
) -> str:
    """Render baseline tables to a Markdown three-line table."""
    out = []
    for header, rows, n_total, footer in tables:
        out.append(f"### {header} ({n_total})")
        out.append("")
        out.append("| Characteristic | Total | Group 1 | Group 2 | p value |")
        out.append("|---|---:|---:|---:|---:|")
        for row in rows:
            if row.is_header:
                out.append(f"| **{row.variable}** | | | | |")
            else:
                total = row.counts.get("Total", "")
                g1 = row.counts.get(list(row.counts.keys())[0], "") if row.counts else ""
                keys = list(row.counts.keys()) if row.counts else []
                g2 = row.counts.get(keys[1], "") if len(keys) > 1 else ""
                p_cell = f"{row.pvalue}{row.stars}" if row.pvalue else ""
                out.append(f"| {row.level} | {total} | {g1} | {g2} | {p_cell} |")
        out.append("")
        out.append(f"*{footer}*")
        out.append("")
    return "\n".join(out)


def render_correlation_markdown(results: List[CorrResult]) -> str:
    """Render correlation matrix to Markdown."""
    if not results:
        return ""
    out = []
    out.append("### Correlation matrix")
    out.append("")
    out.append("| Variable 1 | Variable 2 | Pearson r | p value | Spearman ρ | p value |")
    out.append("|---|---|---:|---:|---:|---:|")
    for r in results:
        pr = f"{r.pearson_r:.3f}{stars(r.pearson_p)}"
        pp = fmt_pvalue(r.pearson_p)
        sr = f"{r.spearman_r:.3f}{stars(r.spearman_p)}"
        sp = fmt_pvalue(r.spearman_p)
        out.append(f"| {r.var1} | {r.var2} | {pr} | {pp} | {sr} | {sp} |")
    out.append("")
    out.append(
        "*Pearson correlation assumes linear relationships; Spearman correlation is rank-based and more robust to outliers. "
        "Significance: * p<0.05, ** p<0.01, *** p<0.001."
    )
    out.append("")
    return "\n".join(out)


def render_cox_markdown(uni: List[CoxResult], multi: List[CoxResult], footer: str) -> str:
    """Render Cox regression results to Markdown."""
    if not uni:
        return ""
    out = []
    out.append("### Cox regression analysis")
    out.append("")
    out.append("| Model | Variable | Level | HR | 95% CI | p value |")
    out.append("|---|---|---|---|---:|---:|")
    for r in uni + multi:
        level = f" ({r.level})" if r.level else ""
        var = f"{r.variable}{level}"
        ci = f"{r.ci_low:.2f}–{r.ci_high:.2f}"
        p = f"{fmt_pvalue(r.pvalue)}{stars(r.pvalue)}"
        out.append(f"| {r.model} | {r.variable} | {r.level} | {r.hr:.2f} | {ci} | {p} |")
    out.append("")
    out.append(f"*{footer}*")
    out.append("")
    return "\n".join(out)


def render_or_markdown(or_rows: List[Dict]) -> str:
    """Render OR summary for Fisher 2x2 tables."""
    if not or_rows:
        return ""
    out = []
    out.append("### Odds ratios from Fisher's exact test (2x2 tables)")
    out.append("")
    out.append("| Grouping variable | Clinical variable | Level | OR | 95% CI | p value |")
    out.append("|---|---|---|---|---:|---:|")
    for row in or_rows:
        p = f"{fmt_pvalue(row['pvalue'])}{stars(row['pvalue'])}"
        out.append(
            f"| {row['group']} | {row['variable']} | {row['level']} | {row['or']} | {row['ci']} | {p} |"
        )
    out.append("")
    out.append(
        "*OR = odds ratio; CI = confidence interval (Woolf method). "
        "Only 2x2 tables analyzed by Fisher's exact test are shown."
    )
    out.append("")
    return "\n".join(out)
