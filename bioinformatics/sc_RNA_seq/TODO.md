# sc_RNA_seq 家族 · TODO（随项目滚动更新）

> 2026-09-16 建立。完成一项勾一项；新事项随时追加。

## 环境

- [x] 安装 scDblFinder（BiocManager，已装 1.24.10）
- [x] 安装 clustree（CRAN，已装 0.5.1；与 ggplot2 4.0 不兼容 → stage03 已 tryCatch 优雅降级）
- [x] 装完后用 example 1 重跑一次全流程，确认双细胞率表 + clustree 图正常产出（双细胞表✓；clustree 图因 ggplot2 4.0 不兼容跳过，待 clustree 更新后复查）

## 主 skill 收尾

- [x] 存量 4 个 bulk 系 skill 迁入 `bioinformatics/bulk_RNA_seq/`（git mv 完成；根路径引用已 sed 更新；AGENTS.md 索引已补 4 行；example 1 冒烟跑通✓）
- [x] `resources/r-deps/` mini-repo 扩展 scRNA 闭包（闭包 245 包：106 已有 + 139 新增 + Bioc3.21 补链；现 277 zips + PACKAGES 重建；celldex/presto/monocle3/bluster 为纯 R 源码包可装，Rsamtools/rtracklayer 二进制缺口待补；扩展脚本 examples/_dev/extend_r_deps.R）
- [ ] 补 r-deps 缺口：Rsamtools/rtracklayer 的 R4.5 win 二进制（手工从 Bioc 3.21 抓或上线前复查）
- [ ] celldex 参考数据 + presto 源码包上 COS（cos-staging 开 resources/ 目录，回填 manifest）
- [x] GSE234527 全量真实验证跑（2026-09-16 通过：11570 真实细胞→QC→去双细胞 10859→Harmony→12 clusters→SingleR；~10min 无爆内存；slim rds 41MB 已出；产物在 D:\single_cell_1\GSE234527_output）
- [x] 主 skill `--export-slim`（DietSeurat 瘦身导出）选项实现——已实测 27.5→9.2 MB，供 COS 分发与用户分享

## 下游 skill（依赖主 skill 真实产出）

- [x] `scRNA-seq-pseudotime`（monocle3；SKILL/README/scripts 完成，example 1 冒烟跑通：轨迹图 4 套 + graph_test + 基因轨迹图；root 必填校验✓；全量数据案例待 GSE234527 验证跑后补）
- [x] `scRNA-seq-virtual-ko`（scTenifoldKnk 1.0.3 已装并跑通；处理了版本坑：函数名/参数名/列名全变；**实测性能：2000 基因×全细胞 8h 跑不完→杀掉；2000×10net×500cell 3.5h+ 未完成；500 基因×5net×500cell ≈17min 出结果（10 显著基因）——nfeatures 是平方级大头，--nc-ncells 默认已改回官方 500**；真实 ACTA2 结果在 D:\single_cell_1\GSE234527_vko_ACTA2）
- [ ] ACTA2 全参数重跑（2000×10×500，出差回来后择机，预计 4h+）

## 复核修复（2026-09-17，见 plan-skill-example-completion.md §12）

- [x] **pseudotime `--resume` 原来是"假"的**：`stage_pseudotime.R` 写 `.checkpoint_cds_learned.rds`
      但**从不读回**，`run_pseudotime.py` 的 `--resume` 也不传给 R → 已修（两处各加 3–10 行）；
      现 `--resume` 会真的跳过"建 cds + learn_graph"，成功结束时才删检查点
- [x] 上述修复的等效实测：把已有 `pseudotime_cds.rds` 当检查点放进新目录，跑
      `--resume --no-graph-test` → 日志出现 `--resume: loading checkpoint`，**无** `building cell_data_set` /
      `learn_graph`，4 套轨迹图与 summary 正常产出，结束后检查点被删除
- [ ] 待补：`--resume` 的**真实崩溃**验证（kill mid-run），本次是等效验证而非真崩溃
- [x] **virtual-ko 无断点、不可续跑** → `SKILL.md` / `README.md` / 网站页已如实标注（别让机器休眠）
- [x] **SKILL.md 时长数字与实测冲突**："2000×10 ≈ 1 h" vs TODO 实测 3.5 h+ 未完成 →
      改为"未跑完（已中止）"，并说明全量耗时尚未标定

- [ ] `scRNA-seq-compare`（占位：组间比例 + pseudobulk DE，用户指定对比组）
- [ ] scTenifoldKnk 1.0.3 二进制 zip 入 COS resources（现为 D:\single_cell_1 本地包）
- [ ] 两个下游 skill 的 examples/output 上线前用真实数据重跑替换冒烟产出

## 发布（按 CONTRIBUTING.md SOP）

- [ ] 上线前 6 个 example 全部真实跑通（用户亲跑，可分次；未跑通不上线）
- [ ] 脱敏 → 英文化 → 冒烟 → 提交 → 教程页九节模板 → 构建发布
