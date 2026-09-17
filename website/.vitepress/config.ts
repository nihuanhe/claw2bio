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
              text: 'Experiment Data Processing',
              items: [
                { text: 'qPCR mRNA (ΔΔCt)', link: '/skills/qpcr-mrna' },
                { text: 'qPCR mtDNA copy number', link: '/skills/qpcr-mtdna' }
              ]
            },
            {
              text: 'Bioinformatics Analysis',
              items: [
                {
                  text: 'Phylogenetic tree',
                  items: []
                },
                {
                  text: 'Single-cell sequencing',
                  items: []
                },
                {
                  text: 'RNA-seq analysis',
                  items: []
                },
                { text: 'Tutorials in Chinese →', link: '/zh/skills/#bioinformatics' }
              ]
            },
            {
              text: 'Figure & Table Generation',
              items: [
                { text: 'Grouped bar plot', link: '/skills/barplot' },
                { text: 'Clinical tables', link: '/skills/clinical-table' }
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
              text: '实验数据处理',
              items: [
                { text: 'qPCR mRNA（ΔΔCt）', link: '/zh/skills/qpcr-mrna' },
                { text: 'qPCR mtDNA 拷贝数', link: '/zh/skills/qpcr-mtdna' }
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
                { text: '生存分析曲线', link: '/zh/skills/survival-curve' }
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
