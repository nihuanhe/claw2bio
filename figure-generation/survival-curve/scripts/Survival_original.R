# 加载必要的包
# 如果未安装，请先运行：install.packages("survival"); install.packages("survminer"); install.packages("readxl"); install.packages("dplyr")
library(survival)
library(survminer)
library(readxl)
library(dplyr)

# 1. 读取数据 (从指定路径的Sheet3)
file_path <- "D:\\Survival\\Survival-data.xlsx" # Windows路径使用双反斜杠转义
df_raw <- read_excel(file_path, sheet = "Sheet1")

# 查看原始数据结构
cat("原始数据维度 (行数, 列数):", dim(df_raw), "\n")
print(head(df_raw))
cat("原始数据列类型:\n")
print(sapply(df_raw, class))

# 2. 数据清理：去除含有缺失值 '?' 的行
# '术后x月' 列中可能包含 '?'，需要先识别并移除
# 首先将 '术后x月' 转换为字符型，然后替换 '?' 为 NA，最后转为数值型
df_clean <- df_raw %>%
  # 步骤1: 将 '术后x月' 列转换为字符型
  mutate(`术后x月` = as.character(`术后x月`)) %>%
  # 步骤2: 将 '术后x月' 列中的 '?' 转换为 NA
  mutate(`术后x月` = na_if(`术后x月`, "?")) %>%
  # 步骤3: 移除 '术后x月' 或 'IHC' 列中为 NA 的行
  filter(!is.na(`术后x月`), !is.na(IHC)) %>%
  # 步骤4: 将 '术后x月' 转换为数值型，确保后续Surv()函数能正确处理
  mutate(`术后x月` = as.numeric(`术后x月`))

# 查看清理后数据
cat("\n清理后数据维度 (行数, 列数):", dim(df_clean), "\n")
print(head(df_clean))
cat("清理后数据列类型:\n")
print(sapply(df_clean, class))
cat("清理后数据中 '术后x月' 是否仍有NA:", any(is.na(df_clean$`术后x月`)), "\n")
cat("清理后数据中 'IHC' 是否仍有NA:", any(is.na(df_clean$IHC)), "\n")
cat("清理后数据中 '存活0,死亡1' 是否仍有NA:", any(is.na(df_clean$`存活0,死亡1`)), "\n")


# 3. 确定IHC的分组阈值 (寻找能最小化p值且满足人数比例的阈值)
IHC_values <- sort(unique(df_clean$IHC)) # 获取所有唯一的IHC表达量值并排序
total_n <- nrow(df_clean)
min_p_value <- 1 # 初始化为最大可能的p值
best_threshold <- NA
best_low_n <- 0
best_high_n <- 0

cat("\n开始搜索最优分组阈值...\n")
for(threshold_candidate in IHC_values) {
  # 根据当前候选阈值进行分组
  temp_groups <- ifelse(df_clean$IHC <= threshold_candidate, "Low Expression", "High Expression")
  
  # 计算各组人数
  low_n <- sum(temp_groups == "Low Expression")
  high_n <- sum(temp_groups == "High Expression")
  
  # 检查是否满足人数比例条件 (>=30%)
  if(low_n >= total_n * 0.30 && high_n >= total_n * 0.30) {
    # 创建临时生存对象
    temp_surv_obj <- Surv(time = df_clean$`术后x月`, event = df_clean$`存活0,死亡1`)
    
    # 进行Log-rank检验
    temp_log_rank_test <- survdiff(temp_surv_obj ~ factor(temp_groups), data = df_clean)
    temp_p_value <- 1 - pchisq(temp_log_rank_test$chisq, df = length(temp_log_rank_test$n) - 1)
    
    # 检查是否是当前找到的最小p值
    if(temp_p_value < min_p_value) {
      min_p_value <- temp_p_value
      best_threshold <- threshold_candidate
      best_low_n <- low_n
      best_high_n <- high_n
    }
  }
}

if(is.na(best_threshold)) {
  stop("未找到满足人数比例条件 (>=30%) 的阈值。")
}

cat("\n[输出] 搜索完成。")
cat("\n[输出] 最优IHC表达量分界值:", best_threshold, "\n")
cat("[输出] 低表达组 (IHC <= ", best_threshold, ") 入组人数: ", best_low_n, " (", round(best_low_n/total_n*100, 2), "%)\n", sep="")
cat("[输出] 高表达组 (IHC > ", best_threshold, ") 入组人数: ", best_high_n, " (", round(best_high_n/total_n*100, 2), "%)\n", sep="")
cat("[输出] 优化后的Log-rank检验P值:", min_p_value, "\n")

# 4. 根据找到的最优阈值创建高/低表达分组
df_clean$expression_group <- ifelse(df_clean$IHC <= best_threshold, "Low Expression", "High Expression")
# 将分组变量转换为因子，确保绘图时顺序正确
df_clean$expression_group <- factor(df_clean$expression_group, levels = c("Low Expression", "High Expression"))

