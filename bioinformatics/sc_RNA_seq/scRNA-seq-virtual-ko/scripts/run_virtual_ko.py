"""scRNA-seq-virtual-ko driver — scTenifoldKnk virtual knockout.

Usage:
    python scripts/run_virtual_ko.py <annotated_seurat.rds> <output_dir> \
        --gene TP53 [--subset-labels "T cells"] [--nfeatures 2000] [--all-genes]

Prerequisite: run the scRNA-seq regular pipeline first; this skill consumes
its `annotated_seurat.rds` (uses the RNA counts layer; optional pre-subset by
cell_type_final labels so the knockout network is built from the cell type
you care about).
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
    ap = argparse.ArgumentParser(description="scTenifoldKnk virtual knockout")
    ap.add_argument("rds")
    ap.add_argument("output")
    ap.add_argument("--gene", required=True, help="gene to virtually knock out")
    ap.add_argument("--subset-labels",
                    help="comma-separated cell_type_final labels to subset first")
    ap.add_argument("--nfeatures", type=int, default=2000,
                    help="variable genes for network construction (default 2000)")
    ap.add_argument("--all-genes", action="store_true",
                    help="use all genes (slow, memory-heavy)")
    ap.add_argument("--nc-nnet", type=int, default=10,
                    help="number of subsampled networks to average (default 10)")
    ap.add_argument("--nc-ncells", type=int, default=500,
                    help="cells per subsampled network (package default 500; "
                         "0 = all cells — WARNING: runtime is ~quadratic in "
                         "genes x cells, all-cells is only safe for tiny inputs)")
    ap.add_argument("--cores", type=int, default=0,
                    help="cores (default: detectCores()-1)")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--rscript")
    args = ap.parse_args()

    out = os.path.abspath(args.output)
    if os.path.exists(out) and os.listdir(out) and not args.overwrite:
        sys.exit("ERROR: output dir not empty; use --overwrite")
    os.makedirs(out, exist_ok=True)
    log_path = os.path.join(out, "virtual_ko.log")
    rscript = find_rscript(args.rscript)

    rargs = ["--rds", os.path.abspath(args.rds), "--output", out,
             "--gene", args.gene, "--nfeatures", str(args.nfeatures),
             "--nc-nnet", str(args.nc_nnet), "--nc-ncells", str(args.nc_ncells),
             "--cores", str(args.cores)]
    if args.subset_labels:
        rargs += ["--subset-labels", args.subset_labels]
    if args.all_genes:
        rargs.append("--all-genes")

    cmd = [rscript, os.path.join(HERE, "stage_virtual_ko.R")] + rargs
    print("[run_virtual_ko] R:", " ".join(cmd), flush=True)
    with open(log_path, "a", encoding="utf-8") as lf:
        lf.write("\n===== %s =====\n" % datetime.datetime.now())
        proc = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT)
    if proc.returncode != 0:
        sys.exit(f"ERROR: stage_virtual_ko.R failed; see {log_path}")

    summ = json.load(open(os.path.join(out, "virtual_ko_summary.json"),
                          encoding="utf-8"))
    L = ["# scRNA-seq-virtual-ko REPORT\n",
         f"- input rds: {args.rds}",
         f"- knocked-out gene: **{summ.get('gene')}** "
         f"(expression rank in data: {summ.get('gene_expr_rank', 'NA')})",
         f"- cells used: {summ.get('n_cells')} | genes in network: "
         f"{summ.get('n_genes')} | networks averaged: {summ.get('nc_nnet')}",
         f"- significant differentially regulated (p_adj<0.05): "
         f"{summ.get('n_significant')}",
         "\n## 注意\n",
         "> 虚拟敲除是**计算预测**（基于基因调控网络的扰动模拟），"
         "结果需实验验证；目标基因表达太低时结果不可靠（见上行 rank）。",
         "\n## Output files\n",
         "| file | content |", "|---|---|",
         "| `<GENE>_diffRegulation.csv` | full scTenifoldKnk result table |",
         "| `<GENE>_barplot_top20.png/pdf` | top-20 |FC| genes |",
         "| `<GENE>_zscore_scatter.png/pdf` | Z-score vs -log10(p_adj) |",
         "| `virtual_ko_summary.json` | machine-readable summary |"]
    open(os.path.join(out, "REPORT.md"), "w", encoding="utf-8").write("\n".join(L))
    print("[run_virtual_ko] DONE. Outputs in", out)


if __name__ == "__main__":
    main()
