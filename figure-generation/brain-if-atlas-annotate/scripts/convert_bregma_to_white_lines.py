"""
Convert Bregma atlas pages (grayscale: dark lines + gray fills on white)
to transparent PNGs with only white lines/fills.

Adapted from 旧例子/convert_atlas_to_white_lines.py
(original handled cyan/blue atlas pages; this handles grayscale pages).

For each input it produces two outputs in the output dir:
  1. atlas_<Bregma>_white_lines_only.png  -- transparent PNG, white lines/fills
  2. _preview_on_black_<Bregma>.png       -- same composited on black (quick visual check)

Usage:
    Single file:
        python convert_bregma_to_white_lines.py <input.png> [<output_dir>]
    Batch over a directory:
        python convert_bregma_to_white_lines.py --batch <input_dir> [<output_dir>]
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image

# Keep pixels whose brightest channel is at or below this (drawn material).
# Grayscale atlas pages: dark lines ~ max<=64, gray fills ~ max 128-169.
GRAY_MAX = 169


def convert_to_rgba(input_path: str) -> np.ndarray:
    """Return an RGBA uint8 array: white drawn material on transparent."""
    img = Image.open(input_path).convert("RGB")
    arr = np.array(img)
    mask = arr.max(axis=2) <= GRAY_MAX
    out = np.zeros((arr.shape[0], arr.shape[1], 4), dtype=np.uint8)
    out[mask, :3] = [255, 255, 255]
    out[mask, 3] = 255
    return out


def save_line_only(rgba: np.ndarray, output_path: str) -> None:
    Image.fromarray(rgba, "RGBA").save(output_path)


def save_preview_on_black(rgba: np.ndarray, output_path: str) -> None:
    # Composite onto pure black so the white line art is visible for checking.
    black = np.zeros_like(rgba)
    black[..., 3] = 255
    a = rgba[..., 3:4] / 255.0
    comp = (rgba[..., :3] * a + black[..., :3] * (1 - a)).astype(np.uint8)
    Image.fromarray(comp, "RGB").save(output_path)


def process_one(input_path: Path, output_dir: Path) -> tuple:
    name = input_path.stem  # "Bregma_0.01mm"
    if name.startswith("Bregma_"):
        name = name[len("Bregma_"):]
    rgba = convert_to_rgba(str(input_path))
    line_path = output_dir / f"atlas_{name}_white_lines_only.png"
    prev_path = output_dir / f"_preview_on_black_{name}.png"
    save_line_only(rgba, str(line_path))
    save_preview_on_black(rgba, str(prev_path))
    return line_path, prev_path


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == "--batch":
        in_dir = Path(sys.argv[2])
        out_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else in_dir / "white_lines_only"
        out_dir.mkdir(parents=True, exist_ok=True)
        inputs = sorted(in_dir.glob("Bregma_*.png"))
        print(f"Found {len(inputs)} Bregma files. Output -> {out_dir}")
        for i, p in enumerate(inputs, 1):
            process_one(p, out_dir)
            if i % 20 == 0 or i == len(inputs):
                print(f"  {i}/{len(inputs)} done")
        print(f"Done. {len(inputs)} images -> {out_dir}")
    else:
        in_path = Path(sys.argv[1])
        out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else in_path.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        line_path, prev_path = process_one(in_path, out_dir)
        print(f"Saved:\n  {line_path}\n  {prev_path}")


if __name__ == "__main__":
    main()
