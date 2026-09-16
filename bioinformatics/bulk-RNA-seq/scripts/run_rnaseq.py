#!/usr/bin/env python3
"""run_rnaseq.py — Claw2Bio bulk-rnaseq entry point.

Diagnoses the input matrix, selects the differential-expression engine
(limma-trend / DESeq2 / edgeR+limma-voom), PRINTS THE RATIONALE (mandatory),
then drives the staged R scripts via subprocess:

    01_qc.R  ->  02_de_<engine>.R     (regular pipeline stops at DEG tables)

Personalized follow-ups live in separate skills (consume this pipeline's outputs):
    ../RNA-seq-enrichment   GO / KEGG / Reactome enrichment from DEG tables
    ../RNA-seq-gene-plot    gene-of-interest abundance / comparison bar plots
    ../RNA-seq-GSEA         GSEA from DEG tables (fgsea + MSigDB GMT)
"""

import argparse
import os
import shutil
import subprocess
import sys

import numpy as np
import pandas as pd

# Line-buffer stdout so the engine-diagnosis box appears BEFORE the noisy R output.
sys.stdout.reconfigure(line_buffering=True)

STAGE_QC = "01_qc.R"
ENGINE_SCRIPTS = {
    "deseq2": "02_de_deseq2.R",
    "edger-limma": "02_de_edger_limma.R",
    "limma": "02_de_edger_limma.R",  # limma-trend mode for non-integer input
}

RULES_TEXT = """\
Engine selection rules (data-driven):
  - non-integer / already-normalized values (FPKM, TPM, log) -> limma-trend
    (negative-binomial models in DESeq2/edgeR require raw integer counts)
  - integer counts, min group size < {min_n}  -> DESeq2
    (most robust dispersion estimation for small replicate numbers)
  - integer counts, min group size >= {min_n} -> edgeR + limma-voom
    (precision weights give more power and are much faster at large n)"""


def find_rscript(user_path=None):
    candidates = [user_path, os.environ.get("RSCRIPT"), shutil.which("Rscript")]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    sys.exit(
        "ERROR: Rscript not found. Install R (https://cloud.r-project.org/) and either\n"
        "  - add its bin folder to PATH, or\n"
        "  - pass --rscript \"<path/to/Rscript.exe>\", or\n"
        "  - set the RSCRIPT environment variable."
    )


def read_table_smart(path, **kw):
    """csv/tsv/txt/space + .gz/.zip: let pandas sniff delimiter & compression."""
    return pd.read_csv(path, sep=None, engine="python", compression="infer", **kw)


def diagnose(counts_path, metadata_path, control):
    df = read_table_smart(counts_path, index_col=0)
    df = df.apply(pd.to_numeric, errors="coerce")
    if df.shape[1] > df.shape[0]:
        print("! More columns than rows — matrix looks transposed (samples x genes).")
        print("  Please provide genes as rows. Aborting before wrong inference.")
        sys.exit(2)

    values = df.values.astype(float)
    values = values[~np.isnan(values)]
    is_integer = bool(np.allclose(values, np.round(values)))

    meta = read_table_smart(metadata_path)
    if not {"sample", "group"} <= set(meta.columns):
        sys.exit("ERROR: metadata CSV must have columns 'sample' and 'group'.")
    missing = set(df.columns) - set(meta["sample"].astype(str))
    if missing:
        print(f"! {len(missing)} sample(s) in counts missing from metadata: {sorted(missing)[:5]}")
        sys.exit(2)
    sizes = meta["group"].value_counts()
    min_n = int(sizes.min())
    ctrl = control or meta["group"].iloc[0]
    if ctrl not in set(meta["group"]):
        sys.exit(f"ERROR: control group '{ctrl}' not found in metadata groups {sorted(set(meta['group']))}.")
    return df, meta, is_integer, sizes, min_n, ctrl


def select_engine(is_integer, min_n, voom_min_n, forced):
    print("\n" + "=" * 64)
    print("ENGINE DIAGNOSIS")
    print("=" * 64)
    print(RULES_TEXT.format(min_n=voom_min_n))
    print("-" * 64)
    print(f"Observed: integer counts = {is_integer}; smallest group n = {min_n}")

    if forced:
        print(f"\n>>> ENGINE FORCED by user: --engine {forced}")
        print(">>> Auto-detection overridden. Make sure the input matches the engine's")
        print("    assumptions (DESeq2/edgeR need raw integer counts).")
        print("=" * 64 + "\n")
        return forced

    if not is_integer:
        engine = "limma"
        why = ("Non-integer values detected (normalized data such as FPKM/TPM/log).\n"
               "    Negative-binomial engines (DESeq2/edgeR) would be statistically invalid here;\n"
               "    limma-trend is the correct choice for normalized expression matrices.")
    elif min_n < voom_min_n:
        engine = "deseq2"
        why = (f"Integer counts with small replication (min group n = {min_n} < {voom_min_n}).\n"
               "    DESeq2 gives the most robust dispersion/shrinkage estimates at small n.")
    else:
        engine = "edger-limma"
        why = (f"Integer counts with comfortable replication (min group n = {min_n} >= {voom_min_n}).\n"
               "    edgeR TMM normalization + limma-voom precision weights give more power\n"
               "    and run much faster at this sample size.")
    print(f"\n>>> SELECTED ENGINE: {engine}")
    print(f">>> WHY: {why}")
    print("=" * 64 + "\n")
    return engine


