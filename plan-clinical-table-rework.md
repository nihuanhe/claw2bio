# Plan v2：clinical-table 全表管线（手稿 Table 1/2 + S1–S8 共 10 张）

日期：2026-09-16 ｜ 状态：**已核准并执行完毕（2026-09-16）** ｜ 取代 v1（v1 已完成部分保留）

> 注（2026-09-17）：全部表格与脚本名已按 plan-clinical-table-rename.md 换代为
> Table 1–10（table1_baseline.R … table10_plasmid_replicons.R）。本文的
> Table 1/2 + S1–S8 编号与脚本名为改名前的历史记录，映射关系见换代 plan。

## 用户需求（原话要点）

手稿 `main-20260905_revised.md` + `supplement-20260905_revised.md` 里所有 Table 都要能做出来；原始数据 = 两个患者 CSV，脱敏后使用；以 `代码操作-260708-完整复现与复用.md` 里的代码为基础**尽可能少地修改**，适配网站用户情景；网站每个 Table 出一张 PNG。

## 表格清单（10 张）

| 表 | 内容 | 输入 | 脚本 |
|---|---|---|---|
| Table 1 | 两队列基线（67 vs 72） | 双 CSV | table1.R |
| Table 2 | Firth 惩罚逻辑回归（9 协变量） | 双 CSV | table2.R（R 包 logistf） |
| S1 | 额外 β-内酰胺酶基因组合 × 碳青霉烯酶组 | CRE | tableS1.R |
| S2 | 物种-ST 组合 × 碳青霉烯酶组（46 行） | CRE | tableS2.R |
| S3 | 磺胺耐药基因组合 × 碳青霉烯酶组 | CRE | tableS3.R |
| S4 | 基础疾病 × CRE 基因型 | CRE | tableS4.R |
| S5 | 侵入操作/白蛋白/住院天数 × CRE 基因型 | CRE | tableS5.R |
| S6 | CRE vs CSE 单因素分析（30 行） | 双 CSV | tableS6.R |
| S7 | 菌株测序质量表（67 行，独立 CSV） | CRE | make_table_s7.py |
| S8 | 质粒复制子携带 × 碳青霉烯酶组（47 行） | CRE | tableS8.R |

管线：9 个 R 脚本按序填充 `Table-all.md`（218 行骨架）+ 各自 CSV；S7 独立 python 生成。

## 关键设计决策（推荐答案，请一并核准）

1. **最小 diff 复用**：9 个 R 脚本 + make_table_s7.py + Table-all.md 骨架**逐字拷贝**入 skill（`figure-generation/clinical-table/scripts/pipeline/` + `examples/pipeline/`），每文件头部加 `[改自 … 仅改动：…]` 清单（沿 phylo-tree 先例）。
2. **脱敏规则 v2**（使脚本能原样跑通的唯一可行方案）：
   - 删：**Patient_ID、Barcode**（人直接标识符）；
   - 留：**Assembly 菌株号**（GSA 公开存款号，非人标识符，S2/S7/S8 行键必需）+ 全部临床列 + 菌株基因组列（Bla_Carb/ESBL/磺胺/ST/species/复制子块/组装指标——这些是菌株特征，手稿补充材料本来就全文发表）；
   - 保留原始列名与 69 行结构（含 2 空行），脚本内部过滤逻辑零改动；
   - **S7 输出删 Patient_ID 列**（1 行 diff）；任何脚本若引用 Patient_ID/Barcode，做最小修补并在头部注明。
3. **进仓文件**：脱敏版 `clinical_data_CRE_67_patients.csv`（约 90 列→删 2 列）+ CSE 版进 `examples/input/pipeline/`；Table-all.md 骨架进仓；填数版进 examples/output。菌株基因组数据=手稿已发表内容，无患者级新增泄露。
4. **双引擎并存**：python 引擎（clinical_table.py，通用两组基线）保留现状；R 管线作为"手稿级全表套件"展示。网站 10 张 PNG 全部以 **R 管线填数版**为源（手稿排版忠实），现有 table1_CRE_vs_CSE.png 由 R 版 Table 1 替换。

## 执行步骤

1. 抽取：从复现文档 §3.6/§4.2–4.11 拷出骨架+9R+1py → pipeline/，加改动头注释（Rscript 路径注释中性化）。
2. 脱敏 CSV 生成：prepare 脚本加 `--keep-assembly` 模式（或新脚本）产出两份脱敏 CSV；grep 全部脚本确认 Patient_ID/Barcode 引用点并最小修补。
3. 本地跑通：检查 logistf 包（缺则装）；`table1→table2→S1..S6→S8`（Rscript 全路径）+ S7；验证 §9.2 十行锚点逐格一致 + Table-all 填数版 218 行。
4. 渲染：render_table_png.py v3——从填数版 Table-all.md 渲 9 张 + S7 CSV 渲 1 张，输出 `public/skills/clinical-table/`（table1/table2/S1..S8.png）。
5. 网站：双语教程页选择器扩为 10 表（图注用手稿表题）+ 快速上手补 R 管线一节；首页卡图换 R 版 Table 1；skills/index 文案改"10 张手稿级表"。
6. 文档：SKILL.md/README 增"Full manuscript table suite (R pipeline)"节（含脱敏声明 v2、logistf 依赖、运行顺序）；REPORT.md 更新。
7. 验证：npm run build 无死链 + OpenCLI 截图目检 10 表选择器；总 plan.md 增补 #48；AGENTS.md 行更新；脱敏扫描（Patient_ID/Barcode 全仓零命中）。

## 风险与预案

- logistf 未装 → 临时装（CRAN）；发布期离线仓补记。
- 脚本对被删列的隐性引用 → 步骤 2 grep 全量排查后再跑。
- S2 模板 46 行标签与数据集合强校验（脚本自带 stopifnot 式校验）→ 若脱敏改动破坏对齐，以原始 CSV 结构为准回退。
- Table-all.md 行协议脆弱（脚本按行号/标记替换）→ 只跑不改骨架。

## 执行记录与偏差（2026-09-16 实际执行）

- **脱敏规则 v2.1（偏差记录，用户对抗审查后拍板）**：决策 2/3 的"删 Patient_ID/Barcode"**未执行**，实际为**假名化数据逐字进仓零补丁**——(a) 两 CSV 的 Patient_ID/Sample/Barcode 本就是内部数字假名（无姓名/出生日期/住院号），Assembly 为 GSA 公开存款号，手稿补充材料已披露同样内容；(b) R 脚本按列位置切片（`d[,4:25]`），删列必错位，违反最小 diff 铁律；(c) "患者级微数据进公开仓"经对抗审查列为高危项，用户拍板**保持现状+显式声明**（假名化口径与准标识符残余风险已在 SKILL.md/README/examples 两 README/pipeline REPORT 四处披露）。"全仓零命中"扫描口径相应改为**姓名类标识符与私有路径零命中**（已通过）。
- 16 项 §9.2 锚点全部对账通过；证据：`examples/output/pipeline/REPORT.md`（锚点表）+ `website_check.png`（网站渲染目检截图；管线重跑留档经用户裁定跳过）。
- Windows Rscript 编码陷阱：UTF-8 中文注释被 GBK 解析致段错误 → 全部脚本头注释改英文（这正是"仅改动头注释"的实际内容），网站用户裸 `Rscript` 可跑。
