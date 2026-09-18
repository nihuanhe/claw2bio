---
layout: home

hero:
  name: Claw2Bio
  text: Lab-validated AI agent skills for biomedical analysis
  tagline: No coding required · Fixed scripts validated in real lab work · Your data never leaves your machine
  actions:
    - theme: brand
      text: Get Started
      link: /get-started
    - theme: alt
      text: Browse Skills
      link: /skills/
---

<h2 class="section-title" id="experiment-data">🧪 Experiment Data Processing</h2>
<p class="section-sub">qPCR and more — turn raw instrument output into statistics and figures. Every image below is a REAL example output of the skill.</p>

<div class="card-grid">
  <a class="task-card" href="/skills/qpcr-mrna">
    <img src="/skills/qpcr-mrna/Figure1_IL6_barplot.png" alt="qPCR mRNA real example output" />
    <div class="card-body">
      <p class="card-name">qPCR mRNA (ΔΔCt)</p>
      <p class="card-desc">ΔΔCt relative expression with t-test / ANOVA + Dunnett, one bar plot per target.</p>
    </div>
  </a>
  <a class="task-card" href="/skills/qpcr-mtdna">
    <img src="/skills/qpcr-mtdna/Figure18B.png" alt="qPCR mtDNA real example output" />
    <div class="card-body">
      <p class="card-name">qPCR mtDNA Copy Number</p>
      <p class="card-desc">ND1/ND5/B2M/POLG pairing, mean copy number, publication-ready plot.</p>
    </div>
  </a>
</div>

<h2 class="section-title" id="bioinformatics">🧬 Bioinformatics Analysis</h2>
<p class="section-sub">Single-cell, bulk RNA-seq, phylogenetics — every card is a real figure produced by the linked skill.</p>

