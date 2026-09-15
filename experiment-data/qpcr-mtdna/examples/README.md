# qpcr-mtdna example

## Input

`input/mtDNA-input.csv` is a raw mtDNA qPCR Ct table with 2 groups (Ctrl-BD-sEVs vs Stress-BD-sEVs), containing:

- `ND1 Ct` / `ND5 Ct`: mtDNA targets
- `B2M Ct` / `POLG Ct`: nuclear references
- 3 biological replicates per group

## Run

```bash
cd qpcr-mtdna
python scripts/run_mtdna.py \
  examples/input/mtDNA-input.csv \
  examples/output \
  --name Figure18B --overwrite
```

## Output

- `output/Figure18B.csv`: raw Ct + Delta Ct + 2^Delta Ct + Mean copy number
- `output/Figure18B.png`: 300-dpi bar plot

P value for this example = 0.986 (ns).
