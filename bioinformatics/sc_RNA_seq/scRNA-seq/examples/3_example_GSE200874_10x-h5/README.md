# Example 3 — GSE200874: 10X h5 multi-sample

> 踩坑档案（case file）。数据不进仓库：GEO 下载见 `../manifest.csv`。

## 症状

4 个 `.h5` 文件（`GSM6045825/6_wt_*` vs `GSM6045827/8_mut_*`），不是目录三件套。

## 诊断与处理

1. stage 00.5 按 `.h5` 扩展名识别 → stage 01 用 `Read10X_h5`（依赖 hdf5r，
   stage 00 检查）；
2. 多样本在合并前各自建对象，barcode 加样本前缀防冲突；
3. 分组走 `sample_metadata.csv`：Control=wt×2，Test=mut×2。
   **注意：metadata 的 `sample` 列必须写"完整样本名"**（即文件名去掉 `.h5`），
   例如 `GSM6045825_wt_filtered_gene_bc_matrices_h5_1`。
   ⚠️ 只写 `GSM6045825` **匹配不上**：`inspect_input.norm_sample_key()` 会把 `GSM\d+_?`
   从 metadata 名与样本名**两侧都剥掉**，于是它被剥成空字符串，4 个样本会**静默**退化成
   探索模式（只留一行 `metadata rows with no matching sample: ['']`）。
4. 上游目录若混着派生对象（本机 `GSE200874_RAW\` 里还有 `combined_pbmc.rds` /
   `ctrl_pbmc.rds` / `test_pbmc.rds`），**直接喂整个目录会被当成 7 个样本**（细胞重复计入）
   → 先只挑出 4 个 `.h5`，或用 `--exclude` 点名剔除。

## 运行（2026-09-17 实测跑通）

```bash
python scripts/run_scrnaseq.py GSE200874_RAW/ output_GSE200874 \
  --metadata metadata_GSE200874.csv --organism mouse \
  --reference MouseRNAseqData --export-slim --overwrite
```

- 本机实际用的 metadata（4 行，sample 列写全名）：
  `GSM6045825_wt_filtered_gene_bc_matrices_h5_1,Control` /
  `..._826_..._h5_2,Control` / `..._827_mut_..._h5_1,Test` / `..._828_mut_..._h5_2,Test`
- `--reference MouseRNAseqData`：本机 celldex 只缓存了 MouseRNAseq（默认 mouse 会先取
  **ImmGen**）；若 ImmGen 取不到（离线 / 沙箱拦缓存目录），stage04 会**整体失败**——
  详见 `TODO.md`「主流程 example 真实跑通」第 3 条
- 实测结果：QC 前 7189 → **QC 后 6408 细胞**；Harmony 整合 → **22 clusters**（resolution 0.5）；
  markers 303,842 行；SingleR 22/22 cluster 全部给出标签（Hepatocytes / Monocytes /
  Granulocytes / Neurons / Cardiomyocytes / Fibroblasts / Oligodendrocytes / Erythrocytes /
  Dendritic cells —— 符合胚胎期混合组织，说明这批"pbmc"命名并不代表纯 PBMC）
- QC 保留率 89.4–98.7%；两个样本 >95% 时 pipeline 会自动给出"收紧 `--mt-max`"的建议

