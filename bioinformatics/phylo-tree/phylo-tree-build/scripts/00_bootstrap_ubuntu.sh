#!/bin/bash
# =====================================================================
# 00_bootstrap_ubuntu.sh — one-time environment setup for phylo-tree-build
# (WSL2 Ubuntu 24.04). Idempotent; safe to re-run.
#
# [改自 CRE 67-isolate 实战复现包 §8.3.3，仅改动：①标题/注释去稿件化；
#  ②apt 加 curl/unzip（下载脚本需要）；③结尾提示补 patch 与 check_env 复核一步]
#
# Toolchain versions as recorded in the original 2026-04-02 ops notes:
#   - IQ-TREE 2.0.7   (apt: iqtree)
#   - MAFFT v7.505    (apt: mafft)
#   - parsnp + harvesttools (bioconda; NOT in Ubuntu 24.04 apt repos)
#   - bcgTree         (conda, bioconda)
#
# Usage (inside WSL Ubuntu):
#   bash 00_bootstrap_ubuntu.sh
# =====================================================================
set -euo pipefail

echo "==> [1/4] apt packages: iqtree (2.0.7), mafft (7.505), wget"
sudo apt update
sudo apt install -y iqtree mafft wget curl unzip
# NOTE: parsnp/harvesttools are not in the Ubuntu 24.04 apt repos;
# they are installed from bioconda in step [3/4] below.

echo "==> versions:"
iqtree2 --version | head -2
mafft --version
parsnp --version 2>/dev/null || parsnp -h | head -2 || true

echo "==> [2/4] Miniconda"
if [ ! -d "$HOME/miniconda3" ]; then
  wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
  bash /tmp/miniconda.sh -b -p "$HOME/miniconda3"
fi
# shellcheck disable=SC1091
source "$HOME/miniconda3/etc/profile.d/conda.sh"

# accept the Anaconda channel Terms of Service (required since conda 25.x)
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main || true
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r || true

echo "==> [3/4] conda env: bcgtree (+ parsnp, harvesttools from bioconda)"
if ! conda env list | grep -q '^bcgtree'; then
  conda create -n bcgtree -c bioconda -c conda-forge bcgtree -y
fi
conda install -n bcgtree -c bioconda -c conda-forge parsnp harvesttools -y
conda activate bcgtree
bcgTree.pl --version 2>/dev/null || bcgTree.pl --help | head -3 || true
parsnp --version 2>/dev/null | head -1 || true

echo "==> [4/4] done. VERIFY (recommended): bash check_env.sh"
echo "    NEXT (once per env): python3 patch_bcgtree_gblocks.py"
echo "    THEN: bash 01_run_bcgtree.sh"
