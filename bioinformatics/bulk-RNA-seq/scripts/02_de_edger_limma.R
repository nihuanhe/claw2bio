#!/usr/bin/env Rscript
# 02_de_edger_limma.R — edgeR + limma-voom branch (integer counts, larger n),
# or limma-trend branch (--mode trend) for non-integer / normalized input.
# Mirrors the workflow of the reference tutorial (edgeR filtering + limma).

suppressPackageStartupMessages({
  library(edgeR)
  library(limma)
  library(ggplot2)
  library(ggrepel)
  library(pheatmap)
  library(clusterProfiler)  # for gene ID conversion (bitr)
})

source(file.path(dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1])), "rnaseq_utils.R"))

opt <- parse_args(commandArgs(trailingOnly = TRUE))
counts_path   <- opt[[1]]
metadata_path <- opt[[2]]
outdir        <- opt[[3]]
control       <- if (!is.null(opt$control)) opt$control else NULL
mode          <- if (!is.null(opt$mode)) opt$mode else "voom"   # voom | trend
PADJ_CUTOFF   <<- as.numeric(if (!is.null(opt$padj)) opt$padj else 0.05)
LFC_CUTOFF    <<- as.numeric(if (!is.null(opt$log2fc)) opt$log2fc else 1)
ORGANISM      <- if (!is.null(opt$organism)) opt$organism else "mouse"

dir.create(outdir, showWarnings = FALSE, recursive = TRUE)
inp <- read_inputs(counts_path, metadata_path, control)
group <- inp$group
design <- model.matrix(~ 0 + group)
colnames(design) <- levels(group)

pairs <- build_contrasts(group, control)
cat("Contrasts:", paste(sapply(pairs, function(p) paste0(p[1], "_vs_", p[2])), collapse = ", "), "\n")

if (mode == "trend") {
  # ---- limma-trend: non-integer / already-normalized expression ----
  x <- inp$counts
  if (max(x, na.rm = TRUE) > 50) {
    cat("Values look un-logged (max > 50): applying log2(x + 1).\n")
    x <- log2(x + 1)
  }
  keep <- rowSums(is.finite(x)) == ncol(x)
  x <- x[keep, ]
  cat(sprintf("limma-trend on %d genes\n", nrow(x)))
  norm_mat <- x
  fit <- lmFit(x, design)
  write.csv(data.frame(gene = rownames(x), x, check.names = FALSE),
            file.path(outdir, "normalized_expression.csv"), row.names = FALSE)
} else {
  # ---- edgeR TMM + limma-voom: integer counts ----
  filtered_path <- file.path(outdir, "filtered_counts.csv")
  if (file.exists(filtered_path)) {
    fc <- read.csv(filtered_path, row.names = 1, check.names = FALSE)
    counts <- as.matrix(fc); storage.mode(counts) <- "numeric"
    cat(sprintf("Using QC-filtered counts: %d genes\n", nrow(counts)))
  } else {
    counts <- inp$counts
    counts <- counts[filterByExpr(counts, group = group), ]
    cat(sprintf("filterByExpr: %d genes\n", nrow(counts)))
  }
  dge <- DGEList(counts = counts, group = group)
  dge <- calcNormFactors(dge, method = "TMM")
  v <- voom(dge, design, plot = FALSE)
  norm_mat <- v$E
  fit <- lmFit(v, design)
  write.csv(data.frame(gene = rownames(norm_mat), norm_mat, check.names = FALSE),
            file.path(outdir, "normalized_expression.csv"), row.names = FALSE)
}

# contrasts
contr_str <- sapply(pairs, function(p) paste0(p[1], " - ", p[2]))
contr_mat <- makeContrasts(contrasts = contr_str, levels = design)

resid_df <- ncol(norm_mat) - qr(design)$rank
if (resid_df < 1) {
  # ---- exploratory mode: no residual degrees of freedom (n = 1 per group) ----
  # A linear model cannot estimate variance here; report fold change only,
  # with p values set to NA. The driver prints/REPORTs the loud warning.
  cat("No residual degrees of freedom (n = 1 per group):\n")
  cat("  EXPLORATORY output: fold change only, p values are NA. Do not use for conclusions.\n")
  deg_tables <- list()
  for (pr in pairs) {
    treat <- pr[1]; ref <- pr[2]
    logfc <- rowMeans(norm_mat[, group == treat, drop = FALSE]) -
             rowMeans(norm_mat[, group == ref,   drop = FALSE])
    df <- data.frame(
      gene           = rownames(norm_mat),
      baseMean       = as.numeric(rowMeans(norm_mat)),
      log2FoldChange = as.numeric(logfc),
      stat           = NA_real_,
      pvalue         = NA_real_,
      padj           = NA_real_,
      stringsAsFactors = FALSE
    )
    df <- add_symbols(df, ORGANISM)
    name <- save_deg(df, treat, ref, outdir)
    deg_tables[[name]] <- df
  }
  cat("  (volcano/MA/heatmap skipped: no p values in exploratory mode)\n")
  cat(sprintf("02_de (%s, mode=%s, exploratory) done.\n",
              ifelse(mode == "trend", "limma-trend", "edgeR+limma-voom"), mode))
  quit(save = "no", status = 0)
}

fit2 <- contrasts.fit(fit, contr_mat)
fit2 <- eBayes(fit2, trend = (mode == "trend"), robust = TRUE)

deg_tables <- list()
for (i in seq_along(pairs)) {
  treat <- pairs[[i]][1]; ref <- pairs[[i]][2]
  tt <- topTable(fit2, coef = i, number = Inf, sort.by = "none")
  df <- data.frame(
    gene           = rownames(tt),
    baseMean       = tt$AveExpr,
    log2FoldChange = tt$logFC,
    stat           = tt$t,
    pvalue         = tt$P.Value,
    padj           = tt$adj.P.Val,
    stringsAsFactors = FALSE
  )
  df <- add_symbols(df, ORGANISM)   # gene ID conversion: Ensembl -> Symbol
  name <- save_deg(df, treat, ref, outdir)
  make_volcano(df, treat, ref, outdir)
  make_ma(df, treat, ref, outdir, x_is_log = TRUE)   # AveExpr is log-scale
  deg_tables[[name]] <- df
}

deg_heatmap(norm_mat, deg_tables, group, outdir)
cat(sprintf("02_de (%s, mode=%s) done.\n",
            ifelse(mode == "trend", "limma-trend", "edgeR+limma-voom"), mode))
