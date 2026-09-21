# plan-batch2-deps.md — 服务器备份清理 + Batch-2 五技能上架 + bulk R 依赖 COS 托管

> 2026-09-21 ｜ 用户已批准三项任务并确认四项决策：
> ① Batch-2 连网站教程页一起上架；② 缺文档的技能补写后上架；
> ③ 181 MB tif 示例 COS 存全量 + git 留小 fixture；④ bulk R 依赖上 COS + 教程加说明。
> 本计划等你核准后执行。

---

## 阶段 0 — 服务器备份目录清理（最简单，先做）

- `sudo rm -rf` 三个目录：`/var/www/claw2bio.bak-pre-deploy`（坑 #8 遗留套娃）、
  `/var/www/claw2bio.bak-20260921-102250`、`/var/www/claw2bio.bak-20260921-104423`
- 保留 `/var/www/claw2bio`（现役）与 `/var/www/claw2bio-downloads`
- 通过 `deploy_site.py exec` 执行；删前列目录确认目标，删后 `ls /var/www` 复核

## 阶段 A — Batch-2 五技能清洗（逐个做，做完整一个再下一个）

统一目标形态（对齐现有 14 技能规范）：`SKILL.md` + `README.md` + `scripts/` +
`examples/{input,output,README.md}`，示例小 fixture 进 git，全量大文件走 COS。

| # | 技能（slug 建议） | 现状 | 要做的事 |
|---|---|---|---|
| A1 | `compress-image` | 完整（SKILL/README/脚本齐），示例 tif 181 MB | 原 tif → `cos-staging/compress-image/data/` 上 COS；生成几 MB 小图做 git 示例；**用自带脚本跑通小示例**验证 |
| A2 | `OFT` | 容器含 3 个子技能（各有 SKILL.md），顶层仅 README | 顶层补 SKILL.md 总览（路由到 3 个子技能）；作为**单一 slug `OFT`** 上架；跑通 `2_oft-analysis` 示例验证 |
| A3 | `IF-免疫荧光`（slug `if-contrast`） | 仅 1 个子技能（ijm 宏），无顶层文档，示例 tif 181 MB | 补写顶层 SKILL.md + README；子技能结构保留；tif → COS + 小 fixture；ijm 是 ImageJ 宏，本机无法跑 → 标注「需在 Fiji/ImageJ 中运行」，以语法审查代替跑通 |
| A4 | `WB-imageJ-定量`（slug `wb-imagej`） | 无 SKILL.md；docs + wb_pipeline.py + 示例 csv | 补写 SKILL.md + README；**跑通 wb_pipeline.py 示例**验证 |
| A5 | `brain-if-atlas-annotate` | 无 SKILL.md/README；200 张脑图谱 PNG 41.5 MB + 转换脚本 | 补写 SKILL.md + README（资源型技能：图谱 PNG 是核心资产，41.5 MB < 50 MB 阈值，随 zip 走服务器）；跑通 `convert_bregma_to_white_lines.py` 验证 |

A6 收尾（5 个都完成后）：
- 根 `.gitignore` 移除 5 行 Batch-2 屏蔽
- `AGENTS.md` 索引表加 5 行（experiment-data 加 IF/OFT/WB，figure-generation 加 brain-if/compress-image）
- `scripts/build_skill_zips.py` 的 `SKILLS` 字典加 5 项
- 跑 `build_skill_zips.py --stage-cos` 打 5 个新包；≤50 MB 走 `deploy_downloads.py`，超阈值走 COS
- `website/download.md` + `zh/download.md` 加 5 个下载条目

**执行铁律**：只用各技能自带脚本跑验证，不现写分析代码；补写的只有 SKILL.md/README 文档。

## 阶段 B — 网站教程页（5 技能 × 中英 = 10 页新写）

- 按 `F:\课题-AI-Openclaw\AI-Agent-skill说明书模板\` 的「零基础复制粘贴」风格新写
  10 个教程页：`website/{,zh/}skills/{if-contrast,OFT,wb-imagej,brain-if-atlas-annotate,compress-image}.md`
- Step 结构对齐现有教程（装技能 → 配环境 → 跑示例 → 换自己数据 → 更多分析）；
  zip 链接指向阶段 A 产出的真实包；无真实运行截图的留「结果说明」文字即可，不放假图
- `config.ts` 中英侧边栏对应分组加 5 项；中英 `skills/index.md` 表格加 5 行
- slug 含中文的问题：`OFT` 目录名大写、`if-contrast`/`wb-imagej` 用英文 slug，URL 全英文

## 阶段 C — bulk-RNA-seq R 依赖 903 MB 上 COS

- 复制 `bioinformatics/bulk_RNA_seq/bulk-RNA-seq/resources/` →
  `cos-staging/bulk-RNA-seq/deps/r-win/`（OrgDb 三包 + r-deps/ 284 文件，平铺），
  按 cos-staging/README 规则 6/8 逐文件登记 `manifest.csv`（file,md5,size,example,note）
- `$env:COS_SECRET_ID/KEY` 注入后跑 `python scripts\sync_cos.py`（幂等），
  传后 census 复核
- 本地 `resources/` 保留不动；git 不动
- bulk 教程（中英 `bulk-RNA-seq.md`）Step 2 加「离线安装」小节：COS 直链 +
  下载后 `install.packages(..., repos=NULL)` 指引；`download.md` 中英各加一条说明

## 阶段 D — 收口

1. `npm run build` → `deploy_site.py deploy` → 线上复核（新页面 200 + 关键字、新 zip 真实下载 + md5、COS 直链抽检）
2. git 提交推送（坑 #16 同命令一条龙），分两到三个 commit（技能清洗 / 网站页 / 依赖说明）
3. `HANDOFF.md` 第五节更新：Batch-2、R 依赖两项标记完成
4. adversarial-review

## 风险与回滚

- IF 的 ijm 宏无法本机跑通 → 页面如实标注，不算阻塞
- COS 上传 ~1.1 GB（903 MB 依赖 + ~360 MB tif），家里带宽下需耐心；sync_cos 幂等可断点重跑
- 所有新 zip 确定性输出，重打可复现；线上任何一步出问题可用 git 历史 + 服务器备份回滚

## 预估提交物

- git：5 个技能目录（清洗后）、5 个 zip 小包链接、10 个教程页、config/index/download 更新、AGENTS.md、.gitignore
- COS：bulk deps 903 MB + 2 个 tif 全量包 + 可能 1-2 个超 50 MB 的技能 zip
- 服务器：3 个 bak 目录删除、新小包进 `/var/www/claw2bio-downloads/`
