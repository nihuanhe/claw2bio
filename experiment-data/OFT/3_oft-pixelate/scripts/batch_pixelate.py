#!/usr/bin/env python3
"""
OFT 像素化后处理工具
将 plot_oft.py 生成的高清 Arena 轨迹图缩放到指定宽度（NEAREST 采样，像素艺术风格）。

用法:
    python batch_pixelate.py <input_dir> <output_dir> [--width 350]

示例:
    python batch_pixelate.py ./results ./artistic_lofi --width 350
"""

from PIL import Image
import os
from argparse import ArgumentParser


def main():
    parser = ArgumentParser(description="OFT 像素化：批量 PNG 缩放")
    parser.add_argument("input_dir", help="包含 arena_*.png 的目录")
    parser.add_argument("output_dir", help="输出目录")
    parser.add_argument("--width", type=int, default=350, help="目标宽度 px（默认 350）")
    args = parser.parse_args()

    input_root = os.path.abspath(args.input_dir)
    output_root = os.path.abspath(args.output_dir)
    target_width = args.width

    processed = 0
    skipped = 0

    for dirpath, dirnames, filenames in os.walk(input_root):
        for fname in filenames:
            if not fname.lower().endswith(".png"):
                continue

            in_path = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(in_path, input_root)
            out_path = os.path.join(output_root, rel_path)

            os.makedirs(os.path.dirname(out_path), exist_ok=True)

            img = Image.open(in_path)
            orig_w, orig_h = img.size
            h = int(orig_h * target_width / orig_w)
            resized = img.resize((target_width, h), Image.Resampling.NEAREST)
            resized.save(out_path, "PNG")
            processed += 1
            print(f"[{processed}] {rel_path} -> {target_width}x{h}")

    print(f"\n完成。处理: {processed} 张，跳过: {skipped} 张。")


if __name__ == "__main__":
    main()
