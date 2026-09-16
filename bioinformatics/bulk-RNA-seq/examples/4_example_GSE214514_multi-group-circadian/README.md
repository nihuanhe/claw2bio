# 案例 4 — GSE214514：多组多样本（Bmal1 KO × 年龄，25 样本）

## 输入

真实公开数据集 [GSE214514](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE214514)：
小鼠小胶质细胞，Bmal1 KO/WT × Young/Aged，4 组共 25 样本（节律/衰老课题常见结构）。

- `input/GSE214514_counts_all.tsv.gz` — 20,362 基因 × 25 样本整数 counts（tsv + gzip 双格式）
- `input/sample_metadata.csv` — `sample,group`（KO_Young / WT_Young / KO_Aged / WT_Aged）；
  从 series_matrix 的 `!Sample_title` 表型行提取构建
- `input/GSE214514_series_matrix.txt` — 该数据集的 series_matrix，**仅供参考**：
  它的数据区是空的（`!Sample_data_row_count "0"`），GEO 上这类文件只携带表型信息，
  counts 在补充文件里——所以本例直接分析 counts 文件

## 测什么

1. 4 组 ≤ `--pairwise-max` 默认 4 → **自动全配对 6 个 contrasts**；
2. tsv.gz 输入自动识别；
3. 组数较多时 DESeq2（min n = 6 < 8）分支；
4. 衰老 vs 基因型效应量级差异巨大（真实生物学：aging 主导），结果 sanity check 的好素材。

## 运行

```bash
python scripts/run_rnaseq.py \
  "examples/4_example_GSE214514_multi-group-circadian/input/GSE214514_counts_all.tsv.gz" \
  "examples/4_example_GSE214514_multi-group-circadian/input/sample_metadata.csv" \
  "examples/4_example_GSE214514_multi-group-circadian/output" \
  --control WT_Young --organism mouse --overwrite
```

## 期望行为

1. Contrasts 行打印 6 个全配对组合。
2. 年龄对比（KO_Aged/WT_Aged vs Young 系）DEG 在 **2500–4400** 量级；
   基因型对比（KO vs WT 同龄）仅 **4–21** 个——衰老效应远大于 Bmal1 基因型效应。
3. 只想要部分比较时：`--contrasts "KO_Young vs WT_Young, KO_Aged vs WT_Aged"`。

## 扩展玩法

- `--pairwise-max 2` 可关掉全配对（只做各组 vs 对照）。
- 年龄当连续变量/交互作用属于多因子设计，见 `../../docs/decision-tree.md`。
