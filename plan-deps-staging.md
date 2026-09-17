# Plan：依赖包离线暂存 + 跑前依赖预检（clinical-table / phylo-tree）

日期：2026-09-17 ｜ 状态：**已核准并执行（2026-09-17）**

## 用户需求（原话）

"类似 cos-staging，把临床表格，树状图这部分可能用到的依赖包放这里，然后调整
readme 和最开始代码（跑代码脚本之前先验证本地依赖的安装情况）。"

## 已核准的 4 项决策（AskUserQuestion）

1. **平台**：Windows 优先（win_amd64 Python wheels + R Windows binary zip）；Linux/macOS 只给在线安装命令
2. **phylo-tree-build 的 WSL2 侧**（apt+conda，GB 级）：不落盘大件，只放**依赖链接清单** + 增强 00 脚本自检 + 新增 WSL 侧 check 脚本
3. **phylo-tree-plot 的 R 包**（ggtree 系 Bioconductor 闭包）：**Windows binary 全闭包**离线打包
4. **预检形态**：每 skill 独立 check 脚本；各 README 快速上手第一步固定为跑 check；**verbatim R 复现脚本（clinical-table pipeline 9+1 个）内部不加任何代码**

## 目标目录结构（cos-staging 新增部分，扁平：一级子文件夹 = skill 名）

```
cos-staging/
├── README.md                                  # 改：补 deps/ 约定（依赖包按 skill 名平铺，一级两层）
├── clinical-table/                            # 临床表格依赖
│   ├── deps/python/                           # win_amd64 wheels（pandas/numpy/scipy/statsmodels 闭包）
│   ├── deps/r-win/                            # logistf 闭包 binary zip（base/recommended 不打）
│   └── manifest.csv
└── phylo-tree/                                # 树状图依赖（build + plot 合并一个文件夹）
    ├── deps/r-win/                            # ggtree 系 8 包全闭包 binary zip（plot 用）
    ├── deps_links.md                          # build WSL2 侧依赖清单（名称/版本/渠道/下载链接）
    └── manifest.csv
```

manifest.csv 沿用 cos-staging README 既有规范：`file,md5,size,example,note`。
（注：deps 采用 skill 名扁平结构，与 README 原「阶段目录/容器/skill」数据目录约定
不同层——README 更新时写明"依赖包按扁平 skill 名存放"。）

## 执行步骤

### w1. clinical-table 离线包生成
- Python：查本机 `python --version`，以本机小版本为准 `pip download --only-binary=:all:
  --platform win_amd64 --python-version <本机>` 下载 4 包闭包到 `deps/python/`
  （README 注明其他 Python 小版本走在线命令）
- R：用本机 Rscript（`D:\myfile\R_2025\R-4.5.2\bin\x64\Rscript.exe`）+
  `tools::package_dependencies(recursive=TRUE)` 求 logistf 闭包，
  剔除 base/recommended（survival 随 R 自带），`download.packages(type="win.binary")`
  到 `deps/r-win/`

### w2. phylo-tree 离线包生成
- 同法求 `c("ggtree","treeio","ggplot2","ggnewscale","RColorBrewer","viridis",
  "cowplot","phytools")` 全闭包（repos = CRAN + BiocManager::repositories()，
  type="win.binary"），剔除 base/recommended 后全量下载到 `phylo-tree/deps/r-win/`
  （build 侧无落盘包，deps_links.md 见 w5）
- `cos-staging/clinical-table/manifest.csv` 与 `cos-staging/phylo-tree/manifest.csv`
  各自登记（逐文件 md5/size/note="离线依赖 win_amd64"）

### w3. 预检脚本
- 新增 `clinical-table/scripts/check_deps.py`：find_spec 检查 pandas/numpy/scipy/
  statsmodels，中文友好输出 + 确切安装命令（在线 pip + 离线
  `pip install --no-index --find-links deps/python`）
