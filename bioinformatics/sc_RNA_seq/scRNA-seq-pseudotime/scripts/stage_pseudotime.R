# stage_pseudotime.R — monocle3 pseudotime on the regular pipeline's output.
# args: --rds <annotated_seurat.rds> --output <dir>
#       (--root-cluster <id> | --root-label <label>)
#       [--subset-labels "a,b"] [--no-graph-test] [--cores 4] [--resume]
# Adapted from the user's validated 拟时序分析.R (Seurat v5 + monocle3):
# reuse the Seurat UMAP/clusters instead of re-embedding.

suppressPackageStartupMessages({
  library(Seurat)
  library(monocle3)
  library(dplyr)
  library(ggplot2)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
get_arg <- function(flag, default = NULL) {
  i <- which(args == flag)
  if (length(i) && i < length(args)) args[i + 1] else default
}
rds_path  <- get_arg("--rds")
out_dir   <- get_arg("--output")
root_clu  <- get_arg("--root-cluster")
root_lab  <- get_arg("--root-label")
subset_l  <- get_arg("--subset-labels")
no_gtest  <- "--no-graph-test" %in% args
list_clu  <- "--list-clusters" %in% args
cores     <- as.integer(get_arg("--cores", "4"))
resume    <- "--resume" %in% args
ckpt_path <- file.path(out_dir, ".checkpoint_cds_learned.rds")

pbmc <- readRDS(rds_path)
if (!"seurat_clusters" %in% colnames(pbmc[[]]))
  stop("[pseudotime] input rds has no seurat_clusters — run the scRNA-seq ",
       "regular pipeline first.")
if (!"umap" %in% Reductions(pbmc))
  stop("[pseudotime] input rds has no UMAP reduction — run the regular pipeline.")
if (!"cell_type_final" %in% colnames(pbmc[[]])) {
  pbmc$cell_type_final <- paste0("Cluster_", pbmc$seurat_clusters)
  cat("[pseudotime] no cell_type_final column; falling back to Cluster_N\n")
}

# ---- optional subset by cell_type_final labels
if (!is.null(subset_l)) {
  keep_lab <- trimws(strsplit(subset_l, ",", fixed = TRUE)[[1]])
  before <- ncol(pbmc)
  pbmc <- subset(pbmc, subset = cell_type_final %in% keep_lab)
  cat(sprintf("[pseudotime] subset to labels {%s}: %d -> %d cells\n",
              paste(keep_lab, collapse = ","), before, ncol(pbmc)))
  if (ncol(pbmc) == 0)
    stop("[pseudotime] subset left 0 cells. Available labels: ",
         paste(unique(pbmc$cell_type_final), collapse = ", "))
}

# ---- cluster -> dominant-label table (printed on --list-clusters, and when a
#      root is invalid). Computed BEFORE learn_graph so a wrong root fails fast.
avail <- data.frame(cluster = levels(factor(pbmc$seurat_clusters)),
                    label = tapply(as.character(pbmc$cell_type_final),
                                   pbmc$seurat_clusters,
                                   function(v) names(sort(table(v),
                                                   decreasing = TRUE))[1]))
if (list_clu) {
  cat("[pseudotime] cluster -> cell_type_final (dominant label per cluster):\n")
  print(avail)
  quit(save = "no", status = 0)
}
if (!is.null(root_lab) && !root_lab %in% pbmc$cell_type_final)
  stop("[pseudotime] --root-label '", root_lab, "' not found. Available:\n",
       paste(capture.output(print(avail)), collapse = "\n"))
if (is.null(root_lab) && !is.null(root_clu) &&
    !root_clu %in% as.character(pbmc$seurat_clusters))
  stop("[pseudotime] --root-cluster '", root_clu, "' not found. Available:\n",
       paste(capture.output(print(avail)), collapse = "\n"))

# ---- build cds, reusing Seurat embeddings (skipped when a checkpoint exists)
if (resume && file.exists(ckpt_path)) {
  cat("[pseudotime] --resume: loading checkpoint", ckpt_path, "\n")
  cds <- readRDS(ckpt_path)
} else {
  if (resume)
    cat("[pseudotime] --resume given but no checkpoint found; running from scratch\n")
  cat("[pseudotime] building cell_data_set ...\n")
  expr <- LayerData(pbmc, assay = "RNA", layer = "data")
  gene_meta <- data.frame(gene_short_name = rownames(pbmc),
                          row.names = rownames(pbmc))
  cds <- new_cell_data_set(expr, cell_metadata = pbmc[[]],
                           gene_metadata = gene_meta)
  reducedDims(cds)$UMAP <- Embeddings(pbmc, reduction = "umap")
  if ("pca" %in% Reductions(pbmc))
    reducedDims(cds)$PCA <- Embeddings(pbmc, reduction = "pca")

  cds <- cluster_cells(cds, reduction_method = "UMAP")
  # keep the Seurat cluster IDs (0-based) instead of monocle's own
  cds@clusters$UMAP$clusters <- factor(pbmc$seurat_clusters)

  # ---- learn graph (memory-peak #1)
  cat("[pseudotime] learn_graph (memory-peak step) ...\n")
  cds <- learn_graph(cds)
  saveRDS(cds, file.path(out_dir, ".checkpoint_cds_learned.rds"))
  cat("[pseudotime] checkpoint written ->", ckpt_path, "\n")
}

# ---- root cells (user's biological choice; already validated above)
if (!is.null(root_lab)) {
  if (!root_lab %in% pbmc$cell_type_final)
    stop("[pseudotime] --root-label '", root_lab, "' not found. Available:\n",
         paste(capture.output(print(avail)), collapse = "\n"))
  root_cells <- colnames(cds)[pbmc$cell_type_final == root_lab]
  root_desc <- paste0("label '", root_lab, "'")
} else {
  if (!root_clu %in% as.character(pbmc$seurat_clusters))
    stop("[pseudotime] --root-cluster '", root_clu, "' not found. Available:\n",
         paste(capture.output(print(avail)), collapse = "\n"))
  root_cells <- colnames(cds)[cds@clusters$UMAP$clusters == root_clu]
  root_desc <- paste0("cluster ", root_clu)
}
cat("[pseudotime] root:", root_desc, "(", length(root_cells), "cells )\n")
cds <- order_cells(cds, root_cells = root_cells)

# ---- plots
save_plot <- function(p, name, w = 8, h = 6) {
  ggsave(file.path(out_dir, paste0(name, ".png")), p, width = w, height = h,
         dpi = 300)
  ggsave(file.path(out_dir, paste0(name, ".pdf")), p, width = w, height = h)
}
p1 <- plot_cells(cds, color_cells_by = "pseudotime", label_cell_groups = FALSE,
                 label_leaves = FALSE, label_branch_points = FALSE,
                 graph_label_size = 3) +
  scale_color_viridis_c(name = "Pseudotime") +
  ggtitle(paste0("Pseudotime (root: ", root_desc, ")"))
save_plot(p1, "trajectory_by_pseudotime")

p2 <- plot_cells(cds, color_cells_by = "cluster",
                 label_cell_groups = TRUE, label_leaves = FALSE,
                 label_branch_points = FALSE)
save_plot(p2, "trajectory_by_cluster")

if ("group" %in% colnames(pbmc[[]])) {
  p3 <- plot_cells(cds, color_cells_by = "group")
  save_plot(p3, "trajectory_by_group")
}
p4 <- plot_cells(cds, color_cells_by = "orig.ident")
save_plot(p4, "trajectory_by_sample")

# ---- pseudotime-associated genes (memory-peak #2)
n_sig <- "graph_test skipped"
if (!no_gtest) {
  cat("[pseudotime] graph_test (slow / memory-peak step) ...\n")
  deg <- graph_test(cds, neighbor_graph = "principal_graph", cores = cores)
  deg <- deg %>% arrange(q_value)
  write.csv(deg, file.path(out_dir, "pseudotime_genes.csv"),
            row.names = FALSE)
  n_sig <- sum(deg$q_value < 0.05, na.rm = TRUE)
  cat("[pseudotime] pseudotime genes (q<0.05):", n_sig, "\n")

  # top gene expression on trajectory (robust plot_cells route)
  sig <- deg %>% filter(q_value < 0.05) %>% pull(gene_short_name)
  if (length(sig) > 0) {
    top_g <- head(sig, 4)
    for (g in top_g) {
      p <- tryCatch(plot_cells(cds, genes = g, label_cell_groups = FALSE,
                               show_trajectory_graph = TRUE) +
                      ggtitle(paste0("Gene: ", g)),
                    error = function(e) NULL)
      if (!is.null(p)) save_plot(p, paste0("gene_", g, "_on_trajectory"))
    }
  }
}

saveRDS(cds, file.path(out_dir, "pseudotime_cds.rds"))
if (file.exists(ckpt_path)) file.remove(ckpt_path)
write_json(list(n_cells = ncol(cds), root = root_desc,
                n_pseudotime_genes = n_sig),
           file.path(out_dir, "pseudotime_summary.json"),
           auto_unbox = TRUE, pretty = TRUE)
cat("[pseudotime] DONE ->", out_dir, "\n")
