# -*- coding: utf-8 -*-
# =====================================================================
# plot_tree_template.R — publication-ready annotated phylogenetic tree
# (battle-tested template from a published 67-isolate CRE study; the
# bundled example redraws the same style on 12 public NCBI genomes).
#
# INPUT CONTRACT
#   1. Newick treefile (e.g. phylo-tree-build's main_tree/total_iqtree.treefile)
#   2. Annotation CSV: first column = SampleID (must match tree tip labels),
#      remaining columns = any categorical annotations (use "-" for none).
#
# HOW TO REUSE (AI agent / user): edit ONLY the CONFIG block below —
# paths, the branch-color column, the ring columns, colors, geometry.
# Everything downstream adapts automatically (ring count, palettes,
# legends). stopifnot guards fail loudly instead of drawing a wrong figure.
#
# Runs on Windows R (tested 4.5.2): ggtree, treeio, ggplot2, ggnewscale,
# RColorBrewer, viridis, cowplot, phytools.
# =====================================================================

suppressPackageStartupMessages({
  library(ggtree); library(treeio); library(ggplot2); library(ggnewscale)
  library(RColorBrewer); library(viridis); library(cowplot)
})

# ======================= CONFIG (EDIT THIS BLOCK) =====================
TREEFILE   <- "examples/input/main_tree/total_iqtree.treefile"  # Newick
ANN_CSV    <- "examples/input/annotation.csv"   # col1 = SampleID
OUT_DIR    <- "examples/output"

GROUP_COL  <- "Genus"            # annotation column mapped to branch colors
GROUP_LEVELS <- c("Escherichia", "Klebsiella", "Enterobacter", "Others")
                                 # order in legend; values not listed -> "Others"
GROUP_COLORS <- c("Escherichia" = "#31A354", "Klebsiella" = "#2C7FB8",
                  "Enterobacter" = "#E34A33", "Others" = "grey50")

RING_COLS  <- c("SpeciesGrp", "ContigBand")   # annotation columns -> rings
RING_NAMES <- c("Species group", "Contig count")  # legend titles, same order
RING_PALETTES <- list(c("#E5F5E0", "#31A354"), c("#EFF3FF", "#08519C"))
                                 # one low->high color pair per ring
RING_NA    <- "lightgray"        # color for "-" / missing values

LAYOUT     <- "circular"         # "circular" or "rectangular"
MIDPOINT_ROOT <- TRUE            # midpoint rooting for visualization
BRANCH_LENGTH <- "none"          # "none" = cladogram; keep NULL-ish default otherwise

RING_WIDTH <- 0.1                # ring thickness (data units)
RING_GAP   <- 1.7                # gap between rings (data units)
FONT       <- "Arial"
FIG_W_CM   <- 14                 # journal column width
TREE_H_CM  <- 12.0               # tree cell height
LEG_H_CM   <- 8.5                # legend grid height
DPI        <- 600
OUT_STEM   <- "phylo_tree"       # output file stem
# =====================================================================

dir.create(OUT_DIR, showWarnings = FALSE, recursive = TRUE)
stopifnot(file.exists(TREEFILE), file.exists(ANN_CSV))

# ---------- 1. tree + branch groups ----------
tree <- read.tree(TREEFILE)
ann <- read.csv(ANN_CSV, stringsAsFactors = FALSE, check.names = FALSE)
stopifnot(ncol(ann) >= 2)
colnames(ann)[1] <- "SampleID"
stopifnot(all(tree$tip.label %in% ann$SampleID))
stopifnot(all(c(GROUP_COL, RING_COLS) %in% colnames(ann)))

# branch coloring by GROUP_COL via groupOTU on per-group tip lists
grp <- ann[[GROUP_COL]][match(tree$tip.label, ann$SampleID)]
grp[!(grp %in% GROUP_LEVELS)] <- "Others"
tip_groups <- split(tree$tip.label, grp)
tip_groups <- tip_groups[names(tip_groups) %in% GROUP_LEVELS]
tree <- groupOTU(tree, .node = tip_groups, group_name = "Grp")
if (MIDPOINT_ROOT) {
  tree <- phytools::midpoint_root(as.phylo(tree))
  tree <- groupOTU(tree, .node = tip_groups, group_name = "Grp")
}

p <- ggtree(tree, layout = LAYOUT, branch.length = BRANCH_LENGTH,
            aes(color = Grp))
p$data$Grp <- as.character(p$data$Grp)
p$data$Grp[!p$data$Grp %in% GROUP_LEVELS] <- "Others"
p$data$Grp <- factor(p$data$Grp, levels = GROUP_LEVELS)
p <- p + scale_color_manual(name = GROUP_COL, values = GROUP_COLORS) +
  theme(legend.position = "right")

# ---------- 2. rings (generic loop) ----------
mk_ring_df <- function(col) {
  d <- data.frame(ann[[col]], row.names = ann$SampleID)
  colnames(d) <- col
  d[tree$tip.label, , drop = FALSE]
}

