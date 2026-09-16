#!/usr/bin/env Rscript
# 04_gene_expression.R — gene-of-interest expression plots.
#   A) one gene  : abundance across groups (bar + SD + jittered points + stats)
#   B) two genes : within-group comparison of two genes (e.g. TP53 vs GAPDH)
# Consumes the normalized matrix + DEG symbol map produced by stages 01/02,
# so it runs engine-agnostically after any 02 branch.

suppressPackageStartupMessages({
  library(ggplot2)
})

script_dir <- dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1]))
source(file.path(script_dir, "rnaseq_utils.R"))

opt <- parse_args(commandArgs(trailingOnly = TRUE))
outdir  <- opt[[1]]
meta_path <- opt[[2]]
genes_arg <- if (!is.null(opt$genes)) opt$genes else stop("provide --genes GENE1[,GENE2,...]")
control <- if (!is.null(opt$control)) opt$control else NULL
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)

query_genes <- trimws(strsplit(genes_arg, ",", fixed = TRUE)[[1]])

# ---- locate normalized matrix produced by stage 02 ----
candidates <- c("vst_normalized_counts.csv", "voom_normalized_logcpm.csv",
                "log_expression_used.csv", "filtered_counts.csv")
norm_file <- NULL
for (f in candidates) {
  p <- file.path(outdir, f)
  if (file.exists(p)) { norm_file <- p; break }
}
if (is.null(norm_file)) stop("no normalized matrix found in ", outdir,
                             " (run stage 02 first)")
ylabel <- switch(basename(norm_file),
                 vst_normalized_counts.csv = "Normalized expression (vst)",
                 voom_normalized_logcpm.csv = "Normalized expression (voom logCPM)",
                 log_expression_used.csv = "Log expression",
                 "Raw counts")
cat("Using normalized matrix:", basename(norm_file), "\n")

norm_mat <- read_table_smart(norm_file, row_names = TRUE)
norm_mat <- as.matrix(norm_mat)
storage.mode(norm_mat) <- "numeric"
meta <- read_table_smart(meta_path, row_names = FALSE)
meta[] <- lapply(meta, as.character)
meta <- meta[match(colnames(norm_mat), meta$sample), ]
if (any(is.na(meta$sample))) stop("sample mismatch between matrix and metadata")
group <- factor(meta$group)
if (!is.null(control) && control %in% levels(group)) group <- relevel(group, ref = control)

# ---- gene symbol map from any DEG table (offline-safe) ----
deg <- list.files(outdir, pattern = "^DEG_.*\\.csv$", full.names = TRUE)[1]
sym_map <- NULL
if (!is.na(deg)) {
  dd <- read.csv(deg, stringsAsFactors = FALSE)
  if (all(c("gene", "symbol") %in% colnames(dd))) {
    sym_map <- setNames(dd$gene, toupper(dd$symbol))
  }
}

resolve_gene <- function(q) {
  # direct ID hit (Ensembl etc.), case-insensitive
  hit <- rownames(norm_mat)[toupper(rownames(norm_mat)) == toupper(q)]
  if (length(hit) > 0) return(hit[1])
  # exact symbol hit via DEG map (case-insensitive)
  if (!is.null(sym_map)) {
    g <- unname(sym_map[toupper(q)])
    if (length(g) > 0 && !is.na(g) && g %in% rownames(norm_mat)) return(g)
    # substring fallback on symbols
    cand <- names(sym_map)[grepl(toupper(q), names(sym_map), fixed = TRUE)]
    if (length(cand) > 0) {
      g <- unname(sym_map[cand[1]])
      if (length(g) > 0 && !is.na(g) && g %in% rownames(norm_mat)) return(g)
    }
  }
  NULL
}

WONG <- c("#0072B2", "#D55E00", "#009E73", "#CC79A7", "#56B4E9", "#F0E442")

# mean +/- SD summary (avoids the Hmisc dependency of mean_sdl)
mean_sd_df <- function(x) {
  m <- mean(x); s <- sd(x)
  data.frame(y = m, ymin = m - s, ymax = m + s)
}

stars <- function(p) {
  if (is.na(p)) return("NA")
  if (p < 0.001) "***" else if (p < 0.01) "**" else if (p < 0.05) "*" else "ns"
}

resolved <- list()
for (q in query_genes) {
  g <- resolve_gene(q)
  if (is.null(g)) { cat(sprintf("  ! gene '%s' not found in matrix, skipped\n", q)); next }
  resolved[[q]] <- g
}
if (length(resolved) == 0) stop("none of the requested genes were found")

display_name <- function(q) q  # keep the user's spelling in figure titles

