# phylo-tree-plot

Publication-ready annotated phylogenetic tree figure from a Newick treefile
+ annotation CSV.

- **Form**: battle-tested R/ggtree template (`scripts/plot_tree_template.R`)
  from a published 67-isolate CRE study. Reuse = copy the template and edit
  only the `CONFIG (EDIT THIS BLOCK)` section. Not a CLI.
- **Style**: midpoint rooting, branch coloring by group, N annotation rings
  with auto palettes, legend grid, 600 dpi PNG + cairo PDF.
- **Example**: 12 public NCBI genomes (tree built by the companion skill
  `phylo-tree-build`).

Read [SKILL.md](SKILL.md) first.

## Dependencies & pre-run check

R (>= 4.1, tested 4.5.2) + 8 packages: ggtree/treeio (Bioconductor) +
ggplot2/ggnewscale/RColorBrewer/viridis/cowplot/phytools (CRAN).

```bash
Rscript scripts/check_deps.R    # step 1: verify; prints install commands if missing
```

## Offline install (Windows, no internet)

Bundle `cos-staging/phylo-tree/deps/r-win/` — 91 binary zips = the full
8-package dependency closure (R 4.5.x Windows; base/recommended packages
that ship with R are not bundled; completeness verified by walking every
staged zip's own DESCRIPTION file). Also on Tencent COS (public read, same
file names as the local `deps/r-win/` tree / `cos-staging/phylo-tree/manifest.csv`):

- COS base URL: `https://my-website-1358159656.cos.ap-guangzhou.myqcloud.com/phylo-tree/deps/r-win/`
- Example direct link (ggtree):
  <https://my-website-1358159656.cos.ap-guangzhou.myqcloud.com/phylo-tree/deps/r-win/ggtree_4.0.5.zip>

```r
zips <- list.files("<absolute path to>/deps/r-win", full.names = TRUE, pattern = "[.]zip$")
for (i in 1:20) {                    # deep chains need many passes (worst case ~11 on clean R 4.5.x)
  have <- rownames(installed.packages())
  todo <- zips[!sub("_.*$", "", basename(zips)) %in% have]
  if (!length(todo)) break
  try(install.packages(todo, repos = NULL, type = "win.binary"), silent = TRUE)
}
```

Then re-run `Rscript scripts/check_deps.R` (expect ALL OK) and follow SKILL.md.
