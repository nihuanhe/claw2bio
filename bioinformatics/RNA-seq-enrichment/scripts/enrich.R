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
offline  <- !is.null(opt$offline)
options(timeout = 600)
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)

orgdb_name <- if (organism == "human") "org.Hs.eg.db" else "org.Mm.eg.db"
kegg_code  <- if (organism == "human") "hsa" else "mmu"

script_dir <- dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1]))
cache_dir <- file.path(script_dir, "..", "resources", "pathway_cache")
load_cache <- function(prefix) {
  t2g <- file.path(cache_dir, sprintf("%s_%s_term2gene.csv", prefix, kegg_code))
  t2n <- file.path(cache_dir, sprintf("%s_%s_term2name.csv", prefix, kegg_code))
  if (!file.exists(t2g)) return(NULL)
  t2g <- read.csv(t2g, colClasses = "character")
  t2n <- if (file.exists(t2n)) read.csv(t2n, colClasses = "character") else NULL
  list(t2g = t2g, t2n = t2n)
}

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
  # KEGG — online REST first (unless --offline), local cache fallback
  kk <- NULL
  if (!offline) {
    kk <- tryCatch(
      enrichKEGG(entrez, organism = kegg_code, pAdjustMethod = "BH", pvalueCutoff = 0.05),
      error = function(e) { cat(sprintf("  %s: KEGG online failed (%s) — trying local cache\n",
                                        label, conditionMessage(e))); NULL })
  }
  if (is.null(kk)) {
    cache <- load_cache("kegg")
    if (!is.null(cache)) {
      kk <- tryCatch(
        enricher(entrez, TERM2GENE = cache$t2g, TERM2NAME = cache$t2n,
                 pAdjustMethod = "BH", pvalueCutoff = 0.05),
        error = function(e) NULL)
      if (!is.null(kk)) cat(sprintf("  %s: KEGG via OFFLINE cache\n", label))
    } else if (offline) {
      cat(sprintf("  %s: --offline and no KEGG cache found (run build_pathway_cache.R)\n", label))
    }
  }
  if (!is.null(kk) && nrow(as.data.frame(kk)) > 0) {
    write.csv(as.data.frame(kk), file.path(outdir, sprintf("KEGG_%s.csv", label)),
              row.names = FALSE)
    p <- dotplot(kk, showCategory = 15, title = sprintf("KEGG — %s", label))
    ggsave(file.path(outdir, sprintf("KEGG_%s_dotplot.png", label)), p,
           width = 9, height = 7, dpi = 300)
  }
  # Reactome — fully offline via local cache (open-license tables)
  rcache <- load_cache("reactome")
  if (!is.null(rcache)) {
    rr <- tryCatch(
      enricher(entrez, TERM2GENE = rcache$t2g, TERM2NAME = rcache$t2n,
               pAdjustMethod = "BH", pvalueCutoff = 0.05),
      error = function(e) NULL)
    if (!is.null(rr) && nrow(as.data.frame(rr)) > 0) {
      write.csv(as.data.frame(rr), file.path(outdir, sprintf("Reactome_%s.csv", label)),
                row.names = FALSE)
      p <- dotplot(rr, showCategory = 15, title = sprintf("Reactome — %s", label))
      ggsave(file.path(outdir, sprintf("Reactome_%s_dotplot.png", label)), p,
             width = 9, height = 7, dpi = 300)
    }
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

# ---- auto report: file -> purpose ----
report_rules <- list(
  c("^GO_.*_dotplot\\.png$", "enrich.R (GO, clusterProfiler, offline via OrgDb)",
    "GO enrichment dotplot (top terms, one ontology per file) / GO 富集气泡图"),
  c("^GO_.*\\.csv$", "enrich.R (GO, clusterProfiler, offline via OrgDb)",
    "GO enrichment table for one contrast x direction x ontology (BP/MF/CC) / GO 富集结果表"),
  c("^KEGG_.*_dotplot\\.png$", "enrich.R (KEGG, online REST or local cache)",
    "KEGG pathway dotplot / KEGG 气泡图"),
  c("^KEGG_.*\\.csv$", "enrich.R (KEGG, online REST or local cache)",
    "KEGG pathway enrichment table / KEGG 富集结果表"),
  c("^Reactome_.*_dotplot\\.png$", "enrich.R (Reactome, offline cache)",
    "Reactome pathway dotplot / Reactome 气泡图"),
  c("^Reactome_.*\\.csv$", "enrich.R (Reactome, offline cache)",
    "Reactome pathway enrichment table / Reactome 富集结果表")
)
report_files <- setdiff(list.files(outdir), "REPORT.md")
rl <- c("# Analysis Report — RNA-seq-enrichment (GO / KEGG / Reactome)", "",
        sprintf("- Input: DEG tables in `%s` (produced by the bulk-RNA-seq regular pipeline)", basename(deg_dir)),
        sprintf("- Organism: %s; cutoffs: padj < %g, |log2FC| > %g", organism, padj_cut, lfc_cut),
        "- Gene sets: up/down per contrast, analyzed separately / 每个对比的上下调分开做",
        "",
        "| File | Produced by | What it is / use |", "|---|---|---|")
for (f in sort(report_files)) {
  hit <- Filter(function(r) grepl(r[1], f), report_rules)
  rl <- c(rl, if (length(hit)) sprintf("| `%s` | %s | %s |", f, hit[[1]][2], hit[[1]][3])
               else sprintf("| `%s` | — | (unclassified output) |", f))
}
rl <- c(rl, "", "_This file is auto-generated by `enrich.R` at the end of every run._", "")
writeLines(rl, file.path(outdir, "REPORT.md"), useBytes = TRUE)

cat("03_enrich done.
")
