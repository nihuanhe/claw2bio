# render_table_png.py — render the manuscript table suite (Tables 1-10)
# from clinical-table's R-pipeline filled output into publication-style PNGs
# (three horizontal rules, no vertical lines) for the website gallery.
# Sources: examples/output/pipeline/Table-all_filled.md (9 tables)
#          examples/output/pipeline/table9_sequencing_quality.csv (Table 9)
# One-off website tooling; run from repo root:
#   python website/scripts/render_table_png.py
import csv
import re
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
SRC_MD = ROOT / "figure-generation/clinical-table/examples/output/pipeline/Table-all_filled.md"
SRC_T9 = ROOT / "figure-generation/clinical-table/examples/output/pipeline/table9_sequencing_quality.csv"
OUT_DIR = ROOT / "website/public/skills/clinical-table"
OUT_DIR.mkdir(parents=True, exist_ok=True)

text = SRC_MD.read_text(encoding="utf-8")

# (heading regex in Table-all_filled.md, output filename, fig width, font size, first-col fraction)
TABLES = [
    (r"## Table 1_Baseline \(revised\)[^\n]*\n(.*?)\n## ", "table1_baseline.png", 9.2, 8.8, 0.32),
    (r"## Table 2_Firth \(revised\)[^\n]*\n(.*?)\n## ", "table2_firth.png", 9.2, 9.0, 0.34),
    (r"## Table 3_esbl_genes \(revised\)[^\n]*\n(.*?)\n## ", "table3_esbl_genes.png", 11.0, 8.5, 0.22),
    (r"## Table 4_sequence_types \(revised\)[^\n]*\n(.*?)\n## ", "table4_sequence_types.png", 12.0, 7.6, 0.36),
    (r"## Table 5_sul_genes \(revised\)[^\n]*\n(.*?)\n## ", "table5_sul_genes.png", 11.0, 8.5, 0.24),
    (r"## Table 6_disease_genotype \(revised\)[^\n]*\n(.*?)\n## ", "table6_disease_genotype.png", 9.5, 8.8, 0.30),
    (r"## Table 7_procedures_genotype \(revised\)[^\n]*\n(.*?)\n## ", "table7_procedures_genotype.png", 9.8, 8.8, 0.30),
    (r"## Table 8_univariate \(revised\)[^\n]*\n(.*?)\n## ", "table8_univariate.png", 9.5, 8.0, 0.32),
    (r"## Table 10_plasmid_replicons \(new\)[^\n]*\n(.*?)\Z", "table10_plasmid_replicons.png", 11.0, 7.6, 0.30),
]


def parse_md_table(block: str):
    rows = []
    for line in block.strip().splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):  # separator row
            continue
        rows.append(cells)
    return rows[0], rows[1:]


def clean_cell(cell: str):
    """strip markdown: **..** -> bold flag; single * italics markers removed"""
    bold = cell.count("**") >= 2 or cell.startswith("**")
    txt = cell.replace("**", "").replace("*", "")
    return txt, bold


def render(header, body, out: Path, width: float, fs: float, col0: float = 0.30):
    n_cols = len(header)
    h_txt = [(textwrap.fill(t, 16), b) for t, b in (clean_cell(c) for c in header)]
    b_txt = [[clean_cell(c) for c in row] for row in body]

    fig, ax = plt.subplots(figsize=(width, 0.30 * (len(body) + 2)), dpi=300)
    ax.axis("off")
    col_widths = [col0] + [(1 - col0) / (n_cols - 1)] * (n_cols - 1)
    tbl = ax.table(cellText=[[t for t, _ in row] for row in b_txt],
                   colLabels=[t for t, _ in h_txt],
                   colWidths=col_widths, loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(fs)
    tbl.scale(1, 1.25)

    # three-line style: hide all borders, then draw top/header/bottom rules
    for cell in tbl.get_celld().values():
        cell.visible_edges = ""
    for c in range(n_cols):
        tbl[0, c].visible_edges = "TB"          # top rule + header rule
        tbl[len(body), c].visible_edges = "B"   # bottom rule
        tbl[0, c].set_text_props(weight="bold")
        tbl[0, c].set_edgecolor("black")
        tbl[len(body), c].set_edgecolor("black")
    # apply bold flags; first column left-aligned
    for c, (_, bold) in enumerate(h_txt):
        if bold:
            tbl[0, c].set_text_props(weight="bold")
    for r, row in enumerate(b_txt, start=1):
        tbl[r, 0].get_text().set_ha("left")
        tbl[r, 0].PAD = 0.02
        if row[0][1]:  # bold group-label row (e.g. **Sex, No. (%)**)
            for c in range(n_cols):
                tbl[r, c].set_text_props(weight="bold")
    tbl[0, 0].get_text().set_ha("left")
    tbl[0, 0].PAD = 0.02

    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"written: {out}")


for pattern, fname, width, fs, col0 in TABLES:
    m = re.search(pattern, text, re.S)
    if not m:
        raise SystemExit(f"table not found for pattern: {pattern}")
    header, body = parse_md_table(m.group(1))
    render(header, body, OUT_DIR / fname, width, fs, col0)

# Table 9 from its standalone CSV
rows = list(csv.reader(SRC_T9.open(encoding="utf-8-sig")))
render(rows[0], rows[1:], OUT_DIR / "table9_sequencing_quality.png", 13.5, 7.2, 0.10)
