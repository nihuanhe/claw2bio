---
name: clinical-table
description: "发表级临床统计三线表，一套管线复现论文全套表格：两队列基线（χ²/Fisher + t）、Firth 惩罚逻辑回归、基因型交叉表、单因素分析、相关性、Cox、OR。已用真实 CRE(67)/CSE(72) 队列研究的全部 10 张表格（Table 1–10 = 手稿 Table 1/2 + 补充材料 S1–S8）验证，逐格对账。触发词：临床基线表、Table 1、三线表、baseline table、Firth、队列对比、Cox、OR。"
---

# clinical-table — 临床统计三线表（通用引擎 + 手稿级全表 R 管线）

## 中文摘要

患者级 CSV 进，发表级 Markdown 三线表出。两个层次：

1. **通用引擎（Python，`scripts/clinical_table.py`）**——两队列（任意两组）
   基线特征对比：分类变量 n(%) + Pearson χ²（无连续性校正，期望 <5 自动
   Fisher），连续变量 mean±SD + Student t；另支持 OR 汇总、相关性矩阵、Cox。
2. **手稿级全表套件（R 管线，`scripts/pipeline/`）**——9 个 R 脚本 + 1 个
   Python 脚本按序运行，从两份假名化患者 CSV 复现一篇论文的**全套 10 张表**
   （Table 1–10）：基线、Firth 惩罚逻辑回归（logistf）、耐药基因/序列型/
   质粒复制子 × 碳青霉烯酶组交叉表、单因素分析、菌株测序质量表。每个脚本
   读 CSV → 计算 → 回填 `Table-all.md` 骨架对应区块 → 出独立 CSV。
   表号映射：Table 1/2 = 手稿正文 Table 1/2；Table 3–10 = 手稿补充材料
   S1–S8（Table 9 = S7，独立 CSV 输出）。

   | 表号 | 小标题 | 手稿表号 | 脚本 |
   |---|---|---|---|
   | Table 1 | baseline | Table 1 | table1_baseline.R |
   | Table 2 | firth | Table 2 | table2_firth.R |
   | Table 3 | esbl_genes | S1 | table3_esbl_genes.R |
   | Table 4 | sequence_types | S2 | table4_sequence_types.R |
   | Table 5 | sul_genes | S3 | table5_sul_genes.R |
   | Table 6 | disease_genotype | S4 | table6_disease_genotype.R |
   | Table 7 | procedures_genotype | S5 | table7_procedures_genotype.R |
   | Table 8 | univariate | S6 | table8_univariate.R |
   | Table 9 | sequencing_quality | S7 | make_table9_sequencing_quality.py |
   | Table 10 | plasmid_replicons | S8 | table10_plasmid_replicons.R |

## When to use

- "复现/生成论文全套表格（Table 1–10）、基线特征表、Firth 回归"
- "分类变量卡方、连续变量 t 检验，三线表格式"
- "OR (95% CI) / 相关性矩阵 / Cox 回归表 / 菌株测序质量表"
- Input: 患者级 CSV（一行一个患者；通用引擎要一个两水平分组列，R 管线按
  `examples/input/pipeline/` 的列结构准备）

## Not for

- KM 生存曲线图 → survival-curve skill

## Environment

- 通用引擎：Python 3.10+，`pandas numpy scipy statsmodels`。
- R 管线：R 4.x + `logistf`（`install.packages("logistf")`）；Table 9 用
  Python stdlib（`make_table9_sequencing_quality.py`）。脚本注释刻意保持 ASCII/英文——UTF-8 中文注释会让 Windows Rscript
  （GBK 解析）段错误崩掉；如需加注释，存 UTF-8 无 BOM 或 `Rscript --encoding=utf-8`。

## Adapt to user's data

1. 通用引擎：数据整理成一行一患者（分组列 `cohort` + 0/1 分类列 + 连续列），
   变量清单在 `clinical_table.py` 顶部 `DEFAULT_CONFIG`（或 `--config`）。
2. R 管线：按 `examples/input/pipeline/` 的两份 CSV 列结构准备自己的双队列
   数据，替换同名文件，按序运行 9+1 个脚本；骨架与运行说明见该目录 README。
3. 用 agent 时直接说："把 DEFAULT_CONFIG 换成我数据的列" 或
   "照 pipeline 的列结构整理我的两个 CSV 并跑全套表"。

## Smoke test (已实测 2026-09-17，Table 1–10 改名后全套重跑通过)

```bash
cd figure-generation/clinical-table
# 1) 通用引擎
python scripts/clinical_table.py examples/input/clinical_cohorts.csv examples/output/clinical_tables.md
# 2) R 管线（examples/input/pipeline/ 内按 README 运行 9+1 个脚本）
```

Expected anchors（R 管线全套，与复现包 §9.2 逐格一致；通用引擎与其 Table 1 一致）：

```
Table 1: Sex chi2=1.116 p=0.2907 | Age t=3.043 p=0.0028 | 69.16±10.43 vs 63.18±12.56
Table 2: Endotracheal intubation coef 2.578, OR 13.17 (2.08-158.92)
Table 3/5 column sums 13/18/22/1/13 (=67) | Table 4 46 rows | Table 8 30 rows | Table 9 67 rows | Table 10 47 rows
```

## Provenance & validation

- 示例数据 = 一项 CRE/CSE 队列研究（投稿返修中）的**假名化**冻结数据集：
  Patient_ID/Sample/Barcode 均为内部数字假名（无姓名/出生日期/住院号），
  Assembly 为 GSA 公开存款号——与该研究已发表补充材料披露口径一致。
- R 管线脚本逐字取自作者复现包（仅头注释中性化）；全部数字与作者独立复核
  脚本逐格对账，证据见 `examples/output/pipeline/REPORT.md`。
- 通用引擎示例 `examples/input/clinical_cohorts.csv`（139 行 × 22 列）由
  `scripts/prepare_cohorts_example.py` 从同一数据派生（仅临床列）。

## Troubleshooting

| 症状 | 原因与处理 |
|---|---|
| p 值与 SPSS 对不上 | χ² 不做 Yates 连续性校正（发表 Table 1 惯例）；SPSS 的 "Continuity Correction" 行才是校正值 |
| R 脚本打开即崩（Windows） | 注释含 UTF-8 中文被 GBK 解析；用仓库内英文注释版，或 `--encoding=utf-8` |
| logistf 缺失 | `install.packages("logistf")`（Table 2 需要） |
| 0.0/1.0 而不是 Yes/No | 输入 CSV 该列含空值被读成浮点；用 dtype=str 读取或在 level_maps 加 "0.0"/"1.0" 键 |
| 连续变量没进基线表 | 加进 `baseline_continuous_vars`（`continuous_vars` 只用于相关性矩阵） |
| Cox 表没生成 | 只有同时存在 `survival_time`/`survival_event` 列才会生成 |
| Table-all.md 被改坏 | 从 examples/input/pipeline/ 恢复骨架；脚本按行协议回填，骨架禁手改 |
