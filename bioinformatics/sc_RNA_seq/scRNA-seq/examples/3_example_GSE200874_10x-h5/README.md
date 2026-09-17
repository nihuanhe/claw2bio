# Example 3 — GSE200874: 10X h5 multi-sample

> 踩坑档案（case file）。数据不进仓库：GEO 下载见 `../manifest.csv`。

## 症状

4 个 `.h5` 文件（`GSM6045825/6_wt_*` vs `GSM6045827/8_mut_*`），不是目录三件套。

## 诊断与处理

1. stage 00.5 按 `.h5` 扩展名识别 → stage 01 用 `Read10X_h5`（依赖 hdf5r，
   stage 00 检查）；
2. 多样本在合并前各自建对象，barcode 加样本前缀防冲突；
3. 分组走 `sample_metadata.csv`：Control=wt×2，Test=mut×2（模糊匹配容忍
   文件名里的 `_filtered_gene_bc_matrices_h5_1` 之类长后缀——metadata 里
   写 GSM 号即可匹配）。

## 运行

```bash
python scripts/run_scrnaseq.py GSE200874_RAW/ output_GSE200874 \
  --metadata metadata_GSE200874.csv --organism mouse --overwrite
```
