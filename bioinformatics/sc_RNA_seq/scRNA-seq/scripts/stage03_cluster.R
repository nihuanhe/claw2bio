# Stage 03 — normalize, (integrate), cluster, UMAP + tSNE.
# args: --plan <json> --output <dir> --organism x
#       [--integrate harmony|cca|rpca|none] [--resolution 0.5]
#       [--sct] [--no-tsne] [--downsample N]
# In:  .checkpoints/02_qc.rds
# Out: .checkpoints/03_clustered.rds, UMAP_*.{png,pdf}, TSNE_*, clustree.png,
#      integration before/after comparison UMAPs.

suppressPackageStartupMessages({
  library(Seurat)
  library(ggplot2)
  library(patchwork)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
get_arg <- function(flag, default = NULL) {
  i <- which(args == flag)
  if (length(i) && i < length(args)) args[i + 1] else default
}
out_dir    <- get_arg("--output")
plan       <- fromJSON(get_arg("--plan"), simplifyVector = FALSE)
integrate  <- get_arg("--integrate", "harmony")
resolution <- as.numeric(get_arg("--resolution", "0.5"))
use_sct    <- "--sct" %in% args
no_tsne    <- "--no-tsne" %in% args
downsample <- as.integer(get_arg("--downsample", "0"))
ck <- file.path(out_dir, ".checkpoints")

pbmc <- readRDS(file.path(ck, "02_qc.rds"))
multi <- length(plan$samples) > 1

# ---- optional downsample (exploratory mode)
if (downsample > 0) {
  pbmc <- subset(pbmc, cells = unlist(lapply(levels(factor(pbmc$orig.ident)),
    function(s) {
      cells <- WhichCells(pbmc, expression = orig.ident == s)
      if (length(cells) > downsample) sample(cells, downsample) else cells
    })))
  cat(sprintf("[stage03] downsampled to <= %d cells/sample: %d cells total\n",
              downsample, ncol(pbmc)))
}

# ---- integration needs per-sample layers: re-split the joined counts layer
if (multi && integrate != "none") {
  cat("[stage03] re-splitting RNA layers by orig.ident for integration\n")
  pbmc[["RNA"]] <- split(pbmc[["RNA"]], f = pbmc$orig.ident)
}

# ---- normalize
if (use_sct) {
  cat("[stage03] SCTransform ...\n")
  pbmc <- SCTransform(pbmc, verbose = FALSE)
} else {
  cat("[stage03] LogNormalize ...\n")
  pbmc <- NormalizeData(pbmc, verbose = FALSE)
  pbmc <- FindVariableFeatures(pbmc, nfeatures = 2000, verbose = FALSE)
  pbmc <- ScaleData(pbmc, verbose = FALSE)
}
npcs <- min(50, ncol(pbmc) - 1, nrow(pbmc) - 1)
pbmc <- RunPCA(pbmc, npcs = npcs, verbose = FALSE)

# ---- UMAP before integration (multi-sample only, for comparison)
dims_use <- 1:min(20, npcs)
if (multi && integrate != "none") {
  pbmc <- RunUMAP(pbmc, dims = dims_use, reduction = "pca",
                  reduction.name = "umap.unintegrated", verbose = FALSE)
  p_pre <- DimPlot(pbmc, reduction = "umap.unintegrated",
                   group.by = "orig.ident") +
    ggtitle("UMAP before integration (by sample)")
  ggsave(file.path(out_dir, "UMAP_before_integration.png"), p_pre,
         width = 8, height = 6, dpi = 300)
  ggsave(file.path(out_dir, "UMAP_before_integration.pdf"), p_pre,
         width = 8, height = 6)
}

# ---- integration (multi-sample, default harmony)
reduction_use <- "pca"
if (multi && integrate != "none") {
  cat(sprintf("[stage03] integrating with %s (memory-peak step) ...\n", integrate))
  method <- switch(integrate,
                   harmony = HarmonyIntegration,
                   cca     = CCAIntegration,
                   rpca    = RPCAIntegration)
  pbmc <- IntegrateLayers(pbmc, method = method,
                          orig.reduction = "pca",
                          new.reduction = paste0("integrated.", integrate),
                          verbose = FALSE)
  reduction_use <- paste0("integrated.", integrate)
} else if (multi) {
  cat("[stage03] integration disabled (--integrate none)\n")
} else {
  cat("[stage03] single sample: integration skipped\n")
}

# ---- cluster + UMAP (+ tSNE)
pbmc <- FindNeighbors(pbmc, reduction = reduction_use, dims = dims_use,
                      verbose = FALSE)
# clustree scan (resolution guide)
if (requireNamespace("clustree", quietly = TRUE)) {
  pbmc <- FindClusters(pbmc, resolution = seq(0.1, 1.2, by = 0.1),
                       verbose = FALSE)
  tryCatch({
    p_tree <- clustree::clustree(pbmc[[]], prefix = "RNA_snn_res.")
    ggsave(file.path(out_dir, "clustree_resolution_scan.png"), p_tree,
           width = 10, height = 8, dpi = 300)
    ggsave(file.path(out_dir, "clustree_resolution_scan.pdf"), p_tree,
           width = 10, height = 8)
  }, error = function(e)
    cat("[stage03] WARNING: clustree plot failed (", conditionMessage(e),
        ") -> skipped; tune --resolution manually\n"))
} else {
  cat("[stage03] clustree not installed -> resolution scan skipped\n")
}
pbmc <- FindClusters(pbmc, resolution = resolution, verbose = FALSE)
pbmc <- RunUMAP(pbmc, dims = dims_use, reduction = reduction_use,
                reduction.name = "umap", verbose = FALSE)

grp <- c("seurat_clusters", "orig.ident")
if ("group" %in% colnames(pbmc[[]])) grp <- c(grp, "group")
for (g in grp) {
  p <- DimPlot(pbmc, reduction = "umap", group.by = g, label = (g == "seurat_clusters")) +
    ggtitle(paste("UMAP by", g))
  fn <- file.path(out_dir, paste0("UMAP_by_", g))
  ggsave(paste0(fn, ".png"), p, width = 8, height = 6, dpi = 300)
  ggsave(paste0(fn, ".pdf"), p, width = 8, height = 6)
}
if (multi && integrate != "none") {
  p_post <- DimPlot(pbmc, reduction = "umap", group.by = "orig.ident") +
    ggtitle("UMAP after integration (by sample)")
  ggsave(file.path(out_dir, "UMAP_after_integration.png"), p_post,
         width = 8, height = 6, dpi = 300)
  ggsave(file.path(out_dir, "UMAP_after_integration.pdf"), p_post,
         width = 8, height = 6)
}

if (!no_tsne) {
  pbmc <- RunTSNE(pbmc, dims = dims_use, reduction = reduction_use,
                  verbose = FALSE, check_duplicates = FALSE)
  for (g in grp) {
    p <- DimPlot(pbmc, reduction = "tsne", group.by = g,
                 label = (g == "seurat_clusters")) +
      ggtitle(paste("t-SNE by", g))
    fn <- file.path(out_dir, paste0("TSNE_by_", g))
    ggsave(paste0(fn, ".png"), p, width = 8, height = 6, dpi = 300)
    ggsave(paste0(fn, ".pdf"), p, width = 8, height = 6)
  }
}

saveRDS(pbmc, file.path(ck, "03_clustered.rds"))
meta <- list(integration = if (multi) integrate else "none (single sample)",
             resolution = resolution,
             n_clusters = length(levels(pbmc$seurat_clusters)),
             normalization = if (use_sct) "SCTransform" else "LogNormalize",
             n_cells = ncol(pbmc))
write_json(meta, file.path(ck, "cluster_summary.json"), auto_unbox = TRUE,
           pretty = TRUE)
cat(sprintf("[stage03] DONE: %d cells, %d clusters -> %s\n",
            ncol(pbmc), meta$n_clusters, file.path(ck, "03_clustered.rds")))