p_cur <- p
ring_palettes <- list()   # remember per-ring colors for standalone legends
for (i in seq_along(RING_COLS)) {
  col <- RING_COLS[i]
  df <- mk_ring_df(col)
  u <- sort(unique(df[[col]])); u <- u[u != "-" & !is.na(u)]
  pal <- RING_PALETTES[[((i - 1) %% length(RING_PALETTES)) + 1]]
  cols <- setNames(colorRampPalette(pal)(length(u)), u)
  cols <- c(cols, c("-" = RING_NA))
  ring_palettes[[col]] <- cols
  if (i > 1) p_cur <- p_cur + new_scale_fill()
  p_cur <- gheatmap(p_cur, df, offset = (i - 1) * RING_GAP, width = RING_WIDTH,
                    colnames = FALSE, color = NA) +
    scale_fill_manual(name = RING_NAMES[i], values = cols, na.value = "white",
                      guide = guide_legend(ncol = 2, byrow = TRUE))
}
n_rings <- length(RING_COLS)
gb <- ggplot_build(p_cur)
is_tile <- vapply(gb$data, function(d) all(c("xmin", "xmax") %in% names(d)), TRUE)
stopifnot(sum(is_tile) == n_rings)
cat("rings drawn:", n_rings, "(", paste(RING_COLS, collapse = ", "), ")\n")

# ---------- 3. standalone legends + grid below the tree ----------
leg_theme <- theme(legend.position = "right",
                   legend.title = element_text(family = FONT, size = 6),
                   legend.text  = element_text(family = FONT, size = 6),
                   legend.key.size = unit(0.25, "cm"),
                   legend.spacing.y = unit(0.03, "cm"))

p_tree <- p_cur + theme(legend.position = "none")

mk_fill_leg <- function(title, values, ncol = 2) {
  d <- data.frame(lab = factor(names(values), levels = names(values)), y = 1)
  g <- ggplot(d, aes(lab, y, fill = lab)) + geom_tile() +
    scale_fill_manual(name = title, values = values,
                      guide = guide_legend(ncol = ncol, byrow = TRUE)) + leg_theme
  get_legend(g)
}
g_grp <- {
  d <- data.frame(lab = factor(GROUP_LEVELS, levels = GROUP_LEVELS), y = 1)
  g <- ggplot(d, aes(lab, y, color = lab, group = 1)) + geom_line(linewidth = 1) +
    scale_color_manual(name = GROUP_COL, values = GROUP_COLORS,
                       guide = guide_legend(ncol = 1)) + leg_theme
  get_legend(g)
}
leg_list <- list(g_grp)
leg_names <- c(GROUP_COL)
for (i in seq_along(RING_COLS)) {
  leg_list <- c(leg_list, list(mk_fill_leg(RING_NAMES[i], ring_palettes[[RING_COLS[i]]])))
  leg_names <- c(leg_names, RING_COLS[i])
}
names(leg_list) <- leg_names

# legend grid: two columns, packed top-left (simple generic layout)
leg_w <- function(g) grid::convertWidth(grid::grobWidth(g), "cm", TRUE)
leg_h <- function(g) grid::convertHeight(grid::grobHeight(g), "cm", TRUE)
legend_cell <- ggdraw()
x_col <- c(0.2, FIG_W_CM / 2)
y_top <- 0.15
col_i <- 1
for (nm in leg_names) {
  g <- leg_list[[nm]]
  legend_cell <- legend_cell +
    draw_grob(g, x = x_col[col_i] / FIG_W_CM,
              y = (LEG_H_CM - y_top - leg_h(g)) / LEG_H_CM,
              width = (leg_w(g) + 0.4) / FIG_W_CM, height = leg_h(g) / LEG_H_CM)
  if (col_i == 1) { col_i <- 2 } else { col_i <- 1; y_top <- y_top + leg_h(g) + 0.4 }
}

final <- plot_grid(ggdraw(p_tree), legend_cell, ncol = 1,
                   rel_heights = c(TREE_H_CM, LEG_H_CM))

# ---------- 4. export (PDF via cairo for font embedding; PNG at DPI) ----------
for (nm in leg_names) {
  g <- leg_list[[nm]]
  ggsave(file.path(OUT_DIR, paste0(OUT_STEM, "_legend_", nm, ".png")),
         ggdraw(g), width = leg_w(g) + 0.4, height = leg_h(g) + 0.2,
         units = "cm", dpi = DPI, bg = "white")
}
ggsave(file.path(OUT_DIR, paste0(OUT_STEM, ".pdf")), final,
       width = FIG_W_CM, height = TREE_H_CM + LEG_H_CM, units = "cm",
       device = cairo_pdf)
ggsave(file.path(OUT_DIR, paste0(OUT_STEM, ".png")), final,
       width = FIG_W_CM, height = TREE_H_CM + LEG_H_CM, units = "cm",
       dpi = DPI, type = "cairo")

# ---------- 5. console anchors (verification) ----------
cat("tree written to", OUT_DIR, "\n")
cat("tips:", length(tree$tip.label),
    "| ring levels:",
    paste(vapply(RING_COLS, function(c)
      paste0(c, "=", length(setdiff(unique(ann[[c]]), "-"))), character(1)),
      collapse = ", "), "\n")
