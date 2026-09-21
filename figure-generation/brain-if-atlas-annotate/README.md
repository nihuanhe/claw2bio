# brain-if-atlas-annotate — 小鼠脑 atlas 线图叠加标注

100 张小鼠脑冠状面 atlas 线图（Bregma +1.97 ~ -8.15 mm），黑线/白线两版，
用于免疫荧光/脑片图的脑区叠加标注。选图即用，无需跑代码。

## 文件结构

```
brain-if-atlas-annotate/
├── SKILL.md                          # 技能定义（AI agent 读这个）
├── black_lines_only/                 # 黑线图 100 张（亮场/浅背景用）
├── white_lines_only/                 # 白线图 100 张（暗背景荧光用）
└── scripts/
    └── convert_bregma_to_white_lines.py   # 黑线图 → 透明底白线图
```

## 快速上手

1. 确定脑片 Bregma 坐标（如 -1.55 mm）
2. 从对应目录取 `Bregma_-1.55mm.png`
3. 在 ImageJ/Photoshop 叠加到荧光图，对齐中线/脑室后标注脑区

需要把自有黑线图转透明底白线图：

```bash
python scripts/convert_bregma_to_white_lines.py --batch black_lines_only
```

依赖：`pip install numpy pillow`（仅转换脚本需要）。
