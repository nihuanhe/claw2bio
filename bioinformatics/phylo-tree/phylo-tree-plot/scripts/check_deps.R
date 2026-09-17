# check_deps.R - pre-run dependency check for phylo-tree-plot.
# Run this FIRST (README step 1):  Rscript scripts/check_deps.R
# Checks all 8 packages used by plot_tree_template.R:
#   ggtree/treeio (Bioconductor) + ggplot2/ggnewscale/RColorBrewer/viridis/cowplot/phytools (CRAN).
# Uses requireNamespace() (namespace load), NOT a name lookup: loading a
# namespace validates the package's Imports chain too, so a residual
# bundle/partial install cannot pass this check and then crash at library().
# Exit code: 0 = all loaded, 1 = something missing/broken.
# NOTE: the offline bundle (cos-staging/phylo-tree/deps/r-win/) is built for
# R 4.5.x (Windows binaries); on other R versions use the online install.

cat("R version:", as.character(getRversion()),
    if (getRversion() < "4.5") "- NOTE: offline bundle targets R 4.5.x; use online install\n" else "- OK for the offline bundle\n")

pkgs <- c("ggtree","treeio","ggplot2","ggnewscale","RColorBrewer","viridis","cowplot","phytools")
ok <- vapply(pkgs, function(p) requireNamespace(p, quietly = TRUE), logical(1))
print(data.frame(pkg = pkgs, loaded = unname(ok)))
if (!all(ok)) {
  cat("\nInstall ONLINE (recommended, works on any R version):\n")
  cat("  install.packages(c(\"ggplot2\",\"ggnewscale\",\"RColorBrewer\",\"viridis\",\"cowplot\",\"phytools\"))\n")
  cat("  if (!requireNamespace(\"BiocManager\", quietly = TRUE)) install.packages(\"BiocManager\")\n")
  cat("  BiocManager::install(c(\"ggtree\",\"treeio\"))\n\n")
  cat("Install OFFLINE (Windows, R 4.5.x): see README 'Offline install (Windows)'.\n")
  cat("  Bundle folder (relative to the repo root): cos-staging/phylo-tree/deps/r-win/\n")
  quit(status = 1)
}
cat("ALL OK - phylo-tree-plot is ready to run.\n")
