# 3_oft-pixelate

**OFT 第三步：像素化后处理**

将步骤2生成的高清 Arena 轨迹图缩放到指定宽度，用于论文拼图或展示。

## 位置

本模块是 OFT 全流程的第三步，依赖步骤2（2_oft-analysis）的输出。

完整流程：
1. [1_tracker_get_data](../1_tracker_get_data/) — 数据采集
2. [2_oft-analysis](../2_oft-analysis/) — 数据分析与可视化
3. **3_oft-pixelate** — 像素化后处理（当前模块）

## 使用方式

```bash
python scripts/batch_pixelate.py <input_dir> <output_dir> [--width 350]
```

## 依赖

- Pillow

## 数据来源

原始代码位置：`D:\小文章\data\OFT\results\results-像素化图片\`
