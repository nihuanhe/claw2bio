# 分组柱状图

> 一句话：宽表 CSV 进，发表级分组柱状图出——带误差线、散点和显著性标注。

::: info 获取本技能 · Get this skill
**方式 A —— 一键引导 prompt（推荐）**。复制下面这段，粘贴到你的 AI agent IDE：

```
请帮我安装 Claw2Bio 技能库中的 "barplot" 技能：
1. 从 GitHub 仓库 https://github.com/claw2bio/claw2bio 只拉取 figure-generation/barplot
   这一个文件夹（用 sparse checkout，不要克隆整库）。
2. 阅读其中的 SKILL.md 并注册该技能。
3. 运行 examples/ 里的示例验证环境，把输出的图给我看。
```

**方式 B —— 独立 zip 包**（几 MB，腾讯 COS 直链）：*打包中，即将上线*。

**方式 C —— 全量示例数据**（COS 按 skill 分目录）：*打包中，即将上线*。
:::

## 它能做什么

自动数出 CSV 的数值列数，选择对应的 2/3/4/5/6 组脚本，输出带均值、SD 误差线、抖动散点和统计标注（2 组 t-test；≥3 组 ANOVA + Tukey HSD）的 300 dpi PNG：

![barplot 示例输出](/cards/barplot.png)

## 快速上手（30 秒）

```bash
cd figure-generation/barplot
pip install pandas numpy scipy matplotlib statsmodels
python scripts/run_barplot.py examples/input/data.csv
```

图会保存在输入 CSV 同目录，名为 `data_barplot.png`。

## 输入格式

宽表——每列一个组，每行一个生物学重复：

```csv
Ctrl,Stress
18533,13055
20650,10017
19467,21995
```

非数值列会被自动忽略。

## 输出文件

| 文件 | 内容 |
|---|---|
| `<input>_barplot.png` | 带统计标注的 300 dpi 分组柱状图 |

## 自定义

编辑所选脚本顶部：

```python
FIGURE_NAME = 'ELISA'
Y_LABEL     = 'IFNβ (pg/mL)'
bar_colors  = [...]   # 默认 Wong 2011 色盲友好配色
```

备选配色（统计逻辑完全相同）：`barplot_2col_green_pink.py`、`barplot_3col_light.py`。

## 常见问题

- **选错了脚本** → 检查是否有多余的非数值列；或直接调用指定脚本。
- **标签被截断** → Y 轴会自动向上扩展；如需自定义范围，改脚本顶部的坐标轴设置。

## 相关链接

- [GitHub 源码与 SKILL.md](https://github.com/claw2bio/claw2bio/tree/main/figure-generation/barplot)
- 相关技能：[qPCR mRNA](/zh/skills/qpcr-mrna) · [临床统计表](/zh/skills/clinical-table)
