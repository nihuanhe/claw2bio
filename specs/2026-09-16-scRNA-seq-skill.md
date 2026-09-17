# Spec: scRNA-seq skill 家族 — 主 skill `scRNA-seq`（常规流程）

> 2026-09-16 grill-me 逐层追问达成共识后固化。施工图纸，供后续 AI 上下文恢复使用。
> 本机未配置 issue tracker，按本地回退规则保存于 `specs/`。

## Problem Statement

用户（湿实验背景的博后）在多台 Windows 机器上用 Seurat 做 scRNA-seq 分析，积累了一批跑通的脚本（`D:\single_cell_1`），但存在三个痛点：

1. **读入就是迷宫**：10X mtx 新旧版、tar 嵌套、h5、h5ad、rds、txt.gz、华大 BGI（gene.column=1、`MT.` 线粒体）等 9 类输入各有一套坑，分散在十几个一次性脚本里，每次换数据要重新改代码（分组信息都是硬编码的）。
2. **旧框架只有"标准路径"**：早前写的框架（图片合集.docx，8 张 PPT 截图）只覆盖八步标准流程，完全没有特殊情况的应对（批次整合、双细胞、BGI 前缀、内存爆炸……）。
3. **内存爆炸是常态**：多样本合并/整合以及后续拟时序经常爆内存，老办法是手动"中途 saveRDS → 清内存 → 重载"。

目标：参照已成熟的 bulk-RNA-seq skill 家族范式，把 scRNA 常规流程沉淀为通用 skill，拟时序/虚拟敲除/组间比较拆为独立下游 skill。

## Solution

在 `bioinformatics/sc_RNA_seq/scRNA-seq/` 新建主 skill（存量 4 个 bulk 系 skill 最后迁入 `bioinformatics/bulk_RNA_seq/`），沿用 bulk-RNA-seq 的全部范式：Python 驱动 + R 分 stage、stage 00 依赖体检、stage 00.5 输入体检自动修复（逐条打印 `[fixed]`）、`docs/decision-tree.md` 症状速查、编号 example 兼回归测试、`REPORT.md` + `run_metadata.json` 产出。

常规流程终点 = **SingleR 自动注释**（读入→QC→标准化→降维聚类→UMAP/t-SNE→marker→注释），产出唯一权威 `annotated_seurat.rds`，供下游 skill（scRNA-seq-pseudotime、scRNA-seq-virtual-ko、未来的 scRNA-seq-compare）消费。

## User Stories

