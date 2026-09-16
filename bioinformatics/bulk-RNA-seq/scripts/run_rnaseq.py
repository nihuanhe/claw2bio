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
import gzip
import os
import re
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


# Known sample-name suffixes stuck onto matrix columns by upstream tools.
NORM_SUFFIX_RE = re.compile(r"(_count|_fpkm|_tpm|\.bam|\.fastq(?:\.gz)?)$", re.IGNORECASE)


def read_counts_any(path):
    """Read an expression matrix; also handles GEO series_matrix '!' comment headers
    (ID_REF header row location + '!series_matrix_table_begin/end' wrapper)."""
    opener = gzip.open if str(path).endswith(".gz") else open
    head = []
    with opener(path, "rt", encoding="utf-8", errors="replace") as fh:
        for _ in range(60):
            line = fh.readline()
            if not line:
                break
            head.append(line)
    bang = any(line.lstrip().startswith("!") for line in head)
    idref = next((i for i, line in enumerate(head) if re.search(r'"?(ID_REF|ID)"?\t', line)), None)
    if bang and idref is not None:
        df = pd.read_csv(path, sep="\t", skiprows=idref, comment="!",
                         index_col=0, compression="infer", low_memory=False)
        df.columns = [str(c).strip().strip('"') for c in df.columns]
        df.index = df.index.astype(str).str.strip().str.strip('"')
        return df, True
    return read_table_smart(path, index_col=0), False


