---
title: "Building a Self-Hosted Developer Blog with Astro: The Complete Guide"
excerpt: "The complete journey of building a self-hosted developer blog with Astro + GitHub Pages: tech selection, architecture design, a five-step setup, a dual-track content strategy, and real pitfalls encountered along the way."
publishDate: 2026-08-01
isFeatured: true
tags:
  - Astro
  - GitHub Pages
  - SEO
  - Blogging
  - Workflow
seo:
  title: "Building a Self-Hosted Developer Blog with Astro: The Complete Guide"
  description: "The complete journey of building a self-hosted developer blog with Astro + GitHub Pages: tech selection, architecture design, a five-step setup, a dual-track content strategy, and real pitfalls encountered along the way."
  pageType: article
---

## Why I Started a Blog

As a developer, **writing things down and sharing them is the best way to learn**. But *where* you write and *how* you organize it determines whether your content can compound in value over the long term.

After comparing platforms like WeChat Official Accounts, Zhihu, and Juejin, I ultimately chose a **self-hosted blog as my home base**. Three core reasons:

1. **Full content ownership**: Not subject to platform algorithms, bans, redesigns, or commercialization
2. **Long-term SEO compounding**: Valuable content keeps earning organic search traffic
3. **Zero server cost**: GitHub Pages hosts for free, paired with Astro to generate a purely static site

## The Dual-Track Content Strategy

This is the core methodology behind this blog — a **"self-hosted home base + community distribution"** dual-track model:

| Track | Platform | Role | Advantage |
|-------|----------|------|-----------|
| **Home base** | This site (Astro) | Compounding SEO & long-term content | Content ownership, SEO accumulation, portability |
| **Distribution** | Dev.to, Juejin | Immediate feedback & traffic | Community exposure, fast interaction, cold-start |

**Key principle: canonical URL**

Every article distributed to communities must point back to the original on this site via `canonical_url`, to avoid search engines flagging duplicate content. This way:
- Communities drive immediate traffic
- Search engine authority eventually accrues to this site
- Even if a platform changes, the content asset is never lost

## Tech Selection: Why Astro

Comparing several mainstream static site options:

| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| **Astro** | Zero JS by default, Islands architecture, extreme performance, native MDX | Relatively young ecosystem | **Content sites (blogs)** |
| Next.js | Powerful, React ecosystem | Heavy, slower builds | Complex applications |
| Hexo / Jekyll | Many themes, mature ecosystem | Less flexible | Traditional blogs |
| Hugo | Extremely fast builds | Go template learning curve | Large documentation |

Several Astro features make it especially well-suited for blogging:

- **Zero JS by default**: pages load no JavaScript by default, blazing-fast first paint
- **Islands architecture**: loads JS only where interaction is needed
- **Native Markdown / MDX support**: writing a post is just writing Markdown
- **Content Collections**: built-in type-safe content management

## Architecture Design

```
┌─────────────────┐   git push   ┌─────────────────────┐   build & deploy   ┌─────────────────┐
│   Local Markdown│ ────────────► │  GitHub Repository  │ ──────────────────► │   GitHub Pages  │
│  (src/content)  │              │  (scc-blog)         │                     │   (static site) │
└─────────────────┘              └─────────────────────┘                     └─────────────────┘
```

**Tech stack**: Astro + Node.js 22 + GitHub Actions + GitHub Pages

| Component | Responsibility |
|-----------|----------------|
| `src/content/blog/` | Markdown article storage |
| `astro.config.mjs` | Astro config (site, base, integrations) |
| `.github/workflows/deploy.yml` | GitHub Actions auto build & deploy |
| `public/` | Static assets (favicon, robots.txt, etc.) |
| `dist/` | Build output directory |

## The Complete Setup Process

### Step 1: Initialize the Astro project

```bash
# In your project directory
npm create astro@latest scc-blog -- --template blog --no-install
cd scc-blog
npm install
```

This generates the official Astro blog template with the homepage, article list, article detail page, BaseHead component, and other basic structure.

### Step 2: Configure GitHub Pages deployment

Create `.github/workflows/deploy.yml`:

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

Configure `astro.config.mjs` for the GitHub Pages subpath:

```javascript
export default defineConfig({
  site: 'https://scchy.github.io',
  base: '/scc-blog',
  integrations: [mdx(), sitemap()],
});
```

**Notes**:
- `site` is the GitHub Pages domain
- `base` must be the repo name, since a project site lives at `https://scchy.github.io/scc-blog/`

### Step 3: Localize content and site info

Convert the default English template to Chinese:

```typescript
// src/consts.ts
export const SITE_TITLE = 'SCC 的博客';
export const SITE_DESCRIPTION = '记录技术、思考与成长的开发者博客';
```

Set the homepage `lang` to `zh-CN`, translate the Hero copy, and add a `canonical_url` field to article frontmatter.

### Step 4: Add README and writing workflow

