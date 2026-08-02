import GithubSlugger from 'github-slugger';

export interface TocItem {
    id: string;
    text: string;
    level: number;
}

// 提取 markdown 正文中的标题（## 和 ###），用于生成 TOC
// 使用与 rehype-slug 相同的 github-slugger，确保 id 与渲染后的锚点一致
export function extractHeadings(markdown: string): TocItem[] {
    const lines = markdown.split('\n');
    const items: TocItem[] = [];
    const slugger = new GithubSlugger();
    const headingRegex = /^(#{2,3})\s+(.+)$/;

    for (const line of lines) {
        const match = line.match(headingRegex);
        if (match) {
            const level = match[1].length; // 2 或 3
            const text = match[2].trim();
            // 去掉 markdown 行内标记
            const cleanText = text
                .replace(/\*\*(.+?)\*\*/g, '$1')
                .replace(/`(.+?)`/g, '$1')
                .replace(/\[(.+?)\]\(.+?\)/g, '$1')
                .trim();
            if (cleanText) {
                items.push({
                    id: slugger.slug(cleanText),
                    text: cleanText,
                    level
                });
            }
        }
    }
    return items;
}

// 估算阅读时间（中文约 400 字/分钟，英文约 200 词/分钟）
export function estimateReadingTime(markdown: string): number {
    const noCode = markdown
        .replace(/```[\s\S]*?```/g, '')
        .replace(/^\s*---[\s\S]*?---/, '')
        .replace(/[#>*_`\-\[\]()|]/g, ' ')
        .replace(/\s+/g, ' ');

    const chineseChars = (noCode.match(/[\u4e00-\u9fa5]/g) || []).length;
    const latinWords = (noCode.match(/[a-zA-Z]+/g) || []).length;

    const minutes = Math.ceil(chineseChars / 400 + latinWords / 200);
    return Math.max(1, minutes);
}
