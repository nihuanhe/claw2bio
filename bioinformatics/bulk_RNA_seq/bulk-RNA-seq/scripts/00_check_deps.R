#!/usr/bin/env Rscript
# 00_check_deps.R — verify (and optionally install) R package dependencies.
# Runs BEFORE any analysis stage. Exits non-zero if anything is still missing,
# so the driver can stop and let the user choose an installation route.

parse_args <- function(args) {
  out <- list(install = FALSE)
  i <- 1
  while (i <= length(args)) {
    if (args[i] == "--install") { out$install <- TRUE; i <- i + 1 }
    else if (startsWith(args[i], "--")) { out[[sub("^--", "", args[i])]] <- args[i + 1]; i <- i + 2 }
    else { out[[length(out) + 1]] <- args[i]; i <- i + 1 }
  }
  out
}
opt <- parse_args(commandArgs(trailingOnly = TRUE))
organism <- if (!is.null(opt$organism)) opt$organism else "mouse"

bioc_pkgs <- c("DESeq2", "edgeR", "limma")
orgdb <- if (!is.null(opt$orgdb)) opt$orgdb else switch(organism,
         human = "org.Hs.eg.db", rat = "org.Rn.eg.db", "org.Mm.eg.db")
if (!is.null(opt$`gene-map`)) {
  cat("--gene-map supplied: OrgDb package not required.\n")
} else {
  bioc_pkgs <- c(bioc_pkgs, orgdb)
}
cran_pkgs <- c("pheatmap", "ggplot2", "ggrepel", "statmod")  # statmod: duplicateCorrelation (paired designs)

check <- function(pkgs) pkgs[!vapply(pkgs, requireNamespace, logical(1), quietly = TRUE)]

missing_bioc <- check(bioc_pkgs)
missing_cran <- check(cran_pkgs)

cat("Dependency check / 依赖检查 (organism:", organism, ")\n")
for (p in c(bioc_pkgs, cran_pkgs)) {
  cat(sprintf("  %-18s %s\n", p, ifelse(p %in% c(missing_bioc, missing_cran), "MISSING", "ok")))
}

if (length(c(missing_bioc, missing_cran)) == 0) {
  cat("ALL_DEPS_OK\n")
  quit(save = "no", status = 0)
}

if (opt$install) {
  cat("\nInstalling missing packages (BiocManager / CRAN)...\n")
  if (!requireNamespace("BiocManager", quietly = TRUE)) install.packages("BiocManager")
  if (length(missing_bioc) > 0) {
    tryCatch(BiocManager::install(missing_bioc, update = FALSE, ask = FALSE),
             error = function(e) cat("Bioc install error:", conditionMessage(e), "\n"))
  }
  if (length(missing_cran) > 0) {
    tryCatch(install.packages(missing_cran),
             error = function(e) cat("CRAN install error:", conditionMessage(e), "\n"))
  }
  # Re-verify after install
  still <- check(c(bioc_pkgs, cran_pkgs))
  if (length(still) == 0) {
    cat("ALL_DEPS_OK (after install)\n")
    quit(save = "no", status = 0)
  } else {
    cat("STILL_MISSING:", paste(still, collapse = ", "), "\n")
    quit(save = "no", status = 1)
  }
}

cat("MISSING_PACKAGES:", paste(c(missing_bioc, missing_cran), collapse = ", "), "\n")
quit(save = "no", status = 1)
