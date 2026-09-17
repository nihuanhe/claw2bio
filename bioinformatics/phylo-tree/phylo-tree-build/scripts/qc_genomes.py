# -*- coding: utf-8 -*-
"""
qc_genomes.py — QC a directory of genome FASTA files (pure stdlib).

Checks per file: valid FASTA (>=1 header, ACGTN alphabet), sequence count,
total length, N50. Prints an anchor summary line at the end.

Usage (Windows or Linux, Python 3.9+):
    python qc_genomes.py <genomes_dir> [--min-len 1000000] [--expect N]

Exit code 1 if any file fails or --expect mismatches.
"""
import os, sys, argparse

ALLOWED = set("ACGTURYKMSWBDHVNacgturykmswbdhvn-\n\r ")

def parse_fasta(path):
    """Return list of sequence lengths; raise on malformed input."""
    lens, cur, seen_header = [], 0, False
    with open(path, encoding="utf-8", errors="strict") as f:
        for line in f:
            if line.startswith(">"):
                if seen_header:
                    lens.append(cur)
                cur, seen_header = 0, True
            else:
                if not seen_header:
                    raise ValueError("sequence data before first header")
                bad = set(line) - ALLOWED
                if bad:
                    raise ValueError(f"illegal characters: {sorted(bad)[:5]}")
                cur += len(line.strip())
    if seen_header:
        lens.append(cur)
    if not lens:
        raise ValueError("no sequences found")
    return lens

def n50(lens):
    s, half = 0, sum(lens) / 2
    for L in sorted(lens, reverse=True):
        s += L
        if s >= half:
            return L
    return 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("genomes_dir")
    ap.add_argument("--min-len", type=int, default=1_000_000,
                    help="minimum total length per genome (default 1 Mb)")
    ap.add_argument("--expect", type=int, default=0,
                    help="expected number of .fasta files (0 = no check)")
    a = ap.parse_args()

    files = sorted(f for f in os.listdir(a.genomes_dir) if f.endswith((".fasta", ".fa", ".fna")))
    print(f"dir: {a.genomes_dir}")
    print(f"fasta files: {len(files)}")
    if a.expect and len(files) != a.expect:
        print(f"FAIL: expected {a.expect} files, found {len(files)}")
        sys.exit(1)

    ok = True
    for fn in files:
        p = os.path.join(a.genomes_dir, fn)
        try:
            lens = parse_fasta(p)
            tot, n50v = sum(lens), n50(lens)
            flag = ""
            if tot < a.min_len:
                flag = f"  <-- WARN total < {a.min_len}"
                ok = False
            print(f"  {fn}: seqs={len(lens)} total={tot:,} bp N50={n50v:,}{flag}")
        except Exception as e:
            print(f"  {fn}: FAIL ({e})")
            ok = False

    print(f"ANCHOR: files={len(files)} all_pass={ok}")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
