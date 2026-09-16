# 案例 1 — GSE270189：干净基准（小鼠，3 组）

## 输入

真实公开数据集 [GSE270189](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE270189)：
小鼠前列腺基底细胞，3 组 × 2 重复（整数 counts，Ensembl ID）。

- `input/counts_matrix.csv` — 18,975 基因 × 6 样本
- `input/sample_metadata.csv` — Control / Mutant / Mutant_Rap

## 测什么

**回归基准**：无任何坑的标准输入。体检 stage 应报告 "Input looks clean — no repairs needed."，
结果数字变动即说明某处被改坏。

## 运行

```bash
python scripts/run_rnaseq.py \
  examples/1_example_GSE270189_clean-mouse-3groups/input/counts_matrix.csv \
  examples/1_example_GSE270189_clean-mouse-3groups/input/sample_metadata.csv \
  examples/1_example_GSE270189_clean-mouse-3groups/output \
  --control Control --organism mouse --overwrite
```

## 期望行为

1. 体检：clean，无修复。
2. 引擎：整数 + 最小组 n=2 → **DESeq2**。
3. DEG（padj < 0.05，|log2FC| > 1）：
   - Mutant vs Control: **1380 up / 1688 down**
   - Mutant_Rap vs Control: **517 up / 763 down**
   - Mutant vs Mutant_Rap: **855 up / 578 down**
4. 每 contrast 有火山图 + MA 图；`normalized_expression.csv`、`run_metadata.json`、`REPORT.md` 齐备。