<div class="card-grid">
  <a class="task-card" href="/skills/scRNA-seq">
    <img src="/skills/scRNA-seq/UMAP_by_annotation.png" alt="scRNA-seq annotated UMAP" />
    <div class="card-body">
      <p class="card-name">Annotated UMAP</p>
      <p class="card-desc">scRNA-seq · raw matrix → QC → Harmony → clusters → SingleR cell types.</p>
    </div>
  </a>
  <a class="task-card" href="/skills/scRNA-seq">
    <img src="/skills/scRNA-seq/UMAP_by_group.png" alt="scRNA-seq UMAP by group" />
    <div class="card-body">
      <p class="card-name">UMAP by Group</p>
      <p class="card-desc">scRNA-seq · group-split embedding after batch integration.</p>
    </div>
  </a>
  <a class="task-card" href="/skills/scRNA-seq">
    <img src="/skills/scRNA-seq/marker_dotplot.png" alt="scRNA-seq marker dotplot" />
    <div class="card-body">
      <p class="card-name">Marker Dotplot</p>
      <p class="card-desc">scRNA-seq · per-cluster marker genes, expression × percent.</p>
    </div>
  </a>
  <a class="task-card" href="/skills/scRNA-seq">
    <img src="/skills/scRNA-seq/marker_heatmap.png" alt="scRNA-seq marker heatmap" />
    <div class="card-body">
      <p class="card-name">Marker Heatmap</p>
      <p class="card-desc">scRNA-seq · top markers per cluster at a glance.</p>
    </div>
  </a>
  <a class="task-card" href="/skills/scRNA-seq">
    <img src="/skills/scRNA-seq/QC_violin_after.png" alt="scRNA-seq QC violin" />
    <div class="card-body">
      <p class="card-name">QC Violin</p>
      <p class="card-desc">scRNA-seq · nFeature / nCount / percent.mt before-after filtering.</p>
    </div>
  </a>
  <a class="task-card" href="/skills/scRNA-seq-pseudotime">
    <img src="/skills/scRNA-seq-pseudotime/trajectory_by_pseudotime.png" alt="pseudotime trajectory" />
    <div class="card-body">
      <p class="card-name">Pseudotime Trajectory</p>
      <p class="card-desc">scRNA-seq-pseudotime · monocle3 trajectory on your annotated rds.</p>
    </div>
  </a>
  <a class="task-card" href="/skills/scRNA-seq-pseudotime">
    <img src="/skills/scRNA-seq-pseudotime/trajectory_by_cluster.png" alt="trajectory by cluster" />
    <div class="card-body">
      <p class="card-name">Trajectory by Cluster</p>
      <p class="card-desc">scRNA-seq-pseudotime · clusters mapped onto the learned tree.</p>
    </div>
  </a>
  <a class="task-card" href="/skills/scRNA-seq-pseudotime">
    <img src="/skills/scRNA-seq-pseudotime/gene_HES4_on_trajectory.png" alt="gene along trajectory" />
    <div class="card-body">
      <p class="card-name">Gene along Trajectory</p>
      <p class="card-desc">scRNA-seq-pseudotime · any gene's expression over pseudotime.</p>
    </div>
  </a>
  <a class="task-card" href="/skills/scRNA-seq-virtual-ko">
    <img src="/skills/scRNA-seq-virtual-ko/ACTA2_barplot_top20.png" alt="virtual KO top20 barplot" />
    <div class="card-body">
      <p class="card-name">Virtual KO — Top Targets</p>
      <p class="card-desc">scRNA-seq-virtual-ko · scTenifoldKnk in-silico knockout ranking.</p>
    </div>
  </a>
  <a class="task-card" href="/skills/scRNA-seq-virtual-ko">
    <img src="/skills/scRNA-seq-virtual-ko/ACTA2_zscore_scatter.png" alt="virtual KO zscore scatter" />
    <div class="card-body">
      <p class="card-name">Virtual KO — Z-score Scatter</p>
      <p class="card-desc">scRNA-seq-virtual-ko · differential regulation after in-silico KO.</p>
    </div>
  </a>
  <a class="task-card" href="/skills/bulk-RNA-seq">
    <img src="/skills/bulk-RNA-seq/Volcano.png" alt="bulk RNA-seq volcano plot" />
    <div class="card-body">
      <p class="card-name">Volcano Plot</p>
      <p class="card-desc">bulk-RNA-seq · counts → QC → DEG, engine auto-selected (DESeq2/edgeR/limma).</p>
    </div>
  </a>
  <a class="task-card" href="/skills/bulk-RNA-seq">
    <img src="/skills/bulk-RNA-seq/MA.png" alt="bulk RNA-seq MA plot" />
    <div class="card-body">
      <p class="card-name">MA Plot</p>
      <p class="card-desc">bulk-RNA-seq · log-fold-change vs mean expression per contrast.</p>
    </div>
  </a>
  <a class="task-card" href="/skills/bulk-RNA-seq">
    <img src="/skills/bulk-RNA-seq/QC_PCA.png" alt="bulk RNA-seq PCA" />
    <div class="card-body">
      <p class="card-name">QC — PCA</p>
      <p class="card-desc">bulk-RNA-seq · sample-level quality control before any DEG call.</p>
    </div>
  </a>
  <a class="task-card" href="/skills/bulk-RNA-seq">
    <img src="/skills/bulk-RNA-seq/QC_correlation_heatmap.png" alt="sample correlation heatmap" />
    <div class="card-body">
      <p class="card-name">QC — Correlation Heatmap</p>
      <p class="card-desc">bulk-RNA-seq · sample-to-sample correlation at a glance.</p>
    </div>
  </a>
  <a class="task-card" href="/skills/bulk-RNA-seq">
    <img src="/skills/bulk-RNA-seq/DEG_heatmap.png" alt="DEG heatmap" />
    <div class="card-body">
      <p class="card-name">DEG Heatmap</p>
      <p class="card-desc">bulk-RNA-seq · top differential genes across all samples.</p>
    </div>
  </a>
  <a class="task-card" href="/skills/RNA-seq-enrichment">
    <img src="/skills/RNA-seq-enrichment/GO_BP_dotplot.png" alt="GO enrichment dotplot" />
    <div class="card-body">
      <p class="card-name">GO Enrichment</p>
      <p class="card-desc">RNA-seq-enrichment · BP/CC/MF dotplots, fully offline.</p>
    </div>
  </a>
  <a class="task-card" href="/skills/RNA-seq-enrichment">
    <img src="/skills/RNA-seq-enrichment/KEGG_dotplot.png" alt="KEGG enrichment dotplot" />
    <div class="card-body">
      <p class="card-name">KEGG Enrichment</p>
      <p class="card-desc">RNA-seq-enrichment · online-first with local cache fallback.</p>
    </div>
  </a>
  <a class="task-card" href="/skills/RNA-seq-enrichment">
    <img src="/skills/RNA-seq-enrichment/Reactome_dotplot.png" alt="Reactome enrichment dotplot" />
    <div class="card-body">
      <p class="card-name">Reactome Enrichment</p>
      <p class="card-desc">RNA-seq-enrichment · offline Reactome pathways.</p>
    </div>
  </a>
  <a class="task-card" href="/skills/RNA-seq-gene-plot">
    <img src="/skills/RNA-seq-gene-plot/GeneExpr_Trp53_by_group.png" alt="gene expression by group" />
    <div class="card-body">
      <p class="card-name">Gene across Groups</p>
      <p class="card-desc">RNA-seq-gene-plot · one gene, SD bars + points + t-test/ANOVA+Tukey.</p>
    </div>
  </a>
  <a class="task-card" href="/skills/RNA-seq-gene-plot">
    <img src="/skills/RNA-seq-gene-plot/GeneExpr_compare_within_group.png" alt="two genes within group" />
    <div class="card-body">
      <p class="card-name">Two Genes, One Group</p>
      <p class="card-desc">RNA-seq-gene-plot · paired comparison inside a group.</p>
    </div>
  </a>
  <a class="task-card" href="/skills/RNA-seq-GSEA">
    <img src="/skills/RNA-seq-GSEA/GSEA_top_curve.png" alt="GSEA enrichment curve" />
    <div class="card-body">
      <p class="card-name">GSEA Curve</p>
      <p class="card-desc">RNA-seq-GSEA · fgsea + MSigDB, auto Entrez/symbol conversion.</p>
    </div>
  </a>
  <a class="task-card" href="/skills/RNA-seq-GSEA">
    <img src="/skills/RNA-seq-GSEA/GSEA_dotplot.png" alt="GSEA dotplot" />
    <div class="card-body">
      <p class="card-name">GSEA Dotplot</p>
      <p class="card-desc">RNA-seq-GSEA · top enriched sets, NES × FDR.</p>
    </div>
  </a>
  <a class="task-card" href="/skills/phylo-tree-build">
    <img src="/skills/phylo-tree-build/phylo_tree.png" alt="core-genome phylogenetic tree" />
    <div class="card-body">
      <p class="card-name">Core-genome Tree — Build</p>
      <p class="card-desc">phylo-tree-build · genome FASTAs → bcgTree → IQ-TREE2 ML treefile (WSL2). Figure drawn by phylo-tree-plot from this skill's treefile.</p>
    </div>
  </a>
  <a class="task-card" href="/skills/phylo-tree-plot">
    <img src="/skills/phylo-tree-plot/phylo_tree.png" alt="annotated phylogenetic tree figure" />
    <div class="card-body">
      <p class="card-name">Core-genome Tree — Plot</p>
      <p class="card-desc">phylo-tree-plot · treefile + annotation CSV → publication-ready ggtree figure.</p>
    </div>
  </a>