# 5. 创建生存对象 (Surv)
# time = '术后x月', event = '存活0,死亡1' (1 代表事件发生 - 死亡)
surv_obj <- Surv(time = df_clean$`术后x月`, event = df_clean$`存活0,死亡1`)

# 6. 进行 Kaplan-Meier 估计
km_fit <- survfit(surv_obj ~ expression_group, data = df_clean)

# 7. 输出生存分析结果摘要
cat("\nKaplan-Meier 生存分析结果摘要:\n")
print(summary(km_fit))

# 8. 进行 Log-rank 检验 (使用最优阈值分组后的最终结果)
log_rank_test_final <- survdiff(surv_obj ~ expression_group, data = df_clean)
cat("\n最终分组的Log-rank 检验结果:\n")
print(log_rank_test_final)
p_value_final <- 1 - pchisq(log_rank_test_final$chisq, df = length(log_rank_test_final$n) - 1)
cat("最终P-value (Log-rank test):", p_value_final, "\n")

# 9. 绘制生存曲线 (使用指定颜色)
# 使用 ggsurvplot 函数
p <- ggsurvplot(
  km_fit,
  data = df_clean,
  risk.table = TRUE,        # 显示风险表
  pval = TRUE,              # 显示p值 (Log-rank检验) - 这里会显示最终的p值
  conf.int = FALSE,          # 不显示置信区间
  xlab = "术后时间 (月)",   # X轴标签
  ylab = "生存概率",        # Y轴标签
  title = paste("Kaplan-Meier 生存曲线 (阈值:", round(best_threshold, 2), ")"), # 图表标题
  legend.title = "IHC 表达水平", # 图例标题
  break.time.by = 12,       # X轴刻度间隔
  risk.table.height = 0.25, # 风险表高度
  # 自定义颜色 (按因子水平顺序: Low, High)
  palette = c("#00B0F0", "#FF0000") # 低表达用蓝色，高表达用红色
)

# 打印图形
print(p$plot) # 只打印生存曲线图
print(p$risk.table) # 打印风险表
cat("\n生存分析图表已生成。\n")

# （可选）保存图表
# ggsave("C:\\Users\\A\\Music\\survival_plot_optimized.png", plot = p$plot, width = 10, height = 8, dpi = 300)
# ggsave("C:\\Users\\A\\Music\\risk_table_optimized.png", plot = p$risk.table, width = 10, height = 4, dpi = 300)



# --- 下面是画风险表 ---
# 10. 创建并显示详细的风险表
cat("\n--- 详细风险表 ---\n")
# 使用summary函数获取每个时间点的详细生存信息
summary_fit <- summary(km_fit)
# summary_fit 包含 time, n.risk, n.event, n.censor, surv, std.err, upper, lower 等信息
# 但是它不直接按组划分 n.risk, n.event, n.censor

# 为了按组显示风险表，我们可以结合原始数据和分组信息来计算
# 创建一个函数来计算特定时间点各组的风险数、事件数和删失数
calculate_group_risk_table <- function(data, fit) {
  # 获取所有时间点（包括事件发生和删失的时间点）
  all_times <- sort(unique(data$`术后x月`))
  groups <- levels(data$expression_group)
  
  # 初始化结果数据框
  risk_table_full <- data.frame(
    Time = all_times,
    stringsAsFactors = FALSE
  )
  
  # 为每个组添加列
  for(g in groups) {
    group_data <- data[data$expression_group == g, ]
    # 计算每个时间点的 n.risk, n.event, n.censor
    n_risk_vec <- sapply(all_times, function(t) {
      sum(group_data$`术后x月` >= t) # 在时间 t 时仍处于风险中的个体数
    })
    n_event_vec <- sapply(all_times, function(t) {
      sum(group_data$`术后x月` == t & group_data$`存活0,死亡1` == 1) # 在时间 t 发生事件的个体数
    })
    n_censor_vec <- sapply(all_times, function(t) {
      sum(group_data$`术后x月` == t & group_data$`存活0,死亡1` == 0) # 在时间 t 被删失的个体数
    })
    
    risk_table_full[[paste0("n.risk_", g)]] <- n_risk_vec
    risk_table_full[[paste0("n.event_", g)]] <- n_event_vec
    risk_table_full[[paste0("n.censor_", g)]] <- n_censor_vec
  }
  
  return(risk_table_full)
}

# 调用函数生成详细风险表
detailed_risk_table <- calculate_group_risk_table(df_clean, km_fit)
print(detailed_risk_table)

# 可以进一步筛选只显示有事件或删失的时间点
cat("\n--- 仅显示有事件或删失的时间点的风险表 ---\n")
events_or_censors <- detailed_risk_table[
  (detailed_risk_table$n.event_Low.Expression > 0 | detailed_risk_table$n.censor_Low.Expression > 0 |
     detailed_risk_table$n.event_High.Expression > 0 | detailed_risk_table$n.censor_High.Expression > 0),
]
print(events_or_censors)

# --- 画风险表的代码结束 ---








