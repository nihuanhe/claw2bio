"""
Barplot launcher for grouped scientific bar charts.

Usage:
    python run_barplot.py <input.csv>

Behavior:
- Reads the input CSV and counts the number of numeric columns.
- Automatically selects the corresponding barplot script:
  2 columns -> barplot_2col.py (default blue/orange)
  3 columns -> barplot_3col.py
  4 columns -> barplot_4col.py
  5 columns -> barplot_5col.py
  6 columns -> barplot_6col.py
- Executes the selected script with the input CSV as argument.

To use the green-pink 2-column variant, run it directly:
    python barplot_2col_green_pink.py <input.csv>
"""

import subprocess
import sys
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent

SCRIPT_MAP = {
    2: "barplot_2col.py",
    3: "barplot_3col.py",
    4: "barplot_4col.py",
    5: "barplot_5col.py",
    6: "barplot_6col.py",
}


def count_numeric_columns(csv_path: str) -> int:
    df = pd.read_csv(csv_path)
    # Drop all-NaN columns (trailing commas)
    df = df.dropna(axis=1, how="all")
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    return len(numeric_cols)


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) < 1:
        print("Usage: python run_barplot.py <input.csv>")
        return 1

    input_csv = argv[0]
    if not Path(input_csv).exists():
        print(f"Error: file not found: {input_csv}")
        return 1

    n_cols = count_numeric_columns(input_csv)
    if n_cols not in SCRIPT_MAP:
        print(
            f"Error: detected {n_cols} numeric columns. "
            f"This launcher supports 2–6 columns. "
            f"Please use the appropriate script in {SCRIPT_DIR} manually."
        )
        return 1

    script = SCRIPT_MAP[n_cols]
    script_path = SCRIPT_DIR / script
    print(f"Detected {n_cols} columns -> using {script}")

    cmd = [
        sys.executable,
        str(script_path),
        input_csv,
    ] + argv[1:]
    return subprocess.call(cmd)


if __name__ == "__main__":
    sys.exit(main())
