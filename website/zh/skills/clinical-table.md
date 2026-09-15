# 临床统计表

> 一句话：患者级 CSV 进，发表级三线表出——基线特征表、相关性矩阵、Cox 回归、OR 汇总。

::: info 获取本技能 · Get this skill
**方式 A —— 一键引导 prompt（推荐）**。复制下面这段，粘贴到你的 AI agent IDE：

```
请帮我安装 Claw2Bio 技能库中的 "clinical-table" 技能：
1. 从 GitHub 仓库 https://github.com/claw2bio/claw2bio 只拉取 figure-generation/clinical-table
   这一个文件夹（用 sparse checkout，不要克隆整库）。
2. 阅读其中的 SKILL.md 并注册该技能。
3. 运行 examples/ 里的示例验证环境，把输出的表格给我看。
```

**方式 B —— 独立 zip 包**（几 MB，腾讯 COS 直链）：*网站上线时提供*。

**方式 C —— 全量示例数据**（COS 按 skill 分目录）：*网站上线时提供*。
:::

## 它能做什么

1. **基线特征表**——标志物 high/low 分组 × 年龄、性别、BMI、肿瘤分化、癌症分期，输出 n (%) 和 p 值。
2. **相关性矩阵**——标志物之间的 Pearson + Spearman 相关。
3. **Cox 回归**——有 `survival_time` / `survival_event` 列时自动输出单因素 + 多因素表。
4. **OR 汇总**——Fisher 精确检验 2×2 表的 OR (95% CI)。

输出为 Markdown 三线表，可用 Pandoc 一键转 DOCX（`pandoc output.md -o output.docx`）。

## 快速上手（30 秒）

```bash
cd figure-generation/clinical-table
pip install pandas numpy scipy statsmodels
python scripts/clinical_table.py examples/input/demo_patients.csv examples/output/clinical_tables.md
```

## 输入格式

患者级 CSV。必需：标志物连续值列（如 `HAMA`）、`Sex`、`Age`（或 `Age-`）、`BMI`（或 `BMI-`）、`Tumor differentiation`、`Cancer stage`。分组列 `<标志物>--` 取 `high`/`low`——也可以让技能自动分组：

```bash
# 按中位数自动分组
python scripts/clinical_table.py input.csv output.md --auto-group
# 指定 cutoff 分组
python scripts/clinical_table.py input.csv output.md --auto-group --group-cutoffs '{"HAMA":29}'
```

标志物列名可用 `--config config.json` 自定义（见脚本内 `DEFAULT_CONFIG`）。

## 输出文件

| 文件 | 内容 |
|---|---|
| `clinical_tables.md` | 全部三线表（Markdown 格式） |

## 常见问题

- **缺少分组列** → 加 `--auto-group`。
- **没有 Cox 表** → 只有同时存在 `survival_time` 和 `survival_event` 列才会生成。
- **lifelines 装不上** → 不需要装；Cox 用 statsmodels PHReg 实现。

## 相关链接

- [GitHub 源码与 SKILL.md](https://github.com/claw2bio/claw2bio/tree/main/figure-generation/clinical-table)
- 相关技能：[分组柱状图](/zh/skills/barplot)
