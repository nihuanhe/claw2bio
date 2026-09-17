#!/bin/bash
# =====================================================================
# 01_run_bcgtree.sh — bcgTree core-gene backbone tree input from a
# directory of genome FASTA assemblies.
#
# [改自 CRE 67-isolate 实战复现包 §8.3.4，仅改动：
#   ① SRC/WORK 改为指向本 skill 示例目录（⚠ 换数据改这里）；
#   ② genomes67/ → genomes/，株数校验 67 → EXPECT_N 变量（默认 12）；
#   ③ 删除两株鲍曼剔除校验（项目特定）；
#   ④ 其余逐字保留，含 RAxML 副产物说明见 01b]
#
# Input : $SRC_IN/genomes/ (*.fasta, one per isolate; filename stem = sample ID)
# Output: $WORK/bcgtree_out/ (bcgTree run), concatenated alignment
#         copied back to $SRC_OUT/main_tree/
#
# NOTE: bcgTree/Perl can choke on non-ASCII paths, so the run executes in
# the pure-ASCII working directory $WORK and results are copied back
# afterwards.
#
# Usage (inside WSL Ubuntu, after 00_bootstrap_ubuntu.sh + patch):
#   bash 01_run_bcgtree.sh
# Expected runtime: ~10 min for 12 genomes; ~1-3 h for ~70 genomes.
# =====================================================================
set -euo pipefail

# ===== ⚠ 路径配置（默认自动定位，一般无需改动）=====
# 默认：脚本所在目录的 ../examples/input（读）与 ../examples/output（写），
# 因此本 skill 拷到任何机器/任何路径都能直接跑。
# 换自己的数据时，用环境变量覆盖即可，例如：
#   SRC_IN=/path/to/my_input SRC_OUT=/path/to/my_output bash 01_run_bcgtree.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_IN="${SRC_IN:-$SCRIPT_DIR/../examples/input}"
SRC_OUT="${SRC_OUT:-$SCRIPT_DIR/../examples/output}"
# 目录契约：$SRC_IN/genomes/ 读入；$SRC_OUT/{main_tree,logs}/ 写出
WORK="${WORK:-$HOME/phylo_work}"   # 纯 ASCII 暂存目录（bcgTree/Perl 怕中文路径）
THREADS=14   # 16 logical CPUs; keep 2 free
EXPECT_N=12  # expected number of *.fasta in $SRC_IN/genomes/
# ================================

echo "==> stage genomes into pure-ASCII working dir"
mkdir -p "$WORK/genomes"
rm -rf "$WORK/bcgtree_out"
rm -f "$WORK"/genomes/*.fa "$WORK"/genomes/*.fasta
cp "$SRC_IN"/genomes/*.fasta "$WORK/genomes/"
N=$(ls "$WORK"/genomes/*.fasta | wc -l)
echo "    genomes staged: $N (expect $EXPECT_N)"
if [ "$N" -ne "$EXPECT_N" ]; then echo "ERROR: genome count != $EXPECT_N"; exit 1; fi

# shellcheck disable=SC1091
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate bcgtree

cd "$WORK/genomes"
GENOME_ARGS=""
for file in *.fasta; do
  id=$(basename "$file" .fasta)
  GENOME_ARGS="$GENOME_ARGS --genome $id=$file"
done

echo "==> running bcgTree (this takes a while)"
mkdir -p "$SRC_OUT/logs"
echo "bcgTree.pl --outdir $WORK/bcgtree_out --threads $THREADS $GENOME_ARGS"
bcgTree.pl --outdir "$WORK/bcgtree_out" --threads "$THREADS" $GENOME_ARGS 2>&1 | tee "$SRC_OUT/logs/bcgtree_$(date +%Y%m%d_%H%M).log"

echo "==> locate concatenated alignment"
CONCAT=$(find "$WORK/bcgtree_out" -name "*.concat.fa" -o -name "all.concat.fa" | head -1)
echo "    found: $CONCAT"
mkdir -p "$SRC_OUT/main_tree"
cp "$CONCAT" "$SRC_OUT/main_tree/all.concat.fa"

echo "==> done. Next: bash 01b_finish_alignment.sh"
