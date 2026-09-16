# rnaseq_utils.R — shared helpers for the bulk-rnaseq DE scripts.
# Sourced by 01_qc.R, 02_de_deseq2.R and 02_de_edger_limma.R (not run standalone).

# Smart table reader: handles .csv/.tsv/.txt, space-delimited, and .gz.
# (.zip must be unpacked first — the driver tells the agent to do so.)
read_table_smart <- function(path, row_names = TRUE) {
  first <- readLines(path, n = 1, warn = FALSE)   # readLines handles .gz natively
  delim <- if (grepl("\t", first)) "\t" else if (grepl(",", first)) "," else if (grepl(";", first)) ";" else ""
  rn <- if (row_names) 1 else NULL
  if (delim == "") {
    df <- read.table(path, header = TRUE, sep = "", row.names = rn, check.names = FALSE)
  } else {
    df <- read.table(path, header = TRUE, sep = delim, row.names = rn,
                     check.names = FALSE)
  }
  df
}

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
  counts <- read_table_smart(counts_path, row_names = TRUE)
  counts <- as.matrix(counts)
  storage.mode(counts) <- "numeric"
  meta <- read_table_smart(metadata_path, row_names = FALSE)
  meta[] <- lapply(meta, as.character)
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

# Map Ensembl/Symbol IDs to gene Symbols and add as a `symbol` column.
# Used so that every downstream figure/table speaks in gene symbols.
add_symbols <- function(df, organism = "mouse") {
  orgdb_name <- if (organism == "human") "org.Hs.eg.db" else "org.Mm.eg.db"
  if (!requireNamespace(orgdb_name, quietly = TRUE)) {
    cat(sprintf("  (%s not installed — keeping raw IDs in outputs)\n", orgdb_name))
    return(df)
  }
  genes <- df$gene
  is_ens <- mean(grepl("^ENS", genes)) > 0.5
  ids <- if (is_ens) gsub("\\..*", "", genes) else genes   # strip Ensembl versions
  keytype <- if (is_ens) "ENSEMBL" else "SYMBOL"
  conv <- tryCatch(
    clusterProfiler::bitr(ids, fromType = keytype, toType = "SYMBOL", OrgDb = orgdb_name),
    error = function(e) NULL)
  if (is.null(conv)) { cat("  (ID conversion failed — keeping raw IDs)\n"); return(df) }
  conv <- conv[!duplicated(conv[[1]]), ]
  sym <- conv$SYMBOL[match(ids, conv[[1]])]
  df$symbol <- ifelse(is.na(sym), genes, sym)
  df <- df[, c("gene", "symbol", setdiff(colnames(df), c("gene", "symbol")))]
  cat(sprintf("  ID conversion: %d/%d genes mapped to symbols\n",
              sum(!is.na(sym)), length(genes)))
  df
}

# Sanitise a (group / contrast) name for use in output filenames.
# Group names may contain spaces, dashes or non-ASCII characters; filenames must not.
sanitize_name <- function(x) {
  x <- gsub("[^A-Za-z0-9._-]+", "_", x)
  x <- gsub("_+", "_", x)
  gsub("^_|_$", "", x)
}

# Standardised DEG table: gene, symbol?, log2FoldChange, stat, pvalue, padj
save_deg <- function(df, treat, ref, outdir) {
  name <- paste0(treat, "_vs_", ref)
  df <- df[order(df$padj, -abs(df$log2FoldChange)), ]
  write.csv(df, file.path(outdir, paste0("DEG_", sanitize_name(name), ".csv")), row.names = FALSE)
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
  label_col <- if ("symbol" %in% colnames(df)) "symbol" else "gene"
  p <- ggplot(df[ok, ], aes(log2FoldChange, -log10(padj), color = sig)) +
    geom_point(alpha = 0.6, size = 1.2) +
    scale_color_manual(values = c("Down" = "#0072B2", "Not significant" = "grey70", "Up" = "#D55E00")) +
    geom_vline(xintercept = c(-LFC_CUTOFF, LFC_CUTOFF), lty = 2, color = "grey50") +
    geom_hline(yintercept = -log10(PADJ_CUTOFF), lty = 2, color = "grey50") +
    ggtitle(paste0(treat, " vs ", ref)) +
    theme_bw() + theme(legend.position = "top")
  if (nrow(top) > 0) p <- p + ggrepel::geom_text_repel(data = top, aes(label = .data[[label_col]]), size = 3, max.overlaps = 20)
  name <- paste0("Volcano_", sanitize_name(paste0(treat, "_vs_", ref)))
  ggsave(file.path(outdir, paste0(name, ".png")), p, width = 9, height = 7, dpi = 300)
  ggsave(file.path(outdir, paste0(name, ".pdf")), p, width = 9, height = 7)
}

# MA plot: mean expression vs log2FC — the basic check that normalisation worked
# and that logFC does not depend on expression level.
# x_is_log = TRUE when baseMean is already on a log scale (limma AveExpr);
# FALSE for raw-count baseMean (DESeq2) -> plotted on log10 axis.
make_ma <- function(df, treat, ref, outdir, x_is_log = FALSE) {
  ok <- !is.na(df$padj) & !is.na(df$log2FoldChange) & !is.na(df$baseMean)
  d <- df[ok, ]
  if (x_is_log) d <- d[is.finite(d$baseMean), ] else d <- d[d$baseMean > 0, ]
  if (nrow(d) < 10) { cat("  (too few genes for MA plot)\n"); return(invisible(NULL)) }
  d$sig <- "Not significant"
  d$sig[d$padj < PADJ_CUTOFF & d$log2FoldChange >  LFC_CUTOFF] <- "Up"
  d$sig[d$padj < PADJ_CUTOFF & d$log2FoldChange < -LFC_CUTOFF] <- "Down"
  p <- ggplot(d, aes(baseMean, log2FoldChange, color = sig)) +
    geom_point(alpha = 0.5, size = 1) +
    scale_color_manual(values = c("Down" = "#0072B2", "Not significant" = "grey70", "Up" = "#D55E00")) +
    geom_hline(yintercept = c(-LFC_CUTOFF, 0, LFC_CUTOFF), lty = c(2, 1, 2), color = "grey50") +
    labs(x = if (x_is_log) "Average log expression" else "Mean of normalised counts (log10 scale)",
         y = "log2 fold change",
         title = paste0("MA: ", treat, " vs ", ref), color = NULL) +
    theme_bw() + theme(legend.position = "top")
  if (!x_is_log) p <- p + scale_x_log10()
  name <- paste0("MA_", sanitize_name(paste0(treat, "_vs_", ref)))
  ggsave(file.path(outdir, paste0(name, ".png")), p, width = 8, height = 6, dpi = 300)
  ggsave(file.path(outdir, paste0(name, ".pdf")), p, width = 8, height = 6)
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
