# compress-image

保持图像视觉清晰度的情况下压缩文件体积，适合将显微镜扫描/科学图表的无压缩 TIFF 转换为更小的格式。

## 功能

- 读取 TIFF、PNG、BMP 等常见科学图像格式
- 默认输出 JPEG 85%，肉眼基本无损，体积大幅减小
- 保留/设置 300 dpi 打印分辨率元数据
- 同时支持无损格式：TIFF LZW、TIFF ZIP、PNG

## 安装依赖

Python 3.10+ with:

```bash
pip install Pillow
```

## 快速开始

```bash
cd compress-image
python scripts/compress_image.py examples/input/sample_small.png examples/output/sample_small_JPEG_85pct.jpeg
```

输出默认保存在 `<output_path>` 指定位置。

> 全量真实示例 `PRV_0001_RGB.tif`（187.49 MB，7903×7903 尼康扫描 RGB 无压缩 TIFF，
> 转 JPEG 85% 后约 2.62 MB）因超出 git/zip 体积阈值未随仓库分发，可从 COS 下载
> （占位链接，上传后回填）：
> `https://my-website-1358159656.cos.ap-guangzhou.myqcloud.com/compress-image/data/PRV_0001_RGB.tif`
> MD5：`7af5ccf1b5823c001303c4ec4526722d`（清单见 `cos-staging/compress-image/manifest.csv`）。
> 仓库内示例为其 1200×1200 降采样版 `examples/input/sample_small.png`（约 0.83 MB）。

## 命令行参数

```bash
python scripts/compress_image.py <input> <output> [--quality 85] [--format jpeg] [--dpi 300]
```

| 参数 | 说明 | 默认值 |
|---|---|---|
| `input` | 输入图像路径 | 必填 |
| `output` | 输出图像路径 | 必填 |
| `--quality` | JPEG 质量，1–100 | 85 |
| `--format` | 输出格式：`jpeg`、`tiff_lzw`、`tiff_zip`、`png` | jpeg |
| `--dpi` | 输出 DPI；不指定则继承输入，输入没有则默认 300 | 无 |

## 格式选择建议

| 用途 | 推荐格式 | 说明 |
|---|---|---|
| 日常查看 / PPT / 论文插图 | `jpeg` 85% | 体积最小，肉眼无损 |
| 需要进一步图像分析 | `tiff_zip` | 无损压缩，像素值不变 |
| 长期原始数据存档 | `tiff_zip` 或 `tiff_lzw` | 无损，兼容性好 |
| 需要透明背景 | `png` | 无损，支持透明 |

## 文件结构

```
compress-image/
├── README.md
├── SKILL.md
├── scripts/
│   └── compress_image.py
├── examples/
│   ├── input/
│   │   └── sample_small.png              # 降采样示例图（1200×1200，约 0.83 MB）
│   └── output/
│       └── sample_small_JPEG_85pct.jpeg  # 压缩后输出示例（约 0.08 MB）
└── .gitignore
```

## 注意事项

- JPEG 是有损压缩，不适合作为需要定量分析的原始数据。
- 若输入 TIFF 本身已是压缩格式，转换收益会减小。
- 透明通道图像转 JPEG 时会自动转为 RGB 白色背景。
