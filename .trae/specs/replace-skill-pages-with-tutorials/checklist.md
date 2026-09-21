# Checklist

- [ ] website/zh/skills/ 14 个技能页全部为对应中文教程内容，无旧速查格式残留（grep「它能做什么」「快速上手」= 0）
- [ ] website/skills/ 14 个技能页全部为英文教程内容，无 "English tutorial is being prepared" 残留
- [ ] /zh/skills/ai-agent-setup 与 /skills/ai-agent-setup 存在且内容为安装教程
- [ ] 全部页面中《教程-AI-Agent安装.md》引用已改为站内 ai-agent-setup 链接（grep「教程-AI-Agent安装.md」= 0）
- [ ] 教程内 `https://www.claw2bio.site/zh/skills/...` 硬编码全部改为站内相对路径（下载 zip/COS 直链除外）
- [ ] 「待补」占位行全部删除（grep = 0）
- [ ] website/public/tutorials/bulk-rna-seq/ 有 19 张 png，与源文件夹逐张同名同大小
- [ ] 中英 bulk 页图片路径均为 /tutorials/bulk-rna-seq/slideXX.png 且 19 张全对应
- [ ] config.ts 中英 skills 侧边栏置顶 ai-agent-setup；两个 index.md 含安装页入口
- [ ] `npm run build` 无报错；dist 中抽查页面/图片存在
- [ ] 线上复核：中英各 ≥3 个技能页 + 2 个安装页 + ≥3 张截图，HTTP 200 且正文含教程标题关键字
- [ ] git 提交推送完成，`git ls-remote origin` 与本地 HEAD 一致
