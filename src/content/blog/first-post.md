---
title: 第一篇：用 Astro 搭建个人开发者博客（完整过程）
excerpt: 从零开始用 Astro + GitHub Pages 搭建自托管开发者博客的完整过程：方案选型、架构设计、五步搭建、双轨内容策略，以及实际踩坑记录。
publishDate: 2026-08-01
isFeatured: true
tags:
  - 经验分享
  - Astro
  - GitHub Pages
  - SEO
  - 博客
  - 工作流
seo:
  title: 用 Astro 搭建个人开发者博客（完整过程）
  description: 从零开始用 Astro + GitHub Pages 搭建自托管开发者博客的完整过程：方案选型、架构设计、五步搭建、双轨内容策略，以及实际踩坑记录。
  pageType: article
---

## 为什么开始写博客

作为一个开发者，**沉淀和输出是最好的学习方式**。但写在哪、怎么沉淀，决定了内容的价值能否长期积累。

对比了公众号、知乎、掘金等平台后，我最终选择了**自托管博客作为主阵地**。核心原因有三个：

1. **内容所有权完全在自己手中**：不会被平台算法、封禁、改版或商业化影响
2. **SEO 长期积累**：有价值的内容可以持续从搜索引擎获得自然流量
3. **零服务器成本**：GitHub Pages 免费托管，配合 Astro 生成纯静态站点

## 双轨内容策略

这是我搭建这个博客的核心方法论——**"自托管主阵地 + 社区分发"**的双轨模式：

| 轨道 | 平台 | 定位 | 优势 |
|------|------|------|------|
| **主阵地** | 本站（Astro） | 沉淀 SEO 与长期内容 | 内容所有权、SEO 积累、可迁移 |
| **分发渠道** | Dev.to、掘金 | 获取即时反馈和流量 | 社区曝光、快速互动、冷启动 |

**关键原则：canonical URL**

所有分发到社区的文章，都必须通过 `canonical_url` 指向本站原文，避免搜索引擎判定为重复内容。这样：
- 社区平台带来即时流量
- 搜索引擎的权重最终归集到本站
- 即使平台变动，内容资产不丢

## 方案选型：为什么选 Astro

对比了几种主流的静态站点方案：

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **Astro** | 零 JS 默认、Islands 架构、性能极致、MDX 原生 | 生态相对新 | **内容型站点（博客）** |
| Next.js | 功能强大、React 生态 | 较重、构建慢 | 复杂应用 |
| Hexo / Jekyll | 主题多、生态成熟 | 灵活性一般 | 传统博客 |
| Hugo | 构建极快 | Go 模板学习曲线 | 大型文档 |

Astro 的几个特性特别适合博客：

- **零 JS 默认**：页面默认不加载 JavaScript，首屏极快
- **Islands 架构**：只在需要交互的地方按需加载 JS
- **Markdown / MDX 原生支持**：写文章就是写 Markdown
- **内容集合（Content Collections）**：内置类型安全的内容管理

## 架构设计

```
┌─────────────────┐   git push   ┌─────────────────────┐   build & deploy   ┌─────────────────┐
│  本地 Markdown  │ ────────────► │  GitHub Repository  │ ──────────────────► │  GitHub Pages   │
│  (src/content)  │              │  (scc-blog)         │                     │  (静态站点)      │
└─────────────────┘              └─────────────────────┘                     └─────────────────┘
```

**技术栈**：Astro + Node.js 22 + GitHub Actions + GitHub Pages

| 组件 | 职责 |
|------|------|
| `src/content/blog/` | Markdown 文章存放 |
| `astro.config.mjs` | Astro 配置（site、base、集成） |
| `.github/workflows/deploy.yml` | GitHub Actions 自动构建部署 |
| `public/` | 静态资源（favicon、robots.txt 等） |
| `dist/` | 构建输出目录 |

## 完整搭建过程

### 第 1 步：初始化 Astro 项目

```bash
# 在你的项目目录下初始化
npm create astro@latest scc-blog -- --template blog --no-install
cd scc-blog
npm install
```

这步会生成 Astro 官方 blog 模板，包含首页、文章列表、文章详情页、BaseHead 组件等基础结构。

### 第 2 步：配置 GitHub Pages 部署

创建 `.github/workflows/deploy.yml`：

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: 'npm'
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-pages-artifact@v4
        with:
          path: ./dist

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/deploy-pages@v4
        id: deployment
```

配置 `astro.config.mjs` 适配 GitHub Pages 子路径：

```javascript
export default defineConfig({
  site: 'https://scchy.github.io',
  base: '/scc-blog',
  integrations: [mdx(), sitemap()],
});
```

**注意点**：
- `site` 是 GitHub Pages 域名
- `base` 必须是仓库名，因为项目页地址是 `https://scchy.github.io/scc-blog/`

### 第 3 步：本地化内容与站点信息

把默认英文模板改成中文：

```typescript
// src/consts.ts
export const SITE_TITLE = 'SCC 的博客';
export const SITE_DESCRIPTION = '记录技术、思考与成长的开发者博客';
```

把首页 `lang` 改为 `zh-CN`，Hero 文案改为中文，文章 frontmatter 增加 `canonical_url` 字段。

