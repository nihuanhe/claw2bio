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
          { text: 'GitHub ↗', link: 'https://github.com/claw2bio/claw2bio' }
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
                { text: 'Coming soon…', link: '/skills/#bioinformatics' }
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
          { text: 'GitHub ↗', link: 'https://github.com/claw2bio/claw2bio' }
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
                { text: '敬请期待…', link: '/zh/skills/#bioinformatics' }
              ]
            },
            {
              text: '图表生成',
              items: [
                { text: '分组柱状图', link: '/zh/skills/barplot' },
                { text: '临床统计表', link: '/zh/skills/clinical-table' }
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
      { icon: 'github', link: 'https://github.com/claw2bio/claw2bio' }
    ],
    footer: {
      message: 'Lab-validated AI agent skills for biomedical research. 实验室实战验证的 AI agent 技能库。',
      copyright: '© 2026 Claw2Bio · <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener">ICP备案号待填</a>'
    },
    search: {
      provider: 'local'
    }
  }
})
