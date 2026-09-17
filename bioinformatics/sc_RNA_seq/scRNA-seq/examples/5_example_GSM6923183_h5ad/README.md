# Example 5 — GSM6923183: h5ad (Scanpy) input

> 踩坑档案（case file）。数据不进仓库：GEO 下载见 `../manifest.csv`。

## 症状

GEO 只给 `GSM6923183_MC_scRNA.h5ad.gz`（AnnData 格式，~5.4 万细胞），
没有 10X 三件套。

## 诊断与处理

1. 解压 `.gz`（tar/gz 单层压缩直接解压即可）；
2. stage 00.5 识别 `.h5ad` → 用 **anndata**（项目统一 Python venv，
   `pip install anndata` 或 `--install-deps`）导出 mtx 三件套到
   `.staging/`：`matrix.mtx`（X.T，基因×细胞）、`barcodes.tsv`、
   `features.tsv`（col1=gene_ids，col2=symbol）。**features 导出必须
   `index=False`**，否则列错位——这是实测踩过的坑；
3. 之后按普通 10X mtx 路径走全流程；
4. 不走 SeuratDisk（GitHub 依赖、安装坑多）。

## 运行

```bash
python scripts/run_scrnaseq.py GSM6923183_MC_scRNA.h5ad output_GSM6923183 \
  --organism human --overwrite
```