# ---------- A) per-gene: abundance across groups ----------
for (q in names(resolved)) {
  g <- resolved[[q]]
  df <- data.frame(sample = colnames(norm_mat), group = group,
                   expr = as.numeric(norm_mat[g, ]))
  write.csv(df, file.path(outdir, sprintf("GeneExpr_%s_values.csv", q)), row.names = FALSE)

  stats_df <- NULL
  ng <- nlevels(group)
  if (ng == 2) {
    pval <- t.test(expr ~ group, data = df)$p.value
    stats_df <- data.frame(label = paste0("t-test p = ", signif(pval, 3), " (", stars(pval), ")"))
  } else {
    fit <- aov(expr ~ group, data = df)
    pval <- summary(fit)[[1]][["Pr(>F)"]][1]
    tuk <- TukeyHSD(fit)$group
    labs <- paste0(rownames(tuk), ": p=", signif(tuk[, "p adj"], 2))
    stats_df <- data.frame(label = c(paste0("ANOVA p = ", signif(pval, 3), " (", stars(pval), ")"), labs))
  }

  p <- ggplot(df, aes(group, expr, fill = group)) +
    stat_summary(fun = mean, geom = "bar", width = 0.6, alpha = 0.85) +
    stat_summary(fun.data = mean_sd_df,
                 geom = "errorbar", width = 0.2) +
    geom_jitter(width = 0.12, size = 2.2, alpha = 0.8) +
    scale_fill_manual(values = WONG) +
    labs(title = paste0(display_name(q), " expression by group"),
         y = ylabel, x = NULL,
         caption = paste(stats_df$label, collapse = "   ")) +
    theme_bw() + theme(legend.position = "none",
                       plot.caption = element_text(hjust = 0.5, size = 9))
  ggsave(file.path(outdir, sprintf("GeneExpr_%s_by_group.png", q)), p,
         width = 7, height = 6, dpi = 300)
  ggsave(file.path(outdir, sprintf("GeneExpr_%s_by_group.pdf", q)), p,
         width = 7, height = 6)
  cat(sprintf("  %s (%s): by-group plot done [%s]\n", q, g,
              paste(stats_df$label, collapse = "; ")))
}

# ---------- B) two genes: within-group comparison ----------
if (length(resolved) >= 2) {
  qs <- names(resolved)
  pairs <- if (length(qs) <= 4) combn(qs, 2, simplify = FALSE) else list(qs[1:2])
  for (pr in pairs) {
    q1 <- pr[1]; q2 <- pr[2]
    df <- data.frame(
      sample = rep(colnames(norm_mat), 2),
      group  = rep(group, 2),
      gene   = rep(c(q1, q2), each = ncol(norm_mat)),
      expr   = c(as.numeric(norm_mat[resolved[[q1]], ]),
                 as.numeric(norm_mat[resolved[[q2]], ]))
    )
    write.csv(df, file.path(outdir, sprintf("GeneExpr_compare_%s_vs_%s_values.csv", q1, q2)),
              row.names = FALSE)
    # paired test per group (same samples measured for both genes)
    labs <- sapply(levels(group), function(gr) {
      a <- norm_mat[resolved[[q1]], group == gr]
      b <- norm_mat[resolved[[q2]], group == gr]
      pv <- tryCatch(t.test(a, b, paired = TRUE)$p.value, error = function(e) NA)
      paste0(gr, ": paired p = ", signif(pv, 3), " (", stars(pv), ")")
    })
    p <- ggplot(df, aes(group, expr, fill = gene)) +
      stat_summary(fun = mean, geom = "bar", position = position_dodge(0.7),
                   width = 0.6, alpha = 0.85) +
      stat_summary(fun.data = mean_sd_df,
                   geom = "errorbar", position = position_dodge(0.7), width = 0.2) +
      geom_point(position = position_jitterdodge(jitter.width = 0.1, dodge.width = 0.7),
                 size = 1.8, alpha = 0.7, show.legend = FALSE) +
      scale_fill_manual(values = WONG) +
      labs(title = paste0(q1, " vs ", q2, " expression within each group"),
           y = ylabel, x = NULL,
           caption = paste(labs, collapse = "   ")) +
      theme_bw() + theme(legend.position = "top",
                         plot.caption = element_text(hjust = 0.5, size = 9))
    ggsave(file.path(outdir, sprintf("GeneExpr_compare_%s_vs_%s_within_group.png", q1, q2)), p,
           width = 8, height = 6, dpi = 300)
    ggsave(file.path(outdir, sprintf("GeneExpr_compare_%s_vs_%s_within_group.pdf", q1, q2)), p,
           width = 8, height = 6)
    cat(sprintf("  %s vs %s: within-group comparison done [%s]\n", q1, q2,
                paste(labs, collapse = "; ")))
  }
}

cat("04_gene_expression done.\n")
