# 临床统计表

> 一句话：患者级 CSV 进，发表级三线表出——本技能已用一篇真实 CRE/CSE 队列研究的**全部 10 张表格**（Table 1–10 = 手稿 Table 1/2 + 补充材料 S1–S8）完整验证：基线对比、Firth 回归、基因型交叉表、单因素分析、测序质量表。

::: info 获取本技能 · Get this skill
**方式 A —— 一键引导 prompt（推荐）**。复制下面这段，粘贴到你的 AI agent IDE：

```
请帮我安装 Claw2Bio 技能库中的 "clinical-table" 技能：
1. 从 GitHub 仓库 https://github.com/claw2bio/claw2bio 只拉取 figure-generation/clinical-table
   这一个文件夹（用 sparse checkout，不要克隆整库）。
2. 阅读其中的 SKILL.md 并注册该技能。
3. 运行 examples/ 里的示例验证环境，把输出的表格给我看。
```

**方式 B —— 独立 zip 包**（几 MB，腾讯 COS 直链）：*打包中，即将上线*。

**方式 C —— 全量示例数据**（COS 按 skill 分目录）：*打包中，即将上线*。
:::

## 它能做什么

**通用引擎（Python，开箱即用）**：两队列基线特征表——分类变量 n (%) + Pearson χ²（期望 <5 自动 Fisher）+ 连续变量 mean±SD + Student t；另支持相关性矩阵、Cox 回归、OR 汇总。

**手稿级全表套件（R 管线）**：`scripts/pipeline/` 内 9 个 R 脚本 + 1 个 Python 脚本，按序运行即从患者级 CSV 复现一篇论文的**全套表格**（Table 1–10 = 手稿正文 Table 1/2 + 补充材料 S1–S8）——基线、Firth 惩罚逻辑回归、耐药基因/序列型/质粒复制子交叉表、单因素分析、菌株测序质量表。

输出为 Markdown 三线表，可用 Pandoc 一键转 DOCX（`pandoc output.md -o output.docx`）。

## 示例输出（真实队列研究全套 10 张表，点击切换）

以下 10 张图全部由本技能 R 管线对**真实 CRE/CSE 队列研究**（投稿中）的假名化患者级数据真实产出，每个数字均与作者独立复核脚本逐格对账：

<div class="table-picker">
  <input type="radio" name="ct-tables" id="ct-t1" checked>
  <input type="radio" name="ct-tables" id="ct-t2">
  <input type="radio" name="ct-tables" id="ct-t3">
  <input type="radio" name="ct-tables" id="ct-t4">
  <input type="radio" name="ct-tables" id="ct-t5">
  <input type="radio" name="ct-tables" id="ct-t6">
  <input type="radio" name="ct-tables" id="ct-t7">
  <input type="radio" name="ct-tables" id="ct-t8">
  <input type="radio" name="ct-tables" id="ct-t9">
  <input type="radio" name="ct-tables" id="ct-t10">
  <label for="ct-t1">Table 1 · Baseline</label>
  <label for="ct-t2">Table 2 · Firth 回归</label>
  <label for="ct-t3">Table 3 · β-内酰胺酶</label>
  <label for="ct-t4">Table 4 · 序列型</label>
  <label for="ct-t5">Table 5 · 磺胺基因</label>
  <label for="ct-t6">Table 6 · 疾病×基因型</label>
  <label for="ct-t7">Table 7 · 操作×基因型</label>
  <label for="ct-t8">Table 8 · 单因素分析</label>
  <label for="ct-t9">Table 9 · 测序质量</label>
  <label for="ct-t10">Table 10 · 质粒复制子</label>
  <div class="ct-panel ct-p1">
    <img src="/skills/clinical-table/table1_baseline.png" alt="Table 1 Baseline 基线特征">
    <p class="ct-cap">Table 1 · Baseline（= 手稿 Table 1）· CRE (n=67) vs CSE (n=72) 基线特征：分类变量 χ²/Fisher + 连续变量 Student t。年龄 69.16±10.43 vs 63.18±12.56（p=0.0028）；性别 p=0.2907。住院时长/机械通气等与 CRE 相关的因素见 Table 2 与 Table 8。</p>
  </div>
  <div class="ct-panel ct-p2">
    <img src="/skills/clinical-table/table2_firth.png" alt="Table 2 Firth 惩罚逻辑回归">
    <p class="ct-cap">Table 2 · Firth（= 手稿 Table 2）· Firth 惩罚多因素逻辑回归（CRE vs CSE，9 个协变量）：小样本罕见事件稳健估计，OR (95% CI) 逐行输出。</p>
  </div>
  <div class="ct-panel ct-p3">
    <img src="/skills/clinical-table/table3_esbl_genes.png" alt="Table 3 ESBL 基因组合">
    <p class="ct-cap">Table 3 · ESBL genes（= 手稿 Supplemental Table S1）· CRE 菌株额外 β-内酰胺酶基因组合 × 碳青霉烯酶组（n (%)，Kleborate 标志已剥离）。</p>
  </div>
  <div class="ct-panel ct-p4">
    <img src="/skills/clinical-table/table4_sequence_types.png" alt="Table 4 序列型">
    <p class="ct-cap">Table 4 · Sequence types（= 手稿 Supplemental Table S2）· CRE 菌株物种–ST 组合 × 碳青霉烯酶组（46 行，每物种未分型行单列）。</p>
  </div>
  <div class="ct-panel ct-p5">
    <img src="/skills/clinical-table/table5_sul_genes.png" alt="Table 5 磺胺耐药基因">
    <p class="ct-cap">Table 5 · sul genes（= 手稿 Supplemental Table S3）· CRE 菌株磺胺耐药基因（sul）组合 × 碳青霉烯酶组。</p>
  </div>
  <div class="ct-panel ct-p6">
    <img src="/skills/clinical-table/table6_disease_genotype.png" alt="Table 6 基础疾病×基因型">
    <p class="ct-cap">Table 6 · Disease × genotype（= 手稿 Supplemental Table S4）· 基础疾病分布 × CRE 基因型（糖尿病/脑血管病/肺部疾病）。</p>
  </div>
  <div class="ct-panel ct-p7">
    <img src="/skills/clinical-table/table7_procedures_genotype.png" alt="Table 7 侵入操作×基因型">
    <p class="ct-cap">Table 7 · Procedures × genotype（= 手稿 Supplemental Table S5）· 侵入操作、白蛋白水平、住院时长 × CRE 基因型。</p>
  </div>
  <div class="ct-panel ct-p8">
    <img src="/skills/clinical-table/table8_univariate.png" alt="Table 8 单因素分析">
    <p class="ct-cap">Table 8 · Univariate（= 手稿 Supplemental Table S6）· CRE 感染相关因素单因素分析（30 行，χ²/Fisher 自动切换）。</p>
  </div>
  <div class="ct-panel ct-p9">
    <img src="/skills/clinical-table/table9_sequencing_quality.png" alt="Table 9 测序质量">
    <p class="ct-cap">Table 9 · Sequencing quality（= 手稿 Supplemental Table S7）· 67 株 CRE 测序质量指标（contigs/N50/GC/数据量/测序深度，独立 CSV 输出）。</p>
  </div>
  <div class="ct-panel ct-p10">
    <img src="/skills/clinical-table/table10_plasmid_replicons.png" alt="Table 10 质粒复制子">
    <p class="ct-cap">Table 10 · Plasmid replicons（= 手稿 Supplemental Table S8）· 质粒复制子携带 × 碳青霉烯酶组（Kleborate/PlasmidFinder，47 行）。</p>
  </div>
