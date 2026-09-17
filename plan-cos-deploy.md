# plan-cos-deploy.md — COS 依赖包上传 + claw2bio.site 上线（2026-09-17）

> 状态：**已执行（2026-09-17 全部完成）**。结果摘要与偏差见文末「## 6. 执行结果」。

## 0. 已查证事实（2026-09-17，腾讯云控制台实地核对）

| 项目 | 事实 |
|---|---|
| 服务器 | 轻量应用服务器 1 台：广州 ap-guangzhou，2C8G / 80GB，Ubuntu 24.04 LTS，IP `119.91.105.37`，运行中，2027-06-21 到期 |
| 服务器现状 | 80 端口已有旧占位站「BioCloud Analyzer」（Web 服务已装，执行时确认 nginx） |
| DNS | DNSPod 管理：`@` A→119.91.105.37、`www` A→119.91.105.37，另有旧 `_dnsauth` TXT |
| ICP | 已备案：**粤ICP备2026052114号**（-1 生物信息数据分析，绑定本机 IP，正常） |
| HTTPS | TrustAsia 免费证书已于 **2026-07-04 过期**，免费额度 0/50 可重新申请 |
| COS | 2 桶均私有：`my-website-1358159656`（0 B，复用）、`paper2026-1358159656`（不动） |
| cos-staging | clinical-table（14 wheels + 56 R zips）+ phylo-tree（91 R zips），两份 manifest（`file,md5,size,example,note`）与磁盘逐文件 md5 一致（前次任务已验证） |

## 1. 已确认决策

1. **服务器**：复用现有轻量服务器，nginx 托管 `website/.vitepress/dist/`
2. **COS 桶**：复用 `my-website-1358159656`，改权限为**公有读私有写**；不开 CDN
3. **直链格式**：`https://my-website-1358159656.cos.ap-guangzhou.myqcloud.com/<key>`
4. **上传工具**：自写 Python 增量同步脚本（cos-python-sdk-v5），密钥只走环境变量
5. **回填范围**（验收按此解释）：仅依赖包 2 处 README 直链 + cos-staging 状态区 + ICP footer；
   14 个教程页与 download.md 的「方式 B zip」占位**本轮不动**（zip 尚未打包，属后续阶段）
6. **SSH**：root 密码方式（仅本会话环境变量，绝不落盘/git）；部署脚本用 paramiko
7. **执行中如遇 nginx 配置与计划冲突**（如装的不是 nginx）：停下来汇报，不擅自换方案

## 2. 需要你提前准备的（执行到对应步骤前给我即可）

- **COS 凭据**：控制台「访问管理 → API 密钥」的 SecretId/SecretKey（或现场新建子账号密钥，最小权限 COS 读写）——仅注入本会话环境变量
- **root 密码**：服务器 SSH 密码（或执行时你在轻量控制台确认端口 22 已放行 + 提供密码）

## 3. 执行步骤

### 阶段 A — 本地环境 + 脚本交付物（仓库 scripts/）

- A1. `pip install cos-python-sdk-v5 paramiko`（仅本机环境，不进仓库）
- A2. 写 `scripts/sync_cos.py`：
  - 读 `COS_SECRET_ID` / `COS_SECRET_KEY` 环境变量，缺则报错退出（密钥零硬编码）
  - 遍历两份 manifest.csv，本地逐文件重算 md5/size 与 manifest 交叉校验，不一致即中止
  - 对象 key = `<skill-name>/<manifest.file>`（如 `clinical-table/deps/python/xxx.whl`）
  - 增量逻辑：先 head_object，ETag == 本地 md5（简单上传保证）且 size 相符 → 跳过；
    否则 put_object 上传，传后 head 复验 ETag/size，失败重试 1 次后中止
  - 收尾输出：uploaded / skipped / 失败清单 + 对象总数与总大小 vs manifest 合计；总数或字节不符 → exit 1
  - 幂等：第二次运行必须全部 skipped
- A3. 写 `scripts/deploy_site.py`（paramiko）：读 `LH_SSH_PASSWORD` 环境变量；
  打包 dist → sftp 上传 → 服务器解压到目标 webroot → 执行 nginx 配置检查/重载（命令序列见阶段 D）

### 阶段 B — COS 桶准备与上传

- B1.（控制台，opencli 操作）`my-website-1358159656` 权限改「公有读私有写」；确认桶无静态网站/CDN 绑定
- B2. 你提供 SecretId/Key → 注入会话环境变量 → 首次运行 `sync_cos.py` 上传 161 个对象（约 211 MB）
- B3. 校验：
  - 脚本自报 161/161、总大小与 manifest 合计一致
  - **第二次运行全部 skipped**（幂等验收）
  - 公网直链抽查 3 个对象（wheel / 小 zip / stringi 大 zip）`curl` 下载 → md5 与 manifest 一致
