# [Verbatim from the CRE 67-isolate reproduction pack sec 4.3. Changes vs the reproduction pack: header comment (ASCII English) + Rscript path neutralized + table renamed to the skill-wide Table1-10 scheme (manuscript number kept alongside). Inputs are the pseudonymized frozen CSVs.]
# encoding: UTF-8
# ----------------------------------------------------------------------------
# Table 2_Firth script (manuscript Table 2): Firth penalized-likelihood multivariable logistic regression (CRE vs CSE)
# Run: Rscript table2_firth.R
# Purpose: read the two clinical datasets -> fit the 9-variable model with logistf
#          -> fill the Table 2_Firth section of Table-all.md -> write table2_firth.csv
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

# ---------------- Combine data and fit the Firth regression ----------------
comb <- data.frame(
  CRE          = c(rep(1, nrow(cre)), rep(0, nrow(cse))),
  Endo_intub   = c(cre$Endo_intub, cse$Endo_intub),          # endotracheal intubation
  Diabetes     = c(cre$Diabetes, cse$Diabetes),
  Cerebro      = c(cre$Cerebro, cse$Cerebro),                # cerebrovascular disease
  Urinary_cath = c(cre$Urinary_cath, cse$Urinary_cath),      # urinary catheterization
  Age          = c(cre$Age, cse$Age),
  Gastric_tube = c(cre$Gastric_tube, cse$Gastric_tube),
  Pulmonary    = c(cre$Pulmonary, cse$Pulmonary),
  Albumin_low  = c(1 - cre$Albumin, 1 - cse$Albumin),        # albumin <= 35 g/L
  Hospital_stay= c(cre$Hospital_stay, cse$Hospital_stay)     # hospital stay > 7 days
)

suppressPackageStartupMessages(library(logistf))
fit <- logistf(CRE ~ Endo_intub + Diabetes + Cerebro + Urinary_cath + Age +
                 Gastric_tube + Pulmonary + Albumin_low + Hospital_stay,
               data = comb, firth = TRUE, pl = TRUE)

co  <- fit$coefficients[-1]       # drop the intercept
se  <- sqrt(diag(fit$var))[-1]
p   <- fit$prob[-1]
lo  <- fit$ci.lower[-1]           # profile penalized-likelihood 95% CI
up  <- fit$ci.upper[-1]
or  <- exp(co)
or_lo <- exp(lo)
or_up <- exp(up)

# ---------------- Build Table 2 data rows ----------------
lbl <- c("Endotracheal intubation", "Diabetes", "Cerebrovascular disease",
         "Urinary catheterization", "Age (per year)", "Gastric tube placement",
         "Pulmonary disease", "Albumin \u226435 g/L", "Hospital stay >7 days")
stopifnot(length(lbl) == length(co))

fmt_p <- function(p) {
  vapply(p, function(pi) {
    s <- if (pi < 0.0001) "<0.0001" else sprintf("%.4f", pi)
    if (pi < 0.05) paste0("**", s, "**") else s
  }, character(1))
}

rows <- lapply(seq_along(co), function(i) {
  c(lbl[i],
    sprintf("%.3f", co[i]),
    sprintf("%.3f", se[i]),
    fmt_p(p[i]),
    sprintf("%.2f (%.2f\u2013%.2f)", or[i], or_lo[i], or_up[i]))
})

# ---------------- Replace the Table 2 row block in Table-all.md ----------------
src <- readLines(MD_FILE, encoding = "UTF-8")
h <- grep("^## Table 2_Firth \\(revised\\)", src)
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
  Factor      = lbl,
  Coefficient = sprintf("%.3f", co),
  SE          = sprintf("%.3f", se),
  P           = fmt_p(p),
  OR          = sprintf("%.2f", or),
  OR_CI_lower = sprintf("%.2f", or_lo),
  OR_CI_upper = sprintf("%.2f", or_up),
  stringsAsFactors = FALSE
)
write.csv(csv_df, "table2_firth.csv", row.names = FALSE, fileEncoding = "UTF-8")

cat("Table 2_Firth done: filled into Table-all.md and written to table2_firth.csv\n")
cat("  Variables: ", paste(names(co), collapse=", "), "\n")
