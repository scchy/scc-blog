#!/usr/bin/env node
/**
 * 掘金自动同步脚本（存草稿模式）
 * 读取 src/content/blog/ 下的中文版文章（.md，排除 .en.md），同步到掘金草稿箱
 * 通过标题匹配，已存在则更新草稿，否则创建新草稿
 * 需要环境变量 JUEJIN_COOKIE
 *
 * 说明：掘金无官方公开 API，此脚本调用 api.juejin.cn 网页端接口（与掘金 MCP server 同源），
 * 使用登录 cookie（sessionid）认证。默认只存草稿，由作者在掘金后台手动发布，规避平台风控。
 */
import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { execFileSync } from 'node:child_process';
import matter from 'gray-matter';

const JUEJIN_COOKIE = (process.env.JUEJIN_COOKIE || '').trim().replace(/\s+/g, ' ');
if (!JUEJIN_COOKIE) {
    console.error('❌ 缺少 JUEJIN_COOKIE 环境变量');
    process.exit(1);
}

const JUEJIN_AID = process.env.JUEJIN_AID || '2608';
const JUEJIN_UUID = (process.env.JUEJIN_UUID || '').trim();
const JUEJIN_CSRF_TOKEN = process.env.JUEJIN_CSRF_TOKEN || '';

if (process.env.DEBUG) {
    console.log(`🔍 DEBUG: cookie长度=${JUEJIN_COOKIE.length}, uuid='${JUEJIN_UUID}', aid='${JUEJIN_AID}'`);
}

const BLOG_DIR = join(process.cwd(), 'src', 'content', 'blog');

// 分类/标签默认值（后端分类 + 后端标签），可在文章 frontmatter 覆盖
const DEFAULT_CATEGORY_ID = process.env.JUEJIN_CATEGORY_ID || '6809637769959178254';
const DEFAULT_TAG_ID = process.env.JUEJIN_TAG_ID || '6809640408797167623';

const API_BASE = 'https://api.juejin.cn';

function buildUrl(base, extraParams = []) {
    const params = [];
    if (JUEJIN_AID) params.push(`aid=${JUEJIN_AID}`);
    if (JUEJIN_UUID) params.push(`uuid=${JUEJIN_UUID}`);
    if (extraParams.length) params.push(...extraParams);
    return params.length ? `${base}?${params.join('&')}` : base;
}

// 使用 curl 发送请求（Node fetch 对含特殊字符的 Cookie header 处理不可靠，curl 已验证稳定）
// cookie 用 --cookie 选项传入，避免 header 转义问题
async function api(path, data, extraParams = []) {
    const url = buildUrl(`${API_BASE}${path}`, extraParams);
    const args = [
        '-s', '-X', 'POST', url,
        '--cookie', JUEJIN_COOKIE,
        '-H', 'Content-Type: application/json',
        '-H', 'Accept: */*',
        '-H', 'Origin: https://juejin.cn',
        '-H', 'Referer: https://juejin.cn/',
        '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        '-d', JSON.stringify(data),
    ];
    if (JUEJIN_CSRF_TOKEN) args.push('-H', `x-secsdk-csrf-token: ${JUEJIN_CSRF_TOKEN}`);

    if (process.env.DEBUG) {
        console.log(`🔍 curl → ${url} | cookie_len=${JUEJIN_COOKIE.length}`);
    }
    let out;
    try {
        out = execFileSync('curl', args, { encoding: 'utf-8' });
    } catch (e) {
        throw new Error(`curl 执行失败: ${e.message}`);
    }
    const body = JSON.parse(out);
    if (body.err_no !== undefined && body.err_no !== 0) {
        throw new Error(`掘金 API err_no=${body.err_no}: ${body.err_msg || JSON.stringify(body)}`);
    }
    return body;
}

// 获取用户已发布文章列表（用于按标题匹配）
async function listArticles() {
    const data = { page_no: 1, page_size: 50, keyword: '', audit_status: null };
    const body = await api('/content_api/v1/article/list_by_user', data, ['spider=0']);
    return (body.data || []).map((a) => ({ id: a.article_id, title: a.article_info?.title }));
}

async function main() {
    // 只同步中文版（.md），排除 .en.md 英文版（英文版走 Dev.to）
    const files = readdirSync(BLOG_DIR).filter((f) => f.endsWith('.md') && !f.endsWith('.en.md'));
    console.log(`📄 发现 ${files.length} 篇中文文章（.md）`);

    // 注：掘金的 article_draft/list（草稿列表）接口返回"请求路由不存在"，不可用。
    // 故只按已发布文章匹配：已发布则更新，未发布则创建新草稿（草稿由作者手动发布）。
    const published = await listArticles();
    console.log(`📚 掘金已发布 ${published.length} 篇文章`);

    for (const file of files) {
        const raw = readFileSync(join(BLOG_DIR, file), 'utf-8');
        const { data, content } = matter(raw);

        const categoryId = data.juejin_category_id || DEFAULT_CATEGORY_ID;
        const tagIds = (data.juejin_tag_ids && data.juejin_tag_ids.length) ? data.juejin_tag_ids : [DEFAULT_TAG_ID];

        const draftPayload = {
            title: data.title,
            mark_content: content.trim(),
            brief_content: data.excerpt || data.description || '',
            category_id: categoryId,
            tag_ids: tagIds,
            cover_image: '',
            edit_type: 10,
            html_content: 'deprecated',
        };

        // 匹配已发布的文章（按标题）→ 更新
        const existingPub = published.find((a) => a.title === data.title);
        if (existingPub) {
            console.log(`🔄 更新已发布文章: ${data.title}（id=${existingPub.id}）`);
            // 更新文章本身
            await api('/content_api/v1/article/update', {
                article_id: existingPub.id,
                ...draftPayload,
            });
            continue;
        }

        // 未匹配到已发布文章 → 创建新草稿（由作者在掘金后台手动发布）
        console.log(`📝 创建草稿: ${data.title}`);
        await api('/content_api/v1/article_draft/create', draftPayload);
    }
    console.log('✅ 掘金同步完成（草稿模式，请在掘金后台手动发布）');
}

main().catch((err) => {
    console.error('❌ 同步失败:', err.message);
    process.exit(1);
});
