# =====================================================================
# survival_curve_template.R — Kaplan-Meier survival curve (+ univariate Cox)
# from a clinical follow-up table with a biomarker column.
#
# [改自"小云科研"教程脚本 Survival.R（公开教学示例），改动清单：
#   ① min-p 遍历搜索截点 → survminer::surv_cutpoint(minprop=0.30)
#     （min-p 有 p-hacking 争议；surv_cutpoint 用 maxstat 标准化方法，
#      minprop=0.30 保持教程"每组≥30%"约束）；
#   ② 硬编码 D:\ 路径/中文列名 → 下方 CONFIG 块集中配置；
#   ③ 只 print 不存盘 → 600dpi PNG + cairo PDF 直接写入 OUT_DIR；
#   ④ 新增单因素 Cox（分组 HR + ggforest 森林图 + 连续 marker HR）；
#   ⑤ 新增 stopifnot/ANCHOR 锚点行（冒烟测试可机器复核）。
#  原始脚本原样保留在 scripts/Survival_original.R 供对照。]
#
# Input : xlsx/csv，至少 3 列：事件(0/1)、随访时间(月)、marker 连续值。
#         其余列（如"患者名字"）自动忽略。
# Output: KM 曲线(含风险表) PNG+PDF、Cox 森林图 PNG+PDF、
#         分组表/风险表/统计结果 CSV。
#
# Usage : 从 skill 根目录运行（路径均为相对路径）：
#   cd figure-generation/survival-curve
#   Rscript scripts/survival_curve_template.R
# =====================================================================

suppressPackageStartupMessages({
  library(survival)
  library(survminer)
  library(readxl)
  library(dplyr)
})

# ================= CONFIG（换数据只改这里）=================
INPUT_FILE  <- "examples/input/Survival-data.csv"   # 优先 .csv（AI 友好）；也支持 .xlsx
INPUT_SHEET <- "Sheet1"                              # 仅 xlsx 有效
OUT_DIR     <- "examples/output"
COL_EVENT   <- "存活0,死亡1"   # 0=删失(存活) 1=事件(死亡)
COL_TIME    <- "术后x月"       # 随访时间（月）
COL_MARKER  <- "IHC"           # 连续 marker（如 IHC 病理评分）
MIN_PROP    <- 0.30            # 每组样本量下限占比（教程设定）
TIME_UNIT   <- "术后时间 (月)"
PALETTE     <- c("#00B0F0", "#FF0000")  # Low=蓝, High=红（教程配色）
# ===========================================================

dir.create(OUT_DIR, showWarnings = FALSE, recursive = TRUE)

## ---- 1. read -------------------------------------------------------------
df_raw <- if (grepl("\\.csv$", INPUT_FILE, ignore.case = TRUE)) {
  read.csv(INPUT_FILE, check.names = FALSE, fileEncoding = "UTF-8")
} else {
  as.data.frame(read_excel(INPUT_FILE, sheet = INPUT_SHEET))
}
cat("ANCHOR: input rows =", nrow(df_raw), "\n")
stopifnot(all(c(COL_EVENT, COL_TIME, COL_MARKER) %in% colnames(df_raw)))

## ---- 2. clean ('?' -> NA, numeric coercion) ------------------------------
df <- df_raw %>%
  mutate(across(all_of(c(COL_EVENT, COL_TIME, COL_MARKER)), as.character)) %>%
  mutate(across(all_of(c(COL_EVENT, COL_TIME, COL_MARKER)),
                ~ na_if(trimws(.x), "?"))) %>%
  filter(!is.na(.data[[COL_EVENT]]), !is.na(.data[[COL_TIME]]),
         !is.na(.data[[COL_MARKER]])) %>%
  mutate(across(all_of(c(COL_EVENT, COL_TIME, COL_MARKER)), as.numeric))
cat("ANCHOR: clean rows =", nrow(df),
    "| events =", sum(df[[COL_EVENT]] == 1), "\n")
stopifnot(nrow(df) >= 10, all(df[[COL_EVENT]] %in% c(0, 1)),
          all(df[[COL_TIME]] >= 0))

## ---- 3. optimal cutpoint (surv_cutpoint, maxstat; min group >= MIN_PROP) --
cut <- surv_cutpoint(df, time = COL_TIME, event = COL_EVENT,
                     variables = COL_MARKER, minprop = MIN_PROP)
cutpoint <- as.numeric(cut$cutpoint["cutpoint"])
cat("ANCHOR: cutpoint =", cutpoint, "\n")

df_cat <- surv_categorize(cut)                 # adds column <COL_MARKER> ("low"/"high")
grp_col <- COL_MARKER
# NOTE: survminer >= 0.5 returns a CHARACTER column, not a factor —
# `levels(x) <- ...` would silently no-op. Convert explicitly.
df_cat[[grp_col]] <- factor(df_cat[[grp_col]],
                            levels = c("low", "high"),
                            labels = c("Low Expression", "High Expression"))