- B4. 若抽查有失败对象：修复后仅重跑脚本（增量特性保证不重传）

### 阶段 C — 占位回填 + 重新 build

- C1. [figure-generation/clinical-table/README.md](figure-generation/clinical-table/README.md)「Offline install」：
  「COS direct links: added at site launch」替换为 deps/python 与 deps/r-win 两个 COS base 直链
  （base URL + 文件名清单见 manifest.csv），并给 1 个示例文件直链
- C2. [bioinformatics/phylo-tree/phylo-tree-plot/README.md](bioinformatics/phylo-tree/phylo-tree-plot/README.md) 同节替换为 deps/r-win base 直链 + 示例
- C3. [cos-staging/README.md](cos-staging/README.md) 状态区：勾选「bucket 创建与域名绑定」（改为复用桶+公有读+桶 URL）与「上传同步脚本」（指向 scripts/sync_cos.py + 日期）
- C4. [website/.vitepress/config.ts](website/.vitepress/config.ts) footer：`ICP备案号待填` →
  `粤ICP备2026052114号`（保留 beian.miit.gov.cn 链接）
- C5. `npm run build`（在 website/）；确认 dist 内含备案号与新直链、无占位残留（grep 验证）

### 阶段 D — 部署到服务器

- D1. 你提供 root 密码 → 环境变量；先用 paramiko 探测：`nginx -v`、现有 server 配置、webroot 位置、
  旧「BioCloud Analyzer」站点结构（先备份其 nginx 配置与 webroot 再动）
- D2. 上传 dist 到 `/var/www/claw2bio/`（具体路径以 D1 探测为准），保留旧站备份目录
- D3. 写/改 nginx server 块：`server_name claw2bio.site www.claw2bio.site`，root 指向新目录，
  `try_files $uri $uri.html $uri/ =404`（VitePress 友好），gzip 开启；`nginx -t` 通过后 reload
- D4. HTTP 冒烟：`curl http://claw2bio.site/` 返回新首页（此阶段 HTTPS 未配，先验证 80）

### 阶段 E — HTTPS 证书

- E1.（控制台，opencli 操作）重新申请免费证书：claw2bio.site + www，DNSPod 自动加 `_dnsauth` TXT 验证；
  旧 TXT 过期记录先清理（控制台确认）
- E2. 签发后从控制台下载证书包（nginx 格式），上传服务器 `/etc/nginx/certs/`（权限 600）
- E3. 配置 443 server 块 + 80 → 301 跳转 https；`nginx -t` → reload
- E4. `curl https://claw2bio.site/` 验证证书链有效、无告警

### 阶段 F — 端到端验收（对照任务验收标准）

- F1. COS：对象数量/总大小 == manifest 合计（脚本报告 + 控制台复核）；抽查 md5 相符；二次运行全跳过
- F2. 网站公网 HTTPS：首页 / 技能总览 / 任一教程页（中英双语各抽 1 页）内容与本地 dist 一致
  （比对关键字符串 + 资源 200）
- F3. 占位直链：README 中示例直链可下载且 md5 == manifest
- F4. cos-staging/README.md 状态区两勾选项 + 备案号 footer 上线可见
- F5. 清理：会话环境变量中的密钥/密码失效（仅进程内，自然失效）；浏览器会话关闭

### 阶段 G — 收尾

- G1. 更新本 plan 状态为「已执行」+ 结果摘要；列出与计划的偏差
- G2. 触发对抗审查 skill（独立 agent 审任务完成度/漏洞/优化空间）
- G3. git 提交与否征求你意见（默认不自动 commit）

## 4. 安全红线

- SecretId/Key、root 密码：只进会话环境变量，绝不写入任何文件、脚本、git、dist
- 提交前 grep 自查仓库与 dist 无 `SECRET|password|119.91` 之外的敏感串
- 服务器操作全部留命令记录（脚本输出），可回溯

## 5. 回滚预案

- 网站回滚：旧 webroot 备份目录 + 旧 nginx 配置备份，一条 `mv` + reload 即可还原
- COS 回滚：桶内对象删除即可（无 CDN/域名绑定，无残留影响）
- 证书回滚：无（原证书已过期，现状 HTTPS 本就是坏的）

## 6. 执行结果（2026-09-17）

### 6.1 结果摘要

