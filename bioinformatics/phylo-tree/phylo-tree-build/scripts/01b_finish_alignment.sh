#!/bin/bash
# =====================================================================
# 01b_finish_alignment.sh — finish step 01 manually: copy the concatenated
# alignment (the only bcgTree product used downstream) into main_tree/ and
# print the sequence count + alignment length as acceptance anchors.
#
# [改自 CRE 67-isolate 实战复现包 §8.3.5，仅改动：SRC/WORK 变量化 +
#  株数锚点 67 → EXPECT_N；其余逐字保留，含 pkill RAxML 副产物]
#
# bcgTree's internal RAxML tree is a default byproduct that this pipeline
# does not use (the tree is built with IQ-TREE2 instead), so RAxML is
# stopped here.
#
# Usage (inside WSL Ubuntu, after 01_run_bcgtree.sh):
#   bash 01b_finish_alignment.sh
# =====================================================================
set -euo pipefail

# ===== ⚠ 路径配置（默认自动定位，与 01 一致）=====
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_OUT="${SRC_OUT:-$SCRIPT_DIR/../examples/output}"
WORK="${WORK:-$HOME/phylo_work}"
EXPECT_N=12
# ==========================================

mkdir -p "$SRC_OUT/main_tree"   # (added) original flow assumed it already existed
cp "$WORK/bcgtree_out/full_alignment.concat.fa" "$SRC_OUT/main_tree/"
cp "$WORK/bcgtree_out/full_alignment.concat.partition" "$SRC_OUT/main_tree/"
cp "$WORK/bcgtree_out/all.concat.fa" "$SRC_OUT/main_tree/" 2>/dev/null || true

echo "alignment sequences: $(grep -c '>' "$SRC_OUT/main_tree/full_alignment.concat.fa") (expect $EXPECT_N)"
echo "alignment length: $(head -2 "$SRC_OUT/main_tree/full_alignment.concat.fa" | tail -1 | tr -d '\n' | wc -c) bp"

# stop the bcgTree-internal RAxML (byproduct; not used downstream)
pkill -f raxmlHPC || true
sleep 2
pgrep -f raxmlHPC || echo "RAxML stopped"

echo "==> done. Next: bash 02_iqtree_main.sh"
