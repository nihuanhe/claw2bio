# Plan：clinical-table 表格命名换代 Table1~10 + 英文小写下划线副标题

日期：2026-09-17 ｜ 状态：待用户核准 ｜ 前置：v2 全表管线已完成并验收

## 用户决策（已确认）

1. **全链路改名**：骨架标题、R 脚本 grep 锚点与输出 CSV 名、脚本文件名、PNG、网站、文档全部改为 Table1~10（用户明确豁免"最小 diff 铁律"）；
2. **按原顺序顺延**：Table1=原Table1、Table2=原Table2、Table3=原S1 … Table10=原S8；
3. **英文小写下划线**：文件名 `table1_baseline.png` 式；网站标签展示形 `Table 1 · Baseline`；
4. **保留手稿映射**：文档/图注双编号并列（如 "Table 3 · ESBL genes（= manuscript Supplemental Table S1）"）。

## 命名映射总表（唯一权威，所有改动以此为准）

| 新名 | 副标题 | 原名 | 脚本新名（原） | CSV/PNG 新名 |
|---|---|---|---|---|
| Table 1 | baseline | Table 1 | table1_baseline.R（table1.R） | table1_baseline |
| Table 2 | firth | Table 2 | table2_firth.R（table2.R） | table2_firth |
| Table 3 | esbl_genes | S1 | table3_esbl_genes.R（tableS1.R） | table3_esbl_genes |
| Table 4 | sequence_types | S2 | table4_sequence_types.R（tableS2.R） | table4_sequence_types |
| Table 5 | sul_genes | S3 | table5_sul_genes.R（tableS3.R） | table5_sul_genes |
| Table 6 | disease_genotype | S4 | table6_disease_genotype.R（tableS4.R） | table6_disease_genotype |
| Table 7 | procedures_genotype | S5 | table7_procedures_genotype.R（tableS5.R） | table7_procedures_genotype |
| Table 8 | univariate | S6 | table8_univariate.R（tableS6.R） | table8_univariate |
| Table 9 | sequencing_quality | S7 | make_table9_sequencing_quality.py（make_table_s7.py） | table9_sequencing_quality |
| Table 10 | plasmid_replicons | S8 | table10_plasmid_replicons.R（tableS8.R） | table10_plasmid_replicons |

- 骨架标题格式：`## Table 1_Baseline (revised). Baseline characteristics …`（保留原 `(revised)`/`(new)` 溯源标记；原 S8 的 `(new)` 不动）。R 脚本 grep 锚点改为如 `^## Table 3_esbl_genes \(revised\)`。
- **不变**：`Table-all.md` 容器文件名、custom.css 选择器 id（#ct-t1..t10 数字本就 1~10 顺延）、CSV 列名、统计逻辑。

## 执行步骤

1. **脚本改名+内部修补**（scripts/pipeline/，10 个文件）：按映射表重命名；每脚本只改 ①区块 grep 锚点正则 ②输出 CSV 文件名 ③cat() 提示文字 ④头注释改动清单（如实写明 "header + section anchor + output filename renamed to skill-wide Table1-10 scheme"）。统计代码一行不动。
2. **骨架标题更新**（examples/input/pipeline/Table-all.md，10 个标题行）→ **scratch 重跑全管线**：脚本 grep 已变，必须重跑验证（stopifnot 全过 = 锚点不回归）；填数版 Table-all_filled.md + 新名 CSV 重进 examples/output/pipeline/，旧名 CSV 删除；REPORT.md 锚点表重对账。
3. **渲染**（website/scripts/render_table_png.py）：TABLES 列表改新标题正则+新 PNG 文件名，重渲 10 张；删 public/skills/clinical-table/ 旧 10 张。
4. **网站**：zh/en 教程页（标签 `Table N · Subtitle`、img src、图注加 "= manuscript Table Sx" 映射）、zh/en index.md 首页卡图路径、zh/en skills/index.md 如有编号表述同步。
5. **文档**：SKILL.md（description/摘要/锚点/管线描述改 Table1~10+映射表）、skill README.md（布局/快速上手命令用新脚本名）、examples/input/pipeline/README.md（运行命令）、examples/output/pipeline/REPORT.md（表名+映射说明）、AGENTS.md 行、总 plan.md #49。
6. **验证**：npm run build 无死链；OpenCLI 截图目检 zh 选择器（替换 examples/output/pipeline/website_check.png）；全仓 grep 旧名（tableS1、Supplemental Table S1、supplemental_table_S7 等）零残留；交付总结。

## 风险与预案

- 脚本 grep 改错 → stopifnot 区块定位失败立即报错，重跑即暴露；逐脚本跑完再进下一步。
- 网站旧 PNG 残留引用 → 步骤 6 全仓 grep 文件名零命中收口。
- 手稿映射断裂 → 映射总表写入 SKILL.md/README/REPORT 三处。
