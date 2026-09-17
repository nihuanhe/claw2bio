#!/bin/bash
# =====================================================================
# 03_parsnp_subtrees.sh — OPTIONAL: parsnp core-SNP + IQ-TREE2 subtree per
# group (e.g. per genus). The main tree (02) usually suffices; subtrees give
# finer within-group resolution for plotting/grafting.
#
# [改自 CRE 67-isolate 实战复现包 §8.3.7，仅改动：
#   ① SRC/WORK/ANN/属清单 抽成头部变量（⚠ 换数据改这里）；
#   ② 分组来源由 wgs67.csv 第 2 列前缀匹配 改为 通用两列 CSV 精确匹配；
#   ③ parsnp174 环境降级为"如 1.5.2 segfault 再建"的备选说明；
#   ④ 其余逐字保留]
#
# ⚠ parsnp 版本实战记录（保留自原流程）：bioconda 默认 parsnp 1.5.2 在
# 原作者机上 segfault；当时的解法是另建 conda 环境 parsnp174
# (parsnp 1.7.4)。本模板默认用 bcgtree 环境内 bioconda 新装的 parsnp；
# 若你的机器 segfault，执行：
#   conda create -n parsnp174 -c bioconda parsnp=1.7.4 -y
# 并把下面 conda activate 改为 parsnp174。
#
# Model for the subtree ML trees: iqtree2 -m GTR+F+G -B 1000 on the parsnp
# core-SNP alignment.
#
# Usage (inside WSL Ubuntu, after 01_run_bcgtree.sh):
#   bash 03_parsnp_subtrees.sh
# =====================================================================
set -euo pipefail

# ===== ⚠ 路径配置（默认自动定位，与 01 一致）=====
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_IN="${SRC_IN:-$SCRIPT_DIR/../examples/input}"
SRC_OUT="${SRC_OUT:-$SCRIPT_DIR/../examples/output}"
WORK="${WORK:-$HOME/phylo_work}"
# 分组文件：两列 CSV（表头 SampleID,Group；Group 例：属名）
ANN="${ANN:-$SRC_IN/annotation.csv}"
# 要建子树的组（空格分隔；组内 <3 株自动跳过）
GENERA="Escherichia Klebsiella Enterobacter"
# ==========================

# shellcheck disable=SC1091
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate bcgtree   # 若 segfault 见头部说明改 parsnp174

group_members () {
  # $1 = group name; prints matching SampleIDs
  awk -F',' -v g="$1" 'NR>1 && $2 == g {print $1}' "$ANN"
}

for GENUS in $GENERA; do
  GDIR="$WORK/parsnp_$GENUS"
  mkdir -p "$GDIR"
  rm -f "$GDIR"/*.fasta
  echo "==> $GENUS:"
  for id in $(group_members "$GENUS"); do
    cp "$WORK/genomes/$id.fasta" "$GDIR/" 2>/dev/null || echo "    [WARN] no fasta for $id"
  done
  N=0; for f in "$GDIR"/*.fasta; do [ -e "$f" ] && N=$((N+1)); done
  echo "    isolates: $N"
  if [ "$N" -lt 3 ]; then echo "    skip (<3 genomes)"; continue; fi

  cd "$GDIR"
  echo "    parsnp..."
  parsnp -c -r ! -d . -p 12 2>&1 | tee "$SRC_OUT/logs/parsnp_${GENUS}.log"
  XMFA=$(find . -name "parsnp.xmfa" | head -1)
  harvesttools -x "$XMFA" -S parsnp.core.snps.fasta

  echo "    iqtree2 (GTR+F+G, 1000 UFBoot)..."
  iqtree2 -s parsnp.core.snps.fasta -nt AUTO -m GTR+F+G -B 1000 --prefix "${GENUS}" 2>&1 | tee "$SRC_OUT/logs/iqtree_${GENUS}.log"

  mkdir -p "$SRC_OUT/subtrees"
  cp "${GENUS}.treefile" "$SRC_OUT/subtrees/${GENUS}.treefile"
done

echo "==> subtrees written to: $SRC_OUT/subtrees/"