def inspect_and_repair(counts_path, metadata_path, control, outdir):
    """Stage 00.5 — input inspection & lossless auto-repair.
    Everything repairable without biological judgement is fixed here, with every
    repair printed; only unfixable problems abort. Returns cleaned paths (new
    files in outdir when repairs were applied; originals otherwise)."""
    fixes, warns = [], []
    raw, special_format = read_counts_any(counts_path)
    if special_format:
        fixes.append("parsed GEO series_matrix layout ('!' comment header / ID_REF row); "
                     "re-saved as a plain table for the R stages")
    raw.columns = [str(c) for c in raw.columns]
    raw.index = raw.index.astype(str)

    # --- mixed GEO matrix: split count / FPKM / annotation columns ---
    numeric_frac = {c: pd.to_numeric(raw[c], errors="coerce").notna().mean() for c in raw.columns}
    num_cols = [c for c in raw.columns if numeric_frac[c] > 0.9]
    annot_cols = [c for c in raw.columns if c not in num_cols]
    count_cols = [c for c in num_cols if re.search(r"_count$", c, re.I)]
    norm_cols = [c for c in num_cols if re.search(r"_(fpkm|tpm)$", c, re.I)]
    if count_cols:
        expr = raw[count_cols].apply(pd.to_numeric, errors="coerce")
        dropped = [c for c in num_cols if c not in count_cols]
        if dropped:
            fixes.append(f"kept {len(count_cols)} '*_count' columns; split off {len(dropped)} other numeric column(s): "
                         f"{', '.join(dropped[:4])}{' ...' if len(dropped) > 4 else ''}")
    else:
        expr = raw[num_cols].apply(pd.to_numeric, errors="coerce")
        if norm_cols:
            fixes.append(f"no '*_count' columns found; using {len(num_cols)} numeric column(s) as-is "
                         "(normalized values -> limma-trend branch expected)")
    if annot_cols:
        os.makedirs(outdir, exist_ok=True)
        annot = raw[annot_cols].copy()
        annot.insert(0, "gene", raw.index)
        annot.to_csv(os.path.join(outdir, "gene_annotation.csv"), index=False)
        fixes.append(f"split off {len(annot_cols)} annotation column(s) "
                     f"({', '.join(annot_cols[:5])}{' ...' if len(annot_cols) > 5 else ''}) "
                     "-> gene_annotation.csv (usable later as --gene-map)")

    # --- sample-name suffix stripping (e.g. GSM123_count -> GSM123) ---
    stripped = [NORM_SUFFIX_RE.sub("", c) for c in expr.columns]
    if stripped != list(expr.columns):
        if len(set(stripped)) == len(stripped):
            expr.columns = stripped
            fixes.append("stripped sample-name suffixes (_count/_FPKM/.bam/...) from matrix columns")
        else:
            warns.append("suffix stripping would create duplicate sample names; kept original column names")

    # --- transposed matrix (samples x genes) ---
    if expr.shape[1] > expr.shape[0]:
        expr = expr.T
        fixes.append(f"matrix looked transposed (samples x genes); transposed to "
                     f"{expr.shape[0]} genes x {expr.shape[1]} samples")

    # --- duplicated gene IDs (symbol matrices): aggregate by mean ---
    # (integer diagnosis must happen BEFORE mean-aggregation — means of integer
    # counts are non-integer and would wrongly route the data to limma-trend)
    is_integer = bool(np.allclose(np.nan_to_num(expr.values.astype(float)),
                                  np.round(np.nan_to_num(expr.values.astype(float)))))
    if expr.index.duplicated().any():
        ndup = int(expr.index.duplicated().sum())
        expr = expr.groupby(level=0).mean()
        if is_integer:
            expr = expr.round()
            fixes.append(f"collapsed {ndup} duplicated gene ID row(s) by mean and rounded back to integers "
                         "(counts engine preserved; e.g. repeated gene symbols)")
        else:
            fixes.append(f"collapsed {ndup} duplicated gene ID row(s) by mean (e.g. repeated gene symbols)")

    # --- value repair ---
    n_na = int(expr.isna().sum().sum())
    if n_na:
        expr = expr.dropna(axis=0)
        fixes.append(f"dropped row(s) containing non-numeric/NA values ({n_na} cell(s))")
    n_neg = int((expr.values < 0).sum())
    if n_neg:
        expr = expr.clip(lower=0)
        fixes.append(f"clipped {n_neg} negative value(s) to 0")

    # --- metadata normalisation ---
    meta = read_table_smart(metadata_path)
    meta.columns = [str(c).strip() for c in meta.columns]
    lower = {c.lower(): c for c in meta.columns}
    ren = {}
    if "sample" not in meta.columns:
        for cand in ("sample_id", "sampleid", "sample_name", "samples", "gsm", "geo_accession", "id"):
            if cand in lower:
                ren[lower[cand]] = "sample"
                break
    if "group" not in meta.columns:
        for cand in ("condition", "group_name", "groups", "treatment", "genotype", "phenotype"):
            if cand in lower:
                ren[lower[cand]] = "group"
                break
    if ren:
        meta = meta.rename(columns=ren)
        fixes.append("renamed metadata column(s): " + ", ".join(f"{k} -> {v}" for k, v in ren.items()))
    if not {"sample", "group"} <= set(meta.columns):
        sys.exit("ERROR: metadata must have columns 'sample' and 'group' "
                 "(auto-renaming found no suitable candidates).")
    meta["sample"] = meta["sample"].astype(str)
    meta["group"] = meta["group"].astype(str)

    # --- sample-name matching (exact, then fuzzy undoing R check.names mangling) ---
    meta_samples = list(meta["sample"])
    if set(meta_samples) != set(expr.columns):
        def keys(s):
            """Fuzzy keys for a name: alphanumeric-only lowercase; plus the
            leading-X-stripped variant (R make.names turns '15' into 'X15')."""
            k = re.sub(r"[^A-Za-z0-9]+", "", str(s)).lower()
            out = [k]
            if re.match(r"^x\d", k):
                out.append(k[1:])
            return out
        by_key = {}
        for s in meta_samples:
            for k in keys(s):
                by_key.setdefault(k, s)
        remap, used = {}, set()
        for c in expr.columns:
            if c in set(meta_samples):
                continue
            hit = next((by_key[k] for k in keys(c) if k in by_key and by_key[k] not in used), None)
            if hit is not None:
                remap[c] = hit
                used.add(hit)
        if remap:
            expr = expr.rename(columns=remap)
            shown = list(remap.items())[:3]
            fixes.append(f"matched {len(remap)} matrix column name(s) to metadata via fuzzy matching "
                         f"(undoes R check.names-style mangling): "
                         + ", ".join(f"{a} -> {b}" for a, b in shown)
                         + (" ..." if len(remap) > 3 else ""))
    missing = set(expr.columns) - set(meta_samples)
    if missing:
        if not (set(expr.columns) & set(meta_samples)):
            sys.exit("ERROR: no overlap between matrix columns and metadata samples -- "
                     "probably the wrong metadata file.")
        expr = expr[[c for c in expr.columns if c not in missing]]
        fixes.append(f"matrix contained {len(missing)} sample(s) absent from metadata; excluded from analysis "
                     f"(metadata defines the analysis set): {sorted(missing)[:5]}")
        if len(missing) > expr.shape[1]:
            warns.append(f"more matrix samples were dropped ({len(missing)}) than kept ({expr.shape[1]}) -- "
                         "double-check that the metadata really describes the intended analysis set")
    extra = set(meta_samples) - set(expr.columns)
    if extra:
        meta = meta[meta["sample"].isin(set(expr.columns))]
        fixes.append(f"metadata listed {len(extra)} sample(s) absent from the matrix; dropped: {sorted(extra)[:5]}")
    expr = expr[meta["sample"].tolist()]   # align column order to metadata

    digit_named = [s for s in meta["sample"] if re.match(r"^\d", s)]
    if digit_named:
        warns.append(f"sample name(s) starting with digits ({', '.join(digit_named[:5])}): R's make.names "
                     "would mangle these; all pipeline stages preserve names verbatim (check.names = FALSE)")
    for p in (counts_path, metadata_path, outdir):
        if any(ord(ch) > 127 for ch in str(p)) or " " in str(p):
            warns.append(f"path contains non-ASCII characters or spaces: {p} -- R on Windows can choke on "
                         "such paths; if a stage fails mysteriously, copy inputs to a plain-ASCII temp path and rerun")
            break

    sizes = meta["group"].value_counts()
    min_n = int(sizes.min())
    ctrl = control or meta["group"].iloc[0]
    if ctrl not in set(meta["group"]):
        sys.exit(f"ERROR: control group '{ctrl}' not found in metadata groups {sorted(set(meta['group']))}.")

    counts2, meta2 = counts_path, metadata_path
    if fixes:
        counts2 = os.path.join(outdir, "cleaned_counts.csv")
        meta2 = os.path.join(outdir, "cleaned_metadata.csv")
        expr.to_csv(counts2, index_label="gene")
        meta.to_csv(meta2, index=False)

    print("\n" + "=" * 64)
    print("INPUT INSPECTION (stage 00.5)")
    print("=" * 64)
    if fixes:
        print("Auto-repairs applied (originals never modified; cleaned copies in output dir):")
        for f in fixes:
            print(f"  [fixed] {f}")
    else:
        print("Input looks clean -- no repairs needed.")
    for w in warns:
        print(f"  [warn ] {w}")
    print("=" * 64 + "\n")
    return counts2, meta2, expr, meta, is_integer, sizes, min_n, ctrl, fixes, warns


