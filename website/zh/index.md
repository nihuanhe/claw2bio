---
layout: home

hero:
  name: Claw2Bio
  text: 实验室实战验证的生物医学 AI agent 技能库
  tagline: 无需写代码 · 固定脚本均经真实课题验证 · 数据不出本机
  actions:
    - theme: brand
      text: 快速上手
      link: /zh/get-started
    - theme: alt
      text: 浏览技能
      link: /zh/skills/
---

<h2 class="section-title" id="experiment-data">🧪 实验数据处理</h2>
<p class="section-sub">qPCR 等——从仪器原始输出直接到统计和图。下面每张图都是对应技能的真实示例产出。</p>

<div class="card-grid">
  <a class="task-card" href="/zh/skills/qpcr-mrna">
    <img src="/skills/qpcr-mrna/Figure1_IL6_barplot.png" alt="qPCR mRNA 真实示例输出" />
    <div class="card-body">
      <p class="card-name">qPCR mRNA（ΔΔCt）</p>
      <p class="card-desc">ΔΔCt 相对表达量，t-test / ANOVA + Dunnett，每个靶标一张图。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/qpcr-mtdna">
    <img src="/skills/qpcr-mtdna/Figure18B.png" alt="qPCR mtDNA 真实示例输出" />
    <div class="card-body">
      <p class="card-name">qPCR mtDNA 拷贝数</p>
      <p class="card-desc">ND1/ND5/B2M/POLG 配对，Mean copy number，发表级图。</p>
    </div>
  </a>
</div>

<h2 class="section-title" id="bioinformatics">🧬 生信数据分析</h2>
<p class="section-sub">单细胞、bulk RNA-seq、进化树——每张卡都是链接技能真实跑出来的图；同一技能多张卡，点进去都是同一个教程页。</p>

