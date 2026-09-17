# [Verbatim from the CRE 67-isolate reproduction pack sec 4.7. Changes vs the reproduction pack: header comment (ASCII English) + Rscript path neutralized + table renamed to the skill-wide Table1-10 scheme (manuscript number kept alongside). Inputs are the pseudonymized frozen CSVs.]
# encoding: UTF-8
# ----------------------------------------------------------------------------
# Table 6_disease_genotype script (manuscript Table 6_disease_genotype): underlying diseases (diabetes/cerebrovascular
# disease/pulmonary disease) x carbapenemase groups
# Run: Rscript table6_disease_genotype.R
# Purpose: read CRE data -> group by Bla_Carb_acquired -> compute n (%) for each
#          underlying disease (Total column denominator = 67) -> fill the
#          Table 6_disease_genotype section of Table-all.md -> write table6_disease_genotype.csv
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

# ---------------- Clinical columns (positional naming consistent with table8_univariate.R) ----------------
cl <- d[, 4:25, drop = FALSE]
names(cl) <- c("Patient_ID","Gender","Age","Weight","Smoking","Surgery","Urinary_cath",
               "Endo_intub","Puncture_drain","Tracheotomy","Hemodialysis","Gastric_tube",
               "Diabetes","Hypertension","CAD","Cerebro","Renal_insuff","Pulmonary",
               "Antibiotic","Prealbumin","Albumin","Hospital_stay")
cl[] <- lapply(cl, function(x) suppressWarnings(as.numeric(as.character(x))))

# Each underlying disease: 1 = present
factors <- c(Diabetes = "Diabetes",
             "Cerebrovascular disease" = "Cerebro",
             "Pulmonary disease" = "Pulmonary")

# ---------------- Read S4 template row labels from Table-all.md ----------------
src <- readLines(MD_FILE, encoding = "UTF-8")
h <- grep("^## Table 6_disease_genotype \\(revised\\)", src)
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
stopifnot(identical(tpl_labels, names(factors)))

# ---------------- Compute n (%) ----------------
fmt_cell <- function(n, tot) if (n == 0) "\u2013" else sprintf("%d (%.1f)", n, 100 * n / tot)

rows <- lapply(names(factors), function(lab) {
  col <- cl[[factors[[lab]]]]
  cnt <- vapply(grp_order, function(g) sum(grp == g & col == 1), integer(1))
  c(lab,
    vapply(grp_order, function(g) fmt_cell(cnt[[g]], grp_n[[g]]), character(1)),
    fmt_cell(sum(cnt), 67))
})

# ---------------- Replace the S4 row block in Table-all.md ----------------
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
write.csv(csv_df, "table6_disease_genotype.csv", row.names = FALSE, fileEncoding = "UTF-8")

cat("Table 6_disease_genotype done: filled into Table-all.md and written to table6_disease_genotype.csv\n")
