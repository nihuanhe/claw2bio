# 案例 3 — GSE167882：paired 设计 + 非整数矩阵 + 毁名样本名

## 输入

真实公开数据集 [GSE167882](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE167882)：
人慢性自发性荨麻疹（CSU）纵向采样——同一批 Subject 在 pre-treatment / mid-treatment
多次采样，另有 health 对照（典型**重复测量/paired 设计**）。

- `input/GSE167882_ensembl_expression_matrix.csv` — 15,504 基因（Ensembl ID）× 21 样本；
  值是**非整数**（log 尺度归一化值）；列名已被 R 毁过（`Subject.1...CSU.v3`，
  原名 `Subject 1 - CSU v3` 中的空格/短横被替换成点）
- `input/GSE167882_gene_symbol_expression_matrix.csv` — 同一数据的 symbol 版本（备选输入）
- `input/sample_metadata.csv` — `sample,group,subject` 三列；`subject` 供 `--paired-by` 使用

## 测什么

1. **paired 引擎规则**：声明 `--paired-by subject` → 强制 limma 系 +
   `duplicateCorrelation`（本例 consensus ≈ 0.73，受试者效应显著）；
2. 非整数输入 → limma-trend 分支；
3. 毁名样本列 → 体检 stage 模糊匹配回 metadata 原名；
4. 组名带短横（`pre-treatment` 等）→ contrast 矩阵按数值构造，不再炸 `makeContrasts`。

## 运行

```bash
python scripts/run_rnaseq.py \
  "examples/3_example_GSE167882_paired-symbol-logcpm-human/input/GSE167882_ensembl_expression_matrix.csv" \
  "examples/3_example_GSE167882_paired-symbol-logcpm-human/input/sample_metadata.csv" \
  "examples/3_example_GSE167882_paired-symbol-logcpm-human/output" \
  --control health --organism human --paired-by subject --overwrite
```

## 期望行为

1. 引擎框：`ENGINE FORCED: limma (paired/repeated-measures design ...)`。
2. `duplicateCorrelation consensus correlation: 0.731`。
3. 3 个 contrasts（mid-treatment/pre-treatment vs health 及相互比较）全部出表出图；
   pre-treatment vs health: **12 up / 6 down**。

## 备选玩法

换 symbol 矩阵作输入可顺带测重复 symbol 聚合（体检 stage 按均值合并并保留整数性）。