### 第 4 步：添加 README 与写作流程

README 记录了本地开发、写作流程、部署地址和内容分发策略，方便后续维护和（可能的）协作。

### 第 5 步：连接远程仓库并推送

```bash
git remote add origin https://github.com/scchy/scc-blog.git
git push origin main
```

推送到 `main` 分支后，GitHub Actions 自动触发构建和部署。

## 数据流

1. 作者在 `src/content/blog/` 下新建 Markdown 文件
2. 填写 Frontmatter（title、description、pubDate、tags、canonical_url）
3. `git commit` + `git push` 到 main 分支
4. GitHub Actions 触发：checkout → setup-node → npm ci → build → deploy-pages
5. GitHub Pages 提供 `dist/` 目录的静态文件

## 实际踩坑记录

### 1. GitHub 用户名不一致

最初配置用的 `scc.github.io`，但实际 GitHub 账号是 `scchy`。导致：
- `astro.config.mjs` 的 `site` 和 `base` 需要修正为 `scchy.github.io`
- `README` 和文章的 `canonical_url` 都要同步改
- git remote 也要改成 `github.com/scchy/scc-blog.git`

**教训**：搭建前先确认 GitHub 用户名，所有 URL 用占位符统一管理，避免散落各处。

### 2. GitHub Pages 404

第一次访问 `https://scchy.github.io/scc-blog/` 返回 404，原因排查：
- GitHub Actions workflow 可能失败
- Pages 的 **Source 必须是 `GitHub Actions`**，不能选 `Deploy from a branch`
- 首次部署有延迟，需要等 5-10 分钟

### 3. push 网络不稳定

本地 `git commit` 成功，但 `git push` 多次因网络抖动失败。解决：
- 用带 token 的 remote URL 重试多次
- push 成功后立即把 remote 重置为干净地址（不带 token）

### 4. SEO 细节补充

搭建完成后补充了 SEO 相关文件：
- `public/robots.txt`：允许搜索引擎抓取，声明 sitemap
- `src/pages/rss.xml.js`：生成 RSS 订阅源
- `BaseHead.astro`：修复 OG 图片 URL，增加 RSS 自动发现

## 博客演进与现状

搭建完成后，博客又经历了多次迭代，当前功能包括：

- **Dante 主题**：从默认 blog 模板迁移到 Dante 主题，博客 + 作品集二合一，支持暗色模式、View Transitions 页面过渡
- **5 大主题分类**：强化学习、LLM + Agent、机器学习与深度学习、亲子成长、经验分享
- **阅读时间 & 文章目录（TOC）**：自动估算阅读时长，生成可跳转的章节目录
- **RSS & Sitemap**：自动生成 RSS 订阅源和站点地图
- **Google Search Console 接入**：已验证域名并提交 sitemap，可监控收录情况
- **SEO 优化**：Open Graph、Twitter Card、canonical URL、robots.txt
- **多平台分发（双语）**：每篇文章维护中文版与英文版，通过 GitHub Actions 自动同步——中文版发本站 + 掘金（存草稿），英文版发 Dev.to（直接发布），全部带 canonical URL 指回本站，避免 SEO 重复

## 多平台分发架构

内容采用**「自托管主阵地 + 社区分发」**的双轨策略，通过 GitHub Actions 实现半自动分发：

```
        ┌──────────────────────────────────────────────┐
        │           src/content/blog/                   │
        │   first-post.md（中文版）  first-post.en.md（英文版）│
        └──────────────────────────────────────────────┘
                          │ git push
                          ▼
              ┌───────────────────────┐
              │   GitHub Actions       │
              └───────────────────────┘
            ┌───────────┼───────────┐
            ▼           ▼           ▼
      ┌──────────┐ ┌─────────┐ ┌─────────┐
      │ 本站(中文) │ │ 掘金(中文)│ │Dev.to(英)│
      │ 自动部署   │ │ 存草稿   │ │ 直接发布 │
      └──────────┘ └─────────┘ └─────────┘
         全部带 canonical_url 指回本站
```

**分发规则**：
- **本站**：部署中文版（`.md`），英文版（`.en.md`）通过 content collection 排除，不生成页面
- **掘金**：同步中文版（`.md`）为**草稿**，由作者在后台手动发布（规避平台对批量发布的 AI 内容风控）
- **Dev.to**：同步英文版（`.en.md`）并**直接发布**（Dev.to 有官方 API，支持全自动）

**关键技术点**：
- 掘金无官方公开 API，通过其网页端 `api.juejin.cn` 接口 + 登录 cookie 实现（与社区 MCP 方案同源）
- 用 `curl` 而非 Node `fetch` 发送带 cookie 的请求——`fetch` 对含特殊字符的 Cookie 头处理不可靠
- 掘金的草稿列表接口不可用，故按**已发布文章**匹配：已发布则更新，否则创建新草稿

## 下一步计划

1. 持续写作，每周至少一篇
2. 补充作品集真实项目
3. 考虑绑定自定义域名和接入评论系统
4. 完善掘金分发：把草稿发布流程半自动化

这个博客会记录我在技术、产品和个人成长方面的思考，欢迎常来看看。
