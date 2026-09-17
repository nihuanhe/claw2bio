"""scRNA-seq-pseudotime driver — monocle3 on the regular pipeline's output.

Usage:
    python scripts/run_pseudotime.py <annotated_seurat.rds> <output_dir> \
        --root-cluster 3            # or --root-label "Naive CD4 T"
        [--subset-labels "Naive CD4 T,Memory CD4 T"]  # subset cells first
        [--resume] [--overwrite] [--rscript PATH]

Prerequisite: run the scRNA-seq regular pipeline first; this skill consumes
its `annotated_seurat.rds` (meta.data: seurat_clusters / cell_type_final).

MEMORY: learn_graph / graph_test are memory-heavy (same league as merge /
integration in the main pipeline). A checkpoint cds rds is written right after
learn_graph; rerun with --resume after a crash to skip cds build + learn_graph.
"""
import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def find_rscript(user_path=None):
    if user_path:
        return user_path
    found = shutil.which("Rscript")
    if found:
        return found
    if os.name == "nt":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\R-core\R")
            return os.path.join(winreg.QueryValueEx(key, "InstallPath")[0],
                                "bin", "Rscript.exe")
        except OSError:
            pass
    sys.exit("ERROR: Rscript not found. Pass --rscript <path>.")


def main():
    ap = argparse.ArgumentParser(description="monocle3 pseudotime on annotated rds")
    ap.add_argument("rds")
    ap.add_argument("output")
    ap.add_argument("--root-cluster", help="cluster id as trajectory root")
    ap.add_argument("--root-label",
                    help="cell_type_final label as root (alternative)")
    ap.add_argument("--subset-labels",
                    help="comma-separated cell_type_final labels to subset first")
    ap.add_argument("--no-graph-test", action="store_true",
                    help="skip graph_test (the slow/memory-heavy step)")
    ap.add_argument("--cores", type=int, default=4)
    ap.add_argument("--resume", action="store_true",
                    help="reuse .checkpoint_cds_learned.rds if present "
                         "(skip cds build + learn_graph)")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--rscript")
    args = ap.parse_args()

    if not args.root_cluster and not args.root_label:
        sys.exit("ERROR: choose the trajectory root: --root-cluster <id> or "
                 "--root-label '<cell_type_final label>'. This is a biological "
                 "decision the pipeline cannot make for you.")
    out = os.path.abspath(args.output)
    if os.path.exists(out) and os.listdir(out) and not (args.overwrite or args.resume):
        sys.exit("ERROR: output dir not empty; use --overwrite or --resume")
    os.makedirs(out, exist_ok=True)
    log_path = os.path.join(out, "pseudotime.log")
    rscript = find_rscript(args.rscript)

    rargs = ["--rds", os.path.abspath(args.rds), "--output", out,
             "--cores", str(args.cores)]
    if args.root_cluster:
        rargs += ["--root-cluster", args.root_cluster]
    if args.root_label:
        rargs += ["--root-label", args.root_label]
    if args.subset_labels:
        rargs += ["--subset-labels", args.subset_labels]
    if args.no_graph_test:
        rargs.append("--no-graph-test")
    if args.resume:
        rargs.append("--resume")

    cmd = [rscript, os.path.join(HERE, "stage_pseudotime.R")] + rargs
    print("[run_pseudotime] R:", " ".join(cmd), flush=True)
    with open(log_path, "a", encoding="utf-8") as lf:
        lf.write("\n===== %s =====\n" % datetime.datetime.now())
        proc = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT)
    if proc.returncode != 0:
        sys.exit(f"ERROR: stage_pseudotime.R failed; see {log_path}")

    # REPORT
    summ = json.load(open(os.path.join(out, "pseudotime_summary.json"),
                          encoding="utf-8"))
    L = ["# scRNA-seq-pseudotime REPORT\n",
         f"- input rds: {args.rds}",
         f"- cells: {summ.get('n_cells')} | root: {summ.get('root')}",
         f"- pseudotime genes (q<0.05): {summ.get('n_pseudotime_genes', 'graph_test skipped')}",
         "\n## Memory / 内存\n",
         "> learn_graph/graph_test 是内存高峰。learn_graph 后自动写 "
         "`.checkpoint_cds_learned.rds`；崩溃后用 `--resume` 复用该检查点"
         "（跳过建 cds 与 learn_graph，成功结束时检查点会自动删除）。",
         "\n## Output files\n",
         "| file | content |", "|---|---|",
         "| `pseudotime_cds.rds` | monocle3 cell_data_set with pseudotime |",
         "| `trajectory_by_pseudotime/cluster/group.*` | trajectory plots |",
         "| `pseudotime_genes.csv` | graph_test result (q<0.05 significant) |",
         "| `pseudotime_summary.json` | machine-readable summary |",
         "\n## Root choice / 起点\n",
         "Root was chosen by the user (biological decision). To redo with another "
         "root, rerun with a different --root-cluster/--root-label."]
    open(os.path.join(out, "REPORT.md"), "w", encoding="utf-8").write("\n".join(L))
    print("[run_pseudotime] DONE. Outputs in", out)


if __name__ == "__main__":
    main()
