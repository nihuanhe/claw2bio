# [Verbatim from the CRE 67-isolate reproduction pack sec 4.9. Changes vs the reproduction pack: header comment (ASCII English) + Rscript path neutralized + table renamed to the skill-wide Table1-10 scheme (manuscript number kept alongside). Inputs are the pseudonymized frozen CSVs.]
# encoding: UTF-8
# ----------------------------------------------------------------------------
# Table 8_univariate script (manuscript Table 8_univariate): univariate analysis of CRE vs CSE
# Run: Rscript table8_univariate.R
# Purpose: for each binary factor, run chi-square (no correction) or Fisher's
#          exact test -> fill the Table 8_univariate section of
#          Table-all.md -> write table8_univariate.csv
# ----------------------------------------------------------------------------
options(stringsAsFactors = FALSE)
# run in the folder containing the frozen CSV files and Table-all.md
# (all inputs ship together in the reproducibility archive)

MD_FILE  <- "Table-all.md"
CRE_FILE <- "clinical_data_CRE_67_patients.csv"
CSE_FILE <- "clinical_data_CSE_72_patients_clean.csv"

# ---------------- Read and clean data ----------------
read_cre <- function() {
  d <- read.csv(CRE_FILE, check.names = FALSE, na.strings = "NA", stringsAsFactors = FALSE)
  d <- d[!(d[["species"]] %in% c("", "abaumannii_2")), , drop = FALSE]
  stopifnot(nrow(d) == 67)
  cl <- d[, 4:25, drop = FALSE]
  names(cl) <- c("Patient_ID","Gender","Age","Weight","Smoking","Surgery","Urinary_cath",
                 "Endo_intub","Puncture_drain","Tracheotomy","Hemodialysis","Gastric_tube",
                 "Diabetes","Hypertension","CAD","Cerebro","Renal_insuff","Pulmonary",
                 "Antibiotic","Prealbumin","Albumin","Hospital_stay")
  cl[] <- lapply(cl, function(x) suppressWarnings(as.numeric(as.character(x))))
  cl
}

read_cse <- function() {
  d <- read.csv(CSE_FILE, check.names = FALSE, na.strings = "NA", stringsAsFactors = FALSE)
  stopifnot(nrow(d) == 72)
  cl <- d[, 2:23, drop = FALSE]
  names(cl) <- c("Patient_ID","Gender","Age","Weight","Smoking","Surgery","Urinary_cath",
                 "Endo_intub","Puncture_drain","Tracheotomy","Hemodialysis","Gastric_tube",
                 "Diabetes","Hypertension","CAD","Cerebro","Renal_insuff","Pulmonary",
                 "Antibiotic","Prealbumin","Albumin","Hospital_stay")
  cl[] <- lapply(cl, function(x) suppressWarnings(as.numeric(as.character(x))))
  cl
}

cre <- read_cre()
cse <- read_cse()
n1 <- nrow(cre); n2 <- nrow(cse)

# ---------------- Statistics utilities ----------------
chisq_or_fisher <- function(a1, a0, b1, b0) {
  tab <- rbind(c(a1, a0), c(b1, b0))
  n <- sum(tab)
  exp_min <- min(outer(rowSums(tab), colSums(tab)) / n)
  if (exp_min < 5) {
    ft <- fisher.test(tab)
    return(c(stat = NA_real_, p = ft$p.value))
  }
  cs <- chisq.test(tab, correct = FALSE)
  c(stat = unname(cs$statistic), p = cs$p.value)
}

fmt_pct <- function(n, tot) sprintf("%d (%.2f)", n, ifelse(tot == 0, 0, 100 * n / tot))
fmt_stat <- function(x) if (is.na(x)) "" else sprintf("%.3f", x)
fmt_p <- function(p) {
  s <- if (p < 0.0001) "<0.0001" else sprintf("%.4f", p)
  if (p < 0.05) paste0("**", s, "**") else s
}

# ---------------- Build S6 data rows ----------------
row_fact <- function(label, col, yes_val, show_stat = TRUE) {
  a <- sum(cre[[col]] == yes_val)
  b <- sum(cse[[col]] == yes_val)
  if (show_stat) {
    st <- chisq_or_fisher(sum(cre[[col]] == 1), sum(cre[[col]] == 0),
                          sum(cse[[col]] == 1), sum(cse[[col]] == 0))
    c(label, fmt_pct(a, n1), fmt_pct(b, n2), fmt_stat(st["stat"]), fmt_p(st["p"]))
  } else {
    c(label, fmt_pct(a, n1), fmt_pct(b, n2), "", "")
  }
}
# group header rows carry the chi-square/P of the whole 2x2 (manuscript layout);
# pure section dividers (col = NULL) carry nothing
row_head <- function(label, col = NULL) {
  if (is.null(col)) return(c(label, "", "", "", ""))
  st <- chisq_or_fisher(sum(cre[[col]] == 1), sum(cre[[col]] == 0),
                        sum(cse[[col]] == 1), sum(cse[[col]] == 0))
  c(label, "", "", fmt_stat(st["stat"]), fmt_p(st["p"]))
}

