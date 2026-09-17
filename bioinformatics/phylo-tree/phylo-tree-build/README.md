# phylo-tree-build

Build a core-genome maximum-likelihood phylogenetic tree (Newick treefile)
from a directory of bacterial genome FASTA assemblies.

- **Pipeline**: bcgTree (core-gene concatenated alignment) → IQ-TREE2
  (`-m MFP -B 1000`) → optional parsnp per-group subtrees.
- **Platform**: WSL2 Ubuntu 24.04 on Windows — screenshot setup guide:
  [docs/wsl-setup.md](docs/wsl-setup.md).
- **Form**: battle-tested template scripts (from a published 67-isolate CRE
  study reproduction package). Paths auto-locate relative to the script;
  override via `SRC_IN` / `SRC_OUT` environment variables — no editing needed.
- **Examples**: 12 public NCBI RefSeq genomes (below).

Read [SKILL.md](SKILL.md) first. Draw the tree with the companion skill
`phylo-tree-plot`.

## Dependencies & pre-run check (WSL2)

One-time environment setup: `bash scripts/00_bootstrap_ubuntu.sh`
(apt: iqtree/mafft; conda env `bcgtree` + parsnp/harvesttools).
Verify WITHOUT installing anything:

```bash
bash scripts/check_env.sh    # verify-only; exit 0 = ready for 01_run_bcgtree.sh
```

The WSL2-side toolchain is GB-scale (apt + conda) and ships as a **link list,
not an offline bundle**: versions, mirrors and upstream URLs in
`cos-staging/phylo-tree/deps_links.md`. (The companion `phylo-tree-plot` DOES
ship an offline R package bundle: `cos-staging/phylo-tree/deps/r-win/`.)

## Example genomes — all PUBLIC NCBI RefSeq assemblies

The 12 assemblies in `examples/input/genomes/` were downloaded from NCBI
with `scripts/download_examples.sh` (NCBI `datasets` CLI), and verified with
`scripts/qc_genomes.py`. Each row links to its NCBI Datasets page
(`https://www.ncbi.nlm.nih.gov/datasets/genome/<accession>/`).

| File stem (SampleID) | Organism | RefSeq accession | NCBI page |
|---|---|---|---|
| Ecoli_K12_MG1655 | Escherichia coli K-12 MG1655 | GCF_000005845.2 | https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_000005845.2/ |
| Ecoli_O157H7_Sakai | Escherichia coli O157:H7 str. Sakai | GCF_000008865.2 | https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_000008865.2/ |
| Ecoli_CFT073 | Escherichia coli CFT073 | GCF_000007445.1 | https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_000007445.1/ |
| Ecoli_UMN026 | Escherichia coli UMN026 | GCF_000026325.1 | https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_000026325.1/ |
| Kpneumoniae_NTUH-K2044 | Klebsiella pneumoniae NTUH-K2044 | GCF_000009885.1 | https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_000009885.1/ |
| Kpneumoniae_MGH78578 | Klebsiella pneumoniae MGH 78578 | GCF_000016305.1 | https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_000016305.1/ |
| Kpneumoniae_HS11286 | Klebsiella pneumoniae HS11286 | GCF_000240185.1 | https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_000240185.1/ |
| Kaerogenes_KCTC2190 | Klebsiella aerogenes KCTC 2190 | GCF_000215745.1 | https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_000215745.1/ |
| Ecloacae_ATCC13047 | Enterobacter cloacae subsp. cloacae ATCC 13047 | GCF_000025565.1 | https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_000025565.1/ |
| Enterobacter_sp638 | Enterobacter sp. 638 | GCF_000016385.1 | https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_000016385.1/ |
| Ckoseri_ATCC_BAA-895 | Citrobacter koseri ATCC BAA-895 | GCF_000018045.1 | https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_000018045.1/ |
| Smarcescens_Db11 | Serratia marcescens Db11 | GCF_000513215.1 | https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_000513215.1/ |

To re-download them (inside WSL or any Linux):

```bash
bash scripts/download_examples.sh
python scripts/qc_genomes.py examples/input/genomes --expect 12
# expect: ANCHOR: files=12 all_pass=True
```