</div>

## 快速上手（30 秒，通用引擎）

```bash
cd figure-generation/clinical-table
pip install pandas numpy scipy statsmodels
python scripts/clinical_table.py examples/input/clinical_cohorts.csv examples/output/clinical_tables.md
```

期望锚点：`CRE n=67, CSE n=72`；Age `69.16±10.43 vs 63.18±12.56, p=0.003`。

## 快速上手（R 管线，复现全套手稿表格）

需要 R（含 `logistf` 包，Table 2 用）。把两份假名化 CSV + `Table-all.md` 骨架放同一目录，按序运行：

```bash
cd examples/input/pipeline   # 两份 CSV 与 Table-all.md 骨架都在这里
Rscript ../../scripts/pipeline/table1_baseline.R    # 填充 Table-all.md 的 Table 1 区块
Rscript ../../scripts/pipeline/table2_firth.R       # Firth 回归
Rscript ../../scripts/pipeline/table3_esbl_genes.R  # 之后 Table 3–8、10 依序
python ../../scripts/pipeline/make_table9_sequencing_quality.py   # Table 9 独立生成 CSV
```

每个脚本：读 CSV → 计算 → 回填 `Table-all.md` 对应区块 → 输出独立 CSV。全表锚点见 `examples/output/pipeline/REPORT.md`。

## 输入格式

- **通用引擎**：患者级 CSV（一行一个患者）：两水平分组列（默认 `cohort`）+ 0/1 二分类列 + 连续列；变量清单在 `DEFAULT_CONFIG` 或 `--config your.json`。
- **R 管线**：两个队列各一份 CSV（列结构见 examples/input/pipeline/），示例数据即假名化真实数据——处理您自己的数据时按相同列结构准备即可。

## 输出文件

| 文件 | 内容 |
|---|---|
| `clinical_tables.md`（通用引擎） | 基线/相关性/Cox/OR 三线表 |
| `Table-all.md`（R 管线） | 填数后的全套手稿表格（224 行） |
| `table1_baseline.csv` … `table10_plasmid_replicons.csv` | 每张表的独立 CSV（Table 9 = `table9_sequencing_quality.csv`） |

## 常见问题

- **p 值与 SPSS 对不上** → 本技能 χ² 不做 Yates 连续性校正（发表 Table 1 惯例）。
- **R 脚本在 Windows 上崩** → 必须用英文注释版本（仓库内已是）；如自行修改注释，保存为 UTF-8 无 BOM，或运行时加 `--encoding=utf-8`。
- **logistf 未安装** → `install.packages("logistf")`。
- **连续变量没进基线表** → 加进 `DEFAULT_CONFIG` 的 `baseline_continuous_vars`。
- **没有 Cox 表** → 只有同时存在 `survival_time` 和 `survival_event` 列才会生成。

## 相关链接

- [GitHub 源码与 SKILL.md](https://github.com/claw2bio/claw2bio/tree/main/figure-generation/clinical-table)
- 相关技能：[KM 生存曲线](/zh/skills/survival-curve)
