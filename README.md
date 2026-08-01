# SCC 的博客

基于 [Astro](https://astro.build) + [GitHub Pages](https://pages.github.com/) 构建的个人开发者博客。

## 本地开发

```bash
npm install
npm run dev
```

## 写作流程

1. 在 `src/content/blog/` 下新建 Markdown 文件
2. 填写 Frontmatter：title、description、pubDate、tags、canonical_url
3. `git push` 到 main 分支，GitHub Actions 自动部署

## 部署

- 站点地址：https://scc.github.io/scc-blog/
- 工作流：`.github/workflows/deploy.yml`

## 内容分发

- Dev.to 同步时加上 `canonical_url` 指向本站
- 掘金同步时在文末加原文链接