1. 作为用户，我想把一个 GEO 下载的 scRNA 原始文件夹直接丢给 agent，让它自动识别格式（10X mtx 新旧版/tar 嵌套/h5/h5ad/rds/txt.gz/BGI/多样本混杂）并读入，以便我不用手改任何读入代码。
2. 作为用户，我想 tar 包里的三件套（含 mm10 嵌套目录）被自动解包整理，以便处理 GSE182135 这类老数据。
3. 作为用户，我想华大 BGI 数据被自动识别（features 列序颠倒 → gene.column=1；`MT.` 线粒体前缀），以便 percent.mt 不再全是 0。
4. 作为用户，我想 h5ad 通过项目统一 Python venv 里的 anndata 导出 mtx 三件套再读入，以便不用装 SeuratDisk/conda。
5. 作为用户，我想读入现成 rds 时自动校验是不是 Seurat 对象、v4 自动升级、多 layer 自动 JoinLayers。
6. 作为用户，我想用一个可选的 sample_metadata.csv（`sample,group`）声明分组，以便分组信息不再硬编码在脚本里；不给 csv 就按单样本探索模式跑。
7. 作为用户，我想样本名对不上（GSM 前缀、`.tar` 后缀残留）时被自动模糊匹配并逐条打印 `[fixed]`。
8. 作为用户，我想 QC 的线粒体模式按基因名前缀自动嗅探（人 MT- / 鼠 Mt- / BGI MT.），可 `--mt-pattern` 覆盖。
9. 作为用户，我想 QC 先用默认阈值跑、前后各出一张小提琴图，保留率异常（<50% 或 >95%）的样本被逐样本打印建议阈值，以便我有依据地调参重跑。
10. 作为用户，我想血红蛋白比例（percent.hb）被标记提示但不自动剔除，以便发现血细胞污染。
11. 作为用户，我想双细胞检测（scDblFinder）默认开启、各样本双细胞率进 REPORT，以便下游拟时序/虚拟敲除不被双细胞污染；可用开关关掉。
12. 作为用户，我想多样本合并后默认做 Harmony 整合、并输出整合前后两张 UMAP 对照，以便直观判断批次校正效果；可换 CCA/RPCA 或关闭。
13. 作为用户，我想聚类分辨率默认 0.5 且附一张 clustree 扫描图，以便有依据地调 `--resolution`。
14. 作为用户，我想 UMAP 和 t-SNE 都算、各出按 cluster/样本/group 着色的三张图，以便对比展示。
15. 作为用户，我想 FindAllMarkers 用 presto 加速，以便大数据不等一晚上。
16. 作为用户，我想 SingleR 用两个参考数据集互相印证、不一致的 cluster 在 REPORT 标黄，以便知道哪里需要人工复核。
17. 作为用户，我想拿到一份手动注释 CSV 模板（由 top10_markers.csv 改造，每群手写细胞类型）和配套应用脚本，README 和 REPORT 都写清用法，以便我把手动注释交给 AI agent 一键应用并重出注释 UMAP。
18. 作为用户，我想 `cell_type_final` 列按 手动注释 > SingleR consensus > Cluster_N 优先级生成，以便下游 skill 只认这一列。
19. 作为用户，我想每个 stage 结束自动落 checkpoint（rds）且支持 `--resume` 续跑，以便内存炸了不从头再来——炸内存是常态不是意外。
20. 作为用户，我想 README/REPORT 显式标注 merge/整合（以及将来拟时序）是内存高峰步骤，且所有输入文件就绪后才进入 merge，以便在 10 台配置不一的机器上有预期。
21. 作为用户，我想超大细胞量时有 `--downsample N` 探索模式可选。
22. 作为用户，我想主流程产出文件名在单/多样本模式下一致（`annotated_seurat.rds` 等），以便下游 skill 不用判断模式。
23. 作为用户，我想 6 个编号 example 各对应一个真实数据集的坑（GSE234527/GSE182135/GSE200874/BGI/GSM6923183/GSE197289），其中 example 1（降采样 fixture）和 example 4（合成 BGI fixture）开箱可跑做回归测试。
24. 作为用户，我想 `examples/manifest.csv` 逐 example 记录数据集/GEO 号/存储位置(repo/geo/cos)/md5，以便"哪个数据是哪个"不靠人脑记。
25. 作为用户，我想 R 依赖走统一的 `resources/r-deps/` Windows 二进制 mini-repo（在 bulk 的 139 包上扩展 scRNA 闭包），celldex 参考和 presto 上 COS，以便国内离线/慢网环境可装。
26. 作为用户，我想 `docs/decision-tree.md` 覆盖读入 7 条/QC 4 条/分析 5 条 + Ensembl 行名共 16+1 条症状速查，每条链到参数或 example。
27. 作为用户，我想完整数据集的 annotated rds（DietSeurat 瘦身版）能从 COS 直接下载，以便不重跑主流程就能直接做拟时序/虚拟敲除；同时我自己真实数据跑出的 rds 只留在本地。

## Implementation Decisions

### 布局与家族

- 容器目录 `bioinformatics/sc_RNA_seq/`（scRNA 全家）与 `bioinformatics/bulk_RNA_seq/`（存量 4 个迁入，互引相对路径层级不变，迁移后批量 grep 验证）；外层容器名纯容器、非 skill。
- 本轮只实现主 skill `sc_RNA_seq/scRNA-seq/`；`scRNA-seq-pseudotime`、`scRNA-seq-virtual-ko` 待主 skill 产出真实数据后再写（README 写清"先跑常规流程拿 annotated rds"）；`scRNA-seq-compare`（用户指定对比组）只在 README 占位。
- skill 内部结构对齐 bulk：`SKILL.md / README.md / scripts/ / examples/ / docs/ / resources/`。

### 实现形态

- Python 驱动（`scripts/run_scrnaseq.py`：CLI、stage 00.5 输入体检、调 Rscript）+ R 分 stage 脚本；stage 间以 rds 传递 Seurat 对象。
- stage 00：R 包逐包版本检查 + anndata 检查，`--install-deps` 代装（R 走 r-deps mini-repo，anndata 走 pip 进统一 venv；**不用 conda、不用 SeuratDisk**）。
- stage 00.5 输入体检（9 类格式嗅探 + 自动修复打印 `[fixed]`）：10X mtx 新版(features 三列 gz)/旧版(genes 两列)/tar(tar.gz) 嵌套解包/10X h5/h5ad(anndata 导出 mtx+features+metadata，features 导出必须 `index=False`)/rds·RData(校验 Seurat 对象、v4 升级、JoinLayers)/txt·csv.gz(行列方向判断)/BGI(features 列序颠倒→gene.column=1，MT. 前缀)/多样本混杂。
- 分组：可选 `--metadata sample_metadata.csv`（`sample,group` 列，样本名模糊匹配）；不给 → 单样本探索模式，REPORT 注明。命令行快捷分组写法作为辅助，csv 是主路径。

### 分析策略

