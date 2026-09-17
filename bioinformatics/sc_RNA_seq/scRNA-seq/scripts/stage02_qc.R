# Stage 02 — QC filtering + doublet detection.
# args: --plan <json> --output <dir> --organism x [--mt-max 20]
#       [--max-features 6000] [--no-doublets]
# In:  .checkpoints/01_merged_raw.rds
# Out: .checkpoints/02_qc.rds, QC_violin_before/after.{png,pdf},
#      qc_summary.json (per-sample retention + threshold advice)

suppressPackageStartupMessages({
  library(Seurat)
  library(ggplot2)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
get_arg <- function(flag, default = NULL) {
  i <- which(args == flag)
  if (length(i) && i < length(args)) args[i + 1] else default
}
out_dir  <- get_arg("--output")
mt_max   <- as.numeric(get_arg("--mt-max", "20"))
max_feat <- as.integer(get_arg("--max-features", "6000"))
min_feat <- as.integer(get_arg("--min-features", "200"))
no_dbl   <- "--no-doublets" %in% args
ck <- file.path(out_dir, ".checkpoints")

pbmc <- readRDS(file.path(ck, "01_merged_raw.rds"))
n_before <- ncol(pbmc)

# ---- QC violin BEFORE
feats <- c("nFeature_RNA", "nCount_RNA", "percent.mt")
p_before <- VlnPlot(pbmc, features = feats, group.by = "orig.ident",
                    ncol = 3, pt.size = 0) +
  geom_hline(data = data.frame(f = "percent.mt"), aes(yintercept = mt_max),
             linetype = "dashed", color = "red")
ggsave(file.path(out_dir, "QC_violin_before.png"), p_before,
       width = 14, height = 5, dpi = 300)
ggsave(file.path(out_dir, "QC_violin_before.pdf"), p_before,
       width = 14, height = 5)

# ---- per-sample filtering (thresholds may later become per-sample)
filt <- subset(pbmc, subset = nFeature_RNA > min_feat &
                 nFeature_RNA < max_feat & percent.mt < mt_max)
if (ncol(filt) == 0) {
  stop(sprintf(paste0(
    "[stage02] FATAL: 0 cells pass QC (nFeature in (%d,%d), percent.mt < %g%%). ",
    "Inspect QC_violin_before.png and relax --mt-max/--max-features-qc/--min-features."),
    min_feat, max_feat, mt_max))
}
n_after <- ncol(filt)
cat(sprintf("[stage02] cells: %d -> %d (%.1f%% kept)\n",
            n_before, n_after, 100 * n_after / n_before))

# ---- per-sample retention + threshold advice (docx rules)
tab <- table(pbmc$orig.ident)
tab_kept <- table(filt$orig.ident)
advice <- list()
for (s in names(tab)) {
  keep_pct <- 100 * (if (s %in% names(tab_kept)) tab_kept[[s]] else 0) / tab[[s]]
  a <- character()
  if (keep_pct < 50)
    a <- c(a, sprintf("retention %.0f%% < 50%%: consider raising --mt-max (e.g. 25) and widening nFeature range (150-5000)", keep_pct))
  if (keep_pct > 95)
    a <- c(a, sprintf("retention %.0f%% > 95%%: consider lowering --mt-max (e.g. 15) and tightening nFeature range", keep_pct))
  advice[[s]] <- list(cells_before = tab[[s]],
                      cells_after  = if (s %in% names(tab_kept)) tab_kept[[s]] else 0,
                      retention_pct = round(keep_pct, 1),
                      advice = a)
  cat(sprintf("[stage02] %-24s keep %5.1f%%\n", s, keep_pct))
}

# ---- doublets (scDblFinder), default on
dbl_rate <- list()
if (!no_dbl && requireNamespace("scDblFinder", quietly = TRUE)) {
  suppressPackageStartupMessages(library(scDblFinder))
  sce <- as.SingleCellExperiment(filt)
  sce <- scDblFinder(sce, samples = sce$orig.ident)
  filt$doublet <- sce$scDblFinder.class
  dbl_rate <- as.list(round(100 * prop.table(table(filt$orig.ident, filt$doublet),
                                             margin = 1)[, "doublet"], 2))
  cat("[stage02] doublet rates per sample (%):\n")
  print(dbl_rate)
  filt <- subset(filt, subset = doublet == "singlet")
  cat(sprintf("[stage02] after doublet removal: %d cells\n", ncol(filt)))
} else {
  cat("[stage02] doublet detection skipped (",
      if (no_dbl) "--no-doublets" else "scDblFinder not installed", ")\n")
}

# ---- QC violin AFTER
p_after <- VlnPlot(filt, features = feats, group.by = "orig.ident",
                   ncol = 3, pt.size = 0)
ggsave(file.path(out_dir, "QC_violin_after.png"), p_after,
       width = 14, height = 5, dpi = 300)
ggsave(file.path(out_dir, "QC_violin_after.pdf"), p_after,
       width = 14, height = 5)

saveRDS(filt, file.path(ck, "02_qc.rds"))
write_json(list(samples = advice, doublet_rate_pct = dbl_rate,
                thresholds = list(mt_max = mt_max, min_features = min_feat,
                                  max_features = max_feat)),
           file.path(ck, "qc_summary.json"), auto_unbox = TRUE, pretty = TRUE)
cat(sprintf("[stage02] DONE: %d cells -> %s\n", ncol(filt),
            file.path(ck, "02_qc.rds")))