def run_stage(rscript, script, args, stage_name):
    here = os.path.dirname(os.path.abspath(__file__))
    cmd = [rscript, os.path.join(here, script)] + args
    print(f"--- Stage: {stage_name} ---")
    print(" ".join(f'"{c}"' if " " in c else c for c in cmd))
    proc = subprocess.run(cmd)
    if proc.returncode != 0:
        sys.exit(f"ERROR: stage '{stage_name}' failed with exit code {proc.returncode}.")


def main():
    ap = argparse.ArgumentParser(description="Bulk RNA-seq pipeline: QC -> DE (engine fork) -> enrichment")
    ap.add_argument("counts", help="counts matrix CSV (genes x samples)")
    ap.add_argument("metadata", help="sample metadata CSV with columns: sample,group")
    ap.add_argument("output", help="output directory")
    ap.add_argument("--control", default=None, help="control group name (default: first group in metadata)")
    ap.add_argument("--engine", choices=["auto"] + list(ENGINE_SCRIPTS), default="auto",
                    help="force DE engine; default 'auto' = data-driven selection")
    ap.add_argument("--voom-min-n", type=int, default=8,
                    help="min group size at which edgeR+limma-voom is preferred over DESeq2 (default 8)")
    ap.add_argument("--organism", choices=["mouse", "human"], default="mouse")
    ap.add_argument("--padj", type=float, default=0.05)
    ap.add_argument("--log2fc", type=float, default=1.0)
    ap.add_argument("--install-deps", action="store_true",
                    help="let the pipeline install missing R packages itself (BiocManager/CRAN)")
    ap.add_argument("--rscript", default=None, help="path to Rscript executable")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    if os.path.exists(args.output) and os.listdir(args.output) and not args.overwrite:
        sys.exit(f"ERROR: output dir '{args.output}' is not empty. Use --overwrite.")
    os.makedirs(args.output, exist_ok=True)

    rscript = find_rscript(args.rscript)
    df, meta, is_integer, sizes, min_n, control = diagnose(args.counts, args.metadata, args.control)
    print(f"Counts: {df.shape[0]} genes x {df.shape[1]} samples")
    print("Group sizes:\n" + sizes.to_string())
    print(f"Control group: {control}")

    # ---- Stage 00: dependency check BEFORE anything else ----
    here = os.path.dirname(os.path.abspath(__file__))
    dep_cmd = [rscript, os.path.join(here, "00_check_deps.R"), "--organism", args.organism]
    if args.install_deps:
        dep_cmd.append("--install")
    dep = subprocess.run(dep_cmd)
    if dep.returncode != 0:
        print(
            "\n" + "=" * 64 + "\n"
            "R package dependencies are missing. Choose how to install them:\n"
            "\n"
            "  A) Let the AI agent install them now:\n"
            "     re-run this command with --install-deps\n"
            "\n"
            "  B) Install manually (e.g. via miniconda or R), then re-run:\n"
            "       conda install -c bioconda bioconductor-deseq2 bioconductor-edger \\\n"
            "         bioconductor-limma\n"
            "     or in R:  BiocManager::install(c('DESeq2','edgeR','limma', ...))\n"
            "\n"
            "缺少 R 依赖包。请选择：A) 让 AI agent 自动安装（重跑时加 --install-deps）；\n"
            "B) 手动安装（miniconda 或在 R 里用 BiocManager），装好后重跑。\n"
            "=" * 64)
        sys.exit(3)

    forced = None if args.engine == "auto" else args.engine
    engine = select_engine(is_integer, min_n, args.voom_min_n, forced)

    common = [args.counts, args.metadata, args.output,
              "--control", control, "--organism", args.organism,
              "--padj", str(args.padj), "--log2fc", str(args.log2fc)]

    run_stage(rscript, STAGE_QC, common, "01_qc")
    de_args = list(common)
    if engine == "limma":
        de_args += ["--mode", "trend"]
    else:
        de_args += ["--mode", "voom"] if engine == "edger-limma" else []
    run_stage(rscript, ENGINE_SCRIPTS[engine], de_args, f"02_de ({engine})")
    print("\nRegular pipeline finished (QC + DEG). Outputs in:", os.path.abspath(args.output))
    print("Next personalized steps: ../RNA-seq-enrichment, ../RNA-seq-gene-plot, ../RNA-seq-GSEA")
    write_run_metadata(args.output, engine, forced, args, control, meta, df, is_integer, rscript)
    write_report(args.output, engine, control, args.counts, args.metadata, meta, df)
    print("REPORT.md + run_metadata.json written to the output directory.")


