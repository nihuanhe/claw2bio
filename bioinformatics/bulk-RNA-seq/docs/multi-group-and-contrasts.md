# 多组与 contrast 策略

## 默认行为

- 每组 vs 对照（对照 = `--control` 或 metadata 第一组）；
- 组数 ≤ `--pairwise-max`（默认 4）时追加全配对（4 组 = 6 个 contrasts）。

## 常见调整

| 需求 | 做法 |
|---|---|
| 6 组也全配对 | `--pairwise-max 6`（30 个 contrasts，运行变久） |
| 只比子集（如只看 young） | `--contrasts "KO_Young vs WT_Young, KO_Aged vs WT_Aged"` |
| 组名带短横/空格 | 无需担心：contrast 按数值矩阵构造，不经字符串解析；`--contrasts` 语法用 `A vs B`（两侧空格），组名里的短横不影响 |

## 超出自动范围的设计（现场定制）

以下属于真正的统计建模决策，skill 不自动处理，让 agent 基于 `scripts/02_de_*.R`
改 design 公式后跑：

- **交互作用**：如 genotype × age（`~genotype*age`），关注交互项系数；
- **连续协变量**：年龄、剂量、时间（ZT 点）作为数值变量而非分组；
- **节律分析**：cosinor/JTK 类方法，与差异表达框架不同；
- **多层 blocking**：paired + batch 叠加且 subject 嵌套于 batch 之外等复杂结构。

务实的替代：先按分层做两两比较（`--contrasts` 显式列出），把交互作用问题转化为
若干可解释的两组对比；确需交互项时再定制。

活例：`examples/4_example_GSE214514_multi-group-circadian`（4 组全配对；
该数据的基因型×年龄交互若关心需定制）。
