# rnaseq_utils.R — shared helpers for the bulk-rnaseq DE scripts.
# Sourced by 02_de_deseq2.R and 02_de_edger_limma.R (not run standalone).

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

script_dir <- function() {
  f <- grep("--file=", commandArgs(FALSE), value = TRUE)
  if (length(f)) dirname(sub("--file=", "", f[1])) else getwd()
}

# Read counts + metadata, align samples, relevel control.
read_inputs <- function(counts_path, metadata_path, control = NULL) {
  counts <- read.csv(counts_path, row.names = 1, check.names = FALSE)
  counts <- as.matrix(counts)
  storage.mode(counts) <- "numeric"
  meta <- read.csv(metadata_path, colClasses = "character")
  stopifnot(all(c("sample", "group") %in% colnames(meta)))
  meta <- meta[match(colnames(counts), meta$sample), ]
  if (any(is.na(meta$sample))) stop("Sample mismatch between counts and metadata.")
  group <- factor(meta$group)
  if (!is.null(control) && control %in% levels(group)) group <- relevel(group, ref = control)
  list(counts = counts, meta = meta, group = group)
}

# Contrast list: every group vs control; if <= 4 groups, all pairwise.
build_contrasts <- function(group, control) {
  lv <- levels(group)
  ctrl <- if (!is.null(control) && control %in% lv) control else lv[1]
  others <- setdiff(lv, ctrl)
  pairs <- lapply(others, function(g) c(g, ctrl))
  if (length(lv) <= 4 && length(others) > 1) {
    extra <- combn(others, 2, simplify = FALSE)
    pairs <- c(pairs, extra)
  }
  pairs  # each element c(treat, ref) -> "treat_vs_ref"
}

# Standardised DEG table: gene, log2FoldChange, stat, pvalue, padj (+ engine extras)
save_deg <- function(df, treat, ref, outdir) {
  name <- paste0(treat, "_vs_", ref)
  df <- df[order(df$padj, -abs(df$log2FoldChange)), ]
  write.csv(df, file.path(outdir, paste0("DEG_", name, ".csv")), row.names = FALSE)
  sig <- !is.na(df$padj) & df$padj < PADJ_CUTOFF & !is.na(df$log2FoldChange)
  up   <- sum(sig & df$log2FoldChange >  LFC_CUTOFF)
  down <- sum(sig & df$log2FoldChange < -LFC_CUTOFF)
  cat(sprintf("  %s: %d up, %d down (padj < %g, |log2FC| > %g)\n",
              name, up, down, PADJ_CUTOFF, LFC_CUTOFF))
  name
}

make_volcano <- function(df, treat, ref, outdir) {
  df$sig <- "Not significant"
  ok <- !is.na(df$padj) & !is.na(df$log2FoldChange)
  df$sig[ok & df$padj < PADJ_CUTOFF & df$log2FoldChange >  LFC_CUTOFF] <- "Up"
  df$sig[ok & df$padj < PADJ_CUTOFF & df$log2FoldChange < -LFC_CUTOFF] <- "Down"
  top <- head(df[ok & df$sig != "Not significant", ][order(df$padj[ok & df$sig != "Not significant"]), ], 10)
  p <- ggplot(df[ok, ], aes(log2FoldChange, -log10(padj), color = sig)) +
    geom_point(alpha = 0.6, size = 1.2) +
    scale_color_manual(values = c("Down" = "#0072B2", "Not significant" = "grey70", "Up" = "#D55E00")) +
    geom_vline(xintercept = c(-LFC_CUTOFF, LFC_CUTOFF), lty = 2, color = "grey50") +
    geom_hline(yintercept = -log10(PADJ_CUTOFF), lty = 2, color = "grey50") +
    ggtitle(paste0(treat, " vs ", ref)) +
    theme_bw() + theme(legend.position = "top")
  if (nrow(top) > 0) p <- p + ggrepel::geom_text_repel(data = top, aes(label = gene), size = 3, max.overlaps = 20)
  name <- paste0("Volcano_", treat, "_vs_", ref)
  ggsave(file.path(outdir, paste0(name, ".png")), p, width = 9, height = 7, dpi = 300)
  ggsave(file.path(outdir, paste0(name, ".pdf")), p, width = 9, height = 7)
}

# Heatmap of top DEGs across all contrasts (needs normalized matrix, genes x samples)
deg_heatmap <- function(norm_mat, deg_tables, group, outdir, top_n = 50) {
  sig_genes <- unique(unlist(lapply(deg_tables, function(df) {
    ok <- !is.na(df$padj) & df$padj < PADJ_CUTOFF & abs(df$log2FoldChange) > LFC_CUTOFF
    head(df$gene[ok][order(df$padj[ok])], top_n)
  })))
  sig_genes <- intersect(sig_genes, rownames(norm_mat))
  if (length(sig_genes) < 2) { cat("  (too few significant genes for heatmap)\n"); return(invisible(NULL)) }
  mat <- norm_mat[sig_genes, , drop = FALSE]
  mat <- t(scale(t(mat)))  # z-score per gene
  mat[is.na(mat)] <- 0
  ann <- data.frame(Group = group); rownames(ann) <- colnames(mat)
  png(file.path(outdir, "DEG_heatmap.png"), width = 2000, height = 2400, res = 300)
  pheatmap(mat, annotation_col = ann, show_rownames = FALSE,
           main = paste0("Top DEGs (z-scored, n=", length(sig_genes), ")"))
  dev.off()
  pdf(file.path(outdir, "DEG_heatmap.pdf"), width = 8, height = 9)
  pheatmap(mat, annotation_col = ann, show_rownames = FALSE,
           main = paste0("Top DEGs (z-scored, n=", length(sig_genes), ")"))
  dev.off()
}
