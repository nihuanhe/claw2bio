# export_slim.R — DietSeurat slim export for COS distribution / sharing.
# args: --rds <annotated_seurat.rds> --out <slim.rds>
# Keeps: RNA counts + data layers, meta.data, pca + umap reductions.
# Drops: scale.data, integrated reduction, tsne, unintegrated umap, graphs.
# Downstream skills (pseudotime / virtual-ko) work fine on the slim object.

suppressPackageStartupMessages(library(Seurat))

args <- commandArgs(trailingOnly = TRUE)
get_arg <- function(flag, default = NULL) {
  i <- which(args == flag)
  if (length(i) && i < length(args)) args[i + 1] else default
}
rds_path <- get_arg("--rds")
out_path <- get_arg("--out")

obj <- readRDS(rds_path)
size_in <- file.size(rds_path) / 1e6

keep_reducs <- intersect(c("pca", "umap"), Reductions(obj))
slim <- DietSeurat(obj, assays = "RNA", dimreducs = keep_reducs,
                   graphs = character(0))
# DietSeurat keeps scale.data by default behaviour varies; force-drop it
slim[["RNA"]] <- SetAssayData(slim[["RNA"]], layer = "scale.data",
                              new.data = NULL)

saveRDS(slim, out_path)
size_out <- file.size(out_path) / 1e6
cat(sprintf("[export_slim] %s -> %s | %.1f MB -> %.1f MB (reductions kept: %s)\n",
            basename(rds_path), basename(out_path), size_in, size_out,
            paste(keep_reducs, collapse = ",")))
