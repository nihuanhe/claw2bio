# Claw2Bio 内容上线标准流程（SOP）

> 本文件是「从主库内容到网站 + GitHub 上线」的唯一标准流程。
> 新增 skill、更新既有 skill，都按此执行。
> English version below · 中文在上。

---

## 中文版

### 阶段 0 · 在主库完成内容（先做内容，后做发布）

主库 = 本仓库根目录（`内容整理\`）。所有创作、实战改进都直接沉淀在这里。

1. 每个 skill 必须是标准结构：
   ```
   <阶段目录>/<skill-name>/
   ├── SKILL.md          # agent 面向的定义文件（含 YAML frontmatter: name/description）
   ├── README.md         # 人类阅读的使用说明
   ├── scripts/          # 分析脚本
   ├── examples/
   │   ├── README.md     # 示例说明 + 运行命令 + 预期结果
   │   ├── input/        # 最小可运行输入（几 MB 以内）
   │   └── output/       # 实际跑出来的输出（必须真实生成，不许手写）
   └── .gitignore
   ```
2. skill 命名：小写英文 + 连字符（如 `qpcr-mrna`），放进对应阶段目录
   （`experiment-data/`、`bioinformatics/`、`figure-generation/`）。
3. 设计规范遵守根目录 `ARCHITECTURE.md`（脚本复用铁律、Adapter 模式、examples 强制规则）。
4. 阶段 0 完成标准：脚本在主库实战跑通，examples/output 为真实产出。

### 阶段 1 · 脱敏（sanitization）

逐项检查，缺一不可：

1. **机器路径**：全文检索并替换为通用写法：
   ```bash
   grep -rn "C:\\\\Users\|D:\\\\科研\|workbuddy\|\.workbuddy" <skill目录>
   ```
   - `C:\Users\A\.workbuddy\...\python` → `python`
   - `D:\科研流程技能库\...` → 仓库内相对路径（如 `cd qpcr-mrna`）
2. **个人信息**：姓名、单位、课题编号、内部项目路径（如 `课题-BDE-Treg`）一律移除。
3. **敏感数据**：示例数据必须脱敏/合成，绝不含可识别患者信息。
4. **密钥口令**：全库扫描：
   ```bash
   grep -rniE "password|密码|secret|token|api[_-]?key" <skill目录>
   ```
   注意：`网站构建\腾讯云电脑配置情况.md` 等含密码文件在主库之外，**严禁复制进仓**。
5. **大文件**：单文件 >5 MB 的原始数据（tif、fcs 等）不进 git，走 COS（见阶段 5）；
   根 `.gitignore` 已屏蔽 `*.tif`，新增大文件类型要补进 `.gitignore`。

### 阶段 2 · 英文化（翻译规范）

1. **SKILL.md**：英文为主。YAML frontmatter 的 `description` 英文正文 + 末尾附
   `（中文摘要：…）`。「Trigger phrases」一节中英触发词都保留。
   文末用 `> 中文提示：…` 块放关键注意事项的中文版。
2. **README.md**：英文为主，标题下方放一行中文一句话简介。
3. **examples/README.md**：英文简述即可。
4. 脚本内的 print/注释保持原样（不影响运行）；脚本新增时优先英文输出。

### 阶段 3 · 冒烟测试（必做，跑通即证）

```bash
cd <阶段目录>/<skill-name>
python scripts/<主脚本> examples/input/<输入> examples/output --overwrite   # 按各 skill 实际命令
```

- 输出与 examples/README.md 声明的预期结果一致（数值、P 值、文件数）。
- 测试产生的临时文件要删除，不得混入提交。
- 未跑通的 skill 不进入阶段 4。

### 阶段 4 · git 提交

```bash
git add -A
git status          # 自查：无大文件、无第二批未完成目录、无临时文件
git commit -m "<英文 imperative 摘要>"
```

- 提交前 `git status` 逐行过一遍；`.gitignore` 挡住的东西不该出现。
- 提交信息用英文，一句话说清改动。

### 阶段 5 · 网站教程页（模板固定，双语齐全）

每个 skill 一页，`website/skills/<name>.md` + `website/zh/skills/<name>.md`，
固定 9 节（顺序不可动）：

1. 标题 + 一句话简介（`>` 引用块）
2. 「获取本技能 / Get this skill」`::: info` 区块，三通道：
   - A. 专属引导 prompt（sparse checkout 只拉该 skill 子目录，中英各自版本）
   - B. 独立 zip（COS 直链，上线时替换占位文字）
   - C. 全量数据（COS 按 skill 分目录链接，上线时替换占位文字）
3. What it does + 真实输出示例图
4. Quick start（30 秒跑通示例）
5. Input format（带 CSV 片段）
6. Output files（表格）
7. Parameters（表格）
8. Troubleshooting（≥2 条）
9. Links（GitHub 源码目录 + 相关技能互链）

配套动作：

- 卡片图：从 `examples/output/` 选一张代表性 PNG，复制为
  `website/public/cards/<skill-name>.png`（输出是表格无图的，先用 emoji 占位卡，
  后期补渲染截图）。
- 首页分区卡网格：`website/index.md` + `website/zh/index.md` 对应分区内加卡。
- 侧边栏：`website/.vitepress/config.ts` 两个 locale 的 sidebar 各加一项。
- Skills 索引页：`website/skills/index.md` + `website/zh/skills/index.md` 表格加行。

### COS 存储约定（大文件分发）

> 2026-07 随 scRNA-seq skill 项目建立，后续 update 直接改本节。

- **本地暂存区** = 根目录 `cos-staging/`（不进 git）。目录层级与仓库阶段目录一一对应：
  `cos-staging/<阶段目录>/<skill容器目录>/<skill-name>/{data,zip,manifest.csv}`。
  详见 `cos-staging/README.md`。
- **manifest 制度**：每个走 COS 的 skill 必须有 `manifest.csv`（`file,md5,size,example,note`），
  「哪个数据是哪个」以 manifest 为唯一权威；skill 仓库内的 `examples/manifest.csv` 记录
  每个 example 对应的数据集/GEO 号/存储位置（repo / geo / cos 链接）/md5。
- **什么上 COS**：自产数据（GEO 下不到的）、per-skill 独立 zip、大体量 R 依赖包；
  GEO 能下载的只记链接不重复上传；几 MB 的合成/降采样 fixture 直接进 git。
- **上传后回填**：COS 直链写回 `website/download.md`、各教程页「获取本技能」区块、
  以及对应 manifest；bucket 名与域名绑定后更新本节。

### 阶段 6 · 构建与发布

```bash
cd website
npm run build      # 必须无死链报错
```

- 本地 `npm run preview` 检查：中英互跳、图片加载、prompt 复制块格式。
- 部署（plan 第 3 步时执行）：dist 上传腾讯云 nginx + GitHub Pages 镜像；
  COS 上传全量数据 + 按 skill zip（打包脚本），替换教程页占位链接；
  Zenodo 存档拿 DOI 后更新 Citation 页。

### 更新既有内容（非新增）时

走同一流程的删减版：改主库 → 阶段 1 脱敏复查 → 涉及文档改动走阶段 2 →
阶段 3 重跑冒烟 → 阶段 4 提交 → 教程页同步改 → 阶段 6 构建发布。
**铁律：先改主库，再同步网站；绝不出现网站与仓库内容漂移。**

---

## English version

### Phase 0 · Finish content in the master library first

The repo root is the single source of truth. Every skill uses the standard layout
(`SKILL.md` with YAML frontmatter, `README.md`, `scripts/`, `examples/` with real
input + real output). Skill names are lowercase-kebab-case and live under the stage
folder matching their purpose. Follow `ARCHITECTURE.md` conventions. Phase 0 is done
when the scripts ran successfully in real lab work and `examples/output` is genuine
script output.

### Phase 1 · Sanitization (checklist, all mandatory)

1. Machine paths: `grep -rn "C:\\\\Users\|D:\\\\科研\|workbuddy" <skill>` — replace with
   generic `python` and repo-relative paths.
2. Personal/institutional identifiers and internal project paths: remove.
3. Example data must be de-identified or synthetic.
4. Secrets scan: `grep -rniE "password|密码|secret|token|api[_-]?key" <skill>`.
5. Files >5 MB never enter git (they go to COS); extend the root `.gitignore`
   for new large file types.

### Phase 2 · Translation

`SKILL.md`: English-first; `description` ends with a `（中文摘要：…）`; trigger phrases
stay bilingual; key notes get a closing `> 中文提示：…` block. `README.md`:
English-first with a one-line Chinese intro under the title. `examples/README.md`:
short English is fine.

### Phase 3 · Smoke test

Run the bundled example exactly as documented; outputs must match the expected
results in `examples/README.md`. Delete temporary test artifacts before committing.
No commit without a passing smoke test.

### Phase 4 · Commit

`git add -A` → review `git status` line by line → commit with a one-line English
imperative message.

### Phase 5 · Website tutorial pages (fixed 9-section template, bilingual)

Create `website/skills/<name>.md` and `website/zh/skills/<name>.md` with the fixed
section order: (1) title + one-liner, (2) "Get this skill" info block with three
channels (per-skill onboarding prompt / standalone COS zip / full COS dataset),
(3) What it does + real output image, (4) Quick start, (5) Input format,
(6) Output files, (7) Parameters, (8) Troubleshooting, (9) Links.
Then: copy a representative output PNG to `website/public/cards/<name>.png`, add a
homepage card in both `index.md` files, register the page in both sidebar locales in
`.vitepress/config.ts`, and add a row to both skills index pages.

### Phase 6 · Build & publish

`cd website && npm run build` must pass with zero dead links. Verify locally with
`npm run preview` (locale cross-links, images, prompt blocks). Deployment (Tencent
nginx + GitHub Pages mirror + COS links + Zenodo DOI) happens at the public launch
milestone defined in plan.md.

### Updating existing content

Same pipeline, shortened: edit the master library → re-check sanitization →
translate if docs changed → re-run the smoke test → commit → sync the tutorial page
→ build & publish. **The library leads, the website follows — never let them drift.**
