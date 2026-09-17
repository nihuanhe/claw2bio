# [Verbatim from the CRE 67-isolate reproduction pack sec 4.10. Changes vs the reproduction pack: header comment (ASCII English) + Rscript path neutralized + table renamed to the skill-wide Table1-10 scheme (manuscript number kept alongside). Inputs are the pseudonymized frozen CSVs.]
# encoding: UTF-8
# ----------------------------------------------------------------------------
# Table 10_plasmid_replicons script (manuscript Table 10_plasmid_replicons): plasmid replicon carriage x carbapenemase groups (counts only)
# Run: Rscript table10_plasmid_replicons.R
# Purpose: read CRE data -> group by Bla_Carb_acquired -> locate the replicon
#          columns between the #FILE.1/#FILE.2 markers (column names look like
#          Name_Allele__Accession, e.g. IncX4_1__CP002895) -> aggregate by the
#          "Name" prefix (multiple columns of the same name count as present if
#          any is present; a non-NA/non-empty value means present) ->
#          cross-tabulate (counts only) -> fill the Table 10_plasmid_replicons
#          section of Table-all.md -> write table10_plasmid_replicons.csv
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

# ---------------- Locate the replicon columns (between #FILE.1 and #FILE.2) ----------------
nms   <- names(d)
i1    <- which(nms == "#FILE.1")
i2    <- which(nms == "#FILE.2")
stopifnot(length(i1) == 1, length(i2) == 1, i2 > i1 + 1)
rep_cols <- nms[(i1 + 1):(i2 - 1)]

# Column name -> replicon name: strip "__Accession" and the trailing "_Allele"
# (e.g. IncX4_1__CP002895 -> IncX4)
rep_key <- function(colname) sub("_[0-9]+$", "", sub("__.*$", "", colname))
rep_map <- setNames(rep_key(rep_cols), rep_cols)

# ---------------- Read S8 template row labels from Table-all.md ----------------
src <- readLines(MD_FILE, encoding = "UTF-8")
h <- grep("^## Table 10_plasmid_replicons \\(new\\)", src)
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

# Every template row name must map to at least one data column
stopifnot(all(tpl_labels %in% rep_map))

# ---------------- Cross-tabulate (counts only; one isolate may carry several replicons) ----------------
present <- function(col) !is.na(d[[col]]) & d[[col]] != "" & d[[col]] != "-"

# cell format: n/N (integer %); dash for zero carriage (manuscript layout)
fmt_cell <- function(n, tot) if (n == 0) "\u2013" else sprintf("%d/%d (%d%%)", n, tot, round(100 * n / tot))

rows <- lapply(tpl_labels, function(lab) {
  cols   <- names(rep_map)[rep_map == lab]
  anypos <- Reduce(`|`, lapply(cols, present), init = rep(FALSE, nrow(d)))
  cnt    <- vapply(grp_order, function(g) sum(grp == g & anypos), integer(1))
  c(lab,
    vapply(grp_order, function(g) fmt_cell(cnt[[g]], grp_n[[g]]), character(1)),
    fmt_cell(sum(cnt), 67))
})

# ---------------- Replace the S8 row block in Table-all.md ----------------
new_block <- c(header_line, sep_line,
               vapply(rows, function(r) paste0("| ", paste(r, collapse = " | "), " |"), character(1)))
# S8 is the LAST section of Table-all.md, so its block often ends at EOF;
# the naive c(src[1:(start-1)], new_block, src[(end+1):length(src)]) idiom then
# yields the junk sequence c(NA, <last row>) because (end+1):length(src)
# evaluates to a *decreasing* vector (e.g. 219:218). Guard explicitly instead.
out <- c(src[1:(start - 1)], new_block)
if (end < length(src)) out <- c(out, src[(end + 1):length(src)])
con <- file(MD_FILE, open = "wb", encoding = "UTF-8")
writeLines(out, con, useBytes = FALSE)
close(con)

# ---------------- Write CSV ----------------
csv_df <- as.data.frame(t(as.data.frame(rows, stringsAsFactors = FALSE)),
                        stringsAsFactors = FALSE)
names(csv_df) <- c("Replicon", grp_order, "Total")
write.csv(csv_df, "table10_plasmid_replicons.csv", row.names = FALSE, fileEncoding = "UTF-8")

cat("Table 10_plasmid_replicons done: filled into Table-all.md and written to table10_plasmid_replicons.csv\n")