- QC：mt 前缀自动嗅探（匹配率最高者，打印理由，`--mt-pattern` 覆盖）；percent.hb 只标记不剔除；默认阈值（mt<20%、200<nFeature<6000）先跑，QC 前后小提琴图各一张，保留率 <50%/>95% 的样本逐样本打印建议阈值（docx 经验规则），支持 `--mt-max` 及 metadata per-sample 阈值列重跑。
- 双细胞：scDblFinder 默认开（`--no-doublets` 关），各样本双细胞率进 REPORT；环境 RNA（SoupX/DecontX）不进 v1（decision-tree 注明原因）。
- 标准化：LogNormalize 默认，`--sct` 可切 SCTransform。
- 整合：多样本默认 Harmony（IntegrateLayers），整合前后 UMAP 对照图；`--integrate cca|rpca|harmony|none`。
- 降维聚类：resolution=0.5 默认 + clustree 扫描图；UMAP+t-SNE 都算，各出 cluster/orig.ident/group 三张着色图（`--no-tsne` 可关）。
- marker：presto 加速 FindAllMarkers，产出 `markers_all.csv` + `top10_markers.csv`。
- 注释：SingleR 双参考（人 HumanPrimaryCellAtlas+BlueprintEncode；鼠 ImmGen+MouseRNAseq，`--organism` 选，`--reference`/`--custom-ref` 换/自带），输出 `SingleR_label_main/fine` + cluster 多数票 `cluster_consensus`；双参考不一致的 cluster REPORT 标黄；`--marker-file` 补充打分；`--no-annotation` 降级。
- 手动注释通道：模板 CSV（`cluster,cell_type`，由 top10_markers.csv 改造）+ `scripts/apply_manual_annotation.R`（`Rscript apply_manual_annotation.R <rds> <csv> <out_dir>` 重打标签并重出注释 UMAP）；README 写流程摘要、REPORT 写详细指引。
- `cell_type_final` 列优先级：手动注释 > cluster_consensus > Cluster_N；下游 skill 一律只读此列。

### 产出契约（下游 skill 的输入标准）

rds 三分规则（红线：用户真实数据的 rds 永远不出本地）：

| rds 来源 | 去向 |
|---|---|
| 用户自己数据跑出的 | 只留本地，绝不上 COS（数据不出本地红线） |
| example fixture 跑出的（几 MB） | 进 git `examples/N/output/` |
| 完整数据集跑出的 annotated rds | 可上 COS，作为下游 skill 的现成输入分发 |

- 主 skill 提供 `--export-slim` 选项：`DietSeurat()` 瘦身导出（去掉 scale.data/多余 reduction，保留下游必需层），专供 COS 分发和用户自行分享。
- 下游 skill（pseudotime/virtual-ko）README 写明"先跑常规主流程拿 annotated rds"，同时注明示例 rds 可从 COS 直接下载跳过主流程。

| 文件 | 内容 |
|---|---|
| `annotated_seurat.rds` | 唯一权威产物，meta.data 含 `orig.ident/group/seurat_clusters/SingleR_*/cell_type_final` |
| `markers_all.csv`、`top10_markers.csv` | presto 全表 + 每群 top10 |
| `annotation_per_cluster.csv` | cluster → 双参考标签 → consensus |
| `QC_violin_before/after`、`UMAP_*`、`TSNE_*`、`clustree`、整合前后对照、marker 热图/dotplot | 图件 png+pdf |
| `run_metadata.json` | 参数、输入诊断、各样本细胞数/双细胞率/保留率、版本、时间戳 |
| `REPORT.md` | 产出说明 + 异常 + 内存高峰警告 + 手动注释指引 + 下游 skill 调用建议 |

单/多样本模式产出文件名一致。不额外导出 csv 矩阵快照（rds 是唯一真相）。

### 内存管理（核心铁律）

- **炸内存是常态**：每个 stage 结束自动 saveRDS 到 `<output>/.checkpoints/`（覆盖写不累积），`--resume` 从最近 checkpoint 续跑。
- merge/整合（及将来拟时序）标注为内存高峰步骤写进 README/REPORT；stage 顺序保证**所有输入就绪（解包/体检/修复完成）后才进入 merge**。
- 细胞数超阈值时建议 `--downsample N`（每样本抽 N 细胞探索）；REPORT 打印各 stage 细胞数曲线。

### Examples 与数据归属

