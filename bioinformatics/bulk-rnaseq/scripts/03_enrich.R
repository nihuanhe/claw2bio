#!/usr/bin/env Rscript
# 03_enrich.R — clusterProfiler GO / KEGG enrichment for every DEG table.
# Engine-agnostic: consumes the DEG_*.csv files produced by stage 02.
# Missing databases / offline KEGG are skipped with a message, never fatal.

suppressPackageStartupMessages({
  library(clusterProfiler)
  library(DOSE)
  library(ggplot2)
})

parse_args <- function(args) {
  out <- list()
  i <- 1
  while (i <= length(args)) {
    if (startsWith(args[i], "--")) {
      key <- sub("^--", "", args[i]); out[[key]] <- args[i + 1]; i <- i + 2
    } else { out[[length(out) + 1]] <- args[i]; i <- i + 1 }
  }
  out
}
opt <- parse_args(commandArgs(trailingOnly = TRUE))
deg_dir  <- opt[[1]]
outdir   <- opt[[2]]
organism <- if (!is.null(opt$organism)) opt$organism else "mouse"
padj_cut <- as.numeric(if (!is.null(opt$padj)) opt$padj else 0.05)
lfc_cut  <- as.numeric(if (!is.null(opt$log2fc)) opt$log2fc else 1)

orgdb_name <- if (organism == "human") "org.Hs.eg.db" else "org.Mm.eg.db"
kegg_code  <- if (organism == "human") "hsa" else "mmu"

if (!requireNamespace(orgdb_name, quietly = TRUE)) {
  cat(sprintf("OrgDb package %s not installed — skipping enrichment.\n", orgdb_name))
  cat(sprintf("Install with: BiocManager::install(\"%s\")\n", orgdb_name))
  quit(save = "no", status = 0)
}
OrgDb <- getNamespace(orgdb_name)

to_entrez <- function(genes) {
  ids <- genes
  keytype <- "SYMBOL"
  if (mean(grepl("^ENS", ids)) > 0.5) {
    ids <- gsub("\\..*", "", ids)   # strip Ensembl version suffix
    keytype <- "ENSEMBL"
  }
  conv <- tryCatch(
    bitr(ids, fromType = keytype, toType = "ENTREZID", OrgDb = orgdb_name),
    error = function(e) NULL)
  if (is.null(conv)) return(NULL)
  conv$ENTREZID
}

run_one <- function(entrez, label) {
  if (is.null(entrez) || length(entrez) < 5) {
    cat(sprintf("  %s: too few mapped genes (%d), skipped\n", label, length(entrez)))
    return(invisible(NULL))
  }
  # GO BP/MF/CC
  for (ont in c("BP", "MF", "CC")) {
    eg <- tryCatch(
      enrichGO(entrez, OrgDb = orgdb_name, ont = ont, pAdjustMethod = "BH",
               pvalueCutoff = 0.05, qvalueCutoff = 0.2, readable = TRUE),
      error = function(e) NULL)
    if (!is.null(eg) && nrow(as.data.frame(eg)) > 0) {
      write.csv(as.data.frame(eg), file.path(outdir, sprintf("GO_%s_%s.csv", label, ont)),
                row.names = FALSE)
      p <- dotplot(eg, showCategory = 15, title = sprintf("GO %s — %s", ont, label))
      ggsave(file.path(outdir, sprintf("GO_%s_%s_dotplot.png", label, ont)), p,
             width = 9, height = 7, dpi = 300)
    }
  }
  # KEGG (needs network for KEGG REST)
  kk <- tryCatch(
    enrichKEGG(entrez, organism = kegg_code, pAdjustMethod = "BH", pvalueCutoff = 0.05),
    error = function(e) { cat(sprintf("  %s: KEGG skipped (%s)\n", label, conditionMessage(e))); NULL })
  if (!is.null(kk) && nrow(as.data.frame(kk)) > 0) {
    write.csv(as.data.frame(kk), file.path(outdir, sprintf("KEGG_%s.csv", label)),
              row.names = FALSE)
    p <- dotplot(kk, showCategory = 15, title = sprintf("KEGG — %s", label))
    ggsave(file.path(outdir, sprintf("KEGG_%s_dotplot.png", label)), p,
           width = 9, height = 7, dpi = 300)
  }
}

deg_files <- list.files(deg_dir, pattern = "^DEG_.*\\.csv$", full.names = TRUE)
if (length(deg_files) == 0) {
  cat("No DEG_*.csv found in", deg_dir, "— nothing to enrich.\n")
  quit(save = "no", status = 0)
}

for (f in deg_files) {
  contrast <- sub("\\.csv$", "", basename(f))
  df <- read.csv(f, stringsAsFactors = FALSE)
  ok <- !is.na(df$padj) & !is.na(df$log2FoldChange)
  up   <- df$gene[ok & df$padj < padj_cut & df$log2FoldChange >  lfc_cut]
  down <- df$gene[ok & df$padj < padj_cut & df$log2FoldChange < -lfc_cut]
  cat(sprintf("%s: %d up, %d down significant genes\n", contrast, length(up), length(down)))
  run_one(to_entrez(up),   paste0(contrast, "_up"))
  run_one(to_entrez(down), paste0(contrast, "_down"))
}

cat("03_enrich done.\n")
