# wb-imagej examples

## Inputs

- `input/FigureR3.csv`: 1 protein (NOXA) × 4 samples (Ctrl-BD-sEV / Stress-BD-sEV / Stress-BD-sEV+ProtK / Stress-BD-sEV+RNase) × 3 reps — 走 ANOVA + Tukey HSD 分支

## Run

```bash
cd WB-imageJ-定量
python scripts/wb_pipeline.py examples/input/FigureR3.csv --control "Ctrl-BD-sEV" --output-dir examples/output
```

`--control` 指定 Tukey HSD 的对照组；`--output-dir` 将产物写入 `output/`（不加则覆盖输入 CSV 并在其旁生成 PNG）。

## Expected outputs

- `output/FigureR3.csv`: 追加 `Normalized_Rep1–3 / Normalized_Mean / Normalized_SD / Normalized_SEM / ANOVA_F / ANOVA_p / p_value / Significance`。关键数字：归一化均值 Ctrl=0.7000、Stress=1.4000、+ProtK=1.1272、+RNase=1.0000；ANOVA F=38.0612，P<0.001；vs 对照的 Tukey 显著性依次为 `***` / `***`（P=0.0009）/ `**`（P=0.0086）
- `output/FigureR3.png`: 4 组柱状图（均值 + SD + 散点 + 显著性文字标注，300 dpi）
