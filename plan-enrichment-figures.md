# plan-enrichment-figures.md — RNA-seq-enrichment 点图标签单行化 + KEGG 去物种后缀

> 2026-09-21 ｜ 用户要求：GO/KEGG dotplot 左侧标注不换行（单行右对齐）；
> KEGG 图去掉 ` - Mus musculus (house mouse)` 物种后缀。Reactome 不动。

## 改动点（`bioinformatics/bulk_RNA_seq/RNA-seq-enrichment/scripts/enrich.R`）

1. GO 分支（L81）：`dotplot(eg, showCategory = 15, label_format = 1000, ...)`
   —— label_format 默认 30 触发折行，设大值即单行；y 轴标签默认右对齐，无需改
2. KEGG 分支：enrichKEGG/缓存结果后加一行
   `kk@result$Description <- sub(" - [A-Za-z]+ [a-z]+ \\([^)]*\\)$", "", kk@result$Description)`
   剥掉物种后缀；dotplot 同样加 `label_format = 1000`
3. Reactome 分支不动
4. 若单行标签被右缘裁切，把 `width = 9` 适当调大（报告里说明最终值）

执行铁律合规性：这属于「CLI 无法表达的最小脚本修改」，改的是 `scripts/` 里的**正式脚本本体**
（不是临时副本），因为需求本身就是改变技能的默认行为——改完即沉淀回 scripts/，符合规则。

## 执行步骤

1. 改 `enrich.R`（上述 2 处）
2. 用本机 R 4.5.2 重跑示例：`Rscript scripts/enrich.R examples/input examples/output --offline`
   （KEGG 走缓存保证可复现），确认 12 张 GO + 4 张 KEGG 图重新生成、标签单行、KEGG 无物种后缀
3. 同步网站图：把对应的 3 张示例图复制到 `website/public/skills/RNA-seq-enrichment/`
   （GO_BP_dotplot.png / KEGG_dotplot.png；Reactome_dotplot.png 若内容变化一并换，否则不动）
   ——先核对网站图与哪个示例输出对应再复制
4. 重新打包：`python scripts/build_skill_zips.py`（只应重建 RNA-seq-enrichment.zip）
5. 分发：`python scripts/deploy_downloads.py`（zip ≤50 MB 走服务器）
6. 网站：`npm run build` → `deploy_site.py deploy` → 线上复核（页面 200 + 图片真实下载 md5 比对）
7. git 提交推送（坑 #16 同命令一条龙）→ adversarial-review

## 验收标准

- 4 张用户点名图 + 其余 GO/KEGG 图标签全部单行不折行
- KEGG 图无 `(house mouse)` 或任何物种后缀
- 网站 3 张展示图与新输出 md5 一致；zip 重建后线上字节数/md5 与本地一致
- enrich.csv 数据内容不变（只改图，不改统计）

## 风险

- KEGG 在线 vs 缓存结果可能不同 → 用 --offline 锁定缓存版
- 单行长标签裁切 → 调 width，复核图片右缘
