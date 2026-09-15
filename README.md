# Claw2Bio

Lab-validated AI agent skills for biomedical data analysis — no coding required.

实验室实战验证的 AI agent 生物医学分析技能库——无需编程基础。

## What is this?

A curated library of **fixed, lab-validated analysis scripts** packaged as AI agent
skills (standard `SKILL.md` format). You talk to your AI coding assistant in natural
language; it applies these battle-tested scripts to your data with only
parameter-level adjustments — no hallucinated pipelines.

覆盖环节：实验数据处理 → 生信数据分析 → 图表生成。
所有分析在本地运行，临床数据不出本地。

## Repository structure

```
experiment-data/     # Stage 1: experimental data processing (qPCR, ...)
bioinformatics/      # Stage 2: bioinformatics analysis (coming soon)
figure-generation/   # Stage 3: figures & tables (bar plots, clinical tables, ...)
website/             # source of the claw2bio.site documentation portal
ARCHITECTURE.md      # design conventions all skills must follow (项目共识与架构决策)
AGENTS.md            # skill index for command-line agents (Codex / OpenCode / pi)
```

Each skill follows the same layout:

```
<skill>/
├── SKILL.md         # agent-facing skill definition
├── README.md        # human-readable usage doc
├── scripts/         # analysis scripts
└── examples/        # minimal runnable input + expected output
```

## Quick start

See the documentation portal **https://claw2bio.site** (Get Started) for the
one-click onboarding prompt that lets your agent fetch, register, and verify a
skill automatically.

Manual smoke test for any skill:

```bash
cd experiment-data/qpcr-mrna
pip install pandas numpy scipy matplotlib
python scripts/run_mrna.py examples/input/mrna-input.csv examples/output --name Figure1 --overwrite
```

## Skills index

See [AGENTS.md](AGENTS.md).

## License

TBD (will be finalized before the repository goes public).
