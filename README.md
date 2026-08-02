# SCC 的博客

基于 [Astro](https://astro.build) + [Dante 主题](https://github.com/JustGoodUI/dante-astro-theme) + [GitHub Pages](https://pages.github.com/) 构建的个人开发者博客（博客 + 作品集二合一）。

## 本地开发

```bash
npm install
npm run dev
```

要求 Node.js ≥ 22。

## 写作流程

1. 在 `src/content/blog/` 下新建 Markdown 文件
2. 填写 Frontmatter：title、excerpt、publishDate、tags、isFeatured、seo
3. `git push` 到 main 分支，GitHub Actions 自动部署

## 作品集

在 `src/content/projects/` 下添加作品条目，首页和 `/projects` 页面自动展示。

## 部署

- 站点地址：https://scchy.github.io/scc-blog/
- 工作流：`.github/workflows/deploy.yml`

## 内容分发

- 主阵地：本站，沉淀 SEO 与长期内容
- 分发渠道：Dev.to、掘金（同步时加 `canonical_url` 指向本站）

## 站点配置

- 站点信息、导航、社交链接：`src/data/site-config.ts`
