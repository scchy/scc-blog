#!/usr/bin/env node
/**
 * Dev.to 自动同步脚本
 * 读取 src/content/blog/ 下的 markdown 文章，同步到 Dev.to
 * 通过文章 slug 匹配，已存在则更新，否则创建
 * 需要环境变量 DEV_API_KEY
 */
import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import matter from 'gray-matter';

const DEV_API_KEY = process.env.DEV_API_KEY;
if (!DEV_API_KEY) {
    console.error('❌ 缺少 DEV_API_KEY 环境变量');
    process.exit(1);
}

const SITE_BASE = 'https://scchy.github.io/scc-blog';
const BLOG_DIR = join(process.cwd(), 'src', 'content', 'blog');

// slug 生成（与博客一致）
function slugify(text) {
    return text
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .replace(/[^a-z0-9\s-]/g, '')
        .trim()
        .replace(/[\s-]+/g, '-');
}

async function api(path, options = {}) {
    const res = await fetch(`https://dev.to/api${path}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            'api-key': DEV_API_KEY,
            ...(options.headers || {})
        }
    });
    if (!res.ok) {
        const body = await res.text();
        throw new Error(`Dev.to API ${res.status}: ${body}`);
    }
    return res.json();
}

// 获取用户所有文章（已发布 + 未发布）
async function getUserArticles() {
    const articles = [];
    for (const ep of ['/articles/me', '/articles/me/unpublished']) {
        let page = 1;
        while (true) {
            const batch = await api(`${ep}?per_page=100&page=${page}`);
            if (batch.length === 0) break;
            articles.push(...batch);
            page++;
        }
    }
    // 按 canonical_url 去重（同一文章可能同时出现在两个列表）
    const seen = new Set();
    return articles.filter((a) => {
        const key = a.canonical_url || a.id;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
    });
}

async function main() {
    const files = readdirSync(BLOG_DIR).filter((f) => f.endsWith('.md'));
    console.log(`📄 发现 ${files.length} 篇文章`);

    const existingArticles = await getUserArticles();
    console.log(`📚 Dev.to 现有 ${existingArticles.length} 篇文章`);

    for (const file of files) {
        const raw = readFileSync(join(BLOG_DIR, file), 'utf-8');
        const { data, content } = matter(raw);
        // 用文件名作为 slug（与博客 URL 一致）
        const slug = data.slug || file.replace(/\.md$/, '');
        // Dev.to tag 规则：只能纯小写字母/数字（a-z0-9），去掉空格、连字符等所有特殊字符
        const tags = (data.tags || [])
            .map((t) => t.toLowerCase().replace(/[^a-z0-9]/g, ''))
            .filter((t) => t.length >= 2 && t.length <= 30)
            .slice(0, 4);
        // Dev.to 至少需要 1 个 tag，没有则用默认
        if (tags.length === 0) tags.push('devto');

        // 是否直接发布：DEV_PUBLISH=1 直接发布，否则存为草稿（默认直接发布）
        const publish = (process.env.DEV_PUBLISH || '1') !== '0';
        const article = {
            title: data.title,
            published: publish,
            description: data.excerpt || data.description || '',
            body_markdown: content.trim(),
            tags,
            canonical_url: canonicalUrl
        };

        const canonicalUrl = `${SITE_BASE}/blog/${slug}/`;
        // 匹配已存在的文章（按 canonical_url，Dev.to 的 slug 是自动生成的不可靠）
        const existing = existingArticles.find((a) => a.canonical_url === canonicalUrl);
        if (existing) {
            console.log(`🔄 更新: ${data.title}`);
            await api(`/articles/${existing.id}`, {
                method: 'PUT',
                body: JSON.stringify({ article })
            });
        } else {
            console.log(`🆕 创建: ${data.title}`);
            await api('/articles', {
                method: 'POST',
                body: JSON.stringify({ article })
            });
        }
    }
    console.log('✅ Dev.to 同步完成');
}

main().catch((err) => {
    console.error('❌ 同步失败:', err.message);
    process.exit(1);
});
