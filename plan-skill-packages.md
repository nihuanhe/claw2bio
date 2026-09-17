# plan-skill-packages.md — 技能 zip 包（方式 B/C）打包与分发

> 状态：**已执行（2026-09-17 全部完成）**。结果与偏差见文末「## 7. 执行结果」。

## 0. 背景与问题

网站 14 个技能教程页的「获取本技能」区块都有三行：

- 方式 A —— 一键引导 prompt（从 GitHub sparse checkout）→ **已可用**
- 方式 B —— 独立 zip 包（几 MB，腾讯 COS 直链）→ 文案为「打包中，即将上线」
- 方式 C —— 全量示例数据（COS 按 skill 分目录）→ 文案为「打包中，即将上线」

现状核查（2026-09-17）：COS 里只有**依赖包**（clinical-table 14 wheels + 56 R zip、
phylo-tree 91 R zip，共 162 对象），**没有任何技能 zip 包**。所以 B/C 不是漏回填，
是这批包尚未生产。

## 1. 已确认决策（本轮问答）

| # | 决策 |
|---|---|
| 1 | **B 包内容** = `SKILL.md` + `README.md` + `scripts/` + `examples/`，**排除** `resources/`（R 二进制依赖）与大数据文件 |
| 2 | **分发规则（阈值 50 MB/包）**：zip ≤ 50 MB → 放服务器；> 50 MB → 放 COS |
| 3 | 小包放**服务器独立目录**（不进 git）：`/var/www/claw2bio-downloads/`，nginx 加 `location /downloads/` 别名，链接形如 `https://claw2bio.site/downloads/<skill>.zip` |
| 4 | 大包按老规矩：先登记进 `cos-staging/`（manifest.csv）→ 复用 `scripts/sync_cos.py` 同步到 COS |
| 5 | 大文件上传放宽 `sync_cos.py` 上限 100 MB → 5 GB，仍用简单上传保证 COS ETag == md5 |

## 2. 实测体积（决定分流结果）

| 技能 | 技能目录合计 | 其中 examples | 其中 resources(R 依赖) | 预计 B 包 | 去向 |
|---|---|---|---|---|---|
| bulk-RNA-seq | 1077.7 MB | 174.0 | 903.6 | ~174 MB | **COS** |
| scRNA-seq | 108.9 MB | 108.7 | – | ~109 MB | **COS** |
| phylo-tree-build | 89.6 MB | 89.6 | – | ~90 MB | **COS** |
| RNA-seq-enrichment | 55.3 MB | 17.8 | 37.5 | ~18 MB | 服务器 |
| scRNA-seq-pseudotime | 9.5 MB | 9.5 | – | ~9.5 MB | 服务器 |
| RNA-seq-GSEA | 6.4 MB | 3.0 | 3.3 | ~3 MB | 服务器 |
| RNA-seq-gene-plot | 5.0 MB | 5.0 | – | ~5 MB | 服务器 |
| 其余 7 个（qpcr-mrna / qpcr-mtdna / scRNA-seq-virtual-ko / phylo-tree-plot / barplot / clinical-table / survival-curve） | 均 < 1 MB | | | < 1 MB | 服务器 |

即：**11 个小包走网站，3 个大包走 COS**。

## 3. 待你确认的细节（我给出推荐答案）

1. **阈值判定对象**：用「打包后的 zip 体积」而不是文件夹体积 → 推荐 zip 体积（更直观）
2. **examples 内的小文件判定**：B 包是否无条件含整个 `examples/`？
   → 推荐：`examples/` 总量 ≤ 50 MB 的技能，整个 examples 进 B 包；超过 50 MB 的
   （scRNA-seq / bulk-RNA-seq / phylo-tree-build）B 包只含 `examples/input` 与
   ≤20 MB 的示例输出，并附一份 `DATA.md` 指向 C（全量数据）所在位置
3. **C 与 B 重复时怎么处理**：`examples/` 本来就 ≤ 50 MB 的技能，C 行没有独立内容
   → 推荐：C 行改写为「已包含在方式 B 包内」，不再单独提供
4. **`resources/` 里的 R 依赖是否也要托管**（bulk-RNA-seq 有 903 MB）
   → 推荐：本轮**不动**；clinical-table / phylo-tree 的依赖已单独托管，其余等有需求再开阶段
5. **文案微调**：`scRNA-seq-pseudotime`(9.5 MB)、`RNA-seq-enrichment`(18 MB) 与页面
   「几 MB」表述不符 → 推荐改为「几 MB～几十 MB」

## 4. 执行步骤

### 阶段 1 — 打包脚本（仓库交付物）
1. 写 `scripts/build_skill_zips.py`：
   - 技能清单内置 14 个 slug（含各自仓库路径）
   - 排除规则：`resources/`、`.git*`、`*.rds` 超过阈值的大文件、`__pycache__`
   - 输出到 `.build/skill-zips/<slug>.zip`（`.build/` 加进 `.gitignore`）
   - 可重跑：按源文件内容 hash 判断，未变化则跳过重建
   - 输出 `manifest.csv`（沿用 `file,md5,size,example,note` 格式）+ 体积分流表

