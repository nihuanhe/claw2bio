# 安装你的第一个 AI Agent（Windows 11，零基础友好）

<!-- 本文是配套教程的前置篇：所有"用 AI Agent 做分析"的教程都假设你已经装好了一个 AI Agent 并接入了模型。文中链接均经逐一查证（2026-09）。 -->

AI Agent 就是一个"能听懂人话、替你操作电脑干活"的软件：你用大白话下指令，它自己规划、执行、交付结果。做生信分析时，它负责装环境、跑脚本、出图，你只需要复制粘贴 prompt。

**选哪个？一句话结论：**

- **零基础 + Windows 11** → 装桌面端（图形界面），推荐 **TRAE** 或 **WorkBuddy**；
- **有一定命令行基础** → 装 CLI 类，推荐 **OpenCode**（开源免费、模型随便接）或 **Pi**（极简、可扩展）。

---

## 一、两类 AI Agent 速览

### A. 桌面端（图形界面，零基础友好）

| 名称 | 出品 | 官网（已查证） | 说明 |
|---|---|---|---|
| **WorkBuddy** | 腾讯 | https://www.workbuddy.cn | 全场景 AI 工作台，中文界面，开箱即用 |
| **TRAE** | 字节跳动 | https://www.trae.ai（国际版）｜ https://www.trae.cn（国内版） | AI 原生 IDE，多语言界面 |
| **Qoder** | 阿里巴巴 | https://qoder.com | Agentic 编程平台 |
| Cursor | Cursor（美国） | https://cursor.com | 国际知名 AI IDE，订阅制 |
| Windsurf | Windsurf（美国） | https://windsurf.com | 国际知名 AI IDE，订阅制 |

### B. CLI 命令行类（适合有一定基础的用户）

| 名称 | 出品 | 官网 / GitHub（已查证） | 说明 |
|---|---|---|---|
| **OpenCode** | SST（开源） | https://opencode.ai ｜ https://github.com/sst/opencode | 开源免费，终端里运行，可接任意模型 API |
| **Claude Code** | Anthropic | https://claude.com/product/claude-code ｜ https://github.com/anthropics/claude-code | 第一梯队，需订阅或 API 额度 |
| **Pi** | Mario Zechner（开源） | https://github.com/badlogic/pi-mono ｜ npm `@earendil-works/pi-coding-agent` | 极简可扩展的 coding agent |
| **Kimi Code** | 月之暗面（Moonshot AI） | https://github.com/MoonshotAI/kimi-code | Kimi 官方终端 agent（旧版 kimi-cli 已升级为 Kimi Code），搭配 Kimi 模型（API 平台 platform.moonshot.cn） |
| Codex CLI | OpenAI | https://github.com/openai/codex | OpenAI 官方命令行 agent |
| Gemini CLI | Google | https://github.com/google-gemini/gemini-cli | Google 官方命令行 agent，有免费额度 |
| Aider | 开源社区 | https://aider.chat | 老牌开源 pair-programming 工具 |

> 说明：CLI 类都需要 Node.js 环境，并在终端里用 npm 安装、手动配置模型 API Key——这正是"需要一点基础"的原因。

---

## 二、桌面端安装：以 WorkBuddy 为例（零基础推荐）

1. 打开官网（如 **https://www.workbuddy.cn** 或 **https://www.trae.ai**），点"下载 / Download"，得到 Windows 安装包；
2. 双击安装包，全程默认选项下一步即可；
3. 首次打开按提示注册/登录；
4. 在输入框旁边的模型下拉里选一个模型，就可以开始对话了。

各桌面端（WorkBuddy、TRAE、Qoder、Cursor、Windsurf）流程完全一样：**官网下载 → 双击安装 → 登录 → 选模型**。

✅ **检查点：** 能在输入框里发消息并收到 AI 回复，就装好了。

---

## 三、CLI 类安装：以 OpenCode 为例（有一定基础）

CLI 类的通用套路只有三步：**装 Node.js → npm 全局安装 → 配 API Key**。

1. **装 Node.js**：到 https://nodejs.org 下载 LTS 版，双击安装（默认选项）。装完打开 PowerShell 输入 `node -v`，能看到版本号即成功；
2. **装 OpenCode**：PowerShell 里执行
   ```
   npm install -g opencode-ai
   ```
3. **配模型 API**：执行 `opencode auth login` 按提示选择服务商并粘贴 API Key（各大模型官网都能申请 Key，不少有免费额度）；
4. 在你想干活的文件夹里执行 `opencode`，进入对话界面。

其他 CLI 类似：Claude Code 是 `npm install -g @anthropic-ai/claude-code`，Gemini CLI 是 `npm install -g @google/gemini-cli`，Codex CLI 是 `npm install -g @openai/codex`，Pi 是 `npm install -g @earendil-works/pi-coding-agent`；**Kimi Code** 例外，不需要 Node.js，PowerShell 一行脚本即可（Windows 需先装 [Git for Windows](https://gitforwindows.org/)）：
```
irm https://code.kimi.com/kimi-code/install.ps1 | iex
```
装完都用各自的登录/配 Key 命令接入模型。

✅ **检查点：** 终端里能进入对话界面、发消息有回复。

---

## 四、关于"连接模型 API"

AI Agent 本体只是"壳"，聪明程度取决于背后接的大模型。两种接法：

- **桌面端自带**：登录后直接用内置模型，什么都不用配；
- **CLI 手动配 Key**：到模型平台（OpenAI、Anthropic、Google、DeepSeek、Moonshot/Kimi、智谱等）注册 → 创建 API Key → 粘贴进 CLI 的配置里。Key 按用量计费，很多平台有免费额度，日常分析足够用。

> 注意：部分模型平台存在地区可用性差异，注册前先看该平台的服务条款和可用地区说明。

---

## 常见问题

**装哪个最省心？** 零基础：WorkBuddy 或 TRAE。有命令行基础：OpenCode。

**可以同时装多个吗？** 可以，互不冲突。很多人桌面端 + CLI 各留一个。

**收费吗？** 桌面端一般免费或有免费额度；CLI 本体免费，但模型 API 按用量计费（多数平台有免费额度）。

**装好后干什么？** 回到你要做的分析教程（比如《零基础——用 AI Agent 做 bulk RNA-seq 差异分析》），从第 1 步开始复制粘贴 prompt 就行。
