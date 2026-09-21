# wb-imagej

Western Blot 条带灰度定量流程：ImageJ 宏测灰度 → Python 内参归一化 + 统计检验 + 柱状图。

## Features

- **ImageJ 宏**（`docs/wb_quantify_imageJ.ijm`）：一键完成 8-bit 转换、Rolling Ball 去背景、反转、ROI 自动排序（带预览确认），导出灰度 CSV
- **Python 管线**（`scripts/wb_pipeline.py`）：归一化（`Mean / beta_actin_mean`）→ 统计 → 作图一步到位
- 重复列数自动检测（`Mean_Rep1..N`，不限于 3 次）
- 2 组：Student's t-test；≥3 组：单因素 ANOVA + Tukey HSD（vs 对照组）
- 输出 300 dpi 柱状图 PNG（均值 + SD 误差线 + 散点 + 显著性标注），Wong 2011 色盲友好配色，支持 2–6 个分组

## Installation

Python 3.10+ with:

```bash
pip install pandas numpy scipy matplotlib statsmodels
```

ImageJ 阶段需要 ImageJ（https://imagej.nih.gov/ij/）或 FIJI（https://fiji.sc/），无需额外插件。

## Quick start

```bash
cd WB-imageJ-定量
python scripts/wb_pipeline.py examples/input/FigureR3.csv --control "Ctrl-BD-sEV" --output-dir examples/output
```

输出 `examples/output/FigureR3.csv`（追加归一化和统计列）与 `examples/output/FigureR3.png`。

## Input CSV format

```csv
Protein,Sample,Mean_Rep1,Mean_Rep2,Mean_Rep3,beta_actin_mean
NOXA,Ctrl-BD-sEV,129.034,100.595,110.981,162.195
NOXA,Stress-BD-sEV,263.26,240.157,233.62,175.485
```

- `Protein`：目的蛋白名（X 轴分组），数量不限
- `Sample`：分组条件，2–6 个
- `Mean_RepN`：ImageJ 灰度 Mean 值，列数自动检测
- `beta_actin_mean`：内参灰度值，同一 Sample 下所有 Protein 共享

## CLI reference

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `input` | 输入 CSV 路径 | 必填（单文件模式） |
| `--control` | 对照组 Sample 名（≥3 组时 Tukey 的对照） | 无 |
| `--output-dir` | 输出目录 | 与输入 CSV 同目录（同名覆盖） |
| `--batch` | 批量模式：扫描 `<dir>/FigureR*/FigureR*.csv` | 无 |

## File structure

```
WB-imageJ-定量/
├── README.md
├── SKILL.md
├── docs/
│   ├── ImageJ操作说明.md        # ImageJ 宏的操作步骤与参数
│   ├── WB计算完整流程.md         # 计算流程背景说明（原始参考脚本）
│   └── wb_quantify_imageJ.ijm   # ImageJ 宏：ROI 测量 → 灰度 CSV
├── scripts/
│   └── wb_pipeline.py           # 归一化 → 统计 → 柱状图（CLI）
└── examples/
    ├── README.md
    ├── input/
    │   └── FigureR3.csv         # 1 蛋白 × 4 组 × 3 重复
    └── output/
        ├── FigureR3.csv         # 归一化 + 统计结果
        └── FigureR3.png         # 柱状图
```

## Notes

- 默认输出 CSV 与输入**同名同目录**（即覆盖输入）；如需保留原始数据请用 `--output-dir`。
- 输入已含 `Normalized_RepX` 列时归一化自动跳过。
- 完整背景与公式推导见 `docs/WB计算完整流程.md`；其中内嵌的脚本是原始参考版本，实际执行统一使用 `scripts/wb_pipeline.py`。
