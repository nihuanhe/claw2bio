#!/bin/bash
# =====================================================================
# download_examples.sh — download the bundled public example genomes
# (12 Enterobacterales assemblies from NCBI RefSeq) for phylo-tree-build.
#
# All genomes are PUBLIC NCBI RefSeq assemblies (no patient data).
# Run inside WSL Ubuntu (or any Linux with bash):
#   bash download_examples.sh [output_dir]
# Default output_dir = <skill>/examples/input/genomes
#
# Requires the NCBI `datasets` CLI; the script offers to install it into
# ~/bin if missing (no root needed).
# =====================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${1:-$SCRIPT_DIR/../examples/input/genomes}"
mkdir -p "$OUT"

# ---- accession = desired file stem (name used downstream as SampleID) ----
# 4 Escherichia / 4 Klebsiella / 2 Enterobacter / 1 Citrobacter / 1 Serratia
read -r -d '' LIST <<'EOF' || true
GCF_000005845.2	Ecoli_K12_MG1655
GCF_000008865.2	Ecoli_O157H7_Sakai
GCF_000007445.1	Ecoli_CFT073
GCF_000026325.1	Ecoli_UMN026
GCF_000009885.1	Kpneumoniae_NTUH-K2044
GCF_000016305.1	Kpneumoniae_MGH78578
GCF_000240185.1	Kpneumoniae_HS11286
GCF_000215745.1	Kaerogenes_KCTC2190
GCF_000025565.1	Ecloacae_ATCC13047
GCF_000016385.1	Enterobacter_sp638
GCF_000018045.1	Ckoseri_ATCC_BAA-895
GCF_000513215.1	Smarcescens_Db11
EOF

# ---- datasets CLI ----
if ! command -v datasets >/dev/null 2>&1; then
  echo "==> NCBI datasets CLI not found; installing into ~/bin"
  mkdir -p "$HOME/bin"
  curl -fsSL "https://ftp.ncbi.nlm.nih.gov/pub/datasets/command-line/v2/linux-amd64/datasets" -o "$HOME/bin/datasets"
  chmod +x "$HOME/bin/datasets"
  export PATH="$HOME/bin:$PATH"
fi
datasets version

echo "==> downloading into: $OUT"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

fail=0
while IFS=$'\t' read -r acc name; do
  [ -z "$acc" ] && continue
  if [ -s "$OUT/$name.fasta" ]; then
    echo "    [skip] $name.fasta exists"
    continue
  fi
  echo "==> $acc -> $name.fasta"
  if ! datasets download genome accession "$acc" --include genome --filename "$TMP/$name.zip"; then
    echo "    [FAIL] download $acc"; fail=1; continue
  fi
  unzip -o -q "$TMP/$name.zip" -d "$TMP/$name"
  fa=$(find "$TMP/$name" -name "*.fna" | head -1)
  if [ -z "$fa" ]; then echo "    [FAIL] no .fna in $acc package"; fail=1; continue; fi
  cp "$fa" "$OUT/$name.fasta"
done <<< "$LIST"

N=$(ls "$OUT"/*.fasta 2>/dev/null | wc -l)
echo "==> done: $N fasta files in $OUT"
[ "$fail" -eq 0 ] || { echo "WARNING: some accessions failed (see [FAIL] lines)"; exit 1; }
