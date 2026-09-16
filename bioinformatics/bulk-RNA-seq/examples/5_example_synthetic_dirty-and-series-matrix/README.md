# 案例 5 — 合成脏数据 + series_matrix（体检 stage 综合压力测试）

## 输入（两个互不相干的合成小数据集）

**(a) `dirty_counts.csv` + `dirty_meta.csv`** — 202 行 × 4 样本，一次集齐 7 种坑：

| 坑 | 具体形态 |
|---|---|
| 样本名后缀 | 列名 `15_count`、`s29_count` … |
| FPKM 列混入 | 另有 4 个 `*_FPKM` 列 |
| 注释列混入 | `gene_name`、`GO_term` 两列非数值列 |
| 重复基因 symbol | `ACTB` 出现两次 |
| 负值 | 一个 -5 |
| metadata 列名不标准 | `sample_id` / `condition` |
| 数字开头样本名 | `15`（R `make.names` 会加成 `X15`） |

**(b) `synth_series_matrix.txt` + `series_meta.csv`** — 仿 GEO series_matrix 格式
（`!` 注释头 + `"ID_REF"` 表头行 + `!series_matrix_table_begin/end` 包裹），
300 探针 × 4 样本的微阵列式 log 值。

## 测什么

体检 stage 的自动修复全覆盖 + series_matrix 解析。合成数据的好处：坑的位置已知，
任何一条 [fixed] 消失都意味着回归。

## 运行

```bash
# (a) 脏数据综合
python scripts/run_rnaseq.py \
  examples/5_example_synthetic_dirty-and-series-matrix/input/dirty_counts.csv \
  examples/5_example_synthetic_dirty-and-series-matrix/input/dirty_meta.csv \
  examples/5_example_synthetic_dirty-and-series-matrix/output_dirty \
  --control TLE-nonHS --organism human --overwrite

# (b) series_matrix 解析
python scripts/run_rnaseq.py \
  examples/5_example_synthetic_dirty-and-series-matrix/input/synth_series_matrix.txt \
  examples/5_example_synthetic_dirty-and-series-matrix/input/series_meta.csv \
  examples/5_example_synthetic_dirty-and-series-matrix/output_series \
  --control Ctrl --organism human --overwrite
```

## 期望行为

- (a)：7 条 [fixed] + 1 条数字样本名 [warn]；重复 symbol 按均值合并后**仍为整数**
  → DESeq2 分支（4 up / 2 down，随机数据无生物学含义）。基因数 < 1000 时
  vst 自动回退 rlog（打印 fallback 信息）。
- (b)：1 条 [fixed]（series_matrix 重存为普通表）→ 非整数 → limma-trend 完成全流程。
