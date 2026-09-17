# [Verbatim from the CRE 67-isolate reproduction pack sec 4.5. Changes vs the reproduction pack: header comment (ASCII English) + Rscript path neutralized + table renamed to the skill-wide Table1-10 scheme (manuscript number kept alongside). Inputs are the pseudonymized frozen CSVs.]
# encoding: UTF-8
# ----------------------------------------------------------------------------
# Table 4_sequence_types script (manuscript Table 4_sequence_types): species-ST combinations x carbapenemase groups (counts only)
# Run: Rscript table4_sequence_types.R
# Purpose: read CRE data -> group by Bla_Carb_acquired -> build combinations of
#          species.1 (abbreviated) + ST ("-" treated as untypeable) ->
#          cross-tabulate (counts only) -> fill the Table 4_sequence_types
#          section of Table-all.md -> write table4_sequence_types.csv
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

# ---------------- Species abbreviation + ST combination keys ----------------
# Rule: abbreviate the first word (initial + ". "), keep the rest; ST "-" is
# recorded as untypeable
abbrev <- function(s) {
  w <- strsplit(s, " ", fixed = TRUE)[[1]]
  paste0(substr(w[1], 1, 1), ". ", paste(w[-1], collapse = " "))
}
sp <- vapply(d[["species.1"]], abbrev, character(1), USE.NAMES = FALSE)
st <- d[["ST"]]
key <- ifelse(is.na(st) | st == "-",
              paste0(sp, " \u2014 untypeable"),
              paste0(sp, " ST", st))

# ---------------- Read S2 template row labels from Table-all.md ----------------
src <- readLines(MD_FILE, encoding = "UTF-8")
h <- grep("^## Table 4_sequence_types \\(revised\\)", src)
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
tpl_keys    <- gsub("\\*", "", tpl_labels)

# The set of template row labels must exactly match the data combination keys
stopifnot(setequal(tpl_keys, key))
stopifnot(!anyDuplicated(tpl_labels))
stopifnot(length(tpl_labels) == length(unique(key)))

# ---------------- Cross-tabulate (counts only) ----------------
rows <- lapply(tpl_labels, function(lab) {
  k  <- gsub("\\*", "", lab)
  idx <- key == k
  cnt <- vapply(grp_order, function(g) sum(idx & grp == g), integer(1))
  c(lab, ifelse(cnt == 0, "\u2013", as.character(cnt)), as.character(sum(cnt)))
})

# ---------------- Replace the S2 row block in Table-all.md ----------------
new_block <- c(header_line, sep_line,
               vapply(rows, function(r) paste0("| ", paste(r, collapse = " | "), " |"), character(1)))
out <- c(src[1:(start - 1)], new_block, src[(end + 1):length(src)])
con <- file(MD_FILE, open = "wb", encoding = "UTF-8")
writeLines(out, con, useBytes = FALSE)
close(con)

# ---------------- Write CSV ----------------
csv_df <- as.data.frame(t(as.data.frame(rows, stringsAsFactors = FALSE)),
                        stringsAsFactors = FALSE)
names(csv_df) <- c("Species_ST", grp_order, "Total")
write.csv(csv_df, "table4_sequence_types.csv", row.names = FALSE, fileEncoding = "UTF-8")

cat("Table 4_sequence_types done: filled into Table-all.md and written to table4_sequence_types.csv\n")
