# 科研流程技能库 — 项目共识与架构决策

> 基于 2026-07-24 grill-me 逐层追问达成。本文档供后续 AI 上下文恢复使用。

---

## 1. 用户与运行环境

| 项目 | 决策 |
|------|------|
| 用户范围 | 单人使用，跨 ~10 台 Windows 11 机器 |
| 同步方案 | Git 私有仓库（每台机器 `git clone/pull/push`） |
| 环境一致性 | 所有机器统一 Python 3.13 managed venv + R 安装 |

---

## 2. 技术架构

| 项目 | 决策 |
|------|------|
| 主语言 | Python 为主，R 通过 subprocess/rpy2 桥接 |
| 接口形态 | WorkBuddy Skill 为主接口（对话调用），底层代码模块化在 `scripts/` |
| 调用模式 | **Adapter 模式**："不修改原始代码"——Skill 复制原代码到临时目录 → 生成适配代码 → 虚拟环境运行 → 产出结果 |

### 脚本复用铁律

构建任何 skill 时，优先复用既有自有脚本（`scripts/` 或已有 repo 中的可用代码）；**禁止 AI 在存在可用脚本的情况下重新实现一遍**。仅当确实无对应脚本时才允许新写，且新写后须沉淀为可复用脚本（纳入 `scripts/` + `examples/`），不得把「一次性生成代码」当作交付物。

**执行时同样适用**——本条不只约束"建 skill 时"：AI agent 运行时同样不得另写脚本，必须优先原样运行 `scripts/` 中已有脚本（只改命令行参数）；确需改动时复制到临时目录做最小改动并说明改了什么；只有完全没有对应脚本时才允许新写，且新写后回沉淀到 `scripts/`。

---

## 3. 仓库组织

### 顶层：6 个研究阶段

```
D:\科研流程技能库\
├── 1_文献调研与阅读 (literature)/
│   ├── paper-downloader/                ← 文献下载工具 ✅
│   └── reference-inserter/              ← 参考文献插入（README 待完善）
├── 2_实验设计与方案 (experiment-design)/ ← 空，待建
├── 3_实验数据处理 (experiment-data)/
│   ├── IF-免疫荧光/                      ← 免疫荧光分析（目录占位）
│   ├── OFT/                             ← 旷场实验全流程三步骤 ✅
│   ├── WB-imageJ-定量/                   ← WB 定量分析（目录占位）
│   ├── qpcr-mtdna/                      ← mtDNA qPCR ΔCt + 柱状图 ✅
│   └── qpcr-mrna/                       ← 通用 mRNA qPCR ΔΔCt + 柱状图 ✅
├── 4_生信数据分析 (bioinformatics)/      ← 空，待建
├── 5_图表生成 (figure-generation)/
│   ├── barplot/                         ← 通用柱状图 ✅
│   ├── brain-if-atlas-annotate/         ← 脑片荧光图像 × 脑图谱配准（目录占位）
│   ├── clinical-table/                  ← 临床三线表 ✅
│   └── compress-image/                  ← 保持清晰度压缩图像体积（TIFF → JPEG/PNG/压缩 TIFF） ✅
├── 6_论文撰写 (paper-writing)/
│   ├── 1-加载后改写适合转docx的md文件/   ← Markdown 预处理（目录占位）
│   └── 2-sci-paper论文代写流水线/        ← SCI 论文代写润色流水线 ✅
└── 7_其他(other)/
    └── md2html-resume/                  ← Markdown 简历转自包含 HTML ✅
└── 项目共识与架构决策.md
```

### 粒度原则

- **每个数据类型一个独立 Git repo**（Micro-Repo 模式）
- 仓库小 → 好理解、好 debug、好维护版本
- 共用代码暂不抽取，等实际跨 repo 重复后再建 `shared-utils`

### 每个 Repo 必须包含 examples/ 目录

> 这条规则来自 OFT 项目实践——换台电脑或隔几个月回来，看到 examples/ 立刻知道怎么用。

```
<repo>/
├── SKILL.md              ← WorkBuddy 对话触发
├── README.md             ← 人类阅读的说明
├── scripts/              ← 核心 Python 脚本
├── examples/
│   ├── README.md         ← 命令行示例 + 参数说明
│   ├── input/            ← 示例输入文件（小样本真实数据）
│   └── output/           ← 示例输出文件（工具跑 input 后的结果）
└── .gitignore            ← 排除 __pycache__/、*.pyc
```

**规则：**
1. `examples/input/` 放工具的最小可运行样本数据（能证明工具跑通即可，不用全量数据）
2. `examples/output/` 放该 input 跑出来的实际结果
3. 多步骤管道（如 OFT）每个独立步骤各带自己的 examples/
4. 数据采集类工具（如 tracker）可不设 examples/，其校准文档和 record.csv 即为参考

### 已规划的 Repo（启动批次）

