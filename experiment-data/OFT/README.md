# OFT — 旷场实验全流程工具链

```
┌─────────────────────────────────────┐
│  1_tracker_get_data   数据采集      │
│  校准参数 + 手动录制（补救措施）     │
│  输出: step,X,Y CSV                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  2_oft-analysis   数据分析与可视化  │
│  轨迹图 + 指标报告 + 汇总表          │
│  输出: arena_*.png + CSV + summary   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  3_oft-pixelate   像素化后处理      │
│  高清图 → 350px 展示用图            │
│  输出: 缩放的 PNG                   │
└─────────────────────────────────────┘
```

| 步骤 | 目录 | 功能 | Python 脚本 |
|------|------|------|-----------|
| 1 | [1_tracker_get_data/](1_tracker_get_data/) | 数据采集与 Arena 校准 | `tracker.py` |
| 2 | [2_oft-analysis/](2_oft-analysis/) | 分析：轨迹图 + 指标表 + 汇总 | `plot_oft.py`, `generate_summary.py` |
| 3 | [3_oft-pixelate/](3_oft-pixelate/) | 后处理：批量像素化 | `batch_pixelate.py` |

> Agent 使用入口见 [SKILL.md](SKILL.md)（路由总览）；各子技能详情见各自目录下的 SKILL.md。
> 注意：步骤1 需要视频文件和人工逐帧点击，无法自动化运行；步骤2、3 的 `examples/` 均已本机跑通验证。

## 快速开始

```bash
# 1. 校准（首次使用）
cd 1_tracker_get_data
python tracker.py          # 手动录制校准点

# 2. 分析
cd ../2_oft-analysis
python scripts/plot_oft.py examples/input/6.csv

# 3. 像素化（可选）
cd ../3_oft-pixelate
python scripts/batch_pixelate.py ../2_oft-analysis/examples/output ./pixelated
```
