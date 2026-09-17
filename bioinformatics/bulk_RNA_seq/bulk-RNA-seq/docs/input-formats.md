# 输入格式坑与自动修复清单

体检 stage（00.5，`run_rnaseq.py` 内）在 01_qc 之前运行。原则：**能无损修复的自动修
并打印 [fixed]；需要判断的打印 [warn]；真正无解的才报错**。原始输入文件永不被修改；
修复后的副本写到输出目录 `cleaned_counts.csv` / `cleaned_metadata.csv`（无修复时不生成）。

## 自动修复清单（按执行顺序）

| # | 坑 | 修复动作 |
|---|---|---|
| 1 | GEO series_matrix（`!` 注释头 + `ID_REF` 表头） | 定位表头行解析，重存为普通表 |
| 2 | 混合矩阵（count + FPKM + 注释列混排） | 保留 `*_count` 列；FPKM 列分离不用；非数值注释列拆出存 `gene_annotation.csv`（可回喂 `--gene-map`） |
| 3 | 列名后缀 `_count`/`_FPKM`/`_TPM`/`.bam`/`.fastq.gz` | 剥离（剥离会造成重名则放弃并警告） |
| 4 | 转置矩阵（列数 > 行数） | 转回 基因×样本 |
| 5 | 重复基因行名（symbol 矩阵） | 按均值聚合；整数 counts 聚合后四舍五回整数（保住 DESeq2/edgeR 引擎资格） |
| 6 | NA/非数值单元格 | 删行 |
| 7 | 负值 | 归零 |
| 8 | metadata 列名 `sample_id`/`condition` 等 | 重命名为 `sample`/`group`（候选表见代码） |
| 9 | 样本名被 R 毁过（空格→点、`15`→`X15`） | 模糊匹配（忽略非字母数字 + 数字前导 X）改回 metadata 原名 |
| 10 | 矩阵/metadata 样本集不一致 | 以 metadata 为分析集：矩阵多余样本排除、metadata 多余行删除；零重叠才报错 |

## 只警告不修复

- 数字开头的样本名：管线全程 `check.names = FALSE` 保留原名，不会炸；但你自己写
  R 后处理脚本时注意 `make.names` 风险。
- 中文/空格路径：Windows 上 R 可能炸 tempdir。体检会提前警告；遇到神秘失败时
  把输入复制到纯 ASCII 路径重跑。
- 矩阵被排除的样本多于保留的样本：提示你核对 metadata 是否给错。

## 不修直接报错

- metadata 找不到任何可当 sample/group 的列；
- 矩阵与 metadata 零重叠；
- `--control` 指定的组不存在。

## series_matrix 特别注意

GEO 的 series_matrix 分两种：

- **带数据的**：解析后直接分析（通常是芯片/归一化值 → limma-trend 分支）。
- **空数据区的**（`!Sample_data_row_count "0"`，如 GSE214514）：只携带表型信息！
  counts 在 Supplementary files。此时 series_matrix 的正确用法是**读表型行构建
  metadata**（`!Sample_title`、`!Sample_characteristics_ch1` 等），counts 另找。

<a id="cel"></a>

## CEL 文件（芯片原始数据）——本 skill 明确不管

`.CEL`（Affymetrix/Clariom 等）是芯片扫描原始文件，需要 oligo/affy 包的 RMA 归一化，
是完全不同的技术栈。本 skill 不含该依赖、不做该流程。遇到 CEL：

1. 先看 GEO 上该 series 有没有已处理的 series_matrix 或补充矩阵（多数有）——有就用它；
2. 没有的话让 agent 用 `oligo::rma()` 现场写一次性脚本处理成表达矩阵，再回本 skill。