- 6 个编号 example：1=GSE234527（标准 mtx.gz，可跑降采样 fixture）、2=GSE182135（tar+旧版 genes+多组+内存）、3=GSE200874（h5）、4=BGI（合成 fixture，可跑；真实 25057A-C 不入库）、5=GSM6923183（h5ad）、6=GSE197289（6 组复杂设计）。
- `examples/manifest.csv`：`example,dataset,accession,input_type,storage(repo/geo/cos),location,md5,note`；含一类专门条目 `type=annotated_rds`（完整数据集跑出的 annotated rds 的 COS 链接 + md5 + Seurat 版本）。
- GitHub 只放小 fixture；自产大数据/per-skill zip/完整数据集的 slim annotated rds 上 COS，本地暂存 `cos-staging/`（已建，含 README 与目录骨架，已加入根 .gitignore）；`CONTRIBUTING.md` 已新增「COS 存储约定」一节（manifest 制度、上 COS 范围、上传后回填规则）。
- 真实 25057A-C（华大，未上 GEO）的任何数据/rds 默认不上 COS，是否公开由用户届时单独拍板。

### 依赖

- 系统 R（统一 R 4.5）+ 扩展统一的 `resources/r-deps/` Windows 二进制 mini-repo（bulk 139 包 + scRNA 闭包：Seurat v5/harmony/SingleR/celldex/presto/scDblFinder/clustree/hdf5r…），一份仓库服务所有 skill。
- celldex 参考数据 + presto 源码包上 COS（cos-staging 开 `resources/` 目录），SKILL.md 写安装命令。
- SKILL.md 写死已测试版本矩阵（Seurat 5.3.1+/R 4.5/…）；rds 读入自动检测 Seurat 对象版本，v4 走升级路径。

### 决策树

`docs/decision-tree.md` v1 共 16+1 条：读入类 7（tar 嵌套/genes vs features/BGI 列序+MT./h5ad index=False/rds 三态/文本矩阵方向/样本名模糊匹配）、QC 类 4（percent.mt 全 0/保留率异常/血细胞污染/双细胞率异常）、分析类 5（批次分离/整合过度/cluster 多少/SingleR 不一致/内存爆炸+downsample）+ Ensembl 行名坑。

## Testing Decisions

- 好测试 = 只测外部行为：跑编号 example → 校验产出文件齐、`run_metadata.json` 关键字段、`[fixed]` 修复记录符合预期；不测内部实现。
- 回归测试 seam = 编号 example（对齐 bulk 的 examples 兼回归测试范式）：example 1（GSE234527 降采样 fixture）与 example 4（合成 BGI fixture）必须开箱可跑，作为冒烟测试；example 2/3/5/6 为踩坑档案（README 症状→诊断→参数 + 数据获取方式）。
- 发布前按 `CONTRIBUTING.md` 阶段 3 跑冒烟测试；examples/output 必须真实生成。
- **开发期验证策略（16GB 内存适配）**：全程在降采样/合成 fixture 上开发调试；用户 D 盘存量 rds（GSE234527/GSE200874/25057A 等的 combined/聚类后 rds）作为预期输出的回归基线，不重跑存量分析；开发期只做一次全量真实验证跑（GSE234527，5 样本，本机曾跑通）。
- **上线前全量验证（用户明确要求）**：网站实际上线前，由用户亲自把 6 个编号 example 全部真实跑通一遍（可分次进行，允许用 `--downsample`/checkpoint 辅助；GSE182135 等大数据可留到内存充裕的机器），跑出的真实输出同时作为网站教程页的素材；未全量跑通不上线。

## Out of Scope

- scRNA-seq-pseudotime / scRNA-seq-virtual-ko 的完整实现（待主 skill 产出真实数据后各自立项；家族级约定——每 stage 落 checkpoint、内存高峰警告——已在本 spec 固定）。
- scRNA-seq-compare（组间比例+pseudobulk DE）仅占位。
- 环境 RNA 校正（SoupX/DecontX）。
- conda 环境管理；SeuratDisk。
- 存量 4 个 bulk 系 skill 迁入 `bulk_RNA_seq/` 的搬迁动作（最后一步执行）。
- 网站教程页/COS 实际上传（按 CONTRIBUTING 阶段 5/6 在发布时执行）。
- 多模态（CITE-seq/ATAC）、空间转录组。

## Further Notes

- 素材档案：3 篇公众号读入文章已存 `D:\pi-data\wechat_articles\`（第 3 篇为十类读入完整代码）；docx 框架图片已导出 `D:\pi-data\docximg\`（8 张 PPT 截图）；用户实战脚本在 `D:\single_cell_1\`（华大读入、tar 解包、h5ad 导出、SingleR/presto/monocle3/scTenifoldKnk 等）。
- 下游 skill 立项目标的参考实现已存在：拟时序 `D:\single_cell_1\拟时序分析.R`（monocle3，复用 Seurat UMAP/cluster，手动指定 root cluster）；虚拟敲除 `D:\single_cell_1\虚拟敲除.R`（scTenifoldKnk，吃 counts 层 + 目标基因）。
- 发布面向 GitHub + claw2bio.site（COS 直链），全程遵守 `CONTRIBUTING.md` SOP（脱敏、英文化、冒烟、教程页九节模板）。
