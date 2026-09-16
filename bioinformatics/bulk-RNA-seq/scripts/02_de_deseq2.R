#!/usr/bin/env Rscript
# 02_de_deseq2.R — DESeq2 differential expression branch.
# Refactored from the lab's battle-tested arsenal (D:\R1\R_RNA-seq).
# Selected automatically for integer counts with small group sizes.

suppressPackageStartupMessages({
  library(DESeq2)
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
PADJ_CUTOFF   <<- as.numeric(if (!is.null(opt$padj)) opt$padj else 0.05)
LFC_CUTOFF    <<- as.numeric(if (!is.null(opt$log2fc)) opt$log2fc else 1)
ORGANISM      <- if (!is.null(opt$organism)) opt$organism else "mouse"
PAIRWISE_MAX  <- as.integer(if (!is.null(opt$`pairwise-max`)) opt$`pairwise-max` else 4)
CONTRASTS     <- opt$contrasts

dir.create(outdir, showWarnings = FALSE, recursive = TRUE)
inp <- read_inputs(counts_path, metadata_path, control)

# Use pre-filtered counts from 01_qc when available (same gene set as QC plots)
filtered_path <- file.path(outdir, "filtered_counts.csv")
if (file.exists(filtered_path)) {
  fc <- read.csv(filtered_path, row.names = 1, check.names = FALSE)
  counts <- as.matrix(fc)
  storage.mode(counts) <- "numeric"
  counts <- round(counts)  # DESeq2 requires integers; values here are already integer
  cat(sprintf("Using QC-filtered counts: %d genes\n", nrow(counts)))
} else {
  counts <- round(inp$counts)
  keep <- rowSums(counts >= 10) >= 2
  counts <- counts[keep, ]
  cat(sprintf("Fallback filtering (>=10 reads in >=2 samples): %d genes\n", nrow(counts)))
}

col_data <- data.frame(group = inp$group)
rownames(col_data) <- colnames(counts)
subject <- get_covariate(inp$meta, opt[["paired-by"]], inp$group, "Paired-by (subject)")
batch   <- get_covariate(inp$meta, opt$batch, inp$group, "Batch")
terms <- c()
if (!is.null(subject)) { col_data$subject <- subject; terms <- c(terms, "subject") }
if (!is.null(batch))   { col_data$batch   <- batch;   terms <- c(terms, "batch") }
terms <- c(terms, "group")
design_f <- as.formula(paste("~", paste(terms, collapse = " + ")))
cat("Design formula:", deparse(design_f), "\n")

dds <- DESeqDataSetFromMatrix(countData = counts, colData = col_data, design = design_f)
dds <- DESeq(dds)
cat("DESeq2 model fitted.\n")

# vst-normalized values for heatmap / downstream skills (canonical name).
# vst() needs >= nsub (1000) genes for its dispersion fit; small/targeted
# matrices fall back to rlog (fine at that scale).
vsd <- tryCatch(
  vst(dds, blind = FALSE),
  error = function(e) {
    cat(sprintf("  vst failed (%s) — falling back to rlog\n", conditionMessage(e)))
    rlog(dds, blind = FALSE)
  })
write.csv(data.frame(gene = rownames(assay(vsd)), assay(vsd), check.names = FALSE),
          file.path(outdir, "normalized_expression.csv"), row.names = FALSE)

pairs <- build_contrasts(inp$group, control, PAIRWISE_MAX, CONTRASTS)
cat("Contrasts:", paste(sapply(pairs, function(p) paste0(p[1], "_vs_", p[2])), collapse = ", "), "\n")

deg_tables <- list()
for (pr in pairs) {
  treat <- pr[1]; ref <- pr[2]
  res <- results(dds, contrast = c("group", treat, ref))
  df <- as.data.frame(res)
  df$gene <- rownames(df)
  df <- df[, c("gene", "baseMean", "log2FoldChange", "lfcSE", "stat", "pvalue", "padj")]
  df <- add_symbols(df, ORGANISM)   # gene ID conversion: Ensembl -> Symbol
  name <- save_deg(df, treat, ref, outdir)
  make_volcano(df, treat, ref, outdir)
  make_ma(df, treat, ref, outdir, x_is_log = FALSE)   # baseMean = raw-count scale
  deg_tables[[name]] <- df
}

deg_heatmap(assay(vsd), deg_tables, inp$group, outdir)
cat("02_de (DESeq2) done.\n")
