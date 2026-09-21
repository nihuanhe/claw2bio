# Tasks

- [x] Task 1: 链接与占位适配脚本化处理准备
  - [x] 1.1 grep 盘点：域名硬编码、安装教程引用、待补占位、图片相对路径
  - [x] 1.2 确认 bulk 教程内 COS 直链与 zip 链接保持原样不改
- [x] Task 2: 落地中文站——13 个教程同名覆盖 `website/zh/skills/*.md`，
  `实例-bulk-RNA-seq.md` → `bulk-RNA-seq.md`，新增 `ai-agent-setup.md`；全部完成链接适配
- [x] Task 3: 落地英文站——同 Task 2，`website/skills/` 下 14 页 + `ai-agent-setup.md`
- [x] Task 4: 截图落地——19 张 png 复制到 `website/public/tutorials/bulk-rna-seq/`，
  中英 bulk 页图片路径改为 `/tutorials/bulk-rna-seq/slideXX.png`，逐张核对文件名一一对应
- [x] Task 5: 站点配置——`config.ts` 中英 skills 侧边栏置顶 ai-agent-setup；
  中英 `skills/index.md` 加入口；全站 grep 确认无旧教程残留引用（如「打包中」「being prepared」）
- [x] Task 6: 本地构建验证——`npm run build` 通过；dist 中抽查页面与图片存在；
  全站 grep 无 `www.claw2bio.site/zh/skills` 硬编码、无「待补」、无 stub 文案
- [x] Task 7: 部署与线上复核——注入 `$env:LH_SSH_PASSWORD`，
  `python scripts\deploy_site.py deploy website\.vitepress\dist /var/www/claw2bio`；
  curl 抽查：中英各 3 个技能页 + 2 个 ai-agent-setup + 3 张截图（HTTP 200 且含教程标题）；
  CDN 注意：以页面正文关键字命中为准，不只看状态码
- [ ] Task 8: git 提交推送——按坑 #16 铁律同一条命令内完成
  `GIT_OBJECT_DIRECTORY` 一条龙，commit + push，复核 `git ls-remote` 一致

# Task Dependencies
- Task 2/3 依赖 Task 1（替换规则清单）
- Task 4 与 Task 2/3 并行可做，但 bulk 页图片路径修改在 Task 2/3 内完成
- Task 5 依赖 Task 2/3（页面存在后才能配侧边栏）
- Task 6 依赖 Task 2–5
- Task 7 依赖 Task 6
- Task 8 依赖 Task 7