| 阶段 | Repo 名称 | 功能 | 状态 |
|------|-----------|------|------|
| 1-文献调研 | `paper-downloader` | 文献下载工具 | ✅ 已完成 |
| 1-文献调研 | `reference-inserter` | 参考文献插入 | 🟡 README 待完善 |
| 3-实验数据处理 | `IF-免疫荧光` | 免疫荧光图像分析 | ⚪ 目录占位 |
| 3-实验数据处理 | `OFT/` | 旷场实验全流程三步骤 | ✅ 已完成 |
| 3-实验数据处理 | `WB-imageJ-定量` | Western Blot ImageJ 定量 | ⚪ 目录占位 |
| 3-实验数据处理 | `qpcr-mtdna` | mtDNA qPCR（ND1/ND5/B2M/POLG）ΔCt + 柱状图 | ✅ 已完成 |
| 3-实验数据处理 | `qpcr-mrna` | 通用 mRNA qPCR ΔΔCt 分析（任意靶标+内参） | ✅ 已完成 |
| 5-图表生成 | `barplot` | 通用柱状图 + 统计标注 | ✅ 已完成 |
| 5-图表生成 | `brain-if-atlas-annotate` | 脑片荧光图像 × 脑图谱配准 + 白色虚线脑区标注 | ⚪ 目录占位 |
| 5-图表生成 | `clinical-table` | 临床三线表 | ✅ 已完成 |
| 5-图表生成 | `compress-image` | 保持清晰度压缩图像体积（TIFF → JPEG 85%/PNG/压缩 TIFF） | ✅ 已完成 |
| 6-论文撰写 | `1-加载后改写适合转docx的md文件` | Markdown 预处理为 docx 转换做准备 | ⚪ 目录占位 |
| 6-论文撰写 | `2-sci-paper论文代写流水线` | SCI 论文代写润色流水线 | ✅ 已完成 |
| 7-其他 | `md2html-resume` | Markdown 简历转自包含 HTML（四色分区、A4 可打印） | ✅ 已完成 |

### OFT 全流程详情

```
OFT/
├── README.md                  ← 三步骤总览 + 快速开始
├── 1_tracker_get_data/        ← 数据采集：Arena 校准参数 + 手动录制（补救措施）
│   ├── SKILL.md, tracker.py, record.csv
│   ├── 像素和现实尺寸转换.txt, tracker-full-screen.pptx
│   └── （数据采集类工具，校准文档即参考）
├── 2_oft-analysis/            ← 分析核心：轨迹图 + 指标表 + 汇总表
│   ├── SKILL.md, README.md
│   ├── scripts/plot_oft.py, generate_summary.py
│   └── examples/
│       ├── input/6.csv        ← 344帧 Tracker 原始数据
│       └── output/arena_6.{png,csv} ← 生成的轨迹图 + 指标报告
└── 3_oft-pixelate/            ← 后处理：批量像素化
    ├── SKILL.md, README.md
    ├── scripts/batch_pixelate.py
    └── examples/
        ├── input/arena_6.png  ← 步骤2输出的 254KB 高清图
        └���─ output/arena_6.png ← 像素化后 18KB（350×317px）
```

- 三步骤各含独立 SKILL.md，通过 WorkBuddy 对话触发
- `plot_oft.py`、`tracker.py` 原代码不动
- `batch_pixelate.py` 硬编码路径已修复为命令行参数
- `generate_summary.py` 已验证：21 只动物汇总与原手工表一致

---

## 4. 共享代码策略

- 暂不建立 `shared-utils` 仓库
- 允许各 repo 内复制共用代码（配色主题、Pandoc 模板等）
- 等同一段代码在 3 个 repo 中出现后，再抽象

---

## 5. 待办事项

- [x] **qPCR mtDNA 测试**：已使用 `D:\科研流程技能库\mtDNA-input.csv` 验证 `qpcr-mtdna` skill，输出与旧脚本一致
- [x] **qPCR mRNA 骨架**：已完成 `qpcr-mrna` skill，使用合成数据验证，默认内参 GAPDH
- [x] 共识文档已写入 `D:\科研流程技能库\项目共识与架构决策.md`
- [x] 论文撰写阶段 `2-sci-paper论文代写流水线` 已建立
- [x] 共识文档已根据实际目录结构更新（2026-08-03）
- [ ] 创建 Git 私有仓库并推送首个模块

---

## 6. 论文撰写阶段讨论要点

进入 `6_论文撰写 (paper-writing)` 阶段，当前包含两个目录：

- `1-加载后改写适合转docx的md文件/`：Markdown 预处理目录占位，尚未完成 SKILL.md。
- `2-sci-paper论文代写流水线/`：已完成 SKILL.md 与 README.md，用于 SCI 论文代写润色流水线。

原 `md2docx` 已拆分为上述两个目录结构。

其余候选 skill 仍待讨论：

1. **figure-assembler**：多子图拼板（A/B/C 标签、统一 DPI、输出 TIFF/PDF）
2. **statistical-report**：汇总各 skills 的统计结果，生成论文可用的统计表
3. **methods-generator**：根据 skill 参数/脚本元数据自动生成 Methods 段落骨架
4. **reference-formatter**：按目标期刊格式整理参考文献（`md2docx` 已覆盖部分需求）
5. **supplementary-packager**：打包所有原始数据、图表、代码到一个补充材料目录

下一步：用户确认下一个优先建设的 skill，或提出新的 paper-writing 场景。

## 7. 下次恢复指引

加载本文档，继续 grill-me 未完成的决策链分支：
- 论文撰写阶段 skill 拆分与优先级
- FACS / WB / IF 等实验数据处理阶段规划
- Git 私有仓库初始化时机
