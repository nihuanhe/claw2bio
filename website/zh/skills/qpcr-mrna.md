# qPCR mRNA（ΔΔCt）

> 一句话：ΔΔCt 法相对表达量分析，从原始 Ct 表直接产出每个靶基因一张发表级柱状图。

::: info 获取本技能 · Get this skill
**方式 A —— 一键引导 prompt（推荐）**。复制下面这段，粘贴到你的 AI agent IDE：

```
请帮我安装 Claw2Bio 技能库中的 "qpcr-mrna" 技能：
1. 从 GitHub 仓库 https://github.com/nihuanhe/claw2bio 只拉取 experiment-data/qpcr-mrna
   这一个文件夹（用 sparse checkout，不要克隆整库）。
2. 阅读其中的 SKILL.md 并注册该技能。
3. 运行 examples/ 里的示例验证环境，把输出的图给我看。
```

**方式 B —— 独立 zip 包**（约 0.2 MB，本站下载）：<https://claw2bio.site/downloads/qpcr-mrna.zip>

**方式 C —— 全量示例数据**：已包含在方式 B 包内（同一个压缩包）。
:::

## 它能做什么

输入原始 qPCR Ct 表（`Target, Sample, Rep1, Rep2, Rep3`），自动以内参基因（默认 `GAPDH`）归一化，计算 ΔΔCt 与相对对照组的 Fold change，自动选择统计方法（2 组 t-test；≥3 组 ANOVA + Dunnett），每个靶基因输出一张 300 dpi 柱状图：

![qPCR mRNA 示例输出](/cards/qpcr-mrna.png)

## 快速上手（30 秒）

技能装好后，直接对 agent 说：

> 运行 qpcr-mrna 的示例，把图给我看。

或手动执行：

```bash
cd experiment-data/qpcr-mrna
pip install pandas numpy scipy matplotlib
python scripts/run_mrna.py examples/input/mrna-input.csv examples/output --name Figure1 --overwrite
```

应得到 `Figure1.csv` 和每个靶标一张 `Figure1_<target>_barplot.png`（示例中 IL6 上调约 6.8 倍，P<0.001）。

## 输入格式

```csv
Target,Sample,Rep1,Rep2,Rep3
IL6,Ctrl,20.10,20.30,20.20
IL6,Treat,17.50,17.80,17.60
GAPDH,Ctrl,18.00,18.10,18.05
GAPDH,Treat,18.20,18.30,18.25
```

- 内参行与普通靶标行格式相同；第一个出现的 `Sample` 默认作为对照组。
- 支持 2–6 组（更多组用扩展布局）。

## 输出文件

| 文件 | 内容 |
|---|---|
| `<name>.csv` | 原始 Ct + ΔCt + Fold change + P 值 + 显著性 |
| `<name>_<target>_barplot.png` | 每个靶基因一张 300 dpi 图 |

## 参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--name` | — | 输出文件名前缀 |
| `--ref-targets` | `GAPDH` | 内参基因名，逗号分隔 |
| `--control` | 第一个 Sample | 对照组名 |
| `--y-label` | — | Y 轴标签 |
| `--dpi` | 300 | PNG 分辨率 |
| `--overwrite` | 关 | 允许覆盖已有输出 |

## 常见问题

- **提示输出文件已存在** → 加 `--overwrite`，或换一个 `--name`。
- **内参没识别到** → 检查拼写，或用 `--ref-targets ACTB` 指定。
- **ModuleNotFoundError** → 让 agent 安装依赖，或手动 `pip install pandas numpy scipy matplotlib`。

## 相关链接

- [GitHub 源码与 SKILL.md](https://github.com/nihuanhe/claw2bio/tree/main/experiment-data/qpcr-mrna)
- 相关技能：[qPCR mtDNA](/zh/skills/qpcr-mtdna) · [分组柱状图](/zh/skills/barplot)
