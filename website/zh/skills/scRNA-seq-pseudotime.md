# scRNA-seq 拟时序分析（monocle3）

> 一句话：在常规流程的注释结果上直接学分化轨迹——复用 Seurat 的 UMAP 和聚类 ID，monocle3 定起点、排拟时序、找拟时序相关基因。

::: info 获取本技能 · Get this skill
**方式 A —— 一键引导 prompt（推荐）**。复制下面这段，粘贴到你的 AI agent IDE：

```
请帮我安装 Claw2Bio 技能库中的 "scRNA-seq-pseudotime" 技能：
1. 从 GitHub 仓库 https://github.com/nihuanhe/claw2bio 只拉取 bioinformatics/sc_RNA_seq/scRNA-seq-pseudotime
   这一个文件夹（用 sparse checkout，不要克隆整库）。
2. 阅读其中的 SKILL.md 并注册该技能。
3. 运行 examples/ 里的示例验证环境，把输出的图给我看。
```

**方式 B —— 独立 zip 包**（约 16.6 MB，本站下载）：<https://claw2bio.site/downloads/scRNA-seq-pseudotime.zip>

**方式 C —— 全量示例数据**：已包含在方式 B 包内（同一个压缩包）。
:::

## 它能做什么

前提是先跑完 [scRNA-seq 常规流程](/zh/skills/scRNA-seq) 拿到 `annotated_seurat.rds`（本技能不做 QC / 聚类）。它复用已有的 UMAP 嵌入与 cluster ID，用 monocle3 学轨迹图，从你指定的起点（root cluster 或细胞类型标签）排出拟时序，并用 graph_test 找拟时序相关基因。真实示例（GSE234527，10,859 个细胞，以 cluster 0 为 root）全程约 11 分钟，找出 13,790 个拟时序相关基因（q < 0.05）。

![拟时序轨迹图](/skills/scRNA-seq-pseudotime/trajectory_by_pseudotime.png)

按拟时序着色的轨迹图——颜色越暖表示离起点越远（示例以 cluster 0 为 root）。

![按 cluster 着色的轨迹图](/skills/scRNA-seq-pseudotime/trajectory_by_cluster.png)

同一轨迹按 cluster 着色，便于确认轨迹走向与细胞类型的对应关系。

![拟时序基因趋势图](/skills/scRNA-seq-pseudotime/gene_HES4_on_trajectory.png)

graph_test 排名靠前的基因（真实示例为 HES4）在轨迹上的表达趋势，top-4 基因各出一张。

**起点选择是生物学决策**：技能拒绝在无 `--root-cluster` / `--root-label` 的情况下运行，会先打印 cluster → 标签对照表帮你选。

## 快速上手（30 秒）

```bash
cd bioinformatics/sc_RNA_seq/scRNA-seq-pseudotime
python scripts/run_pseudotime.py <annotated_seurat.rds> <output_dir> \
  --root-cluster 3            # 或 --root-label "Naive CD4 T"
```

先不带 root 跑一次，技能会打印 cluster → label 表后退出；也可以直接查主流程输出的 `annotation_per_cluster.csv`。

## 输入格式

- 常规流程输出的 `annotated_seurat.rds`（需要 `seurat_clusters`、UMAP reduction；按标签定根时需要 `cell_type_final`）。

## 输出文件

| 文件 | 内容 |
|---|---|
| `pseudotime_cds.rds` | 带拟时序的 monocle3 cell_data_set |
| `trajectory_by_pseudotime/cluster/group/sample.png` | 轨迹图组 |
| `pseudotime_genes.csv` | graph_test 全表（q < 0.05 为显著） |
| `gene_<X>_on_trajectory.png` | top-4 拟时序基因的趋势图 |
| `REPORT.md` / `pseudotime_summary.json` | 报告 + 机器可读摘要 |

## 参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--root-cluster` | — | 作为轨迹起点的 cluster id（二选一，必填） |
| `--root-label` | — | 作为起点的 `cell_type_final` 标签（二选一，必填） |
| `--subset-labels` | — | 先按标签圈定细胞类型再建轨迹 |
| `--no-graph-test` | 关 | 跳过较慢的 graph_test |
| `--cores` | 4 | graph_test 并行核数 |
| `--resume` / `--overwrite` | 关 | `--resume` 复用 `.checkpoint_cds_learned.rds`（跳过建 cds 与 learn_graph）；`--overwrite` 允许写入非空目录 |

## 常见问题

- **不知道该选哪个 root** → 不带 root 跑一次，看打印的对照表；root 是生物学判断，技能不替你决定。
- **learn_graph / graph_test 内存爆了** → 这两步是内存高峰；learn_graph 之后自动写
  `.checkpoint_cds_learned.rds`，崩溃后加 `--resume` 即可复用（跳过建 cds 与 learn_graph，
  不必重算）。运行正常结束时会自动删掉该检查点。
- **graph_test 太慢** → 加 `--no-graph-test` 只要轨迹，或 `--subset-labels` 缩小细胞范围。
- **为什么必须用技能自带脚本，不能让 AI 现写？**
  `scripts/` 里的是经过验证的路径：它们在示例数据上跑过，边界情况有文档记录。AI 现场生成的代码是
  "结果悄悄出错"的最常见来源。遇到没覆盖的情况，先改命令行参数；不够就复制脚本到临时目录做最小改动
  并说明改了什么；只有完全没有对应脚本时才允许新写，且新写后要回沉淀到 `scripts/`。

## 相关链接

- [GitHub 源码与 SKILL.md](https://github.com/nihuanhe/claw2bio/tree/main/bioinformatics/sc_RNA_seq/scRNA-seq-pseudotime)
- 相关技能：[scRNA-seq 常规流程](/zh/skills/scRNA-seq) · [虚拟敲除](/zh/skills/scRNA-seq-virtual-ko)
