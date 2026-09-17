# [Verbatim from the CRE 67-isolate reproduction pack sec 4.6. Changes vs the reproduction pack: header comment (ASCII English) + Rscript path neutralized + table renamed to the skill-wide Table1-10 scheme (manuscript number kept alongside). Inputs are the pseudonymized frozen CSVs.]
# encoding: UTF-8
# ----------------------------------------------------------------------------
# Table 5_sul_genes script (manuscript Table 5_sul_genes): sulfonamide resistance gene (sul) combinations x carbapenemase groups
# Run: Rscript table5_sul_genes.R
# Purpose: read CRE data -> group by Bla_Carb_acquired -> clean
#          Sulfonamides_acquired (strip Kleborate flags */^, de-duplicate,
#          e.g. sul1;sul1;sul2 -> sul1;sul2) to build combination patterns ->
#          cross-tabulate n (%) -> fill the Table 5_sul_genes section of
#          Table-all.md -> write table5_sul_genes.csv
# ----------------------------------------------------------------------------
options(stringsAsFactors = FALSE)
# run in the folder containing the frozen CSV files and Table-all.md
# (all inputs ship together in the reproducibility archive)

MD_FILE  <- "Table-all.md"
CRE_FILE <- "clinical_data_CRE_67_patients.csv"

# ---------------- Read and clean (keep empty species strings for exclusion) ----------------
d <- read.csv(CRE_FILE, check.names = FALSE, stringsAsFactors = FALSE)
d <- d[!(is.na(d[["species"]]) | d[["species"]] %in% c("", "abaumannii_2")), , drop = FALSE]
stopifnot(nrow(d) == 67)

# ---------------- Carbapenemase grouping ----------------
carb <- d[["Bla_Carb_acquired"]]
carb[is.na(carb)] <- "-"
grp <- ifelse(carb == "KPC-2", "KPC-2",
       ifelse(carb == "NDM-1", "NDM-1",
       ifelse(carb %in% c("NDM-5", "NDM-5*"), "NDM-5",
       ifelse(carb == "OXA-181", "OXA-181",
       ifelse(carb == "-", "None", NA_character_)))))
stopifnot(!any(is.na(grp)))

grp_order <- c("KPC-2", "NDM-1", "NDM-5", "OXA-181", "None")
grp_n     <- setNames(c(13, 18, 22, 1, 13), grp_order)
stopifnot(all(table(factor(grp, grp_order)) == grp_n))

# ---------------- sul combination patterns (strip flags, de-duplicate, keep order) ----------------
clean_pattern <- function(x) {
  if (is.na(x) || x == "" || x == "-") return("None detected")
  parts <- strsplit(x, ";", fixed = TRUE)[[1]]
  parts <- gsub("[*^]", "", parts)
  parts <- parts[parts != ""]
  parts <- unique(parts)
  if (length(parts) == 0) return("None detected")
  paste(parts, collapse = ";")
}
sul <- vapply(d[["Sulfonamides_acquired"]], clean_pattern, character(1), USE.NAMES = FALSE)

# Row-label format: genes in italics, e.g. *sul1*;*sul2*
fmt_label <- function(pattern) {
  if (pattern == "None detected") return("None detected")
  paste0("*", gsub(";", "*;*", pattern, fixed = TRUE), "*")
}

# ---------------- Read S3 template row labels from Table-all.md ----------------
src <- readLines(MD_FILE, encoding = "UTF-8")
h <- grep("^## Table 5_sul_genes \\(revised\\)", src)
stopifnot(length(h) == 1)

start <- NA
for (i in (h + 1):length(src)) if (grepl("^\\|", src[i])) { start <- i; break }
stopifnot(!is.na(start))
end <- start
while (end < length(src) && grepl("^\\|", src[end + 1])) end <- end + 1

block       <- src[start:end]
header_line <- block[1]
sep_line    <- block[2]
tpl_labels  <- trimws(sub("\\s*\\|.*$", "", sub("^\\|\\s*", "", block[-(1:2)])))
my_labels   <- vapply(sul, fmt_label, character(1), USE.NAMES = FALSE)

# Template labels without asterisks must match the data patterns (order may
# differ, but the sets must be identical)
tpl_keys   <- gsub("\\*", "", tpl_labels)
data_keys  <- gsub("\\*", "", unique(my_labels))
stopifnot(setequal(tpl_keys, data_keys))
stopifnot(!anyDuplicated(tpl_labels))

# ---------------- Cross-tabulate (counts only; dash for zero cells) ----------------
rows <- lapply(tpl_labels, function(lab) {
  key <- gsub("\\*", "", lab)
  idx <- sul == key
  cnt <- vapply(grp_order, function(g) sum(idx & grp == g), integer(1))
  c(lab, ifelse(cnt == 0, "\u2013", as.character(cnt)), as.character(sum(cnt)))
})

# ---------------- Replace the S3 row block in Table-all.md ----------------
new_block <- c(header_line, sep_line,
               vapply(rows, function(r) paste0("| ", paste(r, collapse = " | "), " |"), character(1)))
out <- c(src[1:(start - 1)], new_block, src[(end + 1):length(src)])
con <- file(MD_FILE, open = "wb", encoding = "UTF-8")
writeLines(out, con, useBytes = FALSE)
close(con)

# ---------------- Write CSV ----------------
csv_df <- as.data.frame(t(as.data.frame(rows, stringsAsFactors = FALSE)),
                        stringsAsFactors = FALSE)
names(csv_df) <- c("Factor", grp_order, "Total")
write.csv(csv_df, "table5_sul_genes.csv", row.names = FALSE, fileEncoding = "UTF-8")

cat("Table 5_sul_genes done: filled into Table-all.md and written to table5_sul_genes.csv\n")