- **COS（阶段 B）**：162/162 对象上传成功，合计 248,249,538 B；二次运行全部 skipped（幂等 ✓）；
  公网直链 md5 抽检 5/5 MATCH（formulaic wheel / stringi zip / R6 zip + README 示例 numpy wheel、ggtree zip）
- **回填 + rebuild（阶段 C）**：clinical-table 与 phylo-tree-plot 两处 README 直链、cos-staging 状态区 3 项勾选、
  footer 备案号（粤ICP备2026052114号）全部落位；`npm run build` 通过，grep 无占位残留
- **部署（阶段 D）**：nginx 1.24.0 复用；旧站备份 `/home/ubuntu/biocloud-backup-20260917.tar.gz`（webroot+配置+ssl）；
  dist（198 文件 / 14 MB）部署至 `/var/www/claw2bio/`；HTTP 冒烟服务器本地与公网域名均 200
- **HTTPS（阶段 E）**：certbot（Let's Encrypt）签发 claw2bio.site + www，2026-12-16 到期，自动续期已配置；
  80→443 301 生效；`ssl_verify_result=0`（证书链无告警）
- **端到端验收（阶段 F）**：5 个页面（en/zh 首页、zh 教程页、download、skills 总览）远端 MD5 == 本地 dist 5/5 MATCH；
  ICP footer 中英双语在线；首页与中文教程页截图渲染正常
- **交付物**：[scripts/sync_cos.py](scripts/sync_cos.py)（幂等增量同步）、[scripts/deploy_site.py](scripts/deploy_site.py)
  （paramiko 部署）、[scripts/nginx-claw2bio.conf](scripts/nginx-claw2bio.conf)（线上 nginx 配置存档）

### 6.2 与计划的偏差

1. **对象数 162 而非 161**：多 1 个为 `phylo-tree/deps_links.md`（WSL2 链接清单，按约定登记进 manifest），合理
2. **桶权限改法**：控制台 SPA 点击不导航 → 改用 COS SDK `put_bucket_acl` 完成公有读私有写
3. **SSH 接入**：实际账号为 ubuntu（非 root）；用户原密码登录失败（OrcaTerm 同样失败）→
   经用户同意改用 CAM API 密钥调 Lighthouse `ResetInstancesPassword` 重置后接入
4. **阶段 E 整段路径变更**：控制台 SSL 页面 iframe 跨域无法自动化，经用户选定改走
   **certbot / Let's Encrypt**（服务器端自动签发+自动续期），未使用腾讯云 TrustAsia 免费证书
5. **webroot 权限**：`/var/www` 需 `sudo mkdir + chown ubuntu` 后方可部署（脚本本身不变）
6. **F2 验收方式升级**：由「关键字符串比对」升级为 5 页面远端 vs 本地 MD5 全等比对（更强）

### 6.3 对抗审查与当轮修复（2026-09-17）

审查结论「部分完成 85%」，以下 4 项已当场修复并留痕：

1. **certbot 续期实证**：`certbot renew --dry-run` 成功（simulated renewals succeeded）；
   `certbot.timer` 每天 18:59 自动运行
2. **sync_cos.py 加固**（对照计划 A2 补漏）：put+verify 失败重试 1 次；head 异常不再裸吞
   （404 之外打 warn）；新增 **list_objects 独立 census**（不再依赖自身计数器）：
   复跑结果 162 skipped + census 162 objects / 248,249,538 B，无 extra/missing/sizediff
3. **443 暴露面收敛**：主 server 块移除 IP/`_`；新增 `ssl_reject_handshake on` default 块——
   实测 `https://119.91.105.37/` TLS 握手被拒（exit 35），域名访问不受影响（200）
4. **SSH 防 MITM**：deploy_site.py 弃用 AutoAddPolicy，固定 ed25519 host key 指纹
   （可用 LH_SSH_HOSTKEY 覆盖），复测连接正常

审查项中**不属于代码、需用户决策/操作**的，见 6.4。

### 6.4 待用户处理/决策

1. **凭据轮换（建议立即）**：COS SecretId/Key、服务器密码、CAM 密钥均已出现在聊天记录
2. **在线占位文案失真**：download.md 与 14+ 教程页「方式 B/C」仍写「网站上线前提供」，
   站点已上线、文案与现实矛盾（此前决策为本轮不动）；若要改需 rebuild + redeploy
3. **git commit**：本次交付物（3 个脚本 + 2 处 README + cos-staging README + config.ts + plan）
   尚未提交（工作区还有更早任务的未提交改动，需一并梳理）
4. [低] README 直链 base URL 以 `/` 结尾时浏览器打开返回对象列表 XML（COS 正常行为），可在 README 注明