- 新增 `clinical-table/scripts/check_deps.R`：检查 logistf（及闭包），
  输出在线 `install.packages` 与离线 `install.packages(repos=NULL, type="win.binary")`
  两种命令；放 `scripts/` 根，**不进 pipeline/**（verbatim 区不动）
- `phylo-tree-plot/scripts/check_deps.R`（已存在）：核对覆盖 8 包，输出补离线安装提示
- 新增 `phylo-tree-build/scripts/check_env.sh`（WSL 侧只查不装）：
  iqtree2/mafft/bcgTree.pl/parsnp/harvesttools/python3 逐项 which+版本，
  缺哪项提示对应安装渠道（apt/bioconda）；`00_bootstrap_ubuntu.sh` 尾部加一行
  "装完可跑 check_env.sh 复核"指引（最小 diff）

### w4. README 更新（4 份）
- `clinical-table/README.md`：Layer 1 / Layer 2 快速上手**第一步改为跑 check 脚本**；
  新增「离线安装（Windows）」小节指向 deps/ 目录（COS 直链占位，上线回填）
- `phylo-tree-plot/README.md`：快速上手第一步跑 check_deps.R + 离线安装小节
- `phylo-tree-build/README.md`：第 0 步前加可选 `bash scripts/check_env.sh` 预检；
  新增「WSL2 依赖清单」小节指向 cos-staging 的 deps_links.md（含链接）
- `cos-staging/README.md`：补 `deps/python|deps/r-win` 目录约定与"离线依赖也走 manifest"规则

### w5. build 侧依赖链接清单
- `cos-staging/phylo-tree/deps_links.md`：iqtree（apt 2.0.7）、mafft（apt 7.505）、bcgtree（bioconda）、
  parsnp/harvesttools（bioconda，含 1.5.2 segfault→1.7.4 备选记录）、各官方上游链接；
  Ubuntu 镜像源（清华/阿里）加速说明

### w6. 验证 + 收尾
- 离线闭包烟测：`pip install --no-index --find-links deps/python --target <临时目录>
  pandas statsmodels` 全新解析安装通过；R 侧 temp lib 装 logistf binary zip 通过 +
  全部 zip 完整性校验（数量与 manifest 一致）
- 三个 check 脚本本机实测通过（Python/R/bash 各一）
- 全仓 grep：README 引用的脚本路径与实际文件一致；cos-staging README 与实际结构一致
- 对抗审查 + 交付总结

## 对抗审查修复轮（2026-09-17，w6 内完成）

一轮审查发现致命缺陷：**phylo-tree 闭包缺 44 包**——首跑用 CRAN-only
`available.packages()` 算闭包，ggtree/treeio（Bioc 包）解析为 NA，整棵依赖子树
被静默丢弃；且首版 R 烟测因本机所有包都在系统库（.Library）泄漏而假绿。修复：

1. 合并 db（aliyun CRAN + 官方 Bioc 3.22，win.binary）重算闭包 → 补下 44 个
   zip，bundle 现 **91 个**；manifest 重生成（92 数据行）
2. **静态闭包证明**（不依赖网络/本地库）：逐 zip 解 DESCRIPTION 走
   Depends/Imports/LinkingTo，断言全部 ⊆ bundle∪base/recommended——两个
   bundle 均 GAP: none（codetools 自 R 4.5 起为 recommended，已正确剔除）
3. 真烟测：清空 R_LIBS_USER/SITE + `.libPaths(lib)` + 91 zip 全新 lib 安装
   + `requireNamespace("ggtree")` 通过（注：本机 .Library 无法排除，故完整性
   由静态证明保证，烟测证 zip 有效性与安装顺序）
4. plot check_deps.R 升级为 **requireNamespace 加载式**检查（防残缺 bundle 假绿）
5. 两个 check_deps.R 加 R 版本打印 + 4.5.x 绑定提示；ct 注释修正
6. README 修正：计数 47→91、pip 命令 CWD 说明、`<absolute path to>` 占位、
   "Requires R 4.x"→R 4.5.x binary 绑定说明、cos-staging README 同步
7. check_env.sh 加 conda fallback（非交互 bash source miniconda profile）
8. check_deps.py 加 Python 3.13/cp313 绑定提示

二轮审查（8 项修复全核验通过）后微调：离线安装循环 `1:10`→`1:20`
（干净机器最深依赖链 ~11 轮，logistf→mice→glmnet→foreach 链）；check_deps.R
排障提示路径标注"相对仓库根"。

## 不做范围（本次明确排除）

- 网站教程页/下载页的 COS 直链回填（随上线阶段统一做，占位即可）
- 其他 skill（qpcr/scRNA/bulk 等）的依赖暂存（后续按需复制本模式）
- WSL2 侧 apt deb / conda pkgs 离线大件
- verbatim R 复现脚本内部改动

## 验证深度声明（可裁）

R 侧闭包烟测为「logistf 实装 + 其余 zip 完整性/数量校验」（ggtree 全闭包实装到隔离
lib 需 10 分钟级且本机包干扰解析，性价比低）；如需全量实装烟测请在核准时注明。
