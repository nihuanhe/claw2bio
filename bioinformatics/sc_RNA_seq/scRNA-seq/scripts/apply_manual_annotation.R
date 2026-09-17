# apply_manual_annotation.R — apply a hand-written cluster -> cell_type CSV.
#
# Usage:
#   Rscript apply_manual_annotation.R <annotated_seurat.rds> <manual_annotation.csv> <out_dir>
#
# <manual_annotation.csv>: two columns, `cluster,cell_type`, one row per cluster
# (make it from top10_markers.csv: one row per cluster, your expert label).
# Overwrites `cell_type_final`, re-saves annotated_seurat.rds in <out_dir> and
# regenerates the annotated UMAP there.

suppressPackageStartupMessages({
  library(Seurat)
  library(ggplot2)
})

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 3) {
  stop("usage: Rscript apply_manual_annotation.R <rds> <manual_annotation.csv> <out_dir>")
}
rds_path <- args[1]
csv_path <- args[2]
out_dir  <- args[3]

obj <- readRDS(rds_path)
lab <- read.csv(csv_path, stringsAsFactors = FALSE, check.names = FALSE)
cols <- tolower(colnames(lab))
if (!all(c("cluster", "cell_type") %in% cols))
  stop("CSV needs columns: cluster,cell_type")
colnames(lab) <- c("cluster", "cell_type")[match(c("cluster", "cell_type"), cols)]
lab$cluster <- as.character(lab$cluster)

cl <- as.character(obj$seurat_clusters)
missing_cl <- setdiff(unique(cl), lab$cluster)
if (length(missing_cl))
  cat("WARNING: clusters without manual label (keep previous cell_type_final):",
      paste(missing_cl, collapse = ", "), "\n")

lab_map <- setNames(lab$cell_type, lab$cluster)
new_lab <- unname(lab_map[cl])
keep <- is.na(new_lab)
new_lab[keep] <- as.character(obj$cell_type_final[keep])
obj$cell_type_final <- unname(new_lab)
obj$manual_annotation <- unname(!keep)

saveRDS(obj, file.path(out_dir, "annotated_seurat.rds"))
p <- DimPlot(obj, group.by = "cell_type_final", label = TRUE, repel = TRUE) +
  ggtitle("UMAP by cell_type_final (manual annotation)")
ggsave(file.path(out_dir, "UMAP_by_annotation.png"), p,
       width = 9, height = 7, dpi = 300)
ggsave(file.path(out_dir, "UMAP_by_annotation.pdf"), p,
       width = 9, height = 7)
cat("manual annotation applied ->", file.path(out_dir, "annotated_seurat.rds"), "\n")
print(table(obj$cell_type_final))
