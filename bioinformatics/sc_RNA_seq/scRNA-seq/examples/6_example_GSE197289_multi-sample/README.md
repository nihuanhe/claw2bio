# Example 6 — GSE197289: 单份大矩阵 + 逐细胞标签（snRNA-seq, mouse）

> 踩坑档案（case file）。数据不进仓库：GEO 下载见 `../manifest.csv`。

## 真实数据形态（2026-09-17 实测，与旧版本文档不符，已更正）

上游只有两份文件，**不是**"6 个样本目录"：

| 文件 | 内容 |
|---|---|
| `data1/Total/GSE197289_snRNA-seq_mouse_raw_counts.RDS.gz`（381 MB） | **双层 gzip**；解开两层后是 `dgCMatrix` **96,933 细胞 × 29,329 基因**（169,068,288 非零、全整数 counts、max 14,939），2,033 MB |
| `data1/Total/GSE197289_snRNA-seq_mouse_barcode_meta.csv.gz`（1.9 MB） | 逐细胞表：`V1,nCount_RNA,nFeature_RNA,percent.mt,sample_name,sex,library,class,cellID,subtype,model,realtime`，如 `CSD_1.5h_male_rep1_bcBSKD,…,CSD_1.5h_male_rep1,male,1,neuron,PEP,PEP,CSD,1.5` |

所以"6 组复杂设计"（CSD/IS/Naive/PBS × 时间 × 性别）是**逐细胞标签**，
而不是 6 个独立样本目录。

## 诊断与处理（三个真坑）

1. **双层 gzip + 扩展名不被识别**：文件叫 `.RDS.gz`，解开第一层后**里面还是 gzip**（魔数 `1f8b08`），
   再解一层才是 RDS（头 `X\n`）。`readRDS(gzfile(p))` 会直接报 `unknown input format`。
   而 pipeline 的输入扫描**只认 `.rds/.rdata/.rda`**，`.rds.gz` 会被**静默跳过**
   → 必须**手动解压（两层）**，再喂解出来的 `.RDS`。
   本次做法：`gzip.open(src) → layer1.bin`（402.9 MB，仍是 gzip）→ 再 `gzip.open` 得到 2,033 MB 的 `.RDS`
2. **裸稀疏矩阵会被 `as.matrix()` 转稠密**：原 `stage01_read.R` 对非 Seurat 的 rds 一律走
   `as(as.matrix(obj), "CsparseMatrix")` → 对这份数据等于 **29,329 × 96,933 × 8 B ≈ 22.7 GB** 稠密矩阵，
   16 GB 机器必爆。**已修**：`inherits(obj, "Matrix")` 时保持稀疏（`as(obj, "CsparseMatrix")`）。
   本次修复后 stage01/02/03/04 全程通过
3. **双细胞率 32.84% 不可信**：把 97k 细胞当成**一个样本**喂 scDblFinder 时，它会按"单样本回收
   97k 细胞"外推 multiplet 率 → 过度去双细胞（94,499 → 63,470）。真实标签就在
   `barcode_meta` 的 `sample_name` 里，但**本流程目前只能按"输入样本"分组、吃不了逐细胞标签**
   → 分组与去双细胞同时失真。这是真实 GEO 数据（一份 counts + 一份 cell metadata）最常见的形态，
   建议后续加 `--cell-metadata`（把逐细胞标签变成 `orig.ident`/`group`）

## 运行（2026-09-17 实测跑通）

```bash
# 0) 手动解两层 gz（pipeline 不认 .rds.gz）
#    外层: GSE197289_snRNA-seq_mouse_raw_counts.RDS.gz -> layer1.bin (仍是 gzip)
#    内层: layer1.bin -> GSE197289_snRNA-seq_mouse_raw_counts.RDS (2,033 MB, dgCMatrix)

python scripts/run_scrnaseq.py GSE197289_snRNA-seq_mouse_raw_counts.RDS output_GSE197289 \
  --organism mouse --reference MouseRNAseqData --export-slim --overwrite
```

- 实测：**96,933 细胞 × 29,329 基因** → QC 后 94,499（97.5%）→ 去双细胞 **63,470 细胞**；
  **28 clusters**（resolution 0.5，单样本不整合）；SingleR（MouseRNAseq）给出
  Oligodendrocytes / Astrocytes / Neurons / Fibroblasts —— **符合 snRNA-seq 脑组织**，注释可信
- 内存：stage02（scDblFinder）是本机峰值，R 进程私有内存约 **11.9 GB**、系统可用一度只剩 1.8 GB
  （靠页面文件撑住）；stage03/04 分别约 4 GB / 7.7 GB。**这台 16 GB 机器是这个数据量的上限**
- 耗时：约 1 h（18:33 → 19:57）
- 产物：`annotated_seurat.rds` 501 MB、slim 382 MB、`markers_all.csv` 94 MB

## 已知限制（要写进网站「特殊情况」）

- **逐细胞标签不能作为分组**：`sample_metadata.csv` 是"按样本"的；本数据的 6 组设计在逐细胞层面，
  目前只能当**单样本探索模式**跑（REPORT 里会写 `single (exploratory, no group info)`）。
  要做组间比较需等 `scRNA-seq-compare`（规划中）或先把矩阵按 `sample_name` 拆成多个输入
- marker 计算走 presto（本流程默认），比 Seurat wilcox 快一个量级；presto 只有 GitHub 源，
  stage 00 会检查，`--install-deps` 可代装
- SingleR 参考（celldex）体积大，国内网络建议从 COS 镜像安装（见 Download 页）；
  若参考取不到（离线/被沙箱拦缓存目录），**stage04 会整体失败** → 用 `--reference <已有缓存的参考名>` 绕过
