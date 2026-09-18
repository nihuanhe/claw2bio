# sc_RNA_seq 家族 · TODO（随项目滚动更新）

> 2026-09-16 建立。完成一项勾一项；新事项随时追加。

## 环境

- [x] 安装 scDblFinder（BiocManager，已装 1.24.10）
- [x] 安装 clustree（CRAN，已装 0.5.1；与 ggplot2 4.0 不兼容 → stage03 已 tryCatch 优雅降级）
- [x] 装完后用 example 1 重跑一次全流程，确认双细胞率表 + clustree 图正常产出（双细胞表✓；clustree 图因 ggplot2 4.0 不兼容跳过，待 clustree 更新后复查）

## 主 skill 收尾

- [x] 存量 4 个 bulk 系 skill 迁入 `bioinformatics/bulk_RNA_seq/`（git mv 完成；根路径引用已 sed 更新；AGENTS.md 索引已补 4 行；example 1 冒烟跑通✓）
- [x] `resources/r-deps/` mini-repo 扩展 scRNA 闭包（闭包 245 包：106 已有 + 139 新增 + Bioc3.21 补链；现 277 zips + PACKAGES 重建；celldex/presto/monocle3/bluster 为纯 R 源码包可装，Rsamtools/rtracklayer 二进制缺口待补；扩展脚本 examples/_dev/extend_r_deps.R）
- [ ] 补 r-deps 缺口：Rsamtools/rtracklayer 的 R4.5 win 二进制（手工从 Bioc 3.21 抓或上线前复查）
- [ ] celldex 参考数据 + presto 源码包上 COS（cos-staging 开 resources/ 目录，回填 manifest）
- [x] GSE234527 全量真实验证跑（2026-09-16 通过：11570 真实细胞→QC→去双细胞 10859→Harmony→12 clusters→SingleR；~10min 无爆内存；slim rds 41MB 已出；产物在 D:\single_cell_1\GSE234527_output）
- [x] 主 skill `--export-slim`（DietSeurat 瘦身导出）选项实现——已实测 27.5→9.2 MB，供 COS 分发与用户分享

## 下游 skill（依赖主 skill 真实产出）

- [x] `scRNA-seq-pseudotime`（monocle3；SKILL/README/scripts 完成，example 1 冒烟跑通：轨迹图 4 套 + graph_test + 基因轨迹图；root 必填校验✓；全量数据案例待 GSE234527 验证跑后补）
- [x] `scRNA-seq-virtual-ko`（scTenifoldKnk 1.0.3 已装并跑通；处理了版本坑：函数名/参数名/列名全变；**实测性能：2000 基因×全细胞 8h 跑不完→杀掉；2000×10net×500cell 3.5h+ 未完成；500 基因×5net×500cell ≈17min 出结果（10 显著基因）——nfeatures 是平方级大头，**--nc-ncells 默认已改回官方 500**；真实 ACTA2 结果在 D:\single_cell_1\GSE234527_vko_ACTA2）
- [x] **计时探路完成（2026-09-17）**：`--nfeatures 2000 --nc-nnet 3 --nc-ncells 500`，真实对象
      （10,859 细胞）→ **90 min**（20:24:03→21:54:11；期间有 ~69 min 被一个重复进程抢 CPU，
      干净环境应更快）；出 **58 个显著基因**（p_adj<0.05），top 命中 **MYLK / TPM1 / DES / CNN1**
      —— 经典平滑肌共调控基因，生物学合理。产物归档 `D:\single_cell_1\_run_vko_probe\probe_2000x3_output`
- [ ] **官方默认 `2000×10×500` 正式跑 → ❌ 数值失败（2026-09-18 02:48）**：
      22:21:06 启动，**建网络 100%（10 个网络，约 2 h）+ CP 分解/张量分解都成功**
      （norm explained 21.8%），随后死在 scTenifoldKnk 内部的**流形对齐**：
      `Error in E$vectors[, E$values > 1e-08] : incorrect number of dimensions`
      （`Calls: scTenifoldKnk -> manifoldAlignment`，另有 22 个 warnings）。无任何结果文件写出。
      → **结论：`--nc-nnet 10` 在这份数据上数值退化**（3 网络时 norm explained 29.9% 可正常跑完）；
      这是包内部实现的问题，skill 侧只能选参数规避
- [x] 规避验证 ✅：**`2000×5×500` 通过（2026-09-18 03:33:58 → 05:30:40，约 2 h；
      前 56 min 有一个孤儿进程抢 CPU）**：**54 个显著基因**，产物齐全（含 `REPORT.md`）。
      对比 3 网络（58 个显著、90 min）→ 两档结果量级一致，说明 3–5 网络都稳定；**10 网络数值失败**
      → **建议把 `--nc-nnet ≤ 5` 写进 SKILL/README**（对这类 2000 基因规模的数据）
- [x] `run_virtual_ko.py` 增加 **`--report-only`**（驱动进程意外退出、R 已跑完时，只重生成
      `REPORT.md` 不重算）——本次探路就靠它补出了缺失的 REPORT

