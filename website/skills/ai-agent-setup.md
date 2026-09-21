# Install Your First AI Agent (Windows 11, Beginner-Friendly)

<!-- This is the prerequisite tutorial for the series: every "do analysis with an AI agent" tutorial assumes you already have an AI agent installed and connected to a model. All links verified (2026-09). -->

An AI agent is software that "understands plain language and operates your computer for you": you give instructions in everyday words, and it plans, executes, and delivers results. For bioinformatics analysis, it installs the environment, runs the scripts, and produces the figures — you just copy and paste prompts.

**Which one to pick? One-sentence answer:**

- **Total beginner + Windows 11** → install a desktop (GUI) agent. Recommended: **TRAE** or **WorkBuddy**;
- **Comfortable with the command line** → install a CLI agent. Recommended: **OpenCode** (open-source, free, works with any model) or **Pi** (minimal and extensible).

---

## 1. Two types of AI agents at a glance

### A. Desktop apps (GUI, beginner-friendly)

| Name | Made by | Official site (verified) | Notes |
|---|---|---|---|
| **WorkBuddy** | Tencent | https://www.workbuddy.cn | All-in-one AI workspace, Chinese UI, ready out of the box |
| **TRAE** | ByteDance | https://www.trae.ai (intl) ｜ https://www.trae.cn (China) | AI-native IDE, multilingual UI |
| **Qoder** | Alibaba | https://qoder.com | Agentic coding platform |
| Cursor | Cursor (US) | https://cursor.com | Well-known international AI IDE, subscription-based |
| Windsurf | Windsurf (US) | https://windsurf.com | Well-known international AI IDE, subscription-based |

### B. CLI agents (for users with some command-line experience)

| Name | Made by | Site / GitHub (verified) | Notes |
|---|---|---|---|
| **OpenCode** | SST (open source) | https://opencode.ai ｜ https://github.com/sst/opencode | Free and open source, runs in the terminal, works with any model API |
| **Claude Code** | Anthropic | https://claude.com/product/claude-code ｜ https://github.com/anthropics/claude-code | Top tier; requires a subscription or API credits |
| **Pi** | Mario Zechner (open source) | https://github.com/badlogic/pi-mono ｜ npm `@earendil-works/pi-coding-agent` | Minimal, extensible coding agent |
| **Kimi Code** | Moonshot AI | https://github.com/MoonshotAI/kimi-code | Official Kimi terminal agent (the older kimi-cli has been superseded by Kimi Code); pairs with Kimi models (API platform: platform.moonshot.cn) |
| Codex CLI | OpenAI | https://github.com/openai/codex | OpenAI's official CLI agent |
| Gemini CLI | Google | https://github.com/google-gemini/gemini-cli | Google's official CLI agent, has a free tier |
| Aider | Open-source community | https://aider.chat | Veteran open-source pair-programming tool |

> Note: CLI agents all require Node.js, are installed via npm in the terminal, and need a manually configured model API key — which is exactly why they assume "a bit of experience".

---

## 2. Installing a desktop app: WorkBuddy as an example (recommended for beginners)

1. Open the official site (e.g., **https://www.workbuddy.cn** or **https://www.trae.ai**) and click "Download" to get the Windows installer;
2. Double-click the installer and accept all default options;
3. On first launch, sign up / log in as prompted;
4. Pick a model from the dropdown next to the input box, and start chatting.

All desktop apps (WorkBuddy, TRAE, Qoder, Cursor, Windsurf) follow the exact same flow: **download from the official site → run the installer → log in → pick a model**.

✅ **Checkpoint:** if you can send a message in the input box and get a reply, you're done.

---

## 3. Installing a CLI agent: OpenCode as an example (some experience needed)

The universal recipe for CLI agents has only three steps: **install Node.js → install globally via npm → configure an API key**.

1. **Install Node.js**: download the LTS version from https://nodejs.org and install with default options. Then open PowerShell and type `node -v` — if a version number appears, it worked;
2. **Install OpenCode**: in PowerShell, run
   ```
   npm install -g opencode-ai
   ```
3. **Configure a model API**: run `opencode auth login`, pick a provider as prompted, and paste your API key (you can apply for a key on any major model platform — many offer free credits);
4. In the folder where you want to work, run `opencode` to enter the chat interface.

Other CLI agents are similar: Claude Code is `npm install -g @anthropic-ai/claude-code`, Gemini CLI is `npm install -g @google/gemini-cli`, Codex CLI is `npm install -g @openai/codex`, and Pi is `npm install -g @earendil-works/pi-coding-agent`. **Kimi Code** is the exception — no Node.js needed, just a one-line PowerShell script (on Windows, install [Git for Windows](https://gitforwindows.org/) first):
```
irm https://code.kimi.com/kimi-code/install.ps1 | iex
```
After installation, each has its own login / key-configuration command.

✅ **Checkpoint:** the terminal shows a chat interface and your messages get replies.

---

## 4. About "connecting a model API"

The agent itself is just the "shell" — how smart it is depends on the model behind it. Two ways to connect:

- **Built-in (desktop apps)**: after logging in, you use the built-in models directly — nothing to configure;
- **Manual API key (CLI agents)**: register on a model platform (OpenAI, Anthropic, Google, DeepSeek, Moonshot/Kimi, Zhipu, etc.) → create an API key → paste it into the CLI's configuration. Keys are billed by usage, and many platforms offer free credits — more than enough for everyday analysis.

> Note: some model platforms have regional availability restrictions — check the platform's terms of service and supported regions before signing up.

---

## FAQ

**Which is the most hassle-free?** For total beginners: WorkBuddy or TRAE. With command-line experience: OpenCode.

**Can I install several at once?** Yes — they don't conflict. Many people keep one desktop app plus one CLI agent.

**Is it free?** Desktop apps are generally free or have a free tier; CLI agents themselves are free, but model APIs are billed by usage (most platforms have free credits).

**What's next after installation?** Go back to the analysis tutorial you want to follow (e.g., "Zero to DEG: Bulk RNA-seq Differential Analysis with an AI Agent") and start copy-pasting prompts from Step 1.