rows <- list(
  row_head("**Surgery**", "Surgery"),
  row_fact("Yes", "Surgery", 1, FALSE),
  row_fact("No", "Surgery", 0, FALSE),
  row_head("**Invasive procedures**"),
  row_fact("Urinary catheterization", "Urinary_cath", 1, TRUE),
  row_fact("Endotracheal intubation", "Endo_intub", 1, TRUE),
  row_fact("Puncture drainage", "Puncture_drain", 1, TRUE),
  row_fact("Tracheotomy", "Tracheotomy", 1, TRUE),
  row_fact("Hemodialysis", "Hemodialysis", 1, TRUE),
  row_fact("Gastric tube", "Gastric_tube", 1, TRUE),
  row_head("**Basic diseases**"),
  row_fact("Diabetes", "Diabetes", 1, TRUE),
  row_fact("Hypertension", "Hypertension", 1, TRUE),
  row_fact("Coronary artery disease", "CAD", 1, TRUE),
  row_fact("Cerebrovascular disease", "Cerebro", 1, TRUE),
  row_fact("Renal insufficiency", "Renal_insuff", 1, TRUE),
  row_fact("Pulmonary disease", "Pulmonary", 1, TRUE),
  row_head("**Antibiotic usage**", "Antibiotic"),
  row_fact("Multiple therapy", "Antibiotic", 1, FALSE),
  row_fact("Monotherapy", "Antibiotic", 0, FALSE),
  row_head("**Laboratory parameters**"),
  row_head("**Albumin**", "Albumin"),
  row_fact("\u226435 g/L", "Albumin", 0, FALSE),
  row_fact(">35 g/L", "Albumin", 1, FALSE),
  row_head("**Prealbumin**", "Prealbumin"),
  row_fact("\u2264280 mg/L", "Prealbumin", 0, FALSE),
  row_fact(">280 mg/L", "Prealbumin", 1, FALSE),
  row_head("**Hospital length of stay**", "Hospital_stay"),
  row_fact(">7 days", "Hospital_stay", 1, FALSE),
  row_fact("\u22647 days", "Hospital_stay", 0, FALSE)
)

# ---------------- Replace the S6 row block in Table-all.md ----------------
src <- readLines(MD_FILE, encoding = "UTF-8")
h <- grep("^## Table 8_univariate \\(revised\\)", src)
stopifnot(length(h) == 1)

start <- NA
for (i in (h + 1):length(src)) if (grepl("^\\|", src[i])) { start <- i; break }
stopifnot(!is.na(start))
end <- start
while (end < length(src) && grepl("^\\|", src[end + 1])) end <- end + 1

block <- src[start:end]
header_line <- block[1]
sep_line    <- block[2]
tpl_labels  <- trimws(sub("\\s*\\|.*$", "", sub("^\\|\\s*", "", block[-(1:2)])))
my_labels   <- vapply(rows, function(r) r[1], character(1))
strip_md <- function(x) gsub("\\*", "", x)  # ** bold is cosmetic only
stopifnot(identical(strip_md(tpl_labels), strip_md(my_labels)))  # row labels match template (order kept)

new_block <- c(header_line, sep_line,
               vapply(rows, function(r) paste0("| ", paste(r, collapse = " | "), " |"), character(1)))

out <- c(src[1:(start - 1)], new_block, src[(end + 1):length(src)])
con <- file(MD_FILE, open = "wb", encoding = "UTF-8")
writeLines(out, con, useBytes = FALSE)
close(con)

# ---------------- Write CSV ----------------
csv_df <- data.frame(
  Factor    = my_labels,
  CRE       = vapply(rows, function(r) r[2], character(1)),
  CSE       = vapply(rows, function(r) r[3], character(1)),
  Statistic = vapply(rows, function(r) r[4], character(1)),
  P         = vapply(rows, function(r) r[5], character(1)),
  stringsAsFactors = FALSE
)
write.csv(csv_df, "table8_univariate.csv", row.names = FALSE, fileEncoding = "UTF-8")

cat("Table 8_univariate done: filled into Table-all.md and written to table8_univariate.csv\n")
