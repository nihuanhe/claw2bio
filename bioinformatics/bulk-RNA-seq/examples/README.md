# Examples — bulk-RNA-seq 编号测例

每个子文件夹是一个真实（或合成）数据集，覆盖一类特殊情况；同时充当回归测试。
Each numbered case covers one class of special situation and doubles as a regression test.

| 编号 | 数据集 | 覆盖的坑 / what it exercises |
|---|---|---|
| `1_example_GSE270189_clean-mouse-3groups` | GSE270189 小鼠前列腺基底细胞，3 组 × 2 重复 | 干净基准：整数 counts、Ensembl ID、DESeq2 分支（回归基准） |
| `2_example_GSE255223_mixed-count-FPKM-annotation` | GSE255223 人 TLE 脑组织 | 混合矩阵（count/FPKM/注释列混排）、`_count` 后缀、`15`→`X15` 的 make.names 毁名、矩阵比 metadata 多 3 个样本 |
| `3_example_GSE167882_paired-symbol-logcpm-human` | GSE167882 人 CSU 纵向采样 | paired 设计（`--paired-by subject`，duplicateCorrelation）、组名带短横、样本名被 R 毁过（模糊匹配修复）、非整数 → limma-trend |
| `4_example_GSE214514_multi-group-circadian` | GSE214514 小鼠小胶质细胞 Bmal1 KO × 年龄 | 4 组 25 样本全配对 6 contrasts、tsv.gz 输入、metadata 从 series_matrix 表型行构建 |
| `5_example_synthetic_dirty-and-series-matrix` | 合成小数据 ×2 | (a) 脏数据综合：后缀+FPKM 列+注释列+重复 symbol+负值+非标准列名+数字开头样本名；(b) series_matrix `!` 头解析 |

运行任何一例（以案例 2 为例）：

```bash
python scripts/run_rnaseq.py \
  "examples/2_example_GSE255223_mixed-count-FPKM-annotation/input/GSE255223_gene_expression_anno.xls.gz" \
  "examples/2_example_GSE255223_mixed-count-FPKM-annotation/input/sample_metadata.csv" \
  "examples/2_example_GSE255223_mixed-count-FPKM-annotation/output" \
  --control TLE-nonHS --organism human --overwrite
```

每例的 README 写明"测哪个坑、期望看到什么警告/行为"。决策树文档见 `../docs/decision-tree.md`。
