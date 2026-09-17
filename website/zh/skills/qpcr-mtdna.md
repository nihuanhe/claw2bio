# qPCR mtDNA 拷贝数

> 一句话：ND1/ND5 线粒体 DNA 拷贝数分析——自动配对 B2M/POLG 核内参，统计和 300 dpi 出图一次完成。

::: info 获取本技能 · Get this skill
**方式 A —— 一键引导 prompt（推荐）**。复制下面这段，粘贴到你的 AI agent IDE：

```
请帮我安装 Claw2Bio 技能库中的 "qpcr-mtdna" 技能：
1. 从 GitHub 仓库 https://github.com/nihuanhe/claw2bio 只拉取 experiment-data/qpcr-mtdna
   这一个文件夹（用 sparse checkout，不要克隆整库）。
2. 阅读其中的 SKILL.md 并注册该技能。
3. 运行 examples/ 里的示例验证环境，把输出的图给我看。
```

**方式 B —— 独立 zip 包**（约 0.1 MB，本站下载）：<https://claw2bio.site/downloads/qpcr-mtdna.zip>

**方式 C —— 全量示例数据**：已包含在方式 B 包内（同一个压缩包）。
:::

## 它能做什么

读取包含 `ND1 Ct`、`ND5 Ct`、`B2M Ct`、`POLG Ct` 行的原始 Ct 表，计算

```
Mean copy number = (2^(B2M-ND1) + 2^(POLG-ND5)) / 2
```

自动统计（2 组 t-test；≥3 组 Tukey HSD）并绘制 300 dpi 柱状图：

![qPCR mtDNA 示例输出](/cards/qpcr-mtdna.png)

## 快速上手（30 秒）

```bash
cd experiment-data/qpcr-mtdna
pip install pandas numpy scipy matplotlib
python scripts/run_mtdna.py examples/input/mtDNA-input.csv examples/output --name Figure18B --overwrite
```

预期输出：`Figure18B.csv`（含 ΔCt / 2^ΔCt / Mean copy number 列）和 `Figure18B.png`。示例数据 P = 0.986（ns）。

## 输入格式

```csv
Target,Sample,Rep1,Rep2,Rep3
ND1 Ct,Ctrl,15.10,14.19,14.66
ND1 Ct,Treat,14.27,14.08,14.72
ND5 Ct,Ctrl,14.25,14.64,14.47
ND5 Ct,Treat,14.88,14.93,14.87
B2M Ct,Ctrl,22.99,22.40,22.53
B2M Ct,Treat,22.62,22.73,22.27
POLG Ct,Ctrl,22.14,22.53,22.43
POLG Ct,Treat,22.80,22.00,22.48
```

必须包含 `ND1 Ct`、`ND5 Ct`、`B2M Ct`、`POLG Ct` 四行。

## 输出文件

| 文件 | 内容 |
|---|---|
| `<name>.csv` | 原始 Ct + Delta Ct + 2^Delta Ct + Mean copy number |
| `<name>.png` | 带统计标注的 300 dpi 柱状图 |

## 参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--name` | — | 输出文件名前缀 |
| `--y-label` | — | Y 轴标签 |
| `--dpi` | 300 | PNG 分辨率 |
| `--overwrite` | 关 | 允许覆盖已有输出 |

整目录批量处理：`python scripts/batch_mtdna.py <目录> --overwrite`。

## 常见问题

- **提示缺少靶标行** → 输入必须正好包含 `ND1 Ct`、`ND5 Ct`、`B2M Ct`、`POLG Ct`（注意带 "Ct" 后缀）。
- **提示输出文件已存在** → 加 `--overwrite`。

## 相关链接

- [GitHub 源码与 SKILL.md](https://github.com/nihuanhe/claw2bio/tree/main/experiment-data/qpcr-mtdna)
- 相关技能：[qPCR mRNA](/zh/skills/qpcr-mrna) · [分组柱状图](/zh/skills/barplot)
