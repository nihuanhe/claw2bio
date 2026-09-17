# Stage 04 — marker genes (presto if available) + SingleR annotation.
# args: --plan <json> --output <dir> --organism human|mouse
#       [--reference <celldex name>] [--custom-ref <rds>]
#       [--marker-file <csv>] [--no-annotation]
# In:  .checkpoints/03_clustered.rds
# Out: markers_all.csv, top10_markers.csv, annotation_per_cluster.csv,
#      annotated_seurat.rds (+ .checkpoints/04_annotated.rds),
#      UMAP_by_annotation.*, marker heatmap/dotplot, annotation_summary.json

suppressPackageStartupMessages({
  library(Seurat)
  library(dplyr)
  library(ggplot2)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
get_arg <- function(flag, default = NULL) {
  i <- which(args == flag)
  if (length(i) && i < length(args)) args[i + 1] else default
}
out_dir   <- get_arg("--output")
organism  <- get_arg("--organism", "human")
ref_name  <- get_arg("--reference")
custom_ref <- get_arg("--custom-ref")
marker_file <- get_arg("--marker-file")
no_annot  <- "--no-annotation" %in% args
ck <- file.path(out_dir, ".checkpoints")

pbmc <- readRDS(file.path(ck, "03_clustered.rds"))
# layers were split for integration in stage03: join them back for DE
pbmc <- JoinLayers(pbmc, assay = "RNA")
Idents(pbmc) <- "seurat_clusters"

# ---------------------------------------------------------------- markers
n_clu <- length(levels(pbmc$seurat_clusters))
if (n_clu < 2) {
  cat("[stage04] only", n_clu, "cluster -> marker DE skipped (nothing to compare)\n")
  markers <- data.frame(cluster = character(), gene = character(),
                        avg_log2FC = numeric(), pct_in = numeric(),
                        pct_out = numeric(), p_val = numeric(),
                        p_val_adj = numeric())
  write.csv(markers, file.path(out_dir, "markers_all.csv"), row.names = FALSE)
  write.csv(markers, file.path(out_dir, "top10_markers.csv"), row.names = FALSE)
  top5 <- character()
} else {
cat("[stage04] FindAllMarkers ...\n")
if (requireNamespace("presto", quietly = TRUE)) {
  # call presto on the matrix directly: the CRAN presto 1.0.0 Seurat method
  # uses the defunct `slot=` arg and breaks on SeuratObject v5
  mat_de <- GetAssayData(pbmc, assay = "RNA", layer = "data")
  mk <- presto::wilcoxauc(mat_de, y = pbmc$seurat_clusters)
  markers <- mk %>%
    group_by(group) %>%
    mutate(p_val_adj = p.adjust(pval, method = "BH")) %>%
    rename(cluster = group, gene = feature, avg_log2FC = logFC,
           p_val = pval) %>%
    select(cluster, gene, avg_log2FC, pct_in = pct_in, pct_out = pct_out,
           p_val, p_val_adj, auc) %>%
    as.data.frame()
} else {
  cat("[stage04] presto not installed -> Seurat wilcox (slow)\n")
  markers <- FindAllMarkers(pbmc, only.pos = FALSE, verbose = FALSE) %>%
    rename(pct_in = pct.1, pct_out = pct.2) %>% as.data.frame()
}
write.csv(markers, file.path(out_dir, "markers_all.csv"), row.names = FALSE)

top10 <- markers %>%
  filter(p_val_adj < 0.05, avg_log2FC > 0) %>%
  group_by(cluster) %>%
  slice_max(order_by = avg_log2FC, n = 10, with_ties = FALSE) %>%
  as.data.frame()
write.csv(top10, file.path(out_dir, "top10_markers.csv"), row.names = FALSE)
cat(sprintf("[stage04] markers: %d rows, top10 -> top10_markers.csv\n",
            nrow(markers)))

# marker heatmap + dotplot (top5 per cluster)
top5 <- top10 %>% group_by(cluster) %>% slice_head(n = 5) %>% pull(gene) %>%
  unique()
top5 <- top5[top5 %in% rownames(pbmc)]
}  # end n_clu >= 2
if (length(top5) >= 2) {
  p_heat <- DoHeatmap(pbmc, features = top5) + NoLegend()
  ggsave(file.path(out_dir, "marker_heatmap.png"), p_heat,
         width = 12, height = 8, dpi = 300)
  ggsave(file.path(out_dir, "marker_heatmap.pdf"), p_heat,
         width = 12, height = 8)
  p_dot <- DotPlot(pbmc, features = top5) + RotatedAxis()
  ggsave(file.path(out_dir, "marker_dotplot.png"), p_dot,
         width = 12, height = 6, dpi = 300)
  ggsave(file.path(out_dir, "marker_dotplot.pdf"), p_dot,
         width = 12, height = 6)
}

# ---------------------------------------------------------------- annotation
annot_summary <- list(mode = "none")
pbmc$cell_type_final <- paste0("Cluster_", pbmc$seurat_clusters)

if (!no_annot && (requireNamespace("SingleR", quietly = TRUE) &&
                  requireNamespace("celldex", quietly = TRUE))) {
  suppressPackageStartupMessages({ library(SingleR); library(celldex) })
  refs <- list()
  if (!is.null(custom_ref)) {
    refs[["custom"]] <- readRDS(custom_ref)
  } else if (!is.null(ref_name)) {
    refs[[ref_name]] <- get(ref_name, envir = asNamespace("celldex"))()
  } else if (organism == "human") {
    refs[["HPCA"]] <- celldex::HumanPrimaryCellAtlasData()
    refs[["BlueprintEncode"]] <- celldex::BlueprintEncodeData()
  } else {
    refs[["ImmGen"]] <- celldex::ImmGenData()
    refs[["MouseRNAseq"]] <- celldex::MouseRNAseqData()
  }
  cat("[stage04] SingleR with references:", paste(names(refs), collapse = ", "), "\n")

  mat <- GetAssayData(pbmc, assay = "RNA", layer = "data")
  per_cell <- list()
  failed_refs <- character()
  for (nm in names(refs)) {
    pred <- tryCatch(
      SingleR(test = mat, ref = refs[[nm]], labels = refs[[nm]]$label.main),
      error = function(e) {
        cat(sprintf("[stage04] WARNING: reference %s failed: %s\n",
                    nm, conditionMessage(e)))
        failed_refs <<- c(failed_refs, nm)
        NULL
      })
    if (!is.null(pred))
      per_cell[[nm]] <- pred$labels[match(colnames(pbmc), rownames(pred))]
  }
  refs <- refs[setdiff(names(refs), failed_refs)]
  if (length(per_cell) == 0) {
    cat("[stage04] WARNING: all references failed (no gene overlap?) -> ",
        "falling back to Cluster_N labels\n")
  }
  if (length(per_cell) > 0) {
  per_cell <- as.data.frame(per_cell)
  rownames(per_cell) <- colnames(pbmc)

  # cluster consensus per reference
  cl <- pbmc$seurat_clusters
  consensus <- lapply(names(refs), function(nm) {
    tapply(per_cell[[nm]], cl, function(v) {
      names(sort(table(v), decreasing = TRUE))[1]
    })
  })
  names(consensus) <- names(refs)
  cons_df <- as.data.frame(consensus)
  cons_df$cluster <- levels(cl)

  # agreement between the two references
  agree <- rep(NA, nrow(cons_df))
  if (ncol(cons_df) >= 3) {
    agree <- cons_df[[1]] == cons_df[[2]]
  }
  cons_df$refs_agree <- agree
  cons_df$cell_type_final <- cons_df[[1]]
  write.csv(cons_df, file.path(out_dir, "annotation_per_cluster.csv"),
            row.names = FALSE)

  # map consensus back to cells
  lab_map <- setNames(cons_df$cell_type_final, cons_df$cluster)
  pbmc$SingleR_consensus <- unname(lab_map[as.character(cl)])
  for (nm in names(refs)) {
    pbmc[[paste0("SingleR_", nm)]] <- per_cell[[nm]]
  }
  pbmc$cell_type_final <- pbmc$SingleR_consensus

  n_disagree <- sum(!is.na(agree) & !agree)
  if (n_disagree > 0)
    cat(sprintf("[stage04] WARNING: %d cluster(s) disagree between references -> flagged for manual review (see REPORT)\n", n_disagree))
  annot_summary <- list(mode = "SingleR",
                        references = names(refs),
                        refs_disagree_clusters = cons_df$cluster[!is.na(agree) & !agree])

  p_annot <- DimPlot(pbmc, group.by = "cell_type_final", label = TRUE,
                     repel = TRUE) + ggtitle("UMAP by cell_type_final (SingleR consensus)")
  ggsave(file.path(out_dir, "UMAP_by_annotation.png"), p_annot,
         width = 9, height = 7, dpi = 300)
  ggsave(file.path(out_dir, "UMAP_by_annotation.pdf"), p_annot,
         width = 9, height = 7)
  }  # end length(per_cell) > 0
  annot_summary$failed_references <- failed_refs
} else {
  cat("[stage04] annotation skipped (",
      if (no_annot) "--no-annotation" else "SingleR/celldex missing", ")\n")
}

# ---------------------------------------------------------------- save
saveRDS(pbmc, file.path(ck, "04_annotated.rds"))
saveRDS(pbmc, file.path(out_dir, "annotated_seurat.rds"))
write_json(annot_summary, file.path(ck, "annotation_summary.json"),
           auto_unbox = TRUE, pretty = TRUE)
cat(sprintf("[stage04] DONE: annotated_seurat.rds written (%d cells)\n",
            ncol(pbmc)))
