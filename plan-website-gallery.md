# Plan：website 图库翻新（真实 output 上图 + 9 个新 skill 中文教程页）

日期：2026-09-16 ｜ 状态：v2 待用户核准（已按 Q6/Q7/Q9 拍板修订）

## 已拍板决策

1. **范围**：首页（双语）卡片全部换真实 output 实拍图 + 新 skill 上线；新 skill 教程页**只写中文**（英文下轮补，英文侧边栏入口先隐藏）。
2. **卡片粒度**：**每种图型 1 卡**（不是每 skill 1 卡、也不是每文件 1 卡）。同一 skill 多张卡时，**全部链接到同一个 skill 教程页**（用户原话：GO 和 KEGG 首页图不同，但点进去都是同一个 skill）。
3. **旧卡图**：/cards/ 现有 3 张若非实拍一律换成 examples/output 实拍。
4. **phylo-tree**：2 卡同图（环形树）不同文案——build 卡强调"FASTA→树文件"，plot 卡强调"树文件→发表图"，分别链各自教程页。
5. **图片管理**：写 `website/scripts/sync_site_images.ps1`，把入选图从各 skill examples/output 复制到 `website/public/skills/<skill>/`；入选清单写在脚本顶部（单一事实源）。
6. **clinical-table**：写一次性渲染脚本把示例三线表渲成 PNG（执行时看其 output 格式定 matplotlib/flextable），用于首页卡和教程页。
7. **教程页结构**（对齐旧 4 页风格）：用途一句话 → 输入契约 → 示例输出画廊（该 skill 全部图型，逐图一句话 + 关键锚点数字）→ 怎么跑 → 仓库链接。

## 首页卡片清单（每图型 1 卡，约 26 卡）

- **experiment-data（2 卡）**：qpcr-mrna=Figure1_IL6_barplot；qpcr-mtdna=Figure18B
- **scRNA（约 8 卡）**：scRNA-seq=注释UMAP/分组UMAP/marker dotplot/marker heatmap/QC 小提琴（5）；pseudotime=拟时序轨迹/基因沿轨迹（2）；virtual-ko=Top20 柱状（1）
- **bulk（约 10 卡）**：bulk-RNA-seq=火山/MA/PCA/相关热图/DEG热图（5）；enrichment=GO/KEGG/Reactome dotplot（3）；gene-plot=单基因跨组/组内两基因对比（2）；GSEA=富集曲线/dotplot（2）——实际 12 卡，执行时按图型归并
- **phylo（2 卡同图）**：build + plot
- **figure（5 卡）**：barplot=2组柱状；clinical-table=三线表PNG；survival-curve=KM曲线/Cox森林图（2）

## 执行步骤

1. sync 脚本 + 入选图复制到 `public/skills/<skill>/`。
2. clinical-table 三线表渲染 PNG。
3. 首页 index.md + zh/index.md：按上面清单翻新 3 分区卡片网格。
4. 新建 10 个中文教程页 `zh/skills/<skill>.md`（scRNA×3、bulk×4、phylo×2、survival-curve），每页含全图型画廊。
5. config.ts：中文侧边栏注册新页（英文侧边栏不加）。
6. `npm run build` 无死链 + `npm run dev` 目检首页 + 抽查 2 页。
7. 收尾：总 plan.md 增补 #46；public/skills/ 图片文件名脱敏扫一遍。

## 明确不做

- 不写英文教程页；不改 get-started/download/citation；不压缩/重命名 skill 原始 output 图（复制不改源）；clinical-table 不动 skill 本体。
