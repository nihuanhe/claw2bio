---
layout: home

hero:
  name: Claw2Bio
  text: 实验室实战验证的 AI agent 生物医学分析技能库
  tagline: 无需编程基础 · 固定脚本经真实科研工作验证 · 数据全程不出本地
  actions:
    - theme: brand
      text: 快速上手
      link: /zh/get-started
    - theme: alt
      text: 浏览技能
      link: /zh/skills/
---

<h2 class="section-title" id="experiment-data">🧪 实验数据处理</h2>
<p class="section-sub">qPCR、Western blot、免疫荧光——把仪器原始输出直接变成统计结果和图。</p>

<div class="card-grid">
  <a class="task-card" href="/zh/skills/qpcr-mrna">
    <img src="/cards/qpcr-mrna.png" alt="qPCR mRNA 示例输出" />
    <div class="card-body">
      <p class="card-name">qPCR mRNA（ΔΔCt）</p>
      <p class="card-desc">ΔΔCt 相对表达量分析，t-test / ANOVA + Dunnett，每个靶标一张柱状图。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/qpcr-mtdna">
    <img src="/cards/qpcr-mtdna.png" alt="qPCR mtDNA 示例输出" />
    <div class="card-body">
      <p class="card-name">qPCR mtDNA 拷贝数</p>
      <p class="card-desc">ND1/ND5/B2M/POLG 自动配对，Mean copy number，发表级出图。</p>
    </div>
  </a>
</div>

<h2 class="section-title" id="bioinformatics">🧬 生信数据分析</h2>
<p class="section-sub">单细胞、bulk RNA-seq 等——随真实课题建设，建成一个上线一个。</p>

<div class="card-grid">
  <div class="task-card soon">
    <div class="card-placeholder">🧫</div>
    <div class="card-body">
      <p class="card-name">单细胞测序分析<span class="soon-badge">Coming soon</span></p>
      <p class="card-desc">从表达矩阵到细胞注释——可复现的固定脚本流程。</p>
    </div>
  </div>
  <div class="task-card soon">
    <div class="card-placeholder">📊</div>
    <div class="card-body">
      <p class="card-name">Bulk RNA-seq<span class="soon-badge">Coming soon</span></p>
      <p class="card-desc">差异表达分析与可视化，全部使用经过验证的固定脚本。</p>
    </div>
  </div>
  <div class="task-card soon">
    <div class="card-placeholder">🌳</div>
    <div class="card-body">
      <p class="card-name">细菌/进化树分析<span class="soon-badge">Coming soon</span></p>
      <p class="card-desc">细菌基因组进化树构建与注释。</p>
    </div>
  </div>
</div>

<h2 class="section-title" id="figure-generation">📈 图表生成</h2>
<p class="section-sub">发表级图表与统计表格，默认色盲友好配色。</p>

<div class="card-grid">
  <a class="task-card" href="/zh/skills/barplot">
    <img src="/cards/barplot.png" alt="barplot 示例输出" />
    <div class="card-body">
      <p class="card-name">分组柱状图</p>
      <p class="card-desc">宽表 CSV 进，300 dpi 带误差线、散点、P 值标注的图出。</p>
    </div>
  </a>
  <a class="task-card" href="/zh/skills/clinical-table">
    <div class="card-placeholder">📋</div>
    <div class="card-body">
      <p class="card-name">临床统计表</p>
      <p class="card-desc">基线特征表、相关性矩阵、Cox 回归——三线表一键生成。</p>
    </div>
  </a>
</div>
