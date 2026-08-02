# AGENTS.md — 博客协作规范

本文件是给**任何 AI 代理或协作者**（Claude、Cursor、Codex 等）以及人工维护者使用的权威工作规范。
开始处理本仓库的任何任务前，请先完整阅读本文件。

## 仓库概览

- **技术栈**：Astro + Dante 主题 + GitHub Pages
- **站点地址**：https://scchy.github.io/scc-blog/
- **仓库**：`scchy/scc-blog`
- **语言**：内容为中文（本站 + 掘金）+ 英文（Dev.to）
- **Node.js**：≥ 22（Dante 主题要求）

## 核心目录结构

```
src/content/blog/          # 博客文章（核心）
  first-post.md            # 中文版（本站 + 掘金）
  first-post.en.md         # 英文版（Dev.to）
src/content/projects/      # 作品集
src/content/pages/         # 静态页（about/contact 等）
src/content.config.ts      # 内容集合 schema（含 .en.md 排除规则）
src/data/site-config.ts    # 站点信息、导航、社交链接
scripts/
  devto-sync.mjs           # Dev.to 同步（读 .en.md）
  juejin-sync.mjs          # 掘金同步（读 .md，存草稿）
.github/workflows/
  deploy.yml               # 本站部署
  devto-sync.yml           # Dev.to + 掘金同步
```

## 写作规范（最重要的规则）

### 每篇文章必须维护中英双语两个文件
```
src/content/blog/<slug>.md        # 中文版
src/content/blog/<slug>.en.md     # 英文版
```

**分发规则**：
| 文件 | 用途 | 平台 |
|------|------|------|
| `<slug>.md` | 中文版 | 本站 + 掘金（存草稿） |
| `<slug>.en.md` | 英文版 | Dev.to（直接发布） |

**不要**在两个文件里写不同的 slug —— slug 由文件名决定，两个文件用相同基础名（如 `first-post` / `first-post.en`）。

### Frontmatter 要求
```yaml
---
title: 文章标题
excerpt: 摘要（掘金/Dev.to 用作 description）
publishDate: YYYY-MM-DD
isFeatured: false
tags:
  - 主题分类        # 本站分类（5大主题之一）
seo:
  title: ...
  description: ...
  pageType: article
---
```

- 英文版 `tags` 用英文单词（Dev.to 标签清洗为小写字母数字）
- 中文版 `tags` 用中文分类

### 5 大主题分类
1. 强化学习（RL）
2. LLM + Agent
3. 机器学习与深度学习（ML + DeepLearning）
4. 亲子成长
5. 经验分享

## 敏感信息脱敏（强制）

**严禁**在文章或提交内容中出现以下信息：
- ❌ 本地绝对路径（如 `/home/...`、`C:\Users\...`）
- ❌ API key、token、cookie、sessionid、密码
- ❌ 私密环境变量值
- ❌ 个人隐私信息（家庭住址、身份证等）

正确做法：用占位符或通用描述代替（如 `在你的项目目录下`）。

## 多平台同步机制

### 触发方式
`git push` 到 `main` 分支，且变更涉及 `src/content/blog/**` 时，自动触发：
1. **本站部署**（`.github/workflows/deploy.yml`）— 构建并部署中文版
2. **Dev.to 同步**（`devto-sync.yml` 内）— 读 `.en.md`，直接发布
3. **掘金同步**（`devto-sync.yml` 内）— 读 `.md`，存草稿

### 关键实现细节
- **Dev.to**：有官方 API，`devto-sync.mjs` 用 `canonical_url` 匹配已存在文章（Dev.to 的 slug 是自动生成的，不可用 slug 匹配），英文版直接发布
- **掘金**：无官方 API，`juejin-sync.mjs` 通过 `api.juejin.cn` 网页端接口 + 登录 cookie 实现；**必须用 curl 发送请求**（Node `fetch` 对含特殊字符的 Cookie 头处理不可靠）；掘金草稿列表接口不可用，按**已发布文章**匹配（已发布则更新，否则创建草稿）
- 所有分发文章带 `canonical_url` 指向本站，避免 SEO 重复

### 需要的 GitHub Secrets
- `DEV_API_KEY`：Dev.to API key
- `JUEJIN_COOKIE`：掘金登录 cookie（含 `sessionid`）
- `JUEJIN_UUID`：掘金 uuid（可选）

## 内容集合排除规则
`src/content.config.ts` 中 blog collection 用 glob 排除 `**/*.en.md`，确保英文版**不在本站生成页面**。修改时勿破坏此规则。

## 构建与验证
```bash
npm install
npm run build      # 本地构建验证（应看到英文版被排除，只生成中文页面）
npm run dev        # 本地开发
```

提交前建议本地 `npm run build` 确认无错误、英文版未生成页面。

## 提交规范
- 提交信息简洁描述改动（如 `docs: ...`、`fix: ...`、`feat: ...`）
- 网络不稳定时 push 需重试；push 成功后 remote 会重置为无 token 地址（勿提交含 token 的 remote）

## 安全提醒
- 掘金 cookie 会过期，需定期更新；如 cookie 曾在不安全环境暴露，建议重新登录更换
- 勿将任何 secret 写入代码或提交历史