### 阶段 2 — 本地打包与分流核对
2. 运行脚本 → 得到 14 个 zip 与体积表 → 按 50 MB 分两组，与你核对去向是否符合预期

### 阶段 3 — 小包上服务器（11 个）
3. 写 `scripts/deploy_downloads.py`：按 manifest md5/size 跳过已存在文件，
   sftp 上传到 `/var/www/claw2bio-downloads/`（目录不存在则 sudo 创建并 chown ubuntu）
4. nginx 配置追加 `location /downloads/ { alias /var/www/claw2bio-downloads/; autoindex off; }`
   （改动前备份配置；`nginx -t` 通过后 reload）
5. 校验：`curl -I https://claw2bio.site/downloads/<skill>.zip` 返回 200 且
   `Content-Length` == 本地文件大小；下载回来 md5 与本地一致

### 阶段 4 — 大包上 COS（3 个 + C 全量数据）
6. 放宽 `scripts/sync_cos.py` 的 `MAX_SIMPLE_UPLOAD` 到 5 GB（保持 ETag == md5 校验）
7. 把 3 个大包与 C 全量数据复制进 `cos-staging/<skill>/packages/`，逐文件重算 md5
   写入对应 `manifest.csv`
8. 运行 `sync_cos.py` → 上传 → 二次运行应为全部 skipped（幂等）

### 阶段 5 — 回填文案 + 重新部署
9. 更新 14 技能 × 中英 = **28 个页面**的 B/C 文案为真实链接
   （小包 → `https://claw2bio.site/downloads/<skill>.zip`；大包 → COS 直链）
10. `npm run build` → grep 确认无「打包中」残留 → `deploy_site.py deploy` 部署
11. 同步更新 `cos-staging/README.md` 状态区与 `AGENTS.md`（若涉及）

### 阶段 6 — 验收
12. 逐条核对：每个 B/C 链接可下载、md5 与本地包一致、页面中英双语无占位残留、
    `sync_cos.py` 二次运行全跳过、`deploy_downloads.py` 二次运行全跳过

## 5. 交付物

- `scripts/build_skill_zips.py`（打包，可重跑）
- `scripts/deploy_downloads.py`（小包上服务器，幂等）
- `scripts/sync_cos.py`（放宽上限，幂等逻辑不变）
- `cos-staging/<skill>/manifest.csv`（大包与 C 数据登记）
- nginx 配置新增 `/downloads/` 段（存档 `scripts/nginx-claw2bio.conf` 同步）
- 网站 28 处文案更新

## 6. 风险与回滚

| 风险 | 应对 |
|---|---|
| nginx 改动影响线上站点 | 改前备份配置；`nginx -t` 通过才 reload；出问题一条命令还原 |
| 网站整体重新部署会替换 `/var/www/claw2bio` | downloads 放独立目录，不受影响（这正是选方案一的原因） |
| 大包上传耗时（约 380 MB） | 增量 + 幂等，中断可重跑 |
| B 包「几 MB」文案与实际不符 | 阶段 5 一并微调为「几 MB～几十 MB」 |
| `resources/` 依赖未托管导致 B 包不能离线跑 | 明确写入 `DATA.md`/README：依赖获取路径见技能 README 的 Offline install 小节 |

## 7. 执行结果（2026-09-17）

### 7.1 交付物

- [scripts/build_skill_zips.py](scripts/build_skill_zips.py) — 打包（确定性 zip、跳过未变、
  `--stage-cos` 自动登记 COS 侧产物）
- [scripts/deploy_downloads.py](scripts/deploy_downloads.py) — 小包上服务器（md5 双向校验、幂等）
- [scripts/sync_cos.py](scripts/sync_cos.py) — 上限放宽到 5 GB（ETag == md5 仍成立）
- `cos-staging/<skill>/{zip,data}/` + 对应 manifest.csv（3 个 COS 侧产物）
- nginx 新增 `location /downloads/`（存档同步至 scripts/nginx-claw2bio.conf）
- 网站 18 个技能页 + download/get-started 中英 4 处的链接与措辞

### 7.2 打包与分流结果（实测）

17 个包共 372.78 MB，**14 个 → 服务器 /downloads/，3 个 → COS**：

| 去向 | 包 |
|---|---|
| 服务器（14） | qpcr-mrna / qpcr-mtdna / scRNA-seq / scRNA-seq-pseudotime / scRNA-seq-virtual-ko / RNA-seq-enrichment / RNA-seq-gene-plot / RNA-seq-GSEA / phylo-tree-build / phylo-tree-build-examples / phylo-tree-plot / barplot / clinical-table / survival-curve |
| COS（3） | bulk-RNA-seq/zip/bulk-RNA-seq.zip、bulk-RNA-seq/data/bulk-RNA-seq-examples.zip、scRNA-seq/data/scRNA-seq-examples.zip |

### 7.3 验收证据

