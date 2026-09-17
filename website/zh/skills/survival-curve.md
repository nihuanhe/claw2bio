# 生存曲线（KM + Cox）

> 一句话：随访表进，Kaplan-Meier 生存曲线 + 风险表 + 单因素 Cox 森林图出——自动 maxstat 最优截点，600 dpi 发表级。

::: info 获取本技能 · Get this skill
**方式 A —— 一键引导 prompt（推荐）**。复制下面这段，粘贴到你的 AI agent IDE：

```
请帮我安装 Claw2Bio 技能库中的 "survival-curve" 技能：
1. 从 GitHub 仓库 https://github.com/nihuanhe/claw2bio 只拉取 figure-generation/survival-curve
   这一个文件夹（用 sparse checkout，不要克隆整库）。
2. 阅读其中的 SKILL.md 并注册该技能。
3. 运行 examples/ 里的示例验证环境，把输出的图给我看。
```

**方式 B —— 独立 zip 包**（约 0.3 MB，本站下载）：<https://claw2bio.site/downloads/survival-curve.zip>

**方式 C —— 全量示例数据**：已包含在方式 B 包内（同一个压缩包）。
:::

## 它能做什么

输入一张随访表（至少 3 列：事件 0/1、随访时间、连续 marker），五步流水线：清洗 → `surv_cutpoint` 找最优截点（maxstat 法，`minprop = 0.30`，每组 ≥30% 样本）→ KM 曲线 + log-rank + 风险表 → 单因素 Cox HR + 森林图 → 三张统计 CSV。

内置示例（52 例公开教学数据，9 个事件）锚点：截点 39.49，低组 36 人 / 高组 16 人，log-rank p = 0.069，Cox HR（High vs Low）= 3.47（95%CI 0.85–14.11，p = 0.082），marker 每单位 HR = 1.0422。

![KM 生存曲线](/skills/survival-curve/KM_curve.png)

KM 曲线（蓝 = Low 组、红 = High 组）+ log-rank p + Number-at-risk 风险表，600 dpi PNG + PDF。

![Cox 森林图](/skills/survival-curve/cox_forest.png)

单因素 Cox 森林图：分组 HR（High vs Low）与连续 marker 每单位 HR，附 95%CI 和 p 值。

**方法学警示（必读）**：数据驱动截点（data-driven cutoff）会系统性高估组间差异（optimism bias）。论文中必须声明截点的确定方法，最好有独立队列验证；事件数过少（<10）时 Cox 结果不可靠，应只做 KM 或在报告中注明。

## 快速上手（30 秒）

**这是模板脚本，不是 CLI**：换数据只改 `scripts/survival_curve_template.R` 顶部的 CONFIG 块（6 个变量：`INPUT_FILE` / `INPUT_SHEET` / `COL_EVENT` / `COL_TIME` / `COL_MARKER` / 可选 `MIN_PROP`、`PALETTE`、`TIME_UNIT`），然后：

```bash
cd figure-generation/survival-curve
Rscript scripts/survival_curve_template.R
```

Windows 直接跑，无 WSL 依赖；需要 R ≥ 4.2（实测 4.5.2）及 `survival` / `survminer`（≥0.5）/ `readxl` / `dplyr`。

跑完对照 ANCHOR 行自查：截点应在 marker 值域内、两组人数均 ≥30%。

## 输入格式

- xlsx 或 csv，至少 3 列：事件（0/1）、随访时间、连续 marker；其余列（如患者 ID）自动忽略。
- `'?'` 和空值自动转 NA；三列强制数值化。

## 输出文件

| 文件 | 内容 |
|---|---|
| KM 曲线 600 dpi PNG + cairo PDF | 曲线 + log-rank p + 风险表 |
| Cox 森林图 600 dpi PNG + PDF | 分组 HR 与连续 marker HR |
| `group_summary.csv` / `risk_table.csv` / `stats_summary.csv` | 分组统计 / 风险人数 / 检验摘要 |

## 配置

CONFIG 块 6 个核心变量：输入文件与 sheet、三列列名映射、（可选）`MIN_PROP`（默认 0.30）、配色、X 轴时间单位。

## 常见问题

- **`未找到满足条件的阈值` / 某组人数为 0** → survminer ≥0.5 的 `surv_categorize` 返回字符列而非因子；模板已显式转 factor，勿回退。
- **`ggforest ... 选择了未定义的列`** → 建模列必须有稳定列名（模板用 `expression_group`），勿在公式里用 `df[[col]]` 内联取列。
- **图中中文乱码** → cairo_pdf 已嵌字体；若仍乱码改 `family="sans"` 或用英文标签。
- **截点方法被审稿人质疑** → 模板用 maxstat（`surv_cutpoint`）而非遍历最小 p 值；但仍需在方法学部分声明，并尽量做外部验证（见上方警示）。
- **为什么必须用技能自带脚本，不能让 AI 现写？**
  `scripts/` 里的是经过验证的路径：它们在示例数据上跑过，边界情况有文档记录。AI 现场生成的代码是
  "结果悄悄出错"的最常见来源。遇到没覆盖的情况，先改命令行参数；不够就复制脚本到临时目录做最小改动
  并说明改了什么；只有完全没有对应脚本时才允许新写，且新写后要回沉淀到 `scripts/`。

## 相关链接

- [GitHub 源码与 SKILL.md](https://github.com/nihuanhe/claw2bio/tree/main/figure-generation/survival-curve)
- 相关技能：[临床统计表](/zh/skills/clinical-table) · [分组柱状图](/zh/skills/barplot)
