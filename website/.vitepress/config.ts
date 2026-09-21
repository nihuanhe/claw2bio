import { defineConfig } from 'vitepress'

// Claw2Bio — claw2bio.site
// Bilingual: English is the default (root), Chinese under /zh/.
export default defineConfig({
  title: 'Claw2Bio',
  description: 'Lab-validated AI agent skills for biomedical data analysis — no coding required.',
  cleanUrls: true,

  locales: {
    root: {
      label: 'English',
      lang: 'en',
      themeConfig: {
        nav: [
          { text: 'Home', link: '/' },
          { text: 'Get Started', link: '/get-started' },
          { text: 'Skills', link: '/skills/' },
          { text: 'Download', link: '/download' },
          { text: 'Citation', link: '/citation' },
          { text: 'GitHub ↗', link: 'https://github.com/nihuanhe/claw2bio' }
        ],
        sidebar: {
          '/skills/': [
            {
              text: 'Skills',
              items: [
                { text: 'Set up your AI Agent (read first)', link: '/skills/ai-agent-setup' }
              ]
            },
            {
              text: 'Experiment Data Processing',
              items: [
                { text: 'qPCR mRNA (ΔΔCt)', link: '/skills/qpcr-mrna' },
                { text: 'qPCR mtDNA copy number', link: '/skills/qpcr-mtdna' },
                { text: 'mIF contrast (ImageJ)', link: '/skills/if-contrast' },
                { text: 'Open-field test', link: '/skills/OFT' },
                { text: 'WB densitometry', link: '/skills/wb-imagej' }
              ]
            },
            {
              text: 'Bioinformatics Analysis',
              items: [
                {
                  text: 'Phylogenetic tree',
                  collapsed: false,
                  items: [
                    { text: 'Phylo tree — build', link: '/skills/phylo-tree-build' },
                    { text: 'Phylo tree — plot', link: '/skills/phylo-tree-plot' }
                  ]
                },
                {
                  text: 'Single-cell sequencing',
                  collapsed: false,
                  items: [
                    { text: 'Single-cell RNA-seq', link: '/skills/scRNA-seq' },
                    { text: 'scRNA-seq pseudotime', link: '/skills/scRNA-seq-pseudotime' },
                    { text: 'scRNA-seq virtual KO', link: '/skills/scRNA-seq-virtual-ko' }
                  ]
                },
                {
                  text: 'RNA-seq analysis',
                  collapsed: false,
                  items: [
                    { text: 'Bulk RNA-seq DEG', link: '/skills/bulk-RNA-seq' },
                    { text: 'Enrichment (GO/KEGG/Reactome)', link: '/skills/RNA-seq-enrichment' },
                    { text: 'Gene expression plots', link: '/skills/RNA-seq-gene-plot' },
                    { text: 'GSEA', link: '/skills/RNA-seq-GSEA' }
                  ]
                }
              ]
            },
            {
              text: 'Figure & Table Generation',
              items: [
                { text: 'Grouped bar plot', link: '/skills/barplot' },
                { text: 'Clinical tables', link: '/skills/clinical-table' },
                { text: 'Survival curve', link: '/skills/survival-curve' },
                { text: 'Brain atlas annotate', link: '/skills/brain-if-atlas-annotate' },
                { text: 'Compress images', link: '/skills/compress-image' }
              ]
            }
          ]
        },
        outline: { level: [2, 3] }
      }
    },
    zh: {
      label: '简体中文',
      lang: 'zh-CN',
      link: '/zh/',
      themeConfig: {
        nav: [
          { text: '首页', link: '/zh/' },
          { text: '快速上手', link: '/zh/get-started' },
          { text: '技能', link: '/zh/skills/' },
          { text: '下载', link: '/zh/download' },
          { text: '引用', link: '/zh/citation' },
          { text: 'GitHub ↗', link: 'https://github.com/nihuanhe/claw2bio' }
        ],
        sidebar: {
          '/zh/skills/': [
            {
              text: '技能',
              items: [
                { text: '安装 AI Agent（先读）', link: '/zh/skills/ai-agent-setup' }
              ]
            },
            {
              text: '实验数据处理',
              items: [
                { text: 'qPCR mRNA（ΔΔCt）', link: '/zh/skills/qpcr-mrna' },
                { text: 'qPCR mtDNA 拷贝数', link: '/zh/skills/qpcr-mtdna' },
                { text: '免疫荧光多通道对比度', link: '/zh/skills/if-contrast' },
                { text: '旷场实验 OFT', link: '/zh/skills/OFT' },
                { text: 'WB 灰度定量', link: '/zh/skills/wb-imagej' }
              ]
            },
            {
              text: '生信数据分析',
              items: [
                {
                  text: '进化树',
                  collapsed: false,
                  items: [
                    { text: '进化树 · 建树', link: '/zh/skills/phylo-tree-build' },
                    { text: '进化树 · 绘图', link: '/zh/skills/phylo-tree-plot' }
                  ]
                },
                {
                  text: '单细胞测序',
                  collapsed: false,
                  items: [
                    { text: '单细胞 RNA-seq', link: '/zh/skills/scRNA-seq' },
                    { text: '单细胞拟时序', link: '/zh/skills/scRNA-seq-pseudotime' },
                    { text: '单细胞虚拟敲除', link: '/zh/skills/scRNA-seq-virtual-ko' }
                  ]
                },
                {
                  text: 'RNA-seq分析',
                  collapsed: false,
                  items: [
                    { text: 'Bulk RNA-seq 差异分析', link: '/zh/skills/bulk-RNA-seq' },
                    { text: '富集分析（GO/KEGG/Reactome）', link: '/zh/skills/RNA-seq-enrichment' },
                    { text: '基因表达对比图', link: '/zh/skills/RNA-seq-gene-plot' },
                    { text: 'GSEA', link: '/zh/skills/RNA-seq-GSEA' }
                  ]
                }
              ]
            },
            {
              text: '图表生成',
              items: [
                { text: '分组柱状图', link: '/zh/skills/barplot' },
                { text: '临床统计表', link: '/zh/skills/clinical-table' },
                { text: '生存分析曲线', link: '/zh/skills/survival-curve' },
                { text: '脑 atlas 叠加标注', link: '/zh/skills/brain-if-atlas-annotate' },
                { text: '图片批量压缩', link: '/zh/skills/compress-image' }
              ]
            }
          ]
        },
        outline: { level: [2, 3], label: '本页目录' }
      }
    }
  },

  themeConfig: {
    logo: '/logo.svg',
    socialLinks: [
      { icon: 'github', link: 'https://github.com/nihuanhe/claw2bio' }
    ],
    footer: {
      message: 'Lab-validated AI agent skills for biomedical research. 实验室实战验证的 AI agent 技能库。',
      copyright: '© 2026 Claw2Bio · <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener">粤ICP备2026052114号</a>'
    },
    search: {
      provider: 'local'
    }
  }
})
