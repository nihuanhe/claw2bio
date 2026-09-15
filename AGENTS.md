# AGENTS.md — Claw2Bio skill index

This file is the entry point for command-line agents (Codex, OpenCode, pi, etc.).
Each skill below has a standard `SKILL.md` (agent-facing definition, English with
Chinese summary), a `README.md`, `scripts/`, and `examples/` with minimal runnable
input and expected output.

## Stage 1 — Experiment data processing (`experiment-data/`)

| Skill | Path | What it does |
|---|---|---|
| qpcr-mrna | `experiment-data/qpcr-mrna/SKILL.md` | mRNA qPCR ΔΔCt analysis + publication-ready bar plots (t-test / ANOVA + Dunnett) |
| qpcr-mtdna | `experiment-data/qpcr-mtdna/SKILL.md` | mtDNA qPCR (ND1/ND5/B2M/POLG) ΔCt + Mean copy number + bar plots |

## Stage 2 — Bioinformatics analysis (`bioinformatics/`)

Coming soon: single-cell RNA-seq, bulk RNA-seq, bacterial phylogenetics.

## Stage 3 — Figure & table generation (`figure-generation/`)

| Skill | Path | What it does |
|---|---|---|
| barplot | `figure-generation/barplot/SKILL.md` | Grouped bar plots from wide-format CSV, auto-selects 2–6 group script |
| clinical-table | `figure-generation/clinical-table/SKILL.md` | Publication-ready clinical three-line tables (baseline, correlation, Cox, OR) |

## Conventions

- All skills follow the design rules in `ARCHITECTURE.md` (script reuse, examples
  smoke-test convention, adapter pattern).
- Scripts run locally; no data leaves the user's machine.
- Python skills expect Python 3.10+ with `pip install pandas numpy scipy matplotlib statsmodels`.
