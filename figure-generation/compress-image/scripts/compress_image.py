#!/usr/bin/env python3
"""
Compress scientific images for smaller file size while keeping visual clarity.

Usage:
    python compress_image.py <input_image> <output_image> [--quality 85] [--format jpeg] [--dpi 300]

Supported output formats:
    jpeg       : Lossy, smallest, good for viewing/printing (default, quality=85)
    tiff_lzw   : Lossless TIFF with LZW compression
    tiff_zip   : Lossless TIFF with ZIP/Adobe Deflate compression
    png        : Lossless PNG

DPI is preserved from the input if available; otherwise defaults to 300x300.
"""

import argparse
import os
from pathlib import Path

from PIL import Image


def get_size_mb(path: Path) -> float:
    return path.stat().st_size / (1024 * 1024)


def resolve_dpi(img: Image.Image, requested_dpi: int | None) -> tuple[int, int]:
    if requested_dpi is not None and requested_dpi > 0:
        return (requested_dpi, requested_dpi)
    dpi = img.info.get("dpi")
    if dpi and isinstance(dpi, tuple) and len(dpi) == 2:
        x, y = dpi
        if x > 0 and y > 0:
            return (int(x), int(y))
    return (300, 300)


def compress_image(input_path: str, output_path: str, fmt: str, quality: int, dpi: int | None) -> None:
    in_path = Path(input_path)
    out_path = Path(output_path)

    if not in_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    out_path.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(in_path) as img:
        target_dpi = resolve_dpi(img, dpi)

        if fmt == "jpeg":
            if img.mode in ("RGBA", "P", "LA"):
                img = img.convert("RGB")
            img.save(out_path, format="JPEG", quality=quality, dpi=target_dpi, optimize=True)
        elif fmt == "tiff_lzw":
            img.save(out_path, format="TIFF", compression="tiff_lzw", dpi=target_dpi)
        elif fmt == "tiff_zip":
            img.save(out_path, format="TIFF", compression="tiff_adobe_deflate", dpi=target_dpi)
        elif fmt == "png":
            img.save(out_path, format="PNG", dpi=target_dpi, optimize=True)
        else:
            raise ValueError(f"Unsupported format: {fmt}")

    before_mb = get_size_mb(in_path)
    after_mb = get_size_mb(out_path)
    ratio = after_mb / before_mb * 100 if before_mb > 0 else 0
    saved_mb = before_mb - after_mb

    print(f"Input : {in_path} ({before_mb:.2f} MB)")
    print(f"Output: {out_path} ({after_mb:.2f} MB)")
    print(f"Ratio : {ratio:.1f}% of original")
    print(f"Saved : {saved_mb:.2f} MB")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compress scientific images while preserving visual clarity."
    )
    parser.add_argument("input", help="Path to input image (TIFF/PNG/BMP/etc.)")
    parser.add_argument("output", help="Path to output image")
    parser.add_argument(
        "--quality",
        type=int,
        default=85,
        help="JPEG quality (1-100). Default 85. Higher = better quality / larger file.",
    )
    parser.add_argument(
        "--format",
        choices=["jpeg", "tiff_lzw", "tiff_zip", "png"],
        default="jpeg",
        help="Output format. Default jpeg.",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=None,
        help="Output DPI. Defaults to input DPI or 300 if unavailable.",
    )
    args = parser.parse_args()

    compress_image(args.input, args.output, args.format, args.quality, args.dpi)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
