# Stage 00 — dependency check for the scRNA-seq pipeline.
# args: --packages pkg1,pkg2,...  [--install]
# Writes .checkpoints/deps.json {pkg: true/false}. Exits 0 always; the python
# driver decides what is fatal.

args <- commandArgs(trailingOnly = TRUE)
get_arg <- function(flag, default = NULL) {
  i <- which(args == flag)
  if (length(i) && i < length(args)) args[i + 1] else default
}
pkgs <- strsplit(get_arg("--packages", ""), ",", fixed = TRUE)[[1]]
do_install <- "--install" %in% args
out_dir <- NULL
oi <- which(args == "--output")
if (length(oi)) out_dir <- args[oi + 1]
ck <- if (!is.null(out_dir)) file.path(out_dir, ".checkpoints") else {
  pi <- which(args == "--plan")
  if (length(pi)) dirname(args[pi + 1]) else file.path(getwd(), ".checkpoints")
}
if (!dir.exists(ck)) dir.create(ck, recursive = TRUE)

status <- setNames(logical(length(pkgs)), pkgs)
for (p in pkgs) {
  ok <- requireNamespace(p, quietly = TRUE)
  if (!ok && do_install) {
    message(sprintf("[stage00] installing %s ...", p))
    tryCatch({
      if (p %in% c("presto")) {
        if (!requireNamespace("remotes", quietly = TRUE)) install.packages("remotes")
        remotes::install_github("immunogenomics/presto", upgrade = "never")
      } else if (p %in% c("SingleR", "celldex", "scDblFinder")) {
        if (!requireNamespace("BiocManager", quietly = TRUE)) install.packages("BiocManager")
        BiocManager::install(p, update = FALSE, ask = FALSE)
      } else {
        install.packages(p, repos = "https://cloud.r-project.org")
      }
    }, error = function(e) message(sprintf("[stage00] install of %s failed: %s", p, e$message)))
    ok <- requireNamespace(p, quietly = TRUE)
  }
  status[p] <- ok
  cat(sprintf("[stage00] %-14s %s\n", p, if (ok) as.character(packageVersion(p)) else "MISSING"))
}

deps_file <- file.path(ck, "deps.json")
if (requireNamespace("jsonlite", quietly = TRUE)) {
  jsonlite::write_json(as.list(status), deps_file, auto_unbox = TRUE)
} else {
  # jsonlite itself may be missing: write minimal JSON by hand
  entries <- sprintf("\"%s\":%s", names(status), tolower(as.character(status)))
  writeLines(paste0("{", paste(entries, collapse = ","), "}"), deps_file)
}
cat(sprintf("[stage00] deps.json written to %s\n", file.path(ck, "deps.json")))
