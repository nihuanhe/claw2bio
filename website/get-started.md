# Get Started

**Zero programming background needed.** In about 10 minutes you will have an AI agent
IDE installed, the Claw2Bio skills loaded, and your first analysis figure on screen.

## Step 1 — Install an AI agent IDE

An "agent IDE" is a chat window that can read files and run commands on your computer.
Pick **one** of these free, graphical tools (all understand Claw2Bio skills out of the box):

| IDE | Why we recommend it |
|---|---|
| **WorkBuddy** | Our default pick — the skills were battle-tested in it; lightweight agent workbench |
| **Trae (CN)** | Free, Chinese UI, works without VPN — solid alternative for users in China |
| **ZCode** | Simple onboarding |
| **OpenCode** | Open source |
| **LobsterAI** | Biomedicine-oriented |

> Detailed install walkthroughs with screenshots (WorkBuddy first) are being added.
> For now, download your chosen IDE from its official site and install with default options.

**Advanced users** who already use a command-line agent (Claude Code, Codex, pi agent,
DeepSeek harness): skip to Step 2 — Claw2Bio ships a root `AGENTS.md` index and
standard `SKILL.md` files that these tools read natively.

## Step 2 — Paste the onboarding prompt

Open a new conversation in your IDE, copy the block below, and paste it in:

```
I'm new to coding. Please set up the Claw2Bio skill library for me:

1. Sparse-checkout the repository https://github.com/claw2bio/claw2bio into a folder
   named "claw2bio" in my current workspace. Do NOT clone the whole repo history.
   If GitHub is unreachable or very slow, stop and tell me — I will give you a
   download link from a domestic mirror instead.
2. Read the AGENTS.md file at the repo root and register every skill it lists.
3. Verify the setup by running the "qpcr-mrna" example (experiment-data/qpcr-mrna):
   install the Python dependencies if needed, run the script on the bundled example
   input, and show me the output figure.

Walk me through anything you need me to click or confirm.
```

The agent will fetch only what's needed, register the skills, and prove the
environment works by reproducing a real example figure.

## Step 3 — Do your own analysis

Drag your own CSV into the workspace and tell the agent what you want, e.g.:

> 用 qpcr-mrna 技能分析我刚放进来的 ct_data.csv，对照组是 Ctrl。

Every skill page on this site also has its own **Get this skill** block if you only
need one skill instead of the whole library.

## FAQ

- **Does my data leave my computer?** No. All scripts run locally; that is a core
  design principle of Claw2Bio.
- **Which Python do I need?** None that you manage yourself — let the agent set it up.
- **GitHub is slow in my region.** Use the per-skill COS zip links on each tutorial
  page (available at site launch).
