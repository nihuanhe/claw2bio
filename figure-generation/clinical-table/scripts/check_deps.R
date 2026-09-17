# check_deps.R - pre-run dependency check for the clinical-table R pipeline.
# Run this FIRST (README Layer-2 step 1):  Rscript ../../scripts/check_deps.R
# The 9+1 pipeline scripts call only ONE package directly: logistf (Table 2,
# Firth penalized logistic regression). Online install pulls its CRAN
# dependency closure automatically; offline, the staged bundle
# (cos-staging/clinical-table/deps/r-win/) already contains the full closure.
# requireNamespace() loads imports, so this check also catches a broken
# partial install. Exit code: 0 = ready, 1 = missing/broken.
# NOTE: the offline bundle is built for R 4.5.x (Windows binaries); on other
# R versions use the online install instead.

cat("R version:", as.character(getRversion()),
    if (getRversion() < "4.5") "- NOTE: offline bundle targets R 4.5.x; use online install\n" else "- OK for the offline bundle\n")

if (requireNamespace("logistf", quietly = TRUE)) {
  cat("OK       logistf", as.character(packageVersion("logistf")),
      "- the R pipeline is ready to run.\n")
} else {
  cat("MISSING  logistf (needed by Table 2, Firth penalized logistic regression),\n")
  cat("         or one of its imported packages is missing/broken.\n\n")
  cat("Install ONLINE (recommended, works on any R version):\n")
  cat("  install.packages(\"logistf\")\n\n")
  cat("Install OFFLINE (Windows, R 4.5.x): see README 'Offline install (Windows)'.\n")
  cat("  Bundle folder (relative to the repo root): cos-staging/clinical-table/deps/r-win/\n")
  quit(status = 1)
}
