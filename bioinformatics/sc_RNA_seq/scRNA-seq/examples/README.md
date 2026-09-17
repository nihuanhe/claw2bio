# Examples / 示例

每个编号 example 覆盖一类特殊情况，兼作回归测试。
数据归属（GEO 链接 / COS 链接 / md5）一律查 **`manifest.csv`**。

| # | 目录 | 数据集 | 覆盖的坑 | 实测状态（2026-09-17） |
|---|---|---|---|---|
| 1 | `1_example_GSE234527_downsampled-10x-mtx` | GSE234527（降采样 fixture 已随仓库） | 标准 10X mtx.gz 多样本两组、metadata 模糊匹配、Harmony 整合 | ✅ 开箱即跑（约 2k 细胞 / 9 clusters） |
| 2 | `2_example_GSE182135_tar-genes-tsv` | GSE182135 | 旧版两列 genes.tsv + 10 样本 4 组 + 内存管理 | ✅ 已真实跑通：57,849 → 去双细胞 **54,484** 细胞 / **21 clusters**（~48 min，峰值 ~5.7 GB） |
| 3 | `3_example_GSE200874_10x-h5` | GSE200874 | 10X h5 多样本 | ✅ 已真实跑通：7,189 → **6,408** 细胞 / **22 clusters**（~20 min） |
| 4 | `4_example_synthetic-BGI` | 合成 fixture（随仓库） | 华大 BGI：features 列序颠倒（gene.column=1）+ `MT.` 线粒体前缀 | ✅ 开箱即跑（单样本探索） |
| 5 | `5_example_GSM6923183_h5ad` | GSM6923183 | h5ad → anndata 导出路线 | ✅ 已真实跑通：53,748 → 去双细胞 **46,059** 细胞 / **27 clusters**（~31 min） |
| 6 | `6_example_GSE197289_multi-sample` | GSE197289 | 单份稀疏 `dgCMatrix` RDS（双层 gzip）+ 逐细胞标签 + presto | ✅ 已真实跑通：96,933 → 去双细胞 **63,470** 细胞 / **28 clusters**（~1 h，峰值 **~11.9 GB**，本机上限） |

## 跑通命令

example 1（多样本、带分组）：

```bash
python scripts/run_scrnaseq.py \
  examples/1_example_GSE234527_downsampled-10x-mtx/input \
  examples/1_example_GSE234527_downsampled-10x-mtx/output \
  --metadata examples/1_example_GSE234527_downsampled-10x-mtx/input/sample_metadata.csv \
  --overwrite
```

预期：5 样本约 2000 细胞 → QC 后 ~1931；9 个 cluster（降采样 fixture，注释噪声大、
双参考不一致属预期）；产出全套 UMAP/t-SNE/QC 图 + markers + `annotated_seurat.rds`。

example 4（华大 BGI 嗅探，合成小数据，参数按 60 基因的玩具数据放宽）：

```bash
python scripts/run_scrnaseq.py \
  examples/4_example_synthetic-BGI/input \
  examples/4_example_synthetic-BGI/output \
  --min-features 5 --mt-max 50 --max-features-qc 50 --no-tsne --overwrite
```

预期：`[fixed]` 打印 gene.column=1 与 `MT.` 前缀识别；单样本探索模式；
合成基因与参考库无重叠 → SingleR 自动降级为 Cluster_N 标签（预期行为）。

> 上线前要求：6 个 example 全部真实跑通一遍 —— **2026-09-17 已完成**（结果见上表；
> 每个 example 的 `README.md` 记录了确切命令、实测数字与踩到的坑）。
> 完整数据集的 slim annotated rds 经 COS 分发，供下游 skill 直接取用。
