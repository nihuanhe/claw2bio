#!/usr/bin/env Rscript
# 01_qc.R — engine-agnostic QC: filtering, logCPM, PCA, sample correlation.
# Refactored from the lab's battle-tested R arsenal (D:\R1\R_RNA-seq).

suppressPackageStartupMessages({
  library(edgeR)
  library(ggplot2)
  library(pheatmap)
})

args <- commandArgs(trailingOnly = TRUE)
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
opt <- parse_args(args)
counts_path   <- opt[[1]]
metadata_path <- opt[[2]]
outdir        <- opt[[3]]
control       <- if (!is.null(opt$control)) opt$control else NULL

dir.create(outdir, showWarnings = FALSE, recursive = TRUE)

counts <- read.csv(counts_path, row.names = 1, check.names = FALSE)
counts <- as.matrix(counts)
storage.mode(counts) <- "numeric"

meta <- read.csv(metadata_path, colClasses = "character")
stopifnot(all(c("sample", "group") %in% colnames(meta)))

# Match and order samples
meta <- meta[match(colnames(counts), meta$sample), ]
if (any(is.na(meta$sample))) stop("Sample mismatch between counts and metadata.")
group <- factor(meta$group)
if (!is.null(control) && control %in% levels(group)) {
  group <- relevel(group, ref = control)
}
cat("Groups:", paste(levels(group), collapse = ", "), "\n")
cat("Samples per group:\n"); print(table(group))

# Filter lowly expressed genes (edgeR filterByExpr — engine-agnostic default)
n_before <- nrow(counts)
keep <- filterByExpr(counts, group = group)
counts_f <- counts[keep, ]
cat(sprintf("Filtering: %d -> %d genes (filterByExpr)\n", n_before, nrow(counts_f)))
write.csv(data.frame(gene = rownames(counts_f), counts_f, check.names = FALSE),
          file.path(outdir, "filtered_counts.csv"), row.names = FALSE)

# Library sizes
lib <- data.frame(sample = colnames(counts_f), group = meta$group,
                  library_size = colSums(counts_f))
write.csv(lib, file.path(outdir, "library_sizes.csv"), row.names = FALSE)

# Normalized logCPM for QC visualisation
dge <- DGEList(counts = counts_f, group = group)
dge <- calcNormFactors(dge)
logcpm <- cpm(dge, log = TRUE, prior.count = 1)

# PCA
pca <- prcomp(t(logcpm), scale. = FALSE)
pct <- round(100 * (pca$sdev^2 / sum(pca$sdev^2)), 1)
pca_df <- data.frame(PC1 = pca$x[, 1], PC2 = pca$x[, 2],
                     sample = rownames(pca$x), group = group)
p <- ggplot(pca_df, aes(PC1, PC2, color = group, label = sample)) +
  geom_point(size = 4) +
  xlab(paste0("PC1: ", pct[1], "% variance")) +
  ylab(paste0("PC2: ", pct[2], "% variance")) +
  theme_bw() + theme(legend.position = "top")
ggsave(file.path(outdir, "QC_PCA_plot.png"), p, width = 8, height = 7, dpi = 300)
ggsave(file.path(outdir, "QC_PCA_plot.pdf"), p, width = 8, height = 7)

# Sample correlation heatmap
cor_mat <- cor(logcpm)
ann <- data.frame(Group = group); rownames(ann) <- colnames(logcpm)
png(file.path(outdir, "QC_sample_correlation_heatmap.png"), width = 1800, height = 1600, res = 300)
pheatmap(cor_mat, annotation_col = ann, main = "Sample correlation (logCPM)")
dev.off()
pdf(file.path(outdir, "QC_sample_correlation_heatmap.pdf"), width = 8, height = 7)
pheatmap(cor_mat, annotation_col = ann, main = "Sample correlation (logCPM)")
dev.off()

# QC summary
sink(file.path(outdir, "QC_summary.txt"))
cat("Claw2Bio bulk-rnaseq QC summary\n")
cat("==============================\n")
cat(sprintf("Input: %s\n", counts_path))
cat(sprintf("Genes: %d before / %d after filtering\n", n_before, nrow(counts_f)))
cat(sprintf("Samples: %d\n", ncol(counts_f)))
cat("Groups:\n"); print(table(group))
cat("\nLibrary sizes:\n"); print(lib)
cat(sprintf("\nPCA variance explained: PC1 %.1f%%, PC2 %.1f%%\n", pct[1], pct[2]))
sink()

cat("01_qc done. Outputs in", outdir, "\n")
