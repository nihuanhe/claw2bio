# 网站技能页替换为零基础教程 Spec

## Why
现有 28 个技能页（中 14 + 英 14）是「速查参考」风格，对零基础用户门槛高；用户已备好
`F:\课题-AI-Openclaw\AI-Agent-skill说明书模板\` 全套「全程复制粘贴 prompt」风格教程
（13 技能 × 中英 + bulk 实例 × 中英 + AI-Agent 安装 × 中英），需整体替换上线。

## What Changes
- **website/zh/skills/**：13 个中文教程同名覆盖对应技能页；`实例-bulk-RNA-seq.md` 覆盖
  `bulk-RNA-seq.md`（含 19 张截图）；新增 `ai-agent-setup.md`（AI-Agent 安装教程）
- **website/skills/**：同上，英文版全量覆盖（10 个 stub 页 + 4 个已有完整页一并替换，
  长期任务「英文页占位」随之完成）
- 旧页内容**完全覆盖不保留**（用户已确认：真实图/实测数字/「获取本技能」区块不并入）
- 链接适配：教程内 `https://www.claw2bio.site/zh/skills/X` 硬编码 → 站内相对路径；
  《教程-AI-Agent安装.md》引用 → `/zh/skills/ai-agent-setup`（英文对应 `/skills/ai-agent-setup`）；
  删除「此处插图：待补」等占位行
- 19 张截图（共约 2.4 MB）复制到 `website/public/tutorials/bulk-rna-seq/`（源文件夹名
  `实例-bulk-RNA-seq-v4_imges` 拼写不规范，不沿用），md 内图片路径改为 `/tutorials/bulk-rna-seq/slideXX.png`
- `website/.vitepress/config.ts` 侧边栏：中英 skills 分组置顶「AI-Agent 安装（先读）」
- `website/zh/skills/index.md` 与 `website/skills/index.md` 技能总览：加 ai-agent-setup 入口
- 构建 → 部署 → 线上复核 → git 提交推送

## Impact
- Affected code: `website/zh/skills/*.md`（15 文件）、`website/skills/*.md`（15 文件）、
  `website/.vitepress/config.ts`、`website/public/tutorials/bulk-rna-seq/`（新增 19 png）
- 不影响：技能仓库代码、分发 zip 包、COS、下载链接（教程内 zip/COS 直链保持原样）
- URL 不变（同名覆盖），无 SEO 断链；新增 2 个 URL（中英 ai-agent-setup）

## ADDED Requirements

### Requirement: 中文技能页全部替换为教程风格
website/zh/skills/ 下 14 个技能页 SHALL 被模板对应中文教程全文覆盖（bulk 用实例版），
保留各自文件名不变。

#### Scenario: 访问中文技能页
- **WHEN** 用户访问 `https://claw2bio.site/zh/skills/barplot`
- **THEN** 页面为「零基础——用 AI Agent 画分组柱状图」教程全文，无旧速查内容残留

### Requirement: 英文技能页全部替换为英文教程
website/skills/ 下 14 个技能页 SHALL 被模板对应英文教程覆盖，10 个 stub 占位页消失。

#### Scenario: 访问英文技能页
- **WHEN** 用户访问 `https://claw2bio.site/skills/scRNA-seq-pseudotime`
- **THEN** 页面为英文教程全文，无 "English tutorial is being prepared" 残留

### Requirement: AI-Agent 安装页
新增 `/zh/skills/ai-agent-setup` 与 `/skills/ai-agent-setup`，内容为模板安装教程，
中英侧边栏 skills 分组置顶；各教程开头的安装教程引用 SHALL 指向该站内页面。

#### Scenario: 从教程跳转安装页
- **WHEN** 用户在任一教程页点击安装教程链接
- **THEN** 到达站内 ai-agent-setup 页（非外部链接、非 404）

### Requirement: bulk 实例截图可访问
19 张截图 SHALL 位于 `website/public/tutorials/bulk-rna-seq/`，
bulk 技能页内所有图片路径重写为该绝对路径，线上逐张可访问（HTTP 200）。

#### Scenario: 图片加载
- **WHEN** 用户打开 `/zh/skills/bulk-RNA-seq`
- **THEN** 19 张截图全部正常渲染，无裂图

## MODIFIED Requirements

### Requirement: 教程内链接适配
所有教程内硬编码 `https://www.claw2bio.site/...` 技能页链接 SHALL 改为站内相对路径
（VitePress cleanUrls 风格）；「插图待补」类占位行 SHALL 删除。

#### Scenario: 站内互链
- **WHEN** 构建后全站 grep `www.claw2bio.site/zh/skills` 与「待补」
- **THEN** 均为 0 命中（下载 zip / COS 直链除外，保持原样）

### Requirement: 侧边栏与总览页
config.ts 中英 skills 侧边栏 SHALL 新增置顶 ai-agent-setup 项；
两个 index.md SHALL 增加安装页入口。

## REMOVED Requirements
无（旧页面内容覆盖属于 MODIFIED 范畴，无独立功能移除）。