## 复核修复（2026-09-17，见 plan-skill-example-completion.md §12）

- [x] **pseudotime `--resume` 原来是"假"的**：`stage_pseudotime.R` 写 `.checkpoint_cds_learned.rds`
      但**从不读回**，`run_pseudotime.py` 的 `--resume` 也不传给 R → 已修（两处各加 3–10 行）；
      现 `--resume` 会真的跳过"建 cds + learn_graph"，成功结束时才删检查点
- [x] 上述修复的等效实测：把已有 `pseudotime_cds.rds` 当检查点放进新目录，跑
      `--resume --no-graph-test` → 日志出现 `--resume: loading checkpoint`，**无** `building cell_data_set` /
      `learn_graph`，4 套轨迹图与 summary 正常产出，结束后检查点被删除
- [ ] 待补：`--resume` 的**真实崩溃**验证（kill mid-run），本次是等效验证而非真崩溃
- [x] **virtual-ko 无断点、不可续跑** → `SKILL.md` / `README.md` / 网站页已如实标注（别让机器休眠）
- [x] **SKILL.md 时长数字与实测冲突**："2000×10 ≈ 1 h" vs TODO 实测 3.5 h+ 未完成 →
      改为"未跑完（已中止）"，并说明全量耗时尚未标定

- [ ] `scRNA-seq-compare`（占位：组间比例 + pseudobulk DE，用户指定对比组）
- [ ] scTenifoldKnk 1.0.3 二进制 zip 入 COS resources（现为 D:\single_cell_1 本地包）
- [ ] 两个下游 skill 的 examples/output 上线前用真实数据重跑替换冒烟产出

## 主流程 example 真实跑通（2026-09-17，AI 在本机按 skill 自带脚本执行）

### ex3 GSE200874（✅ 跑通）

- 命令：`run_scrnaseq.py D:\single_cell_1\_run_ex3\input <ex3>/output --metadata ...\sample_metadata.csv
  --organism mouse --reference MouseRNAseqData --export-slim`
- 结果：4 h5（wt×2 / mut×2）→ QC 前 7189 → **QC 后 6408 细胞、22 clusters**（Harmony 整合，
  resolution 0.5）；markers 303,842 行；SingleR 注释 22/22 cluster 全出（Hepatocytes/Monocytes/
  Granulocytes/Neurons/Cardiomyocytes/…，符合胚胎期混合组织，非纯 PBMC）
- [x] 跑通；[ ] 待办：cluster 数偏多，可用 `--resolution` 调；`clustree_resolution_scan.png` 仍缺（见下）

**本次发现（都要在文档里如实标注）**

1. **metadata 只写 GSM 号无效**：`inspect_input.norm_sample_key()` 把 `GSM\d+_?` 从两侧都剥掉，
   于是 `GSM6045825` 被剥成**空串**、永远匹配不上 → 4 个样本静默退化成探索模式
   （只留一行 `metadata rows with no matching sample: ['']`）。**正解：写完整样本名**。
   `examples/3_.../README.md` 原来写的"metadata 里写 GSM 号即可匹配"是错的（已改）
2. **`D:\single_cell_1\GSE200874_RAW` 混着 3 个派生 `.rds`**（combined/ctrl/test_pbmc），
   直接喂目录会被当成 **7 个样本** → 必须先隔离 4 个 h5 或用 `--exclude`
3. **Trae 沙箱拦住 celldex 缓存目录**（`C:\Users\A\AppData\Local\ArtifactDB\...`）：
   `celldex::ImmGenData()` 建 lock 目录失败 → **整个 stage04 硬失败**（markers 都算完了却拿不到注释）。
   `celldex::MouseRNAseqData()` 已有缓存（17.1 MB，status/LOCK 齐全）→ 用
   `--reference MouseRNAseqData` 可绕过。**建议改脚本：参考抓取也包 tryCatch**，单参考失败不该拖垮全部
4. **`REPORT.md` 的 SingleR references 被逐字符拆开**（`SingleR references: M, o, u, s, e, R, N, A, ...`）：
   `stage04_annotate.R` 用 `write_json(auto_unbox = TRUE)` 把长度 1 的字符向量写成 JSON **字符串**，
   而 `report_writer.py` 用 `', '.join(...)` 当列表处理。**同一个坑**也会打中
   `refs_disagree_clusters`（cluster 12 → `"1, 2"`）。→ 待修（改 `report_writer.py` 归一化）
5. `clustree_resolution_scan.png` 因 clustree 0.5.1 与 ggplot2 4.0 不兼容被 tryCatch 跳过（已知，非本次新增）

### ex2 GSE182135（✅ 跑通：10 样本 / 54,484 细胞 / 21 clusters）

- 命令：`run_scrnaseq.py D:\single_cell_1\GSE182135_RAW <ex2>/output --metadata ...\sample_metadata.csv
  --exclude combined_pbmc,E9_5_pbmc,E10_5_pbmc,E11_5_pbmc,E12_5_pbmc --organism mouse
  --reference MouseRNAseqData --export-slim`