def select_engine(is_integer, min_n, voom_min_n, forced, forced_reason=None):
    print("\n" + "=" * 64)
    print("ENGINE DIAGNOSIS")
    print("=" * 64)
    print(RULES_TEXT.format(min_n=voom_min_n))
    print("-" * 64)
    print(f"Observed: integer counts = {is_integer}; smallest group n = {min_n}")

    if forced:
        if forced_reason:
            print(f"\n>>> ENGINE FORCED: {forced} ({forced_reason})")
        else:
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
    ap.add_argument("--batch", default=None,
                    help="metadata column with batch information; added to the design formula "
                         "and used to colour/shape QC plots")
    ap.add_argument("--paired-by", default=None, dest="paired_by",
                    help="metadata column identifying the subject/patient/animal for paired or "
                         "repeated-measures designs (forces limma + duplicateCorrelation)")
    ap.add_argument("--pairwise-max", type=int, default=4,
                    help="add all pairwise contrasts when group count <= this (default 4)")
    ap.add_argument("--contrasts", default=None,
                    help="explicit contrasts, e.g. 'TreatA vs Control, TreatB vs Control'; "
                         "overrides automatic contrast generation")
    ap.add_argument("--exclude-samples", default=None,
                    help="comma-separated sample names to exclude explicitly (e.g. outliers "
                         "you have judged by eye; the pipeline never excludes on its own)")
    ap.add_argument("--install-deps", action="store_true",
                    help="let the pipeline install missing R packages itself (BiocManager/CRAN)")
    ap.add_argument("--rscript", default=None, help="path to Rscript executable")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    if os.path.exists(args.output) and os.listdir(args.output) and not args.overwrite:
        sys.exit(f"ERROR: output dir '{args.output}' is not empty. Use --overwrite.")
    os.makedirs(args.output, exist_ok=True)

    rscript = find_rscript(args.rscript)
    counts2, meta2, df, meta, is_integer, sizes, min_n, control, fixes, warns = \
        inspect_and_repair(args.counts, args.metadata, args.control, args.output)

    # ---- explicit sample exclusion (never automatic) ----
    if args.exclude_samples:
        excl = [s.strip() for s in args.exclude_samples.split(",") if s.strip()]
        unknown = [s for s in excl if s not in set(meta["sample"])]
        if unknown:
            sys.exit(f"ERROR: --exclude-samples not found in metadata: {unknown}")
        meta = meta[~meta["sample"].isin(excl)]
        df = df[[c for c in df.columns if c not in set(excl)]]
        counts2 = os.path.join(args.output, "cleaned_counts.csv")
        meta2 = os.path.join(args.output, "cleaned_metadata.csv")
        df.to_csv(counts2, index_label="gene")
        meta.to_csv(meta2, index=False)
        fixes.append(f"user-excluded {len(excl)} sample(s) via --exclude-samples: {excl}")
        sizes = meta["group"].value_counts()
        min_n = int(sizes.min())

    # ---- design columns declared on the command line must exist in metadata ----
    for flag, col in (("--batch", args.batch), ("--paired-by", args.paired_by)):
        if col and col not in meta.columns:
            sys.exit(f"ERROR: {flag} column '{col}' not in metadata columns {list(meta.columns)}.")

    # ---- explicit contrasts, validated against the actual groups ----
    explicit = None
    if args.contrasts:
        groups = set(meta["group"])
        pairs = []
        for item in args.contrasts.split(","):
            m = re.split(r"\s+vs\.?\s+", item.strip(), flags=re.I)
            if len(m) != 2:
                sys.exit(f"ERROR: cannot parse contrast '{item}'. Use 'Treat vs Ref', comma-separated.")
            if m[0] not in groups or m[1] not in groups:
                sys.exit(f"ERROR: contrast '{item}' references group(s) not in metadata {sorted(groups)}.")
            pairs.append((m[0], m[1]))
        explicit = ";".join(f"{t}|{r}" for t, r in pairs)

    print(f"Counts: {df.shape[0]} genes x {df.shape[1]} samples")
    print("Group sizes:\n" + sizes.to_string())
    print(f"Control group: {control}")
    if args.batch:
        print(f"Batch column: {args.batch} (levels: {', '.join(sorted(set(meta[args.batch])))})")
    if args.paired_by:
        print(f"Paired by: {args.paired_by} ({meta[args.paired_by].nunique()} subjects)")

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
    forced_reason = None
    exploratory = min_n == 1
    if exploratory and not forced:
        print("\n" + "!" * 64)
        print("!! NO BIOLOGICAL REPLICATES (min group n = 1).")
        print("!! DESeq2/edgeR dispersion estimates require replicates; running in")
        print("!! EXPLORATORY MODE instead: limma-trend on log expression.")
        print("!! Treat all p values as descriptive only -- NOT usable for conclusions.")
        print("!! 无生物学重复：降级为 limma-trend 探索模式，REPORT 中会显著标记。")
        print("!" * 64 + "\n")
        forced, forced_reason = "limma", "no biological replicates (exploratory mode)"
    elif args.paired_by and not forced:
        forced = "edger-limma" if is_integer else "limma"
        forced_reason = (f"paired/repeated-measures design (--paired-by {args.paired_by}): "
                         "limma duplicateCorrelation is the standard approach for repeated measures")
    engine = select_engine(is_integer, min_n, args.voom_min_n, forced, forced_reason=forced_reason)

    common = [counts2, meta2, args.output,
              "--control", control, "--organism", args.organism,
              "--padj", str(args.padj), "--log2fc", str(args.log2fc),
              "--pairwise-max", str(args.pairwise_max)]
    if args.batch:
        common += ["--batch", args.batch]
    if args.paired_by:
        common += ["--paired-by", args.paired_by]
    if explicit:
        common += ["--contrasts", explicit]

    run_stage(rscript, STAGE_QC, common, "01_qc")
    de_args = list(common)
    if engine == "limma":
        de_args += ["--mode", "trend"]
    else:
        de_args += ["--mode", "voom"] if engine == "edger-limma" else []
    run_stage(rscript, ENGINE_SCRIPTS[engine], de_args, f"02_de ({engine})")
    print("\nRegular pipeline finished (QC + DEG). Outputs in:", os.path.abspath(args.output))
    print("Next personalized steps: ../RNA-seq-enrichment, ../RNA-seq-gene-plot, ../RNA-seq-GSEA")
    write_run_metadata(args.output, engine, None if args.engine == "auto" else args.engine,
                       args, control, meta, df, is_integer, rscript, exploratory, fixes, warns)
    write_report(args.output, engine, control, args.counts, args.metadata, meta, df,
                 exploratory=exploratory, fixes=fixes, warns=warns)
    print("REPORT.md + run_metadata.json written to the output directory.")


