# [Verbatim from the CRE 67-isolate reproduction pack sec 4.2. Changes vs the reproduction pack: header comment (ASCII English) + Rscript path neutralized + table renamed to the skill-wide Table1-10 scheme (manuscript number kept alongside). Inputs are the pseudonymized frozen CSVs.]
# encoding: UTF-8
# ----------------------------------------------------------------------------
# Table 1_Baseline script (manuscript Table 1): baseline characteristics (CRE 67 vs CSE 72)
# Run: Rscript table1_baseline.R
# Purpose: read the two clinical datasets -> compute statistics for
#          sex/age/weight/smoking -> fill the Table 1_Baseline section of
#          Table-all.md -> write table1_baseline.csv
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
  d <- d[!(d[["species"]] %in% c("", "abaumannii_2")), , drop = FALSE]  # drop empty rows and A. baumannii
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

# ---------------- Statistics utilities ----------------
# 2x2 chi-square (no continuity correction; Fisher's exact test when expected count < 5)
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

# ---------------- Table 1 statistics ----------------
n1 <- nrow(cre); n2 <- nrow(cse)

sex_cre <- c(Male = sum(cre$Gender == 0), Female = sum(cre$Gender == 1))
sex_cse <- c(Male = sum(cse$Gender == 0), Female = sum(cse$Gender == 1))
sex_stat <- chisq_or_fisher(sex_cre["Male"], sex_cre["Female"], sex_cse["Male"], sex_cse["Female"])

age_t <- t.test(cre$Age, cse$Age, var.equal = TRUE)   # Student's t-test
wt_t  <- t.test(cre$Weight, cse$Weight, var.equal = TRUE)

smk_cre <- c(Yes = sum(cre$Smoking == 1), No = sum(cre$Smoking == 0))
smk_cse <- c(Yes = sum(cse$Smoking == 1), No = sum(cse$Smoking == 0))
smk_stat <- chisq_or_fisher(smk_cre["Yes"], smk_cre["No"], smk_cse["Yes"], smk_cse["No"])

# ---------------- Build Table 1 data rows ----------------
fmt_mean_sd <- function(x) sprintf("%.2f \u00b1 %.2f", mean(x), sd(x))  # "69.16 \u00b1 10.43" (space style of published docx)

# group headers carry the chi-square statistic; category rows carry counts only
# (manuscript layout)
rows <- list(
  c("**Sex, No. (%)**", "", "", fmt_stat(sex_stat["stat"]), fmt_p(sex_stat["p"])),
  c("Male", fmt_pct(sex_cre["Male"], n1), fmt_pct(sex_cse["Male"], n2), "", ""),
  c("Female", fmt_pct(sex_cre["Female"], n1), fmt_pct(sex_cse["Female"], n2), "", ""),
  c("**Age (years), mean \u00b1 SD**", fmt_mean_sd(cre$Age), fmt_mean_sd(cse$Age),
    fmt_stat(abs(age_t$statistic)), fmt_p(age_t$p.value)),
  c("**Weight (kg), mean \u00b1 SD**", fmt_mean_sd(cre$Weight), fmt_mean_sd(cse$Weight),
    fmt_stat(abs(wt_t$statistic)), fmt_p(wt_t$p.value)),
  c("**Smoking status, No. (%)**", "", "", fmt_stat(smk_stat["stat"]), fmt_p(smk_stat["p"])),
  c("Yes", fmt_pct(smk_cre["Yes"], n1), fmt_pct(smk_cse["Yes"], n2), "", ""),
  c("No", fmt_pct(smk_cre["No"], n1), fmt_pct(smk_cse["No"], n2), "", "")
)

# ---------------- Replace the Table 1 row block in Table-all.md ----------------
src <- readLines(MD_FILE, encoding = "UTF-8")
h <- grep("^## Table 1_Baseline \\(revised\\)", src)
stopifnot(length(h) == 1)

start <- NA
for (i in (h + 1):length(src)) if (grepl("^\\|", src[i])) { start <- i; break }
stopifnot(!is.na(start))
end <- start
while (end < length(src) && grepl("^\\|", src[end + 1])) end <- end + 1

block <- src[start:end]
header_line <- block[1]      # keep the original header line
sep_line    <- block[2]      # keep the original separator line
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
  Variable  = my_labels,
  CRE       = vapply(rows, function(r) r[2], character(1)),
  CSE       = vapply(rows, function(r) r[3], character(1)),
  Statistic = vapply(rows, function(r) r[4], character(1)),
  P         = vapply(rows, function(r) r[5], character(1)),
  stringsAsFactors = FALSE
)
write.csv(csv_df, "table1_baseline.csv", row.names = FALSE, fileEncoding = "UTF-8")

cat("Table 1_Baseline done: filled into Table-all.md and written to table1_baseline.csv\n")
cat(sprintf("  Age: t=%.3f, P=%.4f (should be significant, <0.05)\n", abs(age_t$statistic), age_t$p.value))