The README documents local development, the writing workflow, deploy URL, and the content distribution strategy, making future maintenance (and possible collaboration) easier.

### Step 5: Connect the remote and push

```bash
git remote add origin https://github.com/scchy/scc-blog.git
git push origin main
```

After pushing to `main`, GitHub Actions automatically triggers the build and deployment.

## Data Flow

1. Author creates a new Markdown file under `src/content/blog/`
2. Fill in the Frontmatter (title, description, pubDate, tags, canonical_url)
3. `git commit` + `git push` to the main branch
4. GitHub Actions triggers: checkout → setup-node → npm ci → build → deploy-pages
5. GitHub Pages serves the static files from `dist/`

## Real Pitfalls Encountered

### 1. GitHub username mismatch

Initially configured with `scc.github.io`, but the actual GitHub account is `scchy`. This caused:
- `site` and `base` in `astro.config.mjs` needed correcting to `scchy.github.io`
- The `canonical_url` in the README and articles needed updating too
- The git remote also had to change to `github.com/scchy/scc-blog.git`

**Lesson**: confirm your GitHub username before starting; manage all URLs with placeholders to avoid scattering them around.

### 2. GitHub Pages 404

The first visit to `https://scchy.github.io/scc-blog/` returned 404. Troubleshooting:
- The GitHub Actions workflow may have failed
- Pages **Source must be `GitHub Actions`**, not `Deploy from a branch`
- First deployment has a delay; wait 5–10 minutes

### 3. Unstable push network

Local `git commit` succeeded, but `git push` failed multiple times due to network flakiness. Solution:
- Retry multiple times with a tokenized remote URL
- Reset the remote to a clean URL (no token) immediately after a successful push

### 4. SEO details added later

After setup, I added SEO-related files:
- `public/robots.txt`: allow search engines to crawl, declare the sitemap
- `src/pages/rss.xml.js`: generate an RSS feed
- `BaseHead.astro`: fix OG image URLs, add RSS auto-discovery

## Blog Evolution & Current State

After the initial build, the blog went through several more iterations. Current features include:

- **Dante theme**: migrated from the default blog template to the Dante theme — blog + portfolio in one, with dark mode and View Transitions
- **5 topic categories**: Reinforcement Learning, LLM + Agent, ML & Deep Learning, Parenting & Growth, Experience Sharing
- **Reading time & TOC**: auto-estimated reading duration and a jumpable table of contents
- **RSS & Sitemap**: auto-generated RSS feed and site map
- **Google Search Console**: verified the domain and submitted the sitemap, with indexing monitoring
- **SEO optimization**: Open Graph, Twitter Card, canonical URL, robots.txt
- **Multi-platform distribution (bilingual)**: every post is maintained in both Chinese and English, auto-synced via GitHub Actions — Chinese goes to this site + Juejin (as draft), English goes to Dev.to (published directly), all with canonical URLs pointing back here to avoid SEO duplication

## Multi-Platform Distribution Architecture

Content follows the **"self-hosted home base + community distribution"** dual-track strategy, partially automated through GitHub Actions:

```
        ┌──────────────────────────────────────────────┐
        │           src/content/blog/                   │
        │  first-post.md (Chinese)  first-post.en.md (English) │
        └──────────────────────────────────────────────┘
                          │ git push
                          ▼
              ┌───────────────────────┐
              │   GitHub Actions       │
              └───────────────────────┘
            ┌───────────┼───────────┐
            ▼           ▼           ▼
      ┌──────────┐ ┌─────────┐ ┌─────────┐
      │ This site │ │ Juejin  │ │ Dev.to  │
      │ (Chinese) │ │(Chinese)│ │(English)│
      │ auto-deploy│ │ draft   │ │ published│
      └──────────┘ └─────────┘ └─────────┘
          all with canonical_url pointing back here
```

**Distribution rules**:
- **This site**: deploys the Chinese version (`.md`); the English version (`.en.md`) is excluded from the content collection so it doesn't generate a page
- **Juejin**: syncs the Chinese version (`.md`) as a **draft**, published manually by the author in the backend (avoids platform risk-control against AI-batch-published content)
- **Dev.to**: syncs the English version (`.en.md`) and **publishes it directly** (Dev.to has an official API, fully automated)

**Key technical points**:
- Juejin has no official public API; it's accessed via its web `api.juejin.cn` endpoints + login cookie (same source as community MCP solutions)
- Use `curl` instead of Node `fetch` for cookie-bearing requests — `fetch` handles cookies with special characters unreliably
- Juejin's draft-list endpoint is unavailable, so matching is done against **published articles**: update if published, otherwise create a new draft

## What's Next

1. Keep writing — at least one post per week
2. Add real portfolio projects
3. Consider a custom domain and a comments system
4. Improve Juejin distribution: semi-automate the draft publishing flow

This blog documents my thinking on technology, products, and personal growth. Feel free to stop by.