def write_report(outdir, engine, control, counts_path, meta_path, meta, counts_df,
                 exploratory=False, fixes=None, warns=None):
    """Write REPORT.md into the output dir: file -> producing stage -> purpose."""
    rules = [
        (r"^cleaned_counts\.csv$|^cleaned_metadata\.csv$", "00.5 input inspection",
         "Cleaned copy of the input actually analysed (auto-repaired); originals were never modified"),
        (r"^gene_annotation\.csv$", "00.5 input inspection",
         "Annotation columns split off the input matrix — usable later as --gene-map"),
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
    ]
    if exploratory:
        lines += [
            "> ## ⚠️ EXPLORATORY RESULTS — NO BIOLOGICAL REPLICATES (min group n = 1)",
            ">",
            "> At least one group has a single sample. Differential-expression p values in",
            "> this run are **descriptive only and must NOT be used for conclusions**.",
            "> Engine was forced to limma-trend on log expression for this reason.",
            "> 无生物学重复：本报告所有差异分析结果仅供探索，不可作为结论依据。",
            "",
        ]
    lines += [
        f"- Input counts: `{os.path.basename(counts_path)}` ({counts_df.shape[0]} genes × {counts_df.shape[1]} samples)",
        f"- Metadata: `{os.path.basename(meta_path)}` (control group: `{control}`)",
        f"- Engine: **{engine}** (rationale was printed at run time)",
        "- Personalized follow-ups on these outputs: `../RNA-seq-enrichment` (GO/KEGG/Reactome), `../RNA-seq-gene-plot` (gene bar charts), `../RNA-seq-GSEA` (GSEA)",
        "",
    ]
    if fixes:
        lines += ["## Input auto-repairs (stage 00.5)", ""]
        lines += [f"- {f}" for f in fixes]
        lines += [""]
    if warns:
        lines += ["## Input warnings", ""]
        lines += [f"- {w}" for w in warns]
        lines += [""]
    lines += [
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


def write_run_metadata(outdir, engine, forced, args, control, meta, counts_df, is_integer, rscript,
                       exploratory=False, fixes=None, warns=None):
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
        "exploratory_no_replicates": bool(exploratory),
        "input_repairs": fixes or [],
        "input_warnings": warns or [],
        "parameters": {
            "control": control,
            "organism": args.organism,
            "padj": args.padj,
            "log2fc": args.log2fc,
            "voom_min_n": args.voom_min_n,
            "batch": args.batch,
            "paired_by": args.paired_by,
            "pairwise_max": args.pairwise_max,
            "contrasts": args.contrasts,
            "exclude_samples": args.exclude_samples,
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
