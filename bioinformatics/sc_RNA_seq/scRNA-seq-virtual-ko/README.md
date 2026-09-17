# scRNA-seq-virtual-ko

虚拟敲除（scTenifoldKnk，PMID: 35510185）。**前提：先跑 `../scRNA-seq`
常规流程**，拿到 `annotated_seurat.rds` 后再来本 skill。

```bash
python scripts/run_virtual_ko.py <annotated_seurat.rds> <output_dir> --gene TP53
```

- `--subset-labels "某细胞类型"` 先圈定细胞群再建调控网络（推荐）；
- 产出 `<GENE>_diffRegulation.csv` + top20 条形图 + Z 值散点图；
- 大对象很慢：`--nfeatures` / `--nc-nnet` 控制规模；结果是计算预测，需实验验证；
- **无断点、不可续跑**（scTenifoldKnk 是单次不可中断调用）：跑之前确认机器不会休眠，
  否则前功尽弃；
- 详见 `SKILL.md`；示例 `examples/1_smoke/` 吃主流程 example 1 的产出。
