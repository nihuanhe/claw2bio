# qpcr-mrna example

## Input

`input/mrna-input.csv` is a raw mRNA qPCR Ct table with 2 groups (Ctrl vs Treat), 2 targets (IL6, TNF), and `GAPDH` as the reference gene.

## Run

```bash
cd qpcr-mrna
python scripts/run_mrna.py \
  examples/input/mrna-input.csv \
  examples/output \
  --name Figure1 --overwrite
```

## Output

- `output/Figure1.csv`: raw Ct + ΔCt + fold change + statistics
- `output/Figure1_IL6_barplot.png`: IL6 bar plot
- `output/Figure1_TNF_barplot.png`: TNF bar plot

Expected results:
- IL6: ~6.8-fold upregulation in Treat vs Ctrl, P < 0.001
- TNF: ~1.2-fold upregulation in Treat vs Ctrl, P = 0.002
