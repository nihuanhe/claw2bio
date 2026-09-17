# Paired 与 batch 设计

## Paired / 重复测量（`--paired-by <subject 列>`）

**什么时候用**：同一生物学个体（病人、小鼠、细胞系批次）在多个条件/时间点被重复采样，
样本间存在个体内相关。典型信号：metadata 里能写出"哪几个样本来自同一个体"。

**用法**：metadata 加一列 subject（如 `Subject1`），运行时：

```bash
python scripts/run_rnaseq.py counts.csv meta.csv out --control health --paired-by subject
```

**管线内部行为**：

1. 引擎强制 limma 系（整数 counts → edgeR+voom；非整数 → limma-trend），
   用 `duplicateCorrelation(block = subject)` 估计个体内相关。理由框会打印；
   想强制回 DESeq2 用 `--engine deseq2`（design 变 `~subject+group`，
   subject 占自由度，小样本 paired 时统计效率明显低于 duplicateCorrelation——
   开发期模拟：duplicateCorrelation 150/150 检出 vs DESeq2 固定效应 137/150）。
2. QC/输出流程不变。

**判断清单**：

- subject 列每个水平应出现在 ≥2 个样本里，否则配对无意义；
- 如果 subject 与 group 完全混淆（每个 subject 只属于一个组），paired 无意义——不要用；
- consensus correlation 接近 0 说明个体内相关弱，paired 与不配对差别不大。

活例：`examples/3_example_GSE167882_paired-symbol-logcpm-human`。

## Batch 效应（`--batch <批次列>`）

**什么时候用**：样本分多个测序批次/中心/建库批次，且批次不与分组完全混淆
（每个批次里最好每组都有样本）。

**用法**：metadata 加 batch 列，运行时加 `--batch seqbatch`。

**管线内部行为**：

- DESeq2：design 变 `~batch+group`；edgeR/limma：`model.matrix(~0+group+batch)`；
- QC PCA 按 batch 画点形、相关性热图加 batch 注释条，QC_summary 打印 batch×group 列联表。

**判断清单（重要）**：

1. **先不加 batch 跑一次看 PCA**：批次效应明显（样本按批次而非分组聚团）才加。
   批次本就不明显时加 batch 白吃自由度。
2. **绝不自动 ComBat/removeBatchEffect**：隐性矫正会把真实生物学差异一起抹掉；
   进 design 公式（本 skill 的做法）是差异分析中统计上正确的处理方式。
   removeBatchEffect 只用于可视化，需要时让 agent 现场加。
3. batch 与 group 完全混淆（所有对照在批次 1、所有处理在批次 2）时，
   批次与处理**不可区分**，任何方法都救不了——如实报告局限。
