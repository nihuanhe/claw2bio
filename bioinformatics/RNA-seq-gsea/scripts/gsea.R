#!/usr/bin/env Rscript
# gsea.R — GSEA (fgsea) from a DEG table produced by the bulk-RNA-seq pipeline.
#
# PREREQUISITE: run the bulk-RNA-seq regular pipeline first (counts -> DEG tables).
# This script ranks all genes of a DEG_*.csv by a signed metric and runs fgsea
# against one or more GMT gene-set files (MSigDB format).
#
# Usage:
#   Rscript gsea.R <DEG_table.csv> --gmt file1.gmt[,file2.gmt] \
#          [--organism mouse|human] [--id-type auto|entrez|symbol|ensembl] \
#          [--rank auto|log2fc|stat] [--control-label LABEL] [--outdir DIR]
#
# Default GMTs: all *.gmt found in ../resources/gmt/ (MSigDB files are copied
# there by the user — see resources/README.md; a Reactome demo GMT is bundled).

suppressPackageStartupMessages({
  library(fgsea)
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
deg_file <- opt[[1]]
organism <- if (!is.null(opt$organism)) opt$organism else "mouse"
id_type  <- if (!is.null(opt[["id-type"]])) opt[["id-type"]] else "auto"
rank_by  <- if (!is.null(opt$rank)) opt$rank else "auto"
label    <- if (!is.null(opt[["control-label"]])) opt[["control-label"]] else
            sub("\\.csv$", "", basename(deg_file))
outdir   <- if (!is.null(opt$outdir)) opt$outdir else getwd()
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)

script_dir <- dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1]))
gmt_dir <- file.path(script_dir, "..", "resources", "gmt")
gmt_files <- if (!is.null(opt$gmt)) trimws(strsplit(opt$gmt, ",", fixed = TRUE)[[1]]) else
             list.files(gmt_dir, pattern = "\\.gmt$", full.names = TRUE)
if (length(gmt_files) == 0) stop("no GMT files found — put MSigDB .gmt files into resources/gmt/ (see resources/README.md)")

orgdb_name <- if (organism == "human") "org.Hs.eg.db" else "org.Mm.eg.db"

cat("=== Claw2Bio RNA-seq-gsea ===\n")
cat("DEG table:", basename(deg_file), "\n")
cat("GMT files:", paste(basename(gmt_files), collapse = ", "), "\n")

deg <- read.csv(deg_file, stringsAsFactors = FALSE)
lfc_col <- intersect(c("log2fc", "log2FoldChange", "logFC"), colnames(deg))[1]
if (is.na(lfc_col)) stop("DEG table needs a log2fc / log2FoldChange / logFC column")
deg$log2fc <- deg[[lfc_col]]

# ---- build ranked metric ----
metric <- if (rank_by == "stat" && "stat" %in% colnames(deg)) deg$stat else {
  p <- if ("pvalue" %in% colnames(deg)) deg$pvalue else 10^-deg$padj
  p[p <= 0 | is.na(p)] <- min(p[p > 0], na.rm = TRUE)
  sign(deg$log2fc) * -log10(p)
}
genes <- deg$gene

# ---- ID type detection on our side ----
strip_version <- function(x) sub("\\.[0-9]+$", "", x)
is_ensembl <- mean(grepl("^ENS", genes)) > 0.5
is_symbol  <- !is_ensembl && mean(grepl("^[0-9]+$", genes)) < 0.2

load_orgdb <- function() {
  suppressPackageStartupMessages(library(orgdb_name, character.only = TRUE))
  get(orgdb_name)
}

# convert base (genes, metric) to the ID type used by a given GMT
make_ranks <- function(gmt_file) {
  probe <- strsplit(readLines(gmt_file, n = 1, warn = FALSE), "\t")[[1]][-(1:2)]
  gmt_is_numeric <- all(grepl("^[0-9]+$", probe[!is.na(probe)]))
  g <- genes
  if (gmt_is_numeric) {
    if (is_ensembl) {
      OrgDb <- load_orgdb()
      map <- suppressMessages(AnnotationDbi::select(OrgDb, strip_version(genes),
                                                    "ENTREZID", "ENSEMBL"))
      map <- map[!is.na(map$ENTREZID) & !duplicated(map$ENSEMBL), ]
      g <- map$ENTREZID[match(strip_version(genes), map$ENSEMBL)]
    } else if (is_symbol && "symbol" %in% colnames(deg)) {
      OrgDb <- load_orgdb()
      map <- suppressMessages(AnnotationDbi::select(OrgDb, deg$symbol,
                                                    "ENTREZID", "SYMBOL"))
      map <- map[!is.na(map$ENTREZID) & !duplicated(map$SYMBOL), ]
      g <- map$ENTREZID[match(deg$symbol, map$SYMBOL)]
    }
  } else {
    if ("symbol" %in% colnames(deg)) g <- deg$symbol
    else if (is_ensembl) {
      OrgDb <- load_orgdb()
      map <- suppressMessages(AnnotationDbi::select(OrgDb, strip_version(genes),
                                                    "SYMBOL", "ENSEMBL"))
      map <- map[!is.na(map$SYMBOL) & !duplicated(map$ENSEMBL), ]
      g <- map$SYMBOL[match(strip_version(genes), map$ENSEMBL)]
    }
  }
  keep <- !is.na(g) & !is.na(metric)
  rk <- tapply(metric[keep], g[keep], function(v) v[which.max(abs(v))])
  rk <- rk[order(abs(rk), decreasing = TRUE)]
  rk <- rk[!duplicated(names(rk))]
  attr(rk, "idtype") <- if (gmt_is_numeric) "entrez" else "symbol"
  rk
}

