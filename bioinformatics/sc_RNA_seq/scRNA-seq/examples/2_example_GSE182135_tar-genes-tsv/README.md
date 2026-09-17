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

## 运行（2026-09-17 实测跑通）

```bash
python scripts/run_scrnaseq.py GSE182135_RAW/ output_GSE182135 \
  --metadata metadata_GSE182135.csv --exclude combined_pbmc,E9_5_pbmc,E10_5_pbmc,E11_5_pbmc,E12_5_pbmc \
  --organism mouse --reference MouseRNAseqData --export-slim --overwrite
```

- metadata（10 行；`sample` 列要写**完整样本名**，即目录名去掉 `.tar`）：
  `GSM5519136_E9_5_rep1_2018JULY18,E9.5` … `GSM5519145_E12_5_rep2_2018JUNE28,E12.5`
  （4 组：E9.5×2 / E10.5×3 / E11.5×3 / E12.5×2）
- **`--exclude` 不是可选项**：上游目录里混着 5 个派生对象
  （`combined_pbmc.rds` 383 MB / `E9_5_pbmc.rds` 91 MB / `E10_5` 119 MB / `E11_5` 108 MB / `E12_5` 65 MB），
  不排除就会被当成 **15 个样本**（同一批细胞重复计入）
- 实测：10 样本 **57,849 细胞**（19,468 基因）→ QC 后 57,652 → 去双细胞 **54,484 细胞**；
  Harmony 整合 → **21 clusters**（resolution 0.5）；耗时约 **48 min**，内存峰值约 **5.7 GB**（私有）
- QC 保留率 **98–100%**（因为 GEO 给的就是 CellRanger filtered 矩阵）→ 10 个样本**全部**触发
  "retention >95%，建议收紧 `--mt-max`" 的提示，属预期行为

## 关于外层 tar（重要）

`GSE182135_RAW.tar`（2.9 GB）里装的**不是**"tar 套 tar"，而是
`GSE182135_RAW/GSM*_*.tar/`（注意 `.tar` 是**目录名的一部分**）共 10 个三件套目录 + 5 个游离 rds。
把它直接喂给 pipeline 会**静默只用第 1 个样本**：`inspect_input._classify_file()` 在
`len(hits) > 1` 时只 `using hits[0]`（日志会打 `tar contains 10 triplet dirs; using <第一个>`）。
所以本 example 用**目录输入 + `--exclude`**，等价于把外层 tar 解开后的形态。
（已记入 `TODO.md`：建议把 tar 内多个三件套展开成多样本）

