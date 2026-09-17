# REPORT — phylo-tree-build example run (2026-09-16)

Example: 12 public NCBI RefSeq Enterobacterales genomes
(4 Escherichia / 4 Klebsiella / 2 Enterobacter / 1 Citrobacter / 1 Serratia).
No patient data. Input preparation: `scripts/download_examples.sh` (NCBI
datasets CLI) + `scripts/qc_genomes.py` — QC anchor: `files=12 all_pass=True`.

## Pipeline actually executed (WSL2 Ubuntu 24.04)

1. `patch_bcgtree_gblocks.py` — one-time bcgTree↔Gblocks fix: OK
2. `01_run_bcgtree.sh` — bcgTree 1.2.1, 12 genomes, 14 threads: core-gene
   collection (107 gene sets) + muscle + Gblocks + concatenation
3. `01b_finish_alignment.sh` — anchors: `alignment sequences: 12 (expect 12)`,
   `alignment length: 35808 bp`; bcgTree-internal RAxML byproduct stopped
4. `02_iqtree_main.sh` — IQ-TREE 2.0.7 `-m MFP -B 1000`: best-fit model +
   1000 ultrafast bootstraps (tree search 42 s wall-clock)
5. `03_parsnp_subtrees.sh` — parsnp 2.0.3 + IQ-TREE2 (GTR+F+G, 1000 UFBoot)
   for Escherichia (n=4) and Klebsiella (n=4); Enterobacter skipped (n=2 < 3,
   by design)

## Output files

| File | Produced by | Purpose |
|---|---|---|
| `main_tree/full_alignment.concat.fa` | 01/01b (bcgTree) | Concatenated core-gene alignment (12 seqs × 35,808 bp) — the only bcgTree product used downstream |
| `main_tree/full_alignment.concat.partition` | 01b | Per-gene partition map for the alignment |
| `main_tree/all.concat.fa` | 01 | Raw pre-Gblocks concatenation (kept for provenance) |
| `main_tree/total_iqtree.treefile` | 02 (IQ-TREE2) | **Main deliverable**: ML backbone tree (Newick, 12 tips, UFBoot supports) — input for `phylo-tree-plot` |
| `main_tree/total_iqtree.iqtree` | 02 | Full IQ-TREE report (model, likelihood, bootstrap stats) |
| `subtrees/Escherichia.treefile` | 03 (parsnp+IQ-TREE2) | Within-genus subtree (4 tips) |
| `subtrees/Klebsiella.treefile` | 03 | Within-genus subtree (4 tips) |
| `logs/` | 01–03 | Timestamped bcgTree / IQ-TREE / parsnp console logs (audit trail) |

Note: tip labels = FASTA filename stems; these are the SampleID keys for the
annotation CSV consumed by `phylo-tree-plot`.
