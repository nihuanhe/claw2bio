#!/usr/bin/env Rscript
# build_pathway_cache.R — one-time download of pathway TERM2GENE tables so that
# enrichment works OFFLINE afterwards (clusterProfiler::enricher with local tables).
#
#   KEGG     : rest.kegg.jp link/list (kept LOCAL — KEGG license forbids redistribution)
#   Reactome : reactome.org NCBI2Reactome (open license — redistributable via COS)
#
# Usage:  Rscript build_pathway_cache.R [--organism mouse|human|both]

parse_args <- function(args) {
  out <- list()
  i <- 1
  while (i <= length(args)) {
    if (startsWith(args[i], "--")) { out[[sub("^--", "", args[i])]] <- args[i + 1]; i <- i + 2 }
    else { out[[length(out) + 1]] <- args[i]; i <- i + 1 }
  }
  out
}
opt <- parse_args(commandArgs(trailingOnly = TRUE))
organism <- if (!is.null(opt$organism)) opt$organism else "both"
options(timeout = 900)   # rest.kegg.jp can be very slow from CN networks

script_dir <- dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1]))
cache_dir <- file.path(script_dir, "..", "resources", "pathway_cache")
dir.create(cache_dir, showWarnings = FALSE, recursive = TRUE)

kegg_codes <- switch(organism, mouse = "mmu", human = "hsa", both = c("mmu", "hsa"))
reactome_species <- switch(organism, mouse = "Mus musculus", human = "Homo sapiens",
                           both = c("Mus musculus", "Homo sapiens"))

# ---------- KEGG (local cache only; do NOT redistribute) ----------
for (code in kegg_codes) {
  cat("KEGG:", code, "\n")
  link <- tryCatch(read.delim(url(sprintf("https://rest.kegg.jp/link/%s/pathway", code)),
                              header = FALSE, colClasses = "character"),
                   error = function(e) NULL)
  lst <- tryCatch(read.delim(url(sprintf("https://rest.kegg.jp/list/pathway/%s", code)),
                             header = FALSE, colClasses = "character"),
                  error = function(e) NULL)
  if (is.null(link) || is.null(lst)) {
    cat("  download failed (offline?) — skipping", code, "\n"); next
  }
  # link: V1 = path:mmuXXXXX, V2 = mmu:ENTREZ
  term2gene <- data.frame(term = sub("^path:", "", link[[1]]),
                          gene = sub(sprintf("^%s:", code), "", link[[2]]))
  term2name <- data.frame(term = sub("^path:", "", lst[[1]]),
                          name = lst[[2]])
  write.csv(term2gene, file.path(cache_dir, sprintf("kegg_%s_term2gene.csv", code)),
            row.names = FALSE)
  write.csv(term2name, file.path(cache_dir, sprintf("kegg_%s_term2name.csv", code)),
            row.names = FALSE)
  cat(sprintf("  %d terms, %d term-gene pairs\n", nrow(term2name), nrow(term2gene)))
}

# ---------- Reactome (open license; redistributable) ----------
rxn_file <- file.path(cache_dir, "NCBI2Reactome.txt")
if (!file.exists(rxn_file)) {
  cat("Reactome: downloading NCBI2Reactome.txt ...\n")
  ok <- tryCatch({
    download.file("https://reactome.org/download/current/NCBI2Reactome.txt",
                  rxn_file, mode = "wb", quiet = TRUE)
    TRUE
  }, error = function(e) FALSE, warning = function(w) FALSE)
  if (!ok) cat("  download failed (offline?) — skipping Reactome\n")
}
if (file.exists(rxn_file)) {
  rxn <- read.delim(rxn_file, header = FALSE, colClasses = "character", quote = "")
  # V1 Entrez gene, V2 Reactome stable ID, V4 pathway name, V6 species
  for (sp in reactome_species) {
    sub <- rxn[rxn[[6]] == sp, ]
    code <- if (sp == "Mus musculus") "mmu" else "hsa"
    term2gene <- data.frame(term = sub[[2]], gene = sub[[1]])
    term2name <- unique(data.frame(term = sub[[2]], name = sub[[4]]))
    write.csv(term2gene, file.path(cache_dir, sprintf("reactome_%s_term2gene.csv", code)),
              row.names = FALSE)
    write.csv(term2name, file.path(cache_dir, sprintf("reactome_%s_term2name.csv", code)),
              row.names = FALSE)
    cat(sprintf("Reactome %s (%s): %d terms, %d pairs\n", code, sp,
                nrow(term2name), nrow(term2gene)))
  }
}

cat("Cache dir:", normalizePath(cache_dir), "\n")
cat("build_pathway_cache done.\n")
