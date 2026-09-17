# stage_virtual_ko.R — scTenifoldKnk virtual knockout on the regular
# pipeline's annotated_seurat.rds.
# args: --rds <rds> --output <dir> --gene <symbol>
#       [--subset-labels "a,b"] [--nfeatures 2000] [--all-genes]
#       [--nc-nnet 10] [--cores 0]
# Adapted from the user's validated 虚拟敲除.R (PMID: 35510185;
# https://github.com/calab-tamu/sctenifoldknk).

suppressPackageStartupMessages({
  library(Seurat)
  library(scTenifoldKnk)
  library(dplyr)
  library(ggplot2)
  library(ggrepel)
  library(parallel)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
get_arg <- function(flag, default = NULL) {
  i <- which(args == flag)
  if (length(i) && i < length(args)) args[i + 1] else default
}
rds_path <- get_arg("--rds")
out_dir  <- get_arg("--output")
gene     <- get_arg("--gene")
subset_l <- get_arg("--subset-labels")
nfeat    <- as.integer(get_arg("--nfeatures", "2000"))
all_genes <- "--all-genes" %in% args
nc_nnet  <- as.integer(get_arg("--nc-nnet", "10"))
nc_ncells <- as.integer(get_arg("--nc-ncells", "500"))
cores    <- as.integer(get_arg("--cores", "0"))
if (cores <= 0) cores <- max(1, detectCores() - 1)

pbmc <- readRDS(rds_path)
if (nc_ncells <= 0 || nc_ncells > ncol(pbmc)) nc_ncells <- ncol(pbmc)

# ---- optional subset by cell_type_final
if (!is.null(subset_l)) {
  if (!"cell_type_final" %in% colnames(pbmc[[]]))
    stop("[vko] no cell_type_final column; run the regular pipeline first.")
  keep_lab <- trimws(strsplit(subset_l, ",", fixed = TRUE)[[1]])
  before <- ncol(pbmc)
  pbmc <- subset(pbmc, subset = cell_type_final %in% keep_lab)
  cat(sprintf("[vko] subset to {%s}: %d -> %d cells\n",
              paste(keep_lab, collapse = ","), before, ncol(pbmc)))
}

# ---- gene presence + expression sanity
if (!gene %in% rownames(pbmc))
  stop("[vko] gene '", gene, "' not in the matrix. Check symbol spelling ",
       "(case-sensitive) — available example: ",
       paste(head(rownames(pbmc), 5), collapse = ", "))
counts <- LayerData(pbmc, assay = "RNA", layer = "counts")
expr_rank <- match(gene, rownames(pbmc)[order(Matrix::rowSums(counts),
                                              decreasing = TRUE)])
expr_pct <- 100 * mean(counts[gene, ] > 0)
cat(sprintf("[vko] %s: expressed in %.1f%% of cells, abundance rank %d/%d\n",
            gene, expr_pct, expr_rank, nrow(pbmc)))
if (expr_pct < 5)
  cat("[vko] WARNING: target gene expressed in <5% of cells — results may be unreliable\n")

# ---- gene set for network construction
if (all_genes) {
  genes_use <- rownames(pbmc)
} else {
  pbmc <- NormalizeData(pbmc, verbose = FALSE)
  pbmc <- FindVariableFeatures(pbmc, nfeatures = nfeat, verbose = FALSE)
  genes_use <- VariableFeatures(pbmc)
}
if (!gene %in% genes_use) genes_use <- c(genes_use, gene)  # force-include target
cat(sprintf("[vko] network genes: %d (target force-included)\n",
            length(genes_use)))

mat <- as.matrix(counts[genes_use, ])

# ---- virtual knockout (memory-peak step)
cat(sprintf("[vko] sctenifoldknk: %d networks x %d cells/net, %d cores ...\n",
            nc_nnet, nc_ncells, cores))
res <- scTenifoldKnk(countMatrix = mat, gKO = gene, qc = FALSE,
                     nc_nNet = nc_nnet, nc_nCells = nc_ncells,
                     nc_nComp = 3, nCores = cores)
df <- res$diffRegulation
# harmonise column names across package versions (1.0.3: gene/distance/Z/FC/p.value/p.adj)
ren <- c(gene = "Gene", p.adj = "p_adj", p.value = "p_value")
for (old in names(ren)) if (old %in% colnames(df)) colnames(df)[colnames(df) == old] <- ren[old]
write.csv(df, file.path(out_dir, paste0(gene, "_diffRegulation.csv")),
          row.names = FALSE)

# ---- plot A: top20 |FC| barplot
top <- df %>% slice_max(order_by = abs(FC), n = 20, with_ties = FALSE) %>%
  mutate(regulation = ifelse(FC > 0, "up", "down"))
p1 <- ggplot(top, aes(x = reorder(Gene, FC), y = FC, fill = regulation)) +
  geom_bar(stat = "identity", color = "black", width = 0.7, linewidth = 0.2) +
  coord_flip() +
  scale_fill_manual(values = c(up = "#E64B13", down = "#468DD1")) +
  geom_hline(yintercept = 0, linetype = "dashed") +
  labs(title = paste0("Top 20 genes: ", gene, " virtual KO"),
       x = "Gene", y = "Fold Change") +
  theme_bw() +
  theme(legend.position = "top", axis.text.y = element_text(face = "italic"))
ggsave(file.path(out_dir, paste0(gene, "_barplot_top20.png")), p1,
       width = 6, height = 5, dpi = 300)
ggsave(file.path(out_dir, paste0(gene, "_barplot_top20.pdf")), p1,
       width = 6, height = 5)

# ---- plot B: Z-score vs p scatter
df$log_pval <- -log10(df$p_adj)
df$group <- "not significant"
df$group[df$Z > 1.96 & df$p_adj < 0.05] <- "up"
df$group[df$Z < -1.96 & df$p_adj < 0.05] <- "down"
lab_g <- df %>% filter(abs(Z) > 2, p_adj < 0.01)
p2 <- ggplot(df, aes(x = Z, y = log_pval, color = group)) +
  geom_point(size = 0.8, alpha = 0.6) +
  scale_color_manual(values = c(up = "#E64B13", down = "#468DD1",
                                `not significant` = "grey70")) +
  geom_text_repel(data = lab_g, aes(label = Gene), size = 3,
                  max.overlaps = 20, fontface = "italic") +
  labs(title = paste0(gene, " virtual KO: Z-score vs significance"),
       x = "Z-score", y = "-log10(p_adj)") +
  theme_bw() + theme(legend.position = "top")
ggsave(file.path(out_dir, paste0(gene, "_zscore_scatter.png")), p2,
       width = 7, height = 6, dpi = 300)
ggsave(file.path(out_dir, paste0(gene, "_zscore_scatter.pdf")), p2,
       width = 7, height = 6)

n_sig <- sum(df$p_adj < 0.05, na.rm = TRUE)
write_json(list(gene = gene, n_cells = ncol(mat), n_genes = length(genes_use),
                nc_nnet = nc_nnet, nc_ncells = nc_ncells, n_significant = n_sig,
                gene_expr_rank = expr_rank),
           file.path(out_dir, "virtual_ko_summary.json"),
           auto_unbox = TRUE, pretty = TRUE)
cat(sprintf("[vko] DONE: %d significant (p_adj<0.05) -> %s\n", n_sig, out_dir))
