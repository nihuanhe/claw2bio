#!/usr/bin/env bash
# =====================================================================
# check_env.sh - verify-only dependency check for phylo-tree-build
# (WSL2 Ubuntu 24.04). Installs NOTHING: to install missing tools run
# 00_bootstrap_ubuntu.sh first, then re-run this script to re-verify.
#
# Usage (inside WSL Ubuntu, from the scripts/ folder):
#   bash check_env.sh
# Exit code: 0 = all tools present, 1 = something missing.
# =====================================================================
set -uo pipefail

fail=0
check_bin () {  # $1 = command, $2 = install hint
  local name="$1" hint="$2"
  if command -v "$name" >/dev/null 2>&1; then
    echo "OK       $name -> $(command -v "$name")"
  else
    echo "MISSING  $name - install: $hint"
    fail=1
  fi
}

echo "== phylo-tree-build dependency check (WSL2 Ubuntu) =="

# --- apt-side tools (outside conda) ---
check_bin iqtree2 "sudo apt install -y iqtree (Ubuntu 24.04: IQ-TREE 2.0.7)"
check_bin mafft   "sudo apt install -y mafft  (Ubuntu 24.04: 7.505)"
check_bin python3 "sudo apt install -y python3 (needed by patch_bcgtree_gblocks.py)"

# --- conda-side tools (inside the bcgtree env) ---
# Non-interactive bash skips the conda-init block in ~/.bashrc, so source the
# Miniconda profile directly when `conda` is not on PATH (default install path).
if ! command -v conda >/dev/null 2>&1 && [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
  # shellcheck disable=SC1091
  . "$HOME/miniconda3/etc/profile.d/conda.sh"
fi
if command -v conda >/dev/null 2>&1; then
  if conda env list | grep -q '^bcgtree'; then
    ENV_BIN="$(conda info --base)/envs/bcgtree/bin"
    for t in bcgTree.pl parsnp harvesttools; do
      if [ -x "$ENV_BIN/$t" ]; then
        echo "OK       $t (bcgtree env)"
      else
        echo "MISSING  $t - install: conda install -n bcgtree -c bioconda -c conda-forge $t -y"
        fail=1
      fi
    done
  else
    echo "MISSING  conda env 'bcgtree' - install: see 00_bootstrap_ubuntu.sh step [3/4]"
    fail=1
  fi
else
  echo "MISSING  conda - install: see 00_bootstrap_ubuntu.sh step [2/4] (Miniconda)"
  fail=1
fi

echo
if [ "$fail" -eq 0 ]; then
  echo "ALL OK - next: bash 01_run_bcgtree.sh"
else
  echo "INCOMPLETE - fix the MISSING items above (one-time setup: 00_bootstrap_ubuntu.sh)"
fi
exit "$fail"