</div>

<h2 class="section-title" id="figure-generation">📈 Figure & Table Generation</h2>
<p class="section-sub">Publication-ready plots and statistical tables — real outputs, no mock-ups.</p>

<div class="card-grid">
  <a class="task-card" href="/skills/barplot">
    <img src="/skills/barplot/data_barplot.png" alt="grouped bar plot real output" />
    <div class="card-body">
      <p class="card-name">Grouped Bar Plot</p>
      <p class="card-desc">barplot · wide-format CSV in, 300-dpi plot with error bars, scatter, P values out.</p>
    </div>
  </a>
  <a class="task-card" href="/skills/clinical-table">
    <img src="/skills/clinical-table/table1_baseline.png" alt="clinical three-line table" />
    <div class="card-body">
      <p class="card-name">Clinical Three-line Tables</p>
      <p class="card-desc">clinical-table · one pipeline reproducing all 10 tables of a paper (baseline / Firth / genotype cross-tabs / univariate) — showcased on a real cohort study.</p>
    </div>
  </a>
  <a class="task-card" href="/skills/survival-curve">
    <img src="/skills/survival-curve/KM_curve.png" alt="Kaplan-Meier survival curve" />
    <div class="card-body">
      <p class="card-name">Kaplan-Meier Curve</p>
      <p class="card-desc">survival-curve · optimal cutoff + log-rank + number-at-risk table.</p>
    </div>
  </a>
  <a class="task-card" href="/skills/survival-curve">
    <img src="/skills/survival-curve/cox_forest.png" alt="Cox hazard ratio forest plot" />
    <div class="card-body">
      <p class="card-name">Cox Forest Plot</p>
      <p class="card-desc">survival-curve · univariate Cox HR with 95% CI.</p>
    </div>
  </a>
</div>