# analysis column with a STABLE name — ggforest/survfit look variables up in
# `data` by name, so inline df_cat[[grp_col]] in formulas breaks ggforest
df_cat$expression_group <- df_cat[[grp_col]]
n_low  <- sum(df_cat[[grp_col]] == "Low Expression")
n_high <- sum(df_cat[[grp_col]] == "High Expression")
cat("ANCHOR: n_low =", n_low, "| n_high =", n_high, "\n")
stopifnot(n_low >= nrow(df) * MIN_PROP - 1, n_high >= nrow(df) * MIN_PROP - 1)

## ---- 4. Kaplan-Meier + log-rank ------------------------------------------
surv_obj <- Surv(time = df_cat[[COL_TIME]], event = df_cat[[COL_EVENT]])
km_fit <- survfit(surv_obj ~ expression_group, data = df_cat)
lr <- survdiff(surv_obj ~ expression_group, data = df_cat)
p_lr <- 1 - pchisq(lr$chisq, df = length(lr$n) - 1)
cat("ANCHOR: logrank p =", signif(p_lr, 4), "\n")

## ---- 5. univariate Cox (grouped + continuous marker) ----------------------
cox_grp <- coxph(surv_obj ~ expression_group, data = df_cat)
s_cox <- summary(cox_grp)
hr <- round(s_cox$coefficients[1, "exp(coef)"], 3)
ci <- round(s_cox$conf.int[1, c("lower .95", "upper .95")], 3)
p_cox <- signif(s_cox$coefficients[1, "Pr(>|z|)"], 4)
cat("ANCHOR: Cox HR (High vs Low) =", hr,
    "| 95%CI =", ci[1], "-", ci[2], "| p =", p_cox, "\n")

cox_cont <- coxph(Surv(df[[COL_TIME]], df[[COL_EVENT]]) ~ df[[COL_MARKER]])
hr_cont <- round(summary(cox_cont)$coefficients[1, "exp(coef)"], 4)
cat("ANCHOR: Cox HR (marker per unit) =", hr_cont, "\n")

## ---- 6. KM figure (600 dpi PNG + cairo PDF) -------------------------------
km_plot <- ggsurvplot(
  km_fit, data = df_cat,
  risk.table = TRUE, pval = TRUE, conf.int = FALSE,
  xlab = TIME_UNIT, ylab = "生存概率 Survival probability",
  title = paste0("Kaplan-Meier (cutoff: ", round(cutpoint, 2), ")"),
  legend.title = COL_MARKER, legend.labs = c("Low Expression", "High Expression"),
  break.time.by = 12, risk.table.height = 0.25, palette = PALETTE)

png(file.path(OUT_DIR, "KM_curve.png"), width = 8, height = 8,
    units = "in", res = 600)
print(km_plot); dev.off()
cairo_pdf(file.path(OUT_DIR, "KM_curve.pdf"), width = 8, height = 8)
print(km_plot); dev.off()

## ---- 7. Cox forest plot ----------------------------------------------------
forest <- ggforest(cox_grp, data = df_cat)
ggsave(file.path(OUT_DIR, "cox_forest.png"), forest,
       width = 7, height = 3, dpi = 600)
ggsave(file.path(OUT_DIR, "cox_forest.pdf"), forest,
       width = 7, height = 3, device = cairo_pdf)

## ---- 8. tables to CSV -------------------------------------------------------
write.csv(data.frame(group = c("Low Expression", "High Expression"),
                     n = c(n_low, n_high),
                     events = c(sum(df_cat[[COL_EVENT]][df_cat[[grp_col]] == "Low Expression"] == 1),
                                sum(df_cat[[COL_EVENT]][df_cat[[grp_col]] == "High Expression"] == 1))),
          file.path(OUT_DIR, "group_summary.csv"), row.names = FALSE)

risk_tbl <- as.data.frame(summary(km_fit, times = sort(unique(df_cat[[COL_TIME]])))[c(
  "strata", "time", "n.risk", "n.event", "n.censor", "surv")])
write.csv(risk_tbl, file.path(OUT_DIR, "risk_table.csv"), row.names = FALSE)

write.csv(data.frame(
  metric = c("cutpoint", "logrank_p", "cox_HR_high_vs_low", "cox_CI_low",
             "cox_CI_high", "cox_p", "cox_HR_marker_per_unit"),
  value  = c(cutpoint, p_lr, hr, ci[1], ci[2], p_cox, hr_cont)),
  file.path(OUT_DIR, "stats_summary.csv"), row.names = FALSE)

cat("DONE: outputs written to", normalizePath(OUT_DIR), "\n")
