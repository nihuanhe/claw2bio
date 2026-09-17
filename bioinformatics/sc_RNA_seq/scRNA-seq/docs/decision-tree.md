# Decision tree / 决策树 — scRNA-seq 特殊情况速查

症状 → 诊断 → 处理（参数/通道）→ 对应 example。
Stage 00.5 能自动修的都会打印 `[fixed]`；本表覆盖需要人工决策的情况。

## 读入类

| # | 症状 | 诊断 | 处理 | example |
|---|---|---|---|---|
| 1 | GEO 下载的是一堆 .tar/.tar.gz | 10X 三件套裹在 tar 里，可能嵌套 mm10/ 目录 | 自动解包到 `.staging/` 并递归找三件套 `[fixed]` | 2 |
| 2 | 旧数据只有 genes.tsv 没有 features.tsv | 10X 旧版两列格式 | 自动识别，`gene.column=2` | 2 |
| 3 | 读出来基因名是 ID 不是 symbol / 华大数据 | BGI 的 features 列序颠倒（col1=symbol, col2=ID） | 自动 `gene.column=1` `[fixed]` | 4 |
| 4 | percent.mt 全是 0 | 线粒体前缀没匹配上（人 `MT-`、鼠 `Mt-`、BGI `MT.`） | stage 01 自动选匹配最多的前缀并打印；不对就 `--mt-pattern "^MT-"` 覆盖 | 4 |
| 5 | 输入是 .h5ad | Scanpy/AnnData 格式 | 自动用 anndata 导出 10X 三件套（需 `pip install anndata` 或 `--install-deps`）；**不走 SeuratDisk** | 5 |
| 6 | 输入是 .rds/.RData | 可能是 Seurat v4/v5 对象，也可能是裸矩阵 | stage 01 校验：Seurat 对象直接用（多 layer 自动 JoinLayers）；裸矩阵转 CreateSeuratObject | — |
| 7 | 输入是 txt/csv(.gz) 文本矩阵 | 基因可能在行也可能在列 | 自动嗅探方向，需要时转置 `[fixed]` | — |
| 8 | metadata 的样本名和目录对不上 | GSM 前缀、`.tar` 后缀残留等 | 自动模糊匹配 `[fixed]`；仍对不上的进 REPORT warnings | 1 |
| 9 | 基因行名是 Ensembl ID | features 选了 ID 列 | stage 00.5 按 Ensembl 模式判列；symbol 列优先 | 2/4 |

## QC 类

| # | 症状 | 诊断 | 处理 | example |
|---|---|---|---|---|
| 10 | 某样本保留率 <50% | 阈值太狠或该样本质量差 | REPORT 逐样本给建议（如 `--mt-max 25`、放宽 nFeature 150–5000）；改参数 `--resume` 重跑 | 1 |
| 11 | 保留率 >95% | 阈值太松 | REPORT 建议收紧（`--mt-max 15` 等） | 1 |
| 12 | percent.hb 高 | 取样混入血液 | 只标记不剔除；需要剔除时自行 subset（有意保守） | — |
| 13 | 双细胞率异常高（>10%） | 上样浓度过高 | REPORT 标出该样本；scDblFinder 默认开（`--no-doublets` 关） | — |

## 分析类

| # | 症状 | 诊断 | 处理 | example |
|---|---|---|---|---|
| 14 | UMAP 按样本而不是按细胞类型分开 | 批次效应 | 多样本默认已开 Harmony 整合，对照 `UMAP_before/after_integration.png`；还不行换 `--integrate cca/rpca`；整合过度（同一样本内生物学差异被抹平）才用 `none` | 1 |
| 15 | cluster 太多/太少 | resolution 不合适 | 看 `clustree_resolution_scan.png` 选稳定分辨率，`--resolution` 重跑（`--resume` 跳过重活） | 1 |
| 16 | SingleR 两个参考给的标签不一致 | 边界细胞/稀有细胞 | REPORT 标黄这些 cluster → 走手动注释通道 | 1 |
| 17 | R 一跑 readMM/Read10X 就段错误（segfault） | Matrix 与 SeuratObject ABI 不匹配（Matrix 1.7.5 vs 旧 SeuratObject 编译产物） | 重装 Matrix+SeuratObject+Seurat 到同一 CRAN 快照；杀掉残留 Rterm 进程再装 | — |
| 18 | 内存爆掉（merge/整合/拟时序阶段） | 大矩阵在内存峰值步骤 | 这是常态：checkpoint 已落盘，`--resume` 续跑；超大时 `--downsample N` 先探索 | 2 |
| 19 | 报错 "0 cells pass min.features" | 输入是 RAW 矩阵（含空液滴）或极度稀疏 | 换 cellranger 的 filtered 矩阵，或降低 `--min-features` | 1 |
| 20 | 只想看某一个样本 | 多样本对象取子集 | 直接对 `annotated_seurat.rds` subset（`subset(obj, subset = orig.ident == "X")`）后交给下游 skill | — |

## 手动注释通道

1. 复制 `top10_markers.csv` → `manual_annotation.csv`，整理成 `cluster,cell_type` 两列；
2. `Rscript scripts/apply_manual_annotation.R <output>/annotated_seurat.rds manual_annotation.csv <output>`；
3. `cell_type_final` 被覆盖、注释 UMAP 重画；缺标签的 cluster 保留原 `cell_type_final`。
