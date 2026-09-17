# 案例 2 — GSE255223：混合矩阵（count + FPKM + 注释列混排）

## 输入

真实公开数据集 [GSE255223](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE255223)：
人颞叶癫痫（TLE）脑组织，TLE-HS vs TLE-nonHS，各 3 重复。

- `input/GSE255223_gene_expression_anno.xls.gz` — GEO 补充文件原样：一个文件里
  `gene_id`、9 列注释（gene_name/description/GO/KEGG/locus）、9 个 `*_FPKM` 列、
  9 个 `*_count` 列混在一起（历史上需要手工拆列才能分析）
- `input/sample_metadata.csv` — 6 个 "included" 样本；注意 `X15` 是 R `make.names`
  把原始样本名 `15` 加前缀毁掉的形态

## 测什么

体检 stage 的**混合矩阵自动拆解**全链路：

1. 保留 9 个 `*_count` 列，剥掉 `_count` 后缀；9 个 FPKM 列分离不用；
2. 9 列基因注释拆出存为 `gene_annotation.csv`（可回喂 `--gene-map`）；
3. 模糊匹配把矩阵列 `15` 对到 metadata 的 `X15`（撤销 make.names 毁名）；
4. 矩阵比 metadata 多 3 个样本（16/s5/s9，status 非 included）→ 按 metadata 定义的分析集排除。

## 运行

```bash
python scripts/run_rnaseq.py \
  "examples/2_example_GSE255223_mixed-count-FPKM-annotation/input/GSE255223_gene_expression_anno.xls.gz" \
  "examples/2_example_GSE255223_mixed-count-FPKM-annotation/input/sample_metadata.csv" \
  "examples/2_example_GSE255223_mixed-count-FPKM-annotation/output" \
  --control TLE-nonHS --organism human --overwrite
```

## 期望行为

1. 体检打印上述 6 条 [fixed]；组名带短横 `TLE-HS`/`TLE-nonHS` 正常工作。
2. 引擎：整数 + n=3 → **DESeq2**。
3. TLE-HS vs TLE-nonHS: **251 up / 274 down**。
4. 组名含短横 → 输出文件名消毒后正常（`DEG_TLE-HS_vs_TLE-nonHS.csv`，短横保留、空格才替换）。

## 联动技巧

跑完后用拆出的注释表做基因名转换（不依赖 OrgDb 网络查询）：

```bash
# 加 --gene-map examples/2_.../output/gene_annotation.csv 重跑，DEG 表 symbol 列 100% 映射
```
