# scRNA-seq-virtual-ko

虚拟敲除（scTenifoldKnk，PMID: 35510185）。**前提：先跑 `../scRNA-seq`
常规流程**，拿到 `annotated_seurat.rds` 后再来本 skill。

```bash
python scripts/run_virtual_ko.py <annotated_seurat.rds> <output_dir> --gene TP53
```

- `--subset-labels "某细胞类型"` 先圈定细胞群再建调控网络（推荐）；
- 产出 `<GENE>_diffRegulation.csv` + top20 条形图 + Z 值散点图 + `virtual_ko_summary.json`
  + `REPORT.md`；
- **规模与耗时（16 GB / 12 核 Windows 实测，真实 10,859 细胞对象，敲 ACTA2）**：
  `2000×3×500` = **90 min** → 58 个显著基因；`2000×5×500` = **2 h** → 54 个显著基因
  （两者重合 41 个）。**建议 `--nc-nnet` 不超过 5**：包默认的 10 在本数据上跑完 2 h 建网络后
  死在 `manifoldAlignment`（`E$vectors[, E$values > 1e-08] : incorrect number of dimensions`），
  属 scTenifoldKnk 内部数值退化，CLI 无法绕开；
- **无断点、不可续跑**（scTenifoldKnk 是单次不可中断调用）：跑之前确认机器不会休眠，否则前功尽弃。
  若驱动进程意外退出、但 R 已经把结果写出来，可用 **`--report-only`** 只重生成 `REPORT.md`（不重算）；
- 结果是**计算预测**，需实验验证；目标基因表达太低时结果不可靠（summary 里给了表达 rank）；
- 详见 `SKILL.md`。

## 示例

| 示例 | 输入 | 说明 |
|---|---|---|
| `examples/1_smoke/` | 主流程 example 1 的降采样产物（~1820 细胞） | 分钟级回归（500 基因 × 3 nets，敲 ADIRF） |
| `examples/2_real_GSE234527/` | 真实 `annotated_seurat.rds`（10,859 细胞，仓库外/COS） | 敲 **ACTA2**（表达 rank 23/17655）：`2000×3×500` 出 **58 个显著基因**，top 命中 **MYLK / TPM1 / DES / CNN1**（经典平滑肌共调控基因，生物学合理） |
