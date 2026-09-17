#!/bin/bash
# =====================================================================
# 02_iqtree_main.sh — IQ-TREE2 maximum-likelihood backbone tree from the
# bcgTree concatenated core-gene alignment.
#
# [改自 CRE 67-isolate 实战复现包 §8.3.6，仅改动：SRC/WORK 变量化；
#  末尾 tip 计数由稿件专用的株名正则改为通用 tip 名正则]
#
# Model: ModelFinder (best-fit) + 1000 ultrafast bootstraps.
# (The optional parsnp group subtrees use the fixed model -m GTR+F+G
# -B 1000; see 03_parsnp_subtrees.sh.)
#
# Input : $SRC_OUT/main_tree/full_alignment.concat.fa (from 01b)
# Output: $SRC_OUT/main_tree/total_iqtree.treefile (+ full logs)
#
# Usage (inside WSL Ubuntu):
#   bash 02_iqtree_main.sh
# =====================================================================
set -euo pipefail

# ===== ⚠ 路径配置（默认自动定位，与 01/01b 一致）=====
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_OUT="${SRC_OUT:-$SCRIPT_DIR/../examples/output}"
WORK="${WORK:-$HOME/phylo_work}"
# ================================

ALN="$SRC_OUT/main_tree/full_alignment.concat.fa"
if [ ! -s "$ALN" ]; then
  ALN=$(find "$WORK/bcgtree_out" -name "full_alignment.concat.fa" | head -1)
fi
if [ -z "${ALN}" ] || [ ! -s "${ALN}" ]; then
  echo "ERROR: concatenated alignment not found; run 01_run_bcgtree.sh first"; exit 1
fi
echo "==> alignment: $ALN"

mkdir -p "$WORK/iqtree_main"
cd "$WORK/iqtree_main"

echo "==> IQ-TREE2: ModelFinder + 1000 ultrafast bootstraps"
iqtree2 -s "$ALN" -m MFP -B 1000 -nt AUTO --prefix total_iqtree 2>&1 | tee "$SRC_OUT/logs/iqtree_main_$(date +%Y%m%d_%H%M).log"

cp total_iqtree.treefile "$SRC_OUT/main_tree/total_iqtree.treefile"
cp total_iqtree.iqtree "$SRC_OUT/main_tree/" 2>/dev/null || true

echo "==> main tree written to: $SRC_OUT/main_tree/total_iqtree.treefile"
echo "==> tip count check:"
grep -oE '[A-Za-z_][A-Za-z0-9_.-]*:' "$SRC_OUT/main_tree/total_iqtree.treefile" | sort -u | wc -l