<div class="card-grid">
  <a class="task-card" href="/zh/skills/scRNA-seq">
    <img src="/skills/scRNA-seq/UMAP_by_annotation.png" alt="单细胞注释 UMAP" />
    <div class="card-body">
      <p class="card-name">细胞注释 UMAP</p>
      <p class="card-desc">scRNA-seq · 原始矩阵 → QC → Harmony → 聚类 → SingleR 注释。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/scRNA-seq">
    <img src="/skills/scRNA-seq/UMAP_by_group.png" alt="分组 UMAP" />
    <div class="card-body">
      <p class="card-name">分组 UMAP</p>
      <p class="card-desc">scRNA-seq · 批次整合后的分组降维图。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/scRNA-seq">
    <img src="/skills/scRNA-seq/marker_dotplot.png" alt="marker 气泡图" />
    <div class="card-body">
      <p class="card-name">Marker 气泡图</p>
      <p class="card-desc">scRNA-seq · 各 cluster marker 基因，表达量 × 表达比例。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/scRNA-seq">
    <img src="/skills/scRNA-seq/marker_heatmap.png" alt="marker 热图" />
    <div class="card-body">
      <p class="card-name">Marker 热图</p>
      <p class="card-desc">scRNA-seq · 每 cluster top marker 一图看全。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/scRNA-seq">
    <img src="/skills/scRNA-seq/QC_violin_after.png" alt="QC 小提琴图" />
    <div class="card-body">
      <p class="card-name">QC 小提琴图</p>
      <p class="card-desc">scRNA-seq · nFeature / nCount / percent.mt 过滤前后对比。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/scRNA-seq-pseudotime">
    <img src="/skills/scRNA-seq-pseudotime/trajectory_by_pseudotime.png" alt="拟时序轨迹" />
    <div class="card-body">
      <p class="card-name">拟时序轨迹</p>
      <p class="card-desc">scRNA-seq-pseudotime · 在注释好的 rds 上跑 monocle3。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/scRNA-seq-pseudotime">
    <img src="/skills/scRNA-seq-pseudotime/trajectory_by_cluster.png" alt="cluster 轨迹" />
    <div class="card-body">
      <p class="card-name">轨迹 × Cluster</p>
      <p class="card-desc">scRNA-seq-pseudotime · cluster 映射到学习出的轨迹树。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/scRNA-seq-pseudotime">
    <img src="/skills/scRNA-seq-pseudotime/gene_HES4_on_trajectory.png" alt="基因沿轨迹表达" />
    <div class="card-body">
      <p class="card-name">基因沿轨迹表达</p>
      <p class="card-desc">scRNA-seq-pseudotime · 任意基因沿拟时序的表达变化。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/scRNA-seq-virtual-ko">
    <img src="/skills/scRNA-seq-virtual-ko/ACTA2_barplot_top20.png" alt="虚拟敲除 Top20" />
    <div class="card-body">
      <p class="card-name">虚拟敲除 Top 靶点</p>
      <p class="card-desc">scRNA-seq-virtual-ko · scTenifoldKnk 计算机模拟敲除排序。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/scRNA-seq-virtual-ko">
    <img src="/skills/scRNA-seq-virtual-ko/ACTA2_zscore_scatter.png" alt="虚拟敲除 Z 值散点" />
    <div class="card-body">
      <p class="card-name">虚拟敲除 Z 值散点</p>
      <p class="card-desc">scRNA-seq-virtual-ko · 敲除后差异调控全景。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/bulk-RNA-seq">
    <img src="/skills/bulk-RNA-seq/Volcano.png" alt="火山图" />
    <div class="card-body">
      <p class="card-name">火山图</p>
      <p class="card-desc">bulk-RNA-seq · counts → QC → DEG，引擎自动选择（DESeq2/edgeR/limma）。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/bulk-RNA-seq">
    <img src="/skills/bulk-RNA-seq/MA.png" alt="MA 图" />
    <div class="card-body">
      <p class="card-name">MA 图</p>
      <p class="card-desc">bulk-RNA-seq · 每个对比的 logFC–平均表达关系。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/bulk-RNA-seq">
    <img src="/skills/bulk-RNA-seq/QC_PCA.png" alt="PCA 质控" />
    <div class="card-body">
      <p class="card-name">QC · PCA</p>
      <p class="card-desc">bulk-RNA-seq · 差异分析之前的样本质控。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/bulk-RNA-seq">
    <img src="/skills/bulk-RNA-seq/QC_correlation_heatmap.png" alt="样本相关热图" />
    <div class="card-body">
      <p class="card-name">QC · 相关性热图</p>
      <p class="card-desc">bulk-RNA-seq · 样本间相关性一图看全。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/bulk-RNA-seq">
    <img src="/skills/bulk-RNA-seq/DEG_heatmap.png" alt="差异基因热图" />
    <div class="card-body">
      <p class="card-name">差异基因热图</p>
      <p class="card-desc">bulk-RNA-seq · top 差异基因 × 全部样本。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/RNA-seq-enrichment">
    <img src="/skills/RNA-seq-enrichment/GO_BP_dotplot.png" alt="GO 富集气泡图" />
    <div class="card-body">
      <p class="card-name">GO 富集</p>
      <p class="card-desc">RNA-seq-enrichment · BP/CC/MF 气泡图，全程离线。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/RNA-seq-enrichment">
    <img src="/skills/RNA-seq-enrichment/KEGG_dotplot.png" alt="KEGG 富集气泡图" />
    <div class="card-body">
      <p class="card-name">KEGG 富集</p>
      <p class="card-desc">RNA-seq-enrichment · 在线优先 + 本地缓存兜底。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/RNA-seq-enrichment">
    <img src="/skills/RNA-seq-enrichment/Reactome_dotplot.png" alt="Reactome 富集气泡图" />
    <div class="card-body">
      <p class="card-name">Reactome 富集</p>
      <p class="card-desc">RNA-seq-enrichment · 离线 Reactome 通路。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/RNA-seq-gene-plot">
    <img src="/skills/RNA-seq-gene-plot/GeneExpr_Trp53_by_group.png" alt="单基因跨组表达" />
    <div class="card-body">
      <p class="card-name">单基因跨组对比</p>
      <p class="card-desc">RNA-seq-gene-plot · SD 误差线 + 散点 + t-test/ANOVA+Tukey。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/RNA-seq-gene-plot">
    <img src="/skills/RNA-seq-gene-plot/GeneExpr_compare_within_group.png" alt="组内两基因对比" />
    <div class="card-body">
      <p class="card-name">组内两基因对比</p>
      <p class="card-desc">RNA-seq-gene-plot · 同组内配对比较。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/RNA-seq-GSEA">
    <img src="/skills/RNA-seq-GSEA/GSEA_top_curve.png" alt="GSEA 富集曲线" />
    <div class="card-body">
      <p class="card-name">GSEA 富集曲线</p>
      <p class="card-desc">RNA-seq-GSEA · fgsea + MSigDB，Entrez/symbol 自动转换。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/RNA-seq-GSEA">
    <img src="/skills/RNA-seq-GSEA/GSEA_dotplot.png" alt="GSEA 气泡图" />
    <div class="card-body">
      <p class="card-name">GSEA 气泡图</p>
      <p class="card-desc">RNA-seq-GSEA · top 富集基因集，NES × FDR。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/phylo-tree-build">
    <img src="/skills/phylo-tree-build/phylo_tree.png" alt="核心基因组进化树" />
    <div class="card-body">
      <p class="card-name">核心基因组树 · 建树</p>
      <p class="card-desc">phylo-tree-build · 基因组 FASTA → bcgTree → IQ-TREE2 树文件（WSL2）。图为 phylo-tree-plot 用本技能树文件绘制。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/phylo-tree-plot">
    <img src="/skills/phylo-tree-plot/phylo_tree.png" alt="发表级进化树图" />
    <div class="card-body">
      <p class="card-name">核心基因组树 · 绘图</p>
      <p class="card-desc">phylo-tree-plot · 树文件 + 注解表 → 发表级 ggtree 图。</p>
    </div>
  </a>
</div>

<h2 class="section-title" id="figure-generation">📈 图表生成</h2>
<p class="section-sub">发表级图与统计表——全部为真实产出，无示意图。</p>

<div class="card-grid">
  <a class="task-card" href="/zh/skills/barplot">
    <img src="/skills/barplot/data_barplot.png" alt="分组柱状图真实产出" />
    <div class="card-body">
      <p class="card-name">分组柱状图</p>
      <p class="card-desc">barplot · 宽表 CSV 进，300 dpi 误差线 + 散点 + P 值出。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/clinical-table">
    <img src="/skills/clinical-table/table1_baseline.png" alt="临床三线表" />
    <div class="card-body">
      <p class="card-name">临床三线表</p>
      <p class="card-desc">clinical-table · 一套管线复现论文全套 10 张表（基线/Firth/基因型交叉/单因素），示例为真实队列研究。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/survival-curve">
    <img src="/skills/survival-curve/KM_curve.png" alt="KM 生存曲线" />
    <div class="card-body">
      <p class="card-name">KM 生存曲线</p>
      <p class="card-desc">survival-curve · 最优截点 + log-rank + 风险人数表。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/survival-curve">
    <img src="/skills/survival-curve/cox_forest.png" alt="Cox 森林图" />
    <div class="card-body">
      <p class="card-name">Cox 森林图</p>
      <p class="card-desc">survival-curve · 单因素 Cox HR + 95% CI。</p>
    </div>
  </a>
</div>