- **链接**：17/17 返回 200，`Content-Length` 与 manifest 逐一相符（最大 110,622,239 B）
- **端到端 md5**：服务器侧抽检 clinical-table.zip、COS 侧抽检 bulk-RNA-seq.zip，下载后 md5 与 manifest 一致
- **页面**：5 个抽样页（中英）无「打包中 / being packaged / site launch」残留，
  4 个页面远端内容与本地 dist 逐字节相同（md5 MATCH）
- **幂等**：`sync_cos.py` 二次运行 165 skipped + census 165 对象/529,875,795 B 无 extra/missing；
  `deploy_downloads.py` 二次运行 14 skipped
- **目录防护**：网站重新部署后 `/var/www/claw2bio-downloads/` 14 个文件完好（验证了独立目录设计）
- **安全**：`/downloads/` 目录列表返回 403、不存在文件返回 404

### 7.4 与计划的偏差

1. **分流结果 14/3（原估 11/3）**：按规则「examples >50 MB 才拆分，拆分后 B 只保留
   examples/input 与 ≤20 MB 文件」，scRNA-seq（28 MB）与 phylo-tree-build（19 MB）的 B 包
   缩小到阈值以内，因此改走服务器；bulk-RNA-seq 的 B 包 76 MB 仍超阈值 → COS
2. **`resources/` 排除规则细化**：仅当该子树 > 20 MB 时排除。否则 RNA-seq-GSEA 的
   `resources/gmt`（3.3 MB，离线跑 GSEA 必需）会被连带删除
3. **COS 暂存目录用 `{zip,data}/`**（对齐 cos-staging/README.md 既有约定）而非计划草稿写的
   `packages/`；已把先前的 3 个旧布局对象从 COS 删除，脚本 census 在迁移期正确报出它们为
   extra 并 exit 1（设计如此）
4. **页面回填 18 个而非 28 个**：10 个英文技能页目前是「English tutorial is being prepared」
   占位页，本就没有 B/C 段落；另额外修订 download.md / get-started.md 中英各 2 处一致性措辞
5. **文案由「几 MB」改为写实际体积 + 分发位置**（如「约 76 MB，腾讯 COS 直链」），
   避免与实际不符

### 7.5 对抗审查后的修复（2026-09-17，审查结论「部分完成 85%」）

审查发现 3 个真问题（表层分发达标，包内指针与可运行性未达标），已全部修复并复验：

1. **包内 `DATA.md` 死链**（3 个包全中）：模板硬编码 `/{slug}/packages/…`，实际是
   `/{slug}/data/…`；且 phylo-tree-build 的 C 包其实在**服务器**而上游误指向 COS
   → 改为由分流结果注入（先建 C 包拿到真实体积与 URL，再写 B 包），
   `pkg_url()` 与页面链接同一套规则
2. **`DATA.md` 体积写的是未压缩目录**（174/109/90 MB，实为 87/105/31 MB）
   → 改为引用 C 包 zip 的真实体积
3. **fingerprint 未包含生成内容**：只吃 size+mtime，模板改了也会被判 `unchanged`
   → `fingerprint(entries, texts)` 现在把 `DATA.md` 文本一并纳入；实测再次运行时
   3 个受影响包自动重建、其余 14 个正确报 `unchanged`
4. **误导性文档承诺**：5 处「on COS at launch / COS mirror at launch」在这批依赖
   并未托管的情况下是假承诺 → 全部改为「not mirrored online yet」
   （`bulk-RNA-seq` README/SKILL、`RNA-seq-enrichment` SKILL、`resources/README`）
5. **缓存隐患**：`/downloads/` 与 HTML 由 nginx 加 `Cache-Control: no-cache`
   （同名包原地覆盖后不会给旧包；`/assets/` 保持 `immutable` 不受影响）
6. **`sync_cos.py --dry-run` 原先仍要求密钥**（cos SDK 在构造客户端时就校验），
   与"离线校验 manifest"的用法说明不符 → 把客户端构造移到 dry-run 提前返回之后，
   实测无密钥可跑通并输出 165 文件 / 529,875,872 B，带密钥的真实运行仍为 0 upload / 165 skipped

修复后复验：3 个受影响包（scRNA-seq / phylo-tree-build / RNA-seq-enrichment 走服务器，
bulk-RNA-seq 走 COS）重新上传，`sync_cos.py` 报 1 upload / 164 skipped + census 165 对象
一致；`deploy_downloads.py` 报 3 upload / 11 skipped；17/17 链接仍 200 且大小相符；
下载 phylo-tree-build.zip 实测 md5 一致，包内 `DATA.md` 指向的链接返回 200、
`Content-Length` 32,081,102 B 与文中所写「~30.6 MB」相符。

### 7.6 后续可选（未做，需要时再开）

- 10 个英文技能页的正文化（含 B/C 段落）
- `resources/` 里 R 依赖（bulk-RNA-seq 903 MB）的离线托管
- 整库单一 zip（页面已明确标注「暂不提供」）
