# barplot examples

## Inputs

- `input/data.csv`: 2 groups (Ctrl vs Stress) — routed to `barplot_2col.py`
- `input/data_4col.csv`: 4 groups — routed to `barplot_4col.py`
- `input/data_6col.csv`: 6 groups — routed to `barplot_6col.py`

## Run

```bash
cd barplot
python scripts/run_barplot.py examples/input/data.csv
```

The script detects the column count and picks the matching script. The output PNG
is saved next to the input CSV as `<input>_barplot.png`; the committed copies in
`output/` were produced the same way and moved there for reference.

## Expected outputs

- `output/data_barplot.png`: 2-group plot, t-test annotation
- `output/data_4col_barplot.png`: 4-group plot, ANOVA + Tukey annotations
- `output/data_6col_barplot.png`: 6-group plot, ANOVA + Tukey annotations
