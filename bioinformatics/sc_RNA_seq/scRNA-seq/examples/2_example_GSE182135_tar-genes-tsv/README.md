# Example 2 — GSE182135: tar bundles + legacy genes.tsv + 4 groups × 10 samples

> 踩坑档案（case file）。数据不进仓库：GEO 下载见 `../manifest.csv`。

## 症状

- GEO supplementary 是一堆 `GSM*_E9_5_rep1_2018JULY18.tar`，每个 tar 里
  的三件套（`barcodes.tsv / genes.tsv / matrix.mtx`，**未压缩**）埋在
  `<GSM...>/outs/filtered_feature_bc_matrix/mm10/` 这类嵌套目录下；
- 旧版 `genes.tsv` 只有两列（Ensembl ID + symbol）；
- 4 个发育时间点组共 10 个样本，全量合并时 16GB 内存吃紧。

## 诊断与处理

1. stage 00.5 自动解包 tar 到 `.staging/`，递归定位含三件套的目录 `[fixed]`；
2. `genes.tsv` 自动按两列旧版处理（`gene.column=2`）；
3. 行名用 symbol（第 2 列），重复 symbol 自动 `make.unique`；
4. 分组用 `sample_metadata.csv`（4 组），不要学旧代码硬编码 `group_info`；
5. 内存：每个 stage 有 checkpoint；爆了 `--resume` 续跑；或先
   `--downsample 5000` 探索。merge/整合是内存最高峰。

## 运行

```bash
python scripts/run_scrnaseq.py GSE182135_RAW/ output_GSE182135 \
  --metadata metadata_GSE182135.csv --organism mouse --overwrite
```

注意：该数据为小鼠 E9.5–E12.5 胚胎 → `--organism mouse`
（SingleR 用 ImmGen + MouseRNAseq 参考）。