def write_report(outdir, engine, control, counts_path, meta_path, meta, counts_df):
    """Write REPORT.md into the output dir: file -> producing stage -> purpose."""
    import re
    rules = [
        (r"^QC_PCA_plot\.", "01_qc.R",
         "PCA of logCPM expression — check group separation and outlier/batch samples"),
        (r"^QC_sample_correlation_heatmap\.", "01_qc.R",
         "Sample-sample correlation heatmap — replicates should cluster together"),
        (r"^QC_summary\.txt$", "01_qc.R",
         "Filtering stats (genes kept, library sizes)"),
        (r"^filtered_counts\.csv$", "01_qc.R",
         "Count matrix after filterByExpr — input to the DE stage"),
        (r"^library_sizes\.csv$", "01_qc.R",
         "Per-sample library sizes before/after filtering"),
        (r"^run_metadata\.json$", "run_rnaseq.py",
         "Machine-readable run record: engine, parameters, input stats, software versions, timestamp"),
        (r"^normalized_expression\.csv$", "02_de (" + engine + ")",
         "Normalised expression matrix (vst / voom logCPM / log-expression, engine-dependent) — input for the RNA-seq-gene-plot skill"),
        (r"^DEG_.*\.csv$", "02_de (" + engine + ")",
         "Full differential-expression table for one contrast (log2FC, p, padj, symbol) — input for the RNA-seq-enrichment and RNA-seq-GSEA skills"),
        (r"^Volcano_.*\.(png|pdf)$", "02_de (" + engine + ")",
         "Volcano plot of one contrast, top-10 gene labels"),
        (r"^MA_.*\.(png|pdf)$", "02_de (" + engine + ")",
         "MA plot of one contrast — sanity check that normalisation worked and logFC is expression-independent"),
        (r"^DEG_heatmap\.", "02_de (" + engine + ")",
         "Z-scored heatmap of the union of significant DEGs"),
    ]
    # group structure of the input matrix
    group_lines = []
    for g, sub in meta.groupby("group", sort=False):
        samples = list(sub["sample"])
        shown = samples if len(samples) <= 12 else samples[:12] + [f"... (+{len(samples) - 12} more)"]
        group_lines.append(f"- **{g}** (n={len(samples)}): {', '.join(shown)}")
    group_block = "\n".join(group_lines)

    lines = [
        "# Analysis Report — bulk-RNA-seq (regular pipeline: counts → DEG)",
        "",
        f"- Input counts: `{os.path.basename(counts_path)}` ({counts_df.shape[0]} genes × {counts_df.shape[1]} samples)",
        f"- Metadata: `{os.path.basename(meta_path)}` (control group: `{control}`)",
        f"- Engine: **{engine}** (rationale was printed at run time)",
        "- Personalized follow-ups on these outputs: `../RNA-seq-enrichment` (GO/KEGG/Reactome), `../RNA-seq-gene-plot` (gene bar charts), `../RNA-seq-GSEA` (GSEA)",
        "",
        "## Input grouping",
        "",
        group_block,
        "",
        "| File | Produced by | What it is / use |",
        "|---|---|---|",
    ]
    for f in sorted(os.listdir(outdir)):
        if f == "REPORT.md":
            continue
        for pat, stage, desc in rules:
            if re.search(pat, f):
                lines.append(f"| `{f}` | {stage} | {desc} |")
                break
        else:
            lines.append(f"| `{f}` | — | (unclassified output) |")
    lines += ["", "_This file is auto-generated by `run_rnaseq.py` at the end of every run._", ""]
    with open(os.path.join(outdir, "REPORT.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))


def _git_commit(repo_dir):
    """Short commit of the skill repo, or None if unavailable."""
    try:
        p = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=repo_dir,
                           capture_output=True, text=True, timeout=10)
        return p.stdout.strip() if p.returncode == 0 else None
    except Exception:
        return None


def _r_version(rscript):
    try:
        p = subprocess.run([rscript, "--version"], capture_output=True, text=True, timeout=30)
        return (p.stdout or p.stderr).strip().splitlines()[0]
    except Exception:
        return None


def write_run_metadata(outdir, engine, forced, args, control, meta, counts_df, is_integer, rscript):
    """Machine-readable run record: engine, parameters, input stats, versions."""
    import datetime
    import json
    import platform
    record = {
        "pipeline": "bulk-RNA-seq",
        "skill_commit": _git_commit(os.path.dirname(os.path.abspath(__file__)) + "/.."),
        "timestamp": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "engine": engine,
        "engine_forced": bool(forced),
        "parameters": {
            "control": control,
            "organism": args.organism,
            "padj": args.padj,
            "log2fc": args.log2fc,
            "voom_min_n": args.voom_min_n,
        },
        "input": {
            "counts": os.path.basename(args.counts),
            "metadata": os.path.basename(args.metadata),
            "genes": int(counts_df.shape[0]),
            "samples": int(counts_df.shape[1]),
            "integer_counts": bool(is_integer),
        },
        "groups": {g: list(sub["sample"]) for g, sub in meta.groupby("group", sort=False)},
        "versions": {
            "python": platform.python_version(),
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "r": _r_version(rscript),
        },
    }
    with open(os.path.join(outdir, "run_metadata.json"), "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
