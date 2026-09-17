# extend_r_deps.R — extend the shared r-deps Windows-binary mini-repo with the
# scRNA-seq family closure. Run from the machine that builds the repo
# (R 4.5.x, Windows). Idempotent: existing versions are skipped.
#
# repo layout: resources/r-deps/bin/windows/contrib/4.5/*.zip + PACKAGES index
#
# usage: Rscript extend_r_deps.R <path-to-r-deps>

args <- commandArgs(trailingOnly = TRUE)
repo <- if (length(args)) args[1] else
  "E:/工作/博士后阶段/课题/课题-AI-Openclaw/内容整理/bioinformatics/bulk_RNA_seq/bulk-RNA-seq/resources/r-deps"
contrib <- file.path(repo, "bin/windows/contrib/4.5")
dir.create(contrib, recursive = TRUE, showWarnings = FALSE)

# scRNA-seq family packages (drivers check these)
sc_pkgs <- c(
  # main skill
  "Seurat", "SeuratObject", "harmony", "SingleR", "celldex", "scDblFinder",
  "clustree", "presto", "hdf5r", "data.table", "jsonlite", "patchwork",
  # downstream: pseudotime + virtual-ko
  "monocle3", "pbapply", "scTenifoldNet", "enrichR", "igraph", "reshape2",
  "ggrepel"
)

bioc <- BiocManager::repositories()
want <- intersect(c("BioCsoft", "BioCann", "BioCexp", "BioCwor"), names(bioc))
repos <- c(CRAN = "https://cloud.r-project.org", bioc[want])
cat("using repos:
"); print(repos)

# recursive dependencies
avail <- available.packages(repos = repos)
need <- unique(tools::package_dependencies(sc_pkgs, db = avail,
                                           recursive = TRUE) |> unlist())
need <- union(sc_pkgs, need)
# skip only base/recommended packages (this machine installs everything into
# the system library, so filter by Priority, not by location)
ip <- installed.packages()
skip <- rownames(ip)[ip[, "Priority"] %in% c("base", "recommended")]
need <- setdiff(need, skip)

have <- sub("_.*$", "", list.files(contrib, pattern = "\\.zip$"))
todo <- setdiff(need, have)
cat("closure:", length(need), "| already in repo:", length(intersect(need, have)),
    "| to download:", length(todo), "\n")

# download win binaries (Bioc binaries for R 4.5 live in the 3.21 tree;
# current 3.22 binaries target R 4.6 -> fallback chain)
bioc_bin_321 <- sub("packages/3\\.22", "packages/3.21", repos[want])
if (length(todo)) {
  dl <- download.packages(todo, destdir = contrib, repos = repos,
                          type = "win.binary")
  missing_bin <- setdiff(todo, sub("_.*$", "", basename(dl[, 2])))
  if (length(missing_bin)) {
    cat("retrying via Bioc 3.21 binaries:", paste(missing_bin, collapse = ", "), "\n")
    dl2 <- tryCatch(
      download.packages(missing_bin, destdir = contrib,
                        repos = bioc_bin_321, type = "win.binary"),
      error = function(e) NULL)
    got2 <- if (is.null(dl2)) character() else sub("_.*$", "", basename(dl2[, 2]))
    still <- setdiff(missing_bin, got2)
    if (length(still)) {
      cat("no win.binary at all, fetching source for:", paste(still, collapse = ", "), "\n")
      download.packages(still, destdir = contrib, repos = repos, type = "source")
    }
  }
}
tools::write_PACKAGES(contrib, type = "win.binary")
cat("DONE. repo now has", length(list.files(contrib, pattern = "\\.zip$")),
    "binary zips + PACKAGES index rebuilt\n")
