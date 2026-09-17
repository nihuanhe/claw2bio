# Stage 01 — read all samples per ingest plan, build Seurat objects, merge.
# args: --plan <ingest_plan.json> --output <dir> --organism human|mouse
#       [--min-cells 3] [--min-features 200] [--mt-pattern regex]
# Checkpoint: .checkpoints/01_merged_raw.rds  (+ ingest_summary.json)

suppressPackageStartupMessages({
  library(Seurat)
  library(Matrix)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
get_arg <- function(flag, default = NULL) {
  i <- which(args == flag)
  if (length(i) && i < length(args)) args[i + 1] else default
}
plan     <- fromJSON(get_arg("--plan"), simplifyVector = FALSE)
out_dir  <- get_arg("--output")
organism <- get_arg("--organism", "human")
min_cells    <- as.integer(get_arg("--min-cells", "3"))
min_features <- as.integer(get_arg("--min-features", "200"))
mt_override  <- get_arg("--mt-pattern")
ck <- file.path(out_dir, ".checkpoints")

cat("[stage01] mode:", plan$mode, "| samples:", length(plan$samples), "\n")

# ------------------------------------------------------------------ readers
clean_barcodes <- function(bc, sample) {
  bad <- is.na(bc) | bc == ""
  if (any(bad)) bc[bad] <- paste0("cell_", seq_len(sum(bad)))
  bc <- make.unique(bc, sep = "_")
  paste(sample, bc, sep = "_")
}

read_sample <- function(s) {
  cat(sprintf("[stage01] reading %s (type=%s)\n", s$name, s$type))
  counts <- NULL
  if (s$type == "10x_mtx") {
    counts <- Read10X(data.dir = s$path, gene.column = s$gene_column)
    if (is.list(counts)) counts <- counts[["Gene Expression"]]  # multi-assay 10X
  } else if (s$type == "10x_h5") {
    counts <- Read10X_h5(filename = s$path)
    if (is.list(counts)) counts <- counts[["Gene Expression"]]
  } else if (s$type == "text") {
    sep <- if (!is.null(s$delimiter) && s$delimiter == ",") "," else "\t"
    df <- data.table::fread(s$path, sep = sep, header = TRUE, data.table = FALSE)
    rn <- df[[1]]
    df <- df[, -1, drop = FALSE]
    m <- as.matrix(df)
    storage.mode(m) <- "numeric"
    rownames(m) <- rn
    if (isTRUE(s$transpose)) m <- t(m)
    counts <- as(m, "CsparseMatrix")
  } else if (s$type == "rds") {
    obj <- readRDS(s$path)
    if (inherits(obj, "Seurat")) {
      cat(sprintf("[stage01]   rds is a Seurat object (v%s), %d cells x %d features\n",
                  as.character(obj@version), ncol(obj), nrow(obj)))
      return(obj)   # already a Seurat object: use as-is
    }
    counts <- as(as.matrix(obj), "CsparseMatrix")
    cat("[stage01]   rds was a bare matrix -> CreateSeuratObject\n")
  } else {
    stop("unsupported type in plan: ", s$type)
  }
  colnames(counts) <- clean_barcodes(colnames(counts), s$name)
  md <- data.frame(orig.ident = rep(s$name, ncol(counts)),
                   row.names = colnames(counts),
                   stringsAsFactors = FALSE)
  if (!is.null(s$group)) md$group <- rep(s$group, ncol(counts))
  n_pass <- sum(Matrix::colSums(counts > 0) >= min_features)
  if (n_pass == 0) {
    stop(sprintf(paste0(
      "[stage01] FATAL for sample '%s': 0 cells pass min.features=%d. ",
      "This input looks like a RAW/unfiltered matrix (mostly empty droplets) ",
      "or an extremely sparse matrix. Use the cellranger 'filtered' output, ",
      "or lower --min-features."), s$name, min_features))
  }
  if (n_pass < ncol(counts) * 0.05) {
    cat(sprintf(paste0("[stage01] WARNING: only %d/%d cells of sample '%s' pass ",
                       "min.features=%d (raw matrix?)\n"),
                n_pass, ncol(counts), s$name, min_features))
  }
  CreateSeuratObject(counts = counts, project = s$name,
                     min.cells = min_cells, min.features = min_features,
                     meta.data = md)
}

objs <- lapply(plan$samples, read_sample)

# ------------------------------------------------------------------ merge
if (length(objs) > 1) {
  cat("[stage01] merging", length(objs), "objects (memory-peak step)\n")
  pbmc <- merge(objs[[1]], y = objs[-1],
                add.cell.ids = vapply(plan$samples, function(s) s$name, ""),
                project = "sc_merged")
} else {
  pbmc <- objs[[1]]
}
# Seurat v5: join layers if split (also upgrades v4-style single-layer objects)
ly <- Layers(pbmc, assay = "RNA")
if (length(ly) > 1 || !"counts" %in% ly) {
  cat("[stage01] JoinLayers on:", paste(ly, collapse = ","), "\n")
  pbmc <- JoinLayers(pbmc, assay = "RNA")
}

# ------------------------------------------------------------------ QC metrics
gene_names <- rownames(pbmc)
pick_pattern <- function() {
  if (!is.null(mt_override)) return(mt_override)
  pats <- c("^MT-", "^Mt-", "^mt-", "^MT\\.")
  n <- sapply(pats, function(p) sum(grepl(p, gene_names)))
  if (max(n) == 0) return(NA_character_)
  p <- pats[which.max(n)]
  cat(sprintf("[stage01] mt pattern auto-selected: %s (%d genes)\n", p, max(n)))
  p
}
mt_pat <- pick_pattern()
if (!is.na(mt_pat)) {
  pbmc[["percent.mt"]] <- PercentageFeatureSet(pbmc, pattern = mt_pat)
} else {
  pbmc[["percent.mt"]] <- 0
  cat("[stage01] WARNING: no mitochondrial genes matched; percent.mt set to 0\n")
}
hb_pats <- if (organism == "human") c("^HB[AB]") else c("^Hb[ab]")
hb_genes <- gene_names[Reduce(`|`, lapply(hb_pats, grepl, gene_names))]
if (length(hb_genes) > 0) {
  pbmc[["percent.hb"]] <- PercentageFeatureSet(pbmc, features = hb_genes)
  cat(sprintf("[stage01] hemoglobin genes found: %d (flagged, NOT removed)\n",
              length(hb_genes)))
} else {
  pbmc[["percent.hb"]] <- 0
}

# ------------------------------------------------------------------ save
saveRDS(pbmc, file.path(ck, "01_merged_raw.rds"))
summary <- list(
  n_samples  = length(plan$samples),
  n_cells    = ncol(pbmc),
  n_features = nrow(pbmc),
  mt_pattern = mt_pat,
  cells_per_sample = as.list(table(pbmc$orig.ident)),
  has_group  = "group" %in% colnames(pbmc[[]])
)
write_json(summary, file.path(ck, "ingest_summary.json"), auto_unbox = TRUE, pretty = TRUE)
cat(sprintf("[stage01] DONE: %d cells x %d features -> %s\n",
            ncol(pbmc), nrow(pbmc), file.path(ck, "01_merged_raw.rds")))
