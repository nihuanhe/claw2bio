# 特殊情况决策树（症状 → 诊断 → 解法）

> 用法：从"你的数据长什么样 / 你遇到什么报错"出发，按树走到解法。
> 每条都指向参数、主题页和对应的编号 example（`examples/N_example_*`，可直接打开对照）。
> 体检 stage（00.5）能自动修的都不需要你做任何事——先跑一次，看它打印的 [fixed]/[warn]。

## 1. 输入文件形态

| 症状 | 诊断 | 解法 |
|---|---|---|
| 一个文件里又有 count 列又有 FPKM 列还有基因注释列 | GEO 混合矩阵（GSE255223 型） | **自动**：保留 `*_count` 列、拆出注释列存 `gene_annotation.csv`。见 `examples/2_*`；[详情](input-formats.md) |
| 文件开头一堆 `!` 开头的行，找不到表头 | GEO series_matrix | **自动**：定位 `ID_REF` 行解析。注意有些 series_matrix 数据区为空（`!Sample_data_row_count "0"`）——counts 在补充文件里，换补充文件。见 `examples/5_*` 与 `examples/4_*`；[详情](input-formats.md) |
| 矩阵行是样本、列是基因 | 转置矩阵 | **自动**：列数 > 行数时自动转回。[详情](input-formats.md) |
| 报错样本对不上，列名带 `_count`/`_FPKM`/`.bam` | 上游工具加的后缀 | **自动**：后缀剥离后匹配。[详情](input-formats.md) |
| 报错样本对不上，列名里的空格/短横变成了点（`Subject.1...CSU.v3`） | R `check.names` 毁名 | **自动**：模糊匹配撤销毁名。见 `examples/3_*`；[详情](input-formats.md) |
| 样本名 `15` 在 metadata 里变成了 `X15` | R `make.names` 毁名（数字开头） | **自动**：模糊匹配撤销。见 `examples/2_*` |
| metadata 列名是 `sample_id`/`condition` 等 | 非标准列名 | **自动**：重命名为 `sample`/`group`。找不到候选列才报错 |
| metadata 里样本比矩阵多 / 矩阵里样本比 metadata 多 | 分析集不一致 | **自动**：以 metadata 为分析集，多余样本排除并警告。双重检查 metadata 是否给对 |
| 只有 FPKM/TPM，没有 raw counts | 归一化矩阵 | **自动**：走 limma-trend 分支（引擎框会说明理由）。不能转回 counts，不要骗 DESeq2 |
| Excel 文件（.xlsx） | 非文本格式 | 先用 Excel/WPS 另存为 CSV 再喂；agent 可直接代劳 |
| 文件夹里是 `.CEL` 文件 | 芯片原始数据 | **本 skill 不管**。需要 oligo/affy 流程（RMA 归一化），[详情](input-formats.md#cel) |
| 每个样本一个 count 文件 / Salmon 的 quant.sf / featureCounts 输出 | 上游定量产物未合并 | 本 skill 从合并矩阵起步；让 agent 现场合并（按样本列拼接、基因取并集），或见 [downloading-from-GEO.md](downloading-from-GEO.md) |

## 2. 实验设计

| 症状 | 诊断 | 解法 |
|---|---|---|
| 同一批病人/动物在不同条件/时间点重复采样 | paired / 重复测量 | `--paired-by <受试者列>`（metadata 需有该列）→ 强制 limma + duplicateCorrelation。见 `examples/3_*`；[详情](paired-and-batch.md) |
| 样本分两批测序 / 两个中心 / 两次建库 | 批次效应 | `--batch <批次列>`：进 design 公式 + QC 图按批次着色。**先跑不加批次的 QC**，PCA 上批次聚团明显再加。[详情](paired-and-batch.md) |
| 每组只有 1 个样本 | 无生物学重复 | 自动降级 limma-trend 探索模式：只出 fold change（p=NA），REPORT 顶部显著警告。**不可用于结论**。[详情](no-replicates.md) |
| 组数 > 4，想全配对比较 | contrast 上限 | `--pairwise-max N`（如 6 组全配对设 6）。见 `examples/4_*`；[详情](multi-group-and-contrasts.md) |
| 只想比其中几组（如只看 young 组） | contrast 子集 | `--contrasts "KO_Young vs WT_Young, KO_Aged vs WT_Aged"` |
| 交互作用 / 连续变量（年龄、剂量、时间点）/ 节律设计 | 多因子设计 | 超出 skill 自动范围：属于真正的建模决策。让 agent 基于 `scripts/02_de_*.R` 现场定制 design 公式，或先做分层两两比较。[详情](multi-group-and-contrasts.md) |

## 3. 物种与基因 ID

| 症状 | 诊断 | 解法 |
|---|---|---|
| 行名是重复出现的基因名（symbol 矩阵） | 多探针/多转录本同一 symbol | **自动**：按均值聚合并警告（counts 会四舍五回整数保住引擎选择） |
| 大鼠数据 | rat | `--organism rat`（org.Rn.eg.db） |
| 果蝇/斑马鱼/猪等其它有 OrgDb 的物种 | 任意模式物种 | `--orgdb org.Dm.eg.db`（换成对应包名） |
| 非模式物种，没有 OrgDb | 无注释包 | `--gene-map <两列 CSV>`（id,symbol）。混合矩阵拆出的 `gene_annotation.csv` 可直接用。见 `examples/2_*` 联动技巧 |
| OrgDb 没装 / 网络装不上 | 缺注释包 | 不报错：保留原 ID 继续跑；或装 `resources/` 里的离线包 |

## 4. 运行中与结果

| 症状 | 诊断 | 解法 |
|---|---|---|
| QC 报告里出现 "Suspected outlier samples" | 某样本与同组重复相关性 < 0.8 | **只看不动**。你人工确认它确实坏了（PCA 飞点、建库失败记录）后，用 `--exclude-samples s1,s2` 重跑；pipeline 永不自动剔除 |
| 某 R 阶段在中文/空格路径下神秘失败 | 路径编码坑 | 把输入复制到纯 ASCII 临时路径重跑（体检 stage 会提前警告） |
| R 包缺失报错 | 依赖门 | 重跑加 `--install-deps` 让流程自装；或手动 miniconda/BiocManager；或用 `resources/r-deps/` 离线仓 |
| DESeq2 vst 报错 "less than 'nsub' rows" | 基因数 < 1000（靶向 panel/子集矩阵） | **自动**：回退 rlog |
| 结果想复核这次到底怎么跑的 | 复现 | 输出目录的 `run_metadata.json`：引擎、全部参数、输入统计、版本、时间戳 |

## 5. 明确不做的

- FASTQ/SRA/BAM 起步的比对定量（上游见 [downloading-from-GEO.md](downloading-from-GEO.md) 与实验室流程）
- 芯片 CEL 原始数据处理
- 自动剔除 outlier 样本
- 交互作用/连续协变量/节律的自动建模（现场定制，见 §2 末行）