# ---- run fgsea per GMT (rank vector rebuilt per GMT's ID type) ----
for (gf in gmt_files) {
  tag <- sub("\\.gmt$", "", basename(gf))
  ranks <- make_ranks(gf)
  cat(sprintf("GSEA against: %s (%d ranked genes, %s IDs)\n", tag, length(ranks),
              attr(ranks, "idtype")))
  pathways <- gmtPathways(gf)
  set.seed(42)
  res <- tryCatch(fgsea(pathways, ranks, minSize = 10, maxSize = 500,
                        BPPARAM = BiocParallel::SerialParam()),
                  error = function(e) { cat("  failed:", conditionMessage(e), "\n"); NULL })
  if (is.null(res) || nrow(res) == 0) next
  res <- res[order(res$padj), ]
  out_csv <- file.path(outdir, sprintf("GSEA_%s_%s.csv", label, tag))
  res_out <- as.data.frame(res)
  res_out$leadingEdge <- vapply(res$leadingEdge, paste, character(1), collapse = ";")
  write.csv(res_out, out_csv, row.names = FALSE)
  sig <- res[res$padj < 0.05, ]
  cat(sprintf("  significant gene sets (padj<0.05): %d / %d\n", nrow(sig), nrow(res)))
  # summary dotplot: top 15 by padj
  top <- head(res, 15)
  if (nrow(top) > 0) {
    top$direction <- ifelse(top$NES > 0, "up", "down")
    top$pathway <- factor(top$pathway, levels = rev(top$pathway))
    p <- ggplot(top, aes(x = NES, y = pathway, size = -log10(padj), color = direction)) +
      geom_point() +
      scale_color_manual(values = c(up = "#C8181E", down = "#00468B")) +
      labs(title = sprintf("GSEA %s — %s", label, tag), x = "NES", y = NULL) +
      theme_bw()
    ggsave(file.path(outdir, sprintf("GSEA_%s_%s_dotplot.png", label, tag)), p,
           width = 9, height = 6, dpi = 300)
  }
  # classic enrichment curve for the top set
  if (nrow(sig) > 0) {
    topname <- sig$pathway[1]
    pe <- plotEnrichment(pathways[[topname]], ranks) +
      labs(title = sprintf("%s\n%s (NES=%.2f, padj=%.2g)", tag, topname,
                           sig$NES[1], sig$padj[1]))
    ggsave(file.path(outdir, sprintf("GSEA_%s_%s_top_curve.png", label, tag)), pe,
           width = 8, height = 6, dpi = 300)
  }
}
# ---- auto report: file -> purpose ----
report_rules <- list(
  c("^GSEA_.*_dotplot\\.png$", "gsea.R (fgsea)",
    "Top-15 gene sets by padj; x = NES (up=red/down=blue), size = -log10(padj) / NES 气泡图"),
  c("^GSEA_.*_top_curve\\.png$", "gsea.R (fgsea)",
    "Classic enrichment-running-score curve of the top significant set / 顶部通路的经典 GSEA 富集曲线"),
  c("^GSEA_.*\\.csv$", "gsea.R (fgsea)",
    "GSEA result table per GMT (pathway, NES, pvalue, padj, leadingEdge) / GSEA 结果全表")
)
report_files <- setdiff(list.files(outdir), "REPORT.md")
rl <- c("# Analysis Report — RNA-seq-gsea (fgsea + MSigDB GMT)", "",
        sprintf("- DEG table: `%s` (produced by the bulk-RNA-seq regular pipeline)", basename(deg_file)),
        sprintf("- GMT gene sets: %s", paste(basename(gmt_files), collapse = ", ")),
        "- Ranking metric: sign(log2FC) x -log10(pvalue), all genes (no threshold) / 全基因排序，不设阈值",
        "",
        "| File | Produced by | What it is / use |", "|---|---|---|")
for (f in sort(report_files)) {
  hit <- Filter(function(r) grepl(r[1], f), report_rules)
  rl <- c(rl, if (length(hit)) sprintf("| `%s` | %s | %s |", f, hit[[1]][2], hit[[1]][3])
               else sprintf("| `%s` | — | (unclassified output) |", f))
}
rl <- c(rl, "", "_This file is auto-generated by `gsea.R` at the end of every run._", "")
writeLines(rl, file.path(outdir, "REPORT.md"), useBytes = TRUE)

cat("gsea done.\n")
