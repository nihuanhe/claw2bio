# 2_oft-analysis

**OFT 第二步：数据分析与可视化**

## 位置

本模块是 OFT 全流程的第二步。完整流程：

1. [1_tracker_get_data](../1_tracker_get_data/) — 数据采集与校准
2. **2_oft-analysis** — 数据分析与可视化（当前模块）
3. [3_oft-pixelate](../3_oft-pixelate/) — 像素化后处理

## 流程

```
数据采集（步骤1）→ CSV
    │
    ▼
plot_oft.py ──── 逐文件分析 ──── ▶ arena_xxx.png  （轨迹图）
    │                            ▶ arena_xxx.csv  （指标报告）
    │
    ▼
generate_summary.py ──── 扫描汇总 ──── ▶ OFT_results_summary.csv
```

## 使用方式

### 1. 单文件分析

```bash
python scripts/plot_oft.py <数据文件.csv> --total-duration 120 --arena-size 50
```

### 2. 生成汇总表

```bash
python scripts/generate_summary.py <results_dir> -o OFT_results_summary.csv
```

## 参数速查

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--px-per-cm` | 由 `--arena-bounds` 自动推算（≈7.24） | 像素/厘米换算 |
| `--arena-size` | 50 | Arena 边长 (cm) |
| `--total-duration` | 120 | 录制时长 (s) |
| `--center-ratio` | 0.40 | 中心区比例 |
| `--rest-threshold` | 2.0 | 静止阈值 (cm/s) |
| `--dpi` | 300 | 图片分辨率 |
| `--arena-bounds` | 908,384,1270,745 | Arena 四角像素坐标 |

## 快速体验

```bash
python scripts/plot_oft.py examples/input/6.csv
```

详细示例见 [examples/](examples/)。

## 依赖

- Python 3.8+
- matplotlib（其余仅用标准库）

## 数据来源

原始代码位置：`D:\小文章\data\OFT\`