- 输入体检已通过：10 个样本全部按文件名匹配到 4 组（E9.5/E10.5/E11.5/E12.5）✓；
  旧版**两列 `genes.tsv`** ✓；`^mt-` 线粒体前缀自动识别 ✓；5 个游离 rds 被 `--exclude` 剔除 ✓
- 实测：10 样本 **57,849 细胞**（19,468 基因）→ QC 后 57,652 → 去双细胞 **54,484**；
  Harmony → **21 clusters**；markers 48 MB；耗时约 **48 min**（stage03 的 UMAP+t-SNE 约 18 min、
  stage04 markers+SingleR 约 17 min）；内存峰值约 **5.7 GB**（私有），全程无爆内存
- QC 保留率 **98–100%**（GEO 给的是 filtered 矩阵）→ 10 个样本全部触发"收紧 `--mt-max`"提示
- 产物：`annotated_seurat.rds` 998 MB + slim 740 MB（rds 不进 git，按 D5 走 `cos-staging`）
7. **外层 `D:\single_cell_1\GSE182135_RAW.tar`（2.9 GB）装的是 10 个「三件套目录」**，
   而 `inspect_input._classify_file()` 在多层三件套时只 `using hits[0]` → **喂这个 tar 会静默只用第 1 个样本**
   （10 个丢 9 个）；若真是"tar 套 tar"则直接 `unsupported`。
   → 本次改用**目录输入**（10 个已解包目录 + `--exclude`）。**建议改脚本：tar 内多个三件套应展开成多样本**

### ex5 GSM6923183 h5ad（运行中）

8. **h5ad 的 `X` 若不是 counts（scanpy 产出几乎都如此），原 `export_h5ad()` 会导出 log 归一化值** →
   R 里二次归一化、QC 的 `nCount_RNA`/`percent.mt` 全是错的。本 example 的 h5ad 正是这种情况
   （`X` 是 log1p 值、原始 counts 在 `layers['counts']`，`uns` 里有 `log1p`）。
   → **已修** `inspect_input.export_h5ad()`：优先取 `layers['counts'/'count'/'raw_counts'/'umi_counts']`，
   并把来源写进 `[fixed]`。实测维度 53,748 细胞 × 20,320 基因（human，HPCA+Blueprint 参考本机已缓存）
9. h5ad 的 `obs`（Sample/Phenotype/batch/donor_id）**会被导出流程丢弃**（只导 barcodes 三件套）
   → 多样本 h5ad 会被当成**单样本**跑；要按 donor 分组只能自己先拆分。属已知限制，需写进 README

### ex6 GSE197289（运行中：96,933 细胞 × 29,329 基因）

10. **原始文件是"双层 gzip"**：`GSE197289_snRNA-seq_mouse_raw_counts.RDS.gz` 解开第一层后
    **里面还是 gzip**（魔数 `1f8b08`），再解一层才是真正的 RDS（2,033 MB，头 `X\n`）。
    `readRDS(gzfile(p))` 直接报 `unknown input format`。另外 pipeline 的扫描**不认识 `.rds.gz`**
    （只认 `.rds/.rdata/.rda`）→ 这种文件必须先手动解压（本例解两层）才能喂进去
11. 真身是 **`dgCMatrix` 稀疏矩阵**（169,068,288 非零、全整数、max 14,939；小鼠基因名、细胞名与
    `barcode_meta` 完全对得上）→ 原 `stage01_read.R` 的 `as(as.matrix(obj), "CsparseMatrix")` 会**转稠密**
    （29,329 × 96,933 × 8 B ≈ **22.7 GB**）必然爆内存。**已修**：`inherits(obj, "Matrix")` 时保持稀疏、
    不 densify（实测 stage01/02 通过）
12. 规模 **96,933 细胞 × 29,329 基因**；QC 后 94,499（97.5%）；**双细胞率 32.84%** ——
    把 97k 细胞当成**一个样本**喂 scDblFinder，它会按"单样本回收 97k 细胞"外推 multiplet 率，
    属于**过度去双细胞**。真实样本标签其实就在 `barcode_meta`（`sample_name` 列，
    如 `CSD_1.5h_male_rep1`）里，但 **pipeline 只能按"输入样本"分组、吃不了逐细胞标签** →
    分组与去双细胞同时失真。这是真实 GEO 数据最常见形态（一份 counts + 一份 cell metadata），
    **建议作为下一步功能**（如 `--cell-metadata` 把逐细胞标签变成 orig.ident/group）
13. ex6 README 原写的"6 个样本目录、6 组各进 `sample_metadata.csv`"与本地数据形态不符
    （本地是一份大矩阵 + 逐细胞标签表），需要重写

## 发布（按 CONTRIBUTING.md SOP）

- [ ] 上线前 6 个 example 全部真实跑通（用户亲跑，可分次；未跑通不上线）
- [ ] 脱敏 → 英文化 → 冒烟 → 提交 → 教程页九节模板 → 构建发布
