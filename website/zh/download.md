# 下载

Claw2Bio 的数据分三层分发，无需从 GitHub 拉取 50 GB 整库：

| 层级 | 内容 | 位置 |
|---|---|---|
| **迷你示例**（随仓库） | 每个技能几 MB，clone 后 30 秒可跑 | [GitHub 仓库](https://github.com/nihuanhe/claw2bio) |
| **全量数据与按技能 zip** | 完整示例数据、单技能独立 zip | 各技能教程页上的直链（COS / 本站） |
| **学术存档** | 带 DOI 的发布版快照 | Zenodo——*即将上线* |

## 按技能 zip

最新上架技能的独立 zip 包（每个 < 50 MB，由本站分发）：

**实验数据处理**

| 技能 | zip |
|---|---|
| [免疫荧光多通道对比度](/zh/skills/if-contrast) | [if-contrast.zip](https://claw2bio.site/downloads/if-contrast.zip)——多通道免疫荧光批量对比度调整 |
| [旷场实验 OFT](/zh/skills/OFT) | [OFT.zip](https://claw2bio.site/downloads/OFT.zip)——Tracker 轨迹 → 分析图 → 像素化热图 |
| [WB 灰度定量](/zh/skills/wb-imagej) | [wb-imagej.zip](https://claw2bio.site/downloads/wb-imagej.zip)——ImageJ 宏灰度定量 → Python 归一化 + 统计 + 柱状图 |

**图表生成**

| 技能 | zip |
|---|---|
| [脑 atlas 叠加标注](/zh/skills/brain-if-atlas-annotate) | [brain-if-atlas-annotate.zip](https://claw2bio.site/downloads/brain-if-atlas-annotate.zip)——小鼠脑 atlas 线稿叠加，IF 脑区标注 |
| [图片批量压缩](/zh/skills/compress-image) | [compress-image.zip](https://claw2bio.site/downloads/compress-image.zip)——超大扫描 TIFF → 可分享 JPEG |

> bulk-RNA-seq 技能的 R 依赖（完整离线包仓库，约 425 MB）已托管在腾讯 COS，离线安装直链见 [bulk-RNA-seq 教程](/zh/skills/bulk-RNA-seq)。

## 整库 zip

*暂不提供整库压缩包。* 对大多数用户，我们更推荐按技能获取：
打开所需技能的教程页，使用顶部的**「获取本技能」**区块。
