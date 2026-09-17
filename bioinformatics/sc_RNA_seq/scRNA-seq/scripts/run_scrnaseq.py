#!/usr/bin/env python3
"""scRNA-seq regular pipeline driver (stages 00 -> 05).

Usage:
    python scripts/run_scrnaseq.py <input> <output_dir> [options]

<input> : a directory (single 10X dir, multi-sample dir, or a dir of files)
          or a single file (.h5/.h5ad/.rds/.txt.gz/.csv.gz/...).

Stages:
    00    dependency check (R packages + anndata when h5ad present)
    00.5  input inspection & auto-repair (the heart of this skill)
    01    read & build Seurat object(s), merge, QC metrics   [R]
    02    QC filtering + doublets                            [R]
    03    normalize / integrate / cluster / UMAP / tSNE      [R]
    04    markers (presto) + SingleR annotation              [R]
    05    REPORT.md + run_metadata.json                      [python]

Every stage checkpoints an rds under <output>/.checkpoints/ ; --resume skips
completed stages. merge/integration is the memory-peak stage — all inputs are
fully unpacked and inspected BEFORE it starts.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import inspect_input  # noqa: E402

R_PACKAGES = ["Seurat", "harmony", "SingleR", "celldex", "scDblFinder",
              "clustree", "presto", "hdf5r", "Matrix", "ggplot2", "dplyr",
              "patchwork", "data.table", "jsonlite"]
# packages that are optional at runtime (stage degrades gracefully if absent)
OPTIONAL_R = {"scDblFinder": "--no-doublets", "clustree": "clustree plot skipped"}

STAGES = ["00_deps", "00.5_inspect", "01_read", "02_qc", "03_cluster",
          "04_annotate", "05_report"]


def log(msg):
    print(f"[run_scrnaseq] {msg}", flush=True)


def find_rscript(user_path=None):
    if user_path:
        return user_path
    exe = "Rscript.exe" if os.name == "nt" else "Rscript"
    # 1) PATH
    found = shutil.which("Rscript") or shutil.which(exe)
    if found:
        return found
    # 2) Windows registry
    if os.name == "nt":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\R-core\R")
            install_path = winreg.QueryValueEx(key, "InstallPath")[0]
            cand = os.path.join(install_path, "bin", "Rscript.exe")
            if os.path.exists(cand):
                return cand
        except OSError:
            pass
    sys.exit("ERROR: Rscript not found. Pass --rscript <path>.")


def run_r(rscript, script, args, log_path):
    cmd = [rscript, os.path.join(HERE, script)] + args
    log("R: " + " ".join(cmd))
    with open(log_path, "a", encoding="utf-8") as lf:
        lf.write("\n===== %s %s =====\n" % (datetime.datetime.now(), script))
        proc = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT)
    if proc.returncode != 0:
        sys.exit(f"ERROR: {script} failed (code {proc.returncode}). See {log_path}")


def stage_done(out_dir, stage):
    return os.path.exists(os.path.join(out_dir, ".checkpoints", f".done_{stage}"))


def mark_done(out_dir, stage):
    ck = os.path.join(out_dir, ".checkpoints")
    os.makedirs(ck, exist_ok=True)
    open(os.path.join(ck, f".done_{stage}"), "w").write(
        datetime.datetime.now().isoformat())


def main():
    ap = argparse.ArgumentParser(description="scRNA-seq regular pipeline")
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--metadata", help="sample metadata CSV (sample,group)")
    ap.add_argument("--exclude", default="",
                    help="comma-separated sample names to exclude (e.g. stray rds files)")
    ap.add_argument("--organism", default="human",
                    choices=["human", "mouse"], help="default references + mt/hb prefixes")
    ap.add_argument("--mt-pattern", help="regex override for mitochondrial genes")
    ap.add_argument("--min-cells", type=int, default=3)
    ap.add_argument("--min-features", type=int, default=200)
    ap.add_argument("--mt-max", type=float, default=20.0)
    ap.add_argument("--max-features-qc", type=int, default=6000)
    ap.add_argument("--no-doublets", action="store_true")
    ap.add_argument("--integrate", default="harmony",
                    choices=["harmony", "cca", "rpca", "none"])
    ap.add_argument("--sct", action="store_true", help="SCTransform instead of LogNormalize")
    ap.add_argument("--resolution", type=float, default=0.5)
    ap.add_argument("--no-tsne", action="store_true")
    ap.add_argument("--downsample", type=int, default=0,
                    help="subsample N cells per sample (exploratory)")
    ap.add_argument("--reference", help="SingleR reference override (celldex name)")
    ap.add_argument("--custom-ref", help="path to user-provided reference rds")
    ap.add_argument("--marker-file", help="marker CSV for supplementary scoring")
    ap.add_argument("--no-annotation", action="store_true")
    ap.add_argument("--install-deps", action="store_true")
    ap.add_argument("--export-slim", action="store_true",
                    help="also write annotated_seurat.slim.rds (DietSeurat, for COS/sharing)")
    ap.add_argument("--rscript")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    out = os.path.abspath(args.output)
    if os.path.exists(out) and os.listdir(out) and not (args.overwrite or args.resume):
        sys.exit("ERROR: output dir not empty; use --overwrite or --resume")
    os.makedirs(out, exist_ok=True)
    ck = os.path.join(out, ".checkpoints")
    os.makedirs(ck, exist_ok=True)
    log_path = os.path.join(out, "pipeline.log")
    rscript = find_rscript(args.rscript)

    # ---------- stage 00 : dependency check ----------
    if not (args.resume and stage_done(out, "00_deps")):
        log("stage 00: checking R dependencies")
        rargs = ["--packages", ",".join(R_PACKAGES), "--output", out]
        if args.install_deps:
            rargs.append("--install")
        run_r(rscript, "stage00_check_deps.R", rargs, log_path)
        dep_json = os.path.join(ck, "deps.json")
        deps = json.load(open(dep_json, encoding="utf-8"))
        missing = [p for p, ok in deps.items() if not ok]
        hard_missing = [p for p in missing if p not in OPTIONAL_R]
        if hard_missing:
            sys.exit("ERROR: missing R packages: %s — install them (BiocManager/"
                     "r-deps mini-repo) or rerun with --install-deps" % ", ".join(hard_missing))
        for p in missing:
            log(f"WARNING: optional package {p} missing -> {OPTIONAL_R[p]}")
        mark_done(out, "00_deps")

    # ---------- stage 00.5 : input inspection ----------
    plan_path = os.path.join(ck, "ingest_plan.json")
    if not (args.resume and stage_done(out, "00.5_inspect")):
        log("stage 00.5: inspecting inputs")
        staging = os.path.join(out, ".staging")
        os.makedirs(staging, exist_ok=True)
        plan = inspect_input.build_plan(args.input, args.metadata, staging)
        if args.exclude:
            excl = {s.strip() for s in args.exclude.split(",")}
            dropped = [s["name"] for s in plan["samples"] if s["name"] in excl]
            plan["samples"] = [s for s in plan["samples"] if s["name"] not in excl]
            if dropped:
                log("excluded samples: " + ", ".join(dropped))
                plan.setdefault("warnings", []).append(
                    "user-excluded samples: " + ", ".join(dropped))
        json.dump(plan, open(plan_path, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        for s in plan["samples"]:
            log(f"  sample {s['name']}: type={s['type']} "
                f"group={s.get('group', '-')}")
            for fx in s.get("fixes", []):
                print(f"    [fixed] {fx}", flush=True)
        for w in plan.get("warnings", []):
            log(f"  WARNING: {w}")
        # anndata needed?
        if any(s["type"] == "h5ad" for s in plan["samples"]):
            try:
                import anndata  # noqa: F401
            except ImportError:
                if args.install_deps:
                    subprocess.check_call([sys.executable, "-m", "pip",
                                           "install", "anndata"])
                else:
                    sys.exit("ERROR: h5ad input needs python package 'anndata' "
                             "(pip install anndata, or rerun with --install-deps)")
        mark_done(out, "00.5_inspect")

    # ---------- R stages 01-04 ----------
    common = ["--plan", plan_path, "--output", out,
              "--organism", args.organism]
    stage_args = {
        "01_read": common + ["--min-cells", str(args.min_cells),
                             "--min-features", str(args.min_features)] +
                   (["--mt-pattern", args.mt_pattern] if args.mt_pattern else []),
        "02_qc": common + ["--mt-max", str(args.mt_max),
                           "--max-features", str(args.max_features_qc),
                           "--min-features", str(args.min_features)] +
                 (["--no-doublets"] if args.no_doublets else []),
        "03_cluster": common + ["--integrate", args.integrate,
                                "--resolution", str(args.resolution)] +
                    (["--sct"] if args.sct else []) +
                    (["--no-tsne"] if args.no_tsne else []) +
                    (["--downsample", str(args.downsample)] if args.downsample else []),
        "04_annotate": common +
                       (["--reference", args.reference] if args.reference else []) +
                       (["--custom-ref", args.custom_ref] if args.custom_ref else []) +
                       (["--marker-file", args.marker_file] if args.marker_file else []) +
                       (["--no-annotation"] if args.no_annotation else []),
    }
    for stage, script in [("01_read", "stage01_read.R"),
                          ("02_qc", "stage02_qc.R"),
                          ("03_cluster", "stage03_cluster.R"),
                          ("04_annotate", "stage04_annotate.R")]:
        if args.resume and stage_done(out, stage):
            log(f"{stage}: done, skipping (--resume)")
            continue
        run_r(rscript, script, stage_args[stage], log_path)
        mark_done(out, stage)

    # ---- optional slim export (for COS distribution / sharing)
    if args.export_slim:
        log("exporting slim annotated rds (DietSeurat)")
        run_r(rscript, "export_slim.R",
              ["--rds", os.path.join(out, "annotated_seurat.rds"),
               "--out", os.path.join(out, "annotated_seurat.slim.rds")],
              log_path)

    # ---------- stage 05 : report ----------
    log("stage 05: writing REPORT.md + run_metadata.json")
    import report_writer
    report_writer.write_report(out, plan_path, vars(args))
    mark_done(out, "05_report")
    log(f"ALL DONE. Outputs in {out}")


if __name__ == "__main__":
    main()
