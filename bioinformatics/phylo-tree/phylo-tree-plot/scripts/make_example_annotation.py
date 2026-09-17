# -*- coding: utf-8 -*-
"""
make_example_annotation.py — build the annotation CSV for the bundled
12-genome example (phylo-tree-plot examples/input/annotation.csv).

Annotation values are public NCBI metadata (species names) plus metrics
computed from the FASTA files themselves (contig count band). Pure stdlib.

Usage (Windows or Linux):
    python make_example_annotation.py <genomes_dir> <out_csv>
"""
import csv, os, sys

# SampleID (= fasta stem = tree tip label) -> (Genus, SpeciesGrp)
META = {
    "Ecoli_K12_MG1655":        ("Escherichia",  "E. coli"),
    "Ecoli_O157H7_Sakai":      ("Escherichia",  "E. coli"),
    "Ecoli_CFT073":            ("Escherichia",  "E. coli"),
    "Ecoli_UMN026":            ("Escherichia",  "E. coli"),
    "Kpneumoniae_NTUH-K2044":  ("Klebsiella",   "K. pneumoniae"),
    "Kpneumoniae_MGH78578":    ("Klebsiella",   "K. pneumoniae"),
    "Kpneumoniae_HS11286":     ("Klebsiella",   "K. pneumoniae"),
    "Kaerogenes_KCTC2190":     ("Klebsiella",   "K. aerogenes"),
    "Ecloacae_ATCC13047":      ("Enterobacter", "E. cloacae complex"),
    "Enterobacter_sp638":      ("Enterobacter", "Enterobacter sp."),
    "Ckoseri_ATCC_BAA-895":    ("Others",       "C. koseri"),
    "Smarcescens_Db11":        ("Others",       "S. marcescens"),
}

def n_seqs(path):
    with open(path, encoding="utf-8", errors="strict") as f:
        return sum(1 for l in f if l.startswith(">"))

def band(n):
    return "1-2" if n <= 2 else ("3-5" if n <= 5 else "6+")

def main():
    gdir, out = sys.argv[1], sys.argv[2]
    rows = []
    for stem, (genus, sp) in sorted(META.items()):
        p = os.path.join(gdir, stem + ".fasta")
        if not os.path.exists(p):
            sys.exit(f"ERROR: missing {p}")
        rows.append([stem, genus, sp, band(n_seqs(p))])
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["SampleID", "Genus", "SpeciesGrp", "ContigBand"])
        w.writerows(rows)
    print(f"annotation written: {out} (n = {len(rows)})")

if __name__ == "__main__":
    main()
