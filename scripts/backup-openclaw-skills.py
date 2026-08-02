#!/usr/bin/env python3
"""
每周备份 OpenClaw 技能到 scc-blog 仓库，并生成汇总博客文章。
用法：
    python3 scripts/backup-openclaw-skills.py
"""
from pathlib import Path
from datetime import datetime, timezone
import shutil
import re

# 配置
HOME = Path.home()
SKILL_DIRS = [
    HOME / '.openclaw' / 'workspace' / 'skills',
    HOME / '.openclaw' / 'extensions',
]
BLOG_REPO = Path('/home/scc/sccWork/devData/sccDisk/openClaw/gitProj/scc-blog')
BACKUP_DIR = BLOG_REPO / 'public' / 'openclaw-skills-backup'
POSTS_DIR = BLOG_REPO / 'src' / 'content' / 'blog'
SITE_URL = 'https://scchy.github.io/scc-blog'


def parse_skill_name(md_path: Path) -> tuple[str, str]:
    """从 SKILL.md 提取 name 和 description。"""
    text = md_path.read_text(encoding='utf-8')
    name_match = re.search(r'^name:\s*(.+)$', text, re.MULTILINE)
    desc_match = re.search(r'^description:\s*\|\s*\n?\s*(.+?)(?:\n\n|\n\w)', text, re.DOTALL | re.MULTILINE)
    name = name_match.group(1).strip() if name_match else md_path.parent.name
    desc = ''
    if desc_match:
        desc = ' '.join(line.strip() for line in desc_match.group(1).splitlines() if line.strip())
    return name, desc


def backup_skills() -> list[dict]:
    """扫描技能目录，复制 SKILL.md 到备份目录，返回技能列表。"""
    skills = []
    if BACKUP_DIR.exists():
        shutil.rmtree(BACKUP_DIR)
    BACKUP_DIR.mkdir(parents=True)

    for root in SKILL_DIRS:
        if not root.exists():
            continue
        for skill_md in root.rglob('SKILL.md'):
            skill_dir = skill_md.parent
            rel = skill_dir.relative_to(root)
            target_dir = BACKUP_DIR / rel
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(skill_md, target_dir / 'SKILL.md')
            # 复制同目录下脚本（scripts/ 或 references/）
            for sub in ('scripts', 'references'):
                src_sub = skill_dir / sub
                if src_sub.exists():
                    shutil.copytree(src_sub, target_dir / sub, dirs_exist_ok=True)
            name, desc = parse_skill_name(skill_md)
            skills.append({'name': name, 'desc': desc, 'path': str(rel)})

    return sorted(skills, key=lambda x: x['name'])


def group_skills(skills: list[dict]) -> dict[str, list[dict]]:
    """简单按关键字分组。"""
    groups = {}
    for s in skills:
        desc_lower = s['desc'].lower()
        if 'feishu' in desc_lower:
            key = '飞书工具类'
        elif 'model' in desc_lower or '模型' in desc_lower or '路由' in desc_lower:
            key = '模型管理类'
        elif 'search' in desc_lower or 'todo' in desc_lower or 'token' in desc_lower:
            key = '搜索与效率类'
        else:
            key = '其他'
        groups.setdefault(key, []).append(s)
    return groups


def generate_post(skills: list[dict]) -> str:
    """生成博客 Markdown 内容。"""
    today = datetime.now(timezone.utc).astimezone().strftime('%Y-%m-%d')
    total_files = sum(1 for _ in BACKUP_DIR.rglob('*') if _.is_file())
    size_kb = sum(f.stat().st_size for f in BACKUP_DIR.rglob('*') if f.is_file()) / 1024
    groups = group_skills(skills)

    lines = [
        '---',
        f"title: 'OpenClaw 技能库备份与整理（{today}）'",
        "description: '记录个人 OpenClaw 助手技能库的 weekly backup，包含技能分类、用途与自动化计划。'",
        f"pubDate: {today}",
        "tags: ['openclaw', 'skills', 'backup', 'workflow']",
        f"canonical_url: {SITE_URL}/blog/openclaw-skills-backup-{today}/",
        '---',
        '',
        f"> 每周把 `~/.openclaw/workspace/skills` 和 `~/.openclaw/extensions` 下的技能整理一次，避免本地环境翻车导致丢失。\n",
        f"## 本周备份概况\n",
        f"- **备份时间**：{today}",
        f"- **技能总数**：{len(skills)} 个",
        f"- **文件总数**：{total_files} 个",
        f"- **占用空间**：约 {size_kb:.1f} KB\n",
        "## 技能分类\n",
    ]

    for group_name, items in groups.items():
        lines.append(f"### {group_name}（{len(items)} 个）\n")
        lines.append("| 技能 | 用途 |")
        lines.append("|------|------|")
        for s in items:
            lines.append(f"| `{s['name']}` | {s['desc']} |")
        lines.append('')

    lines.extend([
        "## 为什么做这件事\n",
        "OpenClaw 的技能都是 Markdown + 可选脚本，结构简单但数量会越来越多。每周备份一次可以：\n",
        "1. **防丢失**：本地环境重装或误删时能快速恢复",
        "2. **可追溯**：通过 Git 历史查看技能演进",
        "3. **可分享**：整理成博客后，方便给他人参考\n",
        "## 自动备份脚本\n",
        "备份脚本已放在仓库 `scripts/backup-openclaw-skills.py`，运行后会：\n",
        "1. 扫描 `~/.openclaw/workspace/skills` 和 `~/.openclaw/extensions`",
        "2. 将 SKILL.md 及相关脚本复制到 `public/openclaw-skills-backup/`",
        "3. 在 `src/content/blog/` 生成本周汇总文章\n",
        "```bash\npython3 scripts/backup-openclaw-skills.py\n```\n",
        "## 相关链接\n",
        "- 博客源码：[github.com/scchy/scc-blog](https://github.com/scchy/scc-blog)",
        f"- 站点地址：[{SITE_URL}]({SITE_URL})",
        "",
    ])

    return '\n'.join(lines)


def main():
    print("[1/3] 扫描并备份技能...")
    skills = backup_skills()
    print(f"  发现 {len(skills)} 个技能")

    print("[2/3] 生成博客文章...")
    today = datetime.now(timezone.utc).astimezone().strftime('%Y-%m-%d')
    post_path = POSTS_DIR / f'openclaw-skills-backup-{today}.md'
    post_path.write_text(generate_post(skills), encoding='utf-8')
    print(f"  已生成 {post_path}")

    print("[3/3] 完成。建议执行：")
    print("  git add .")
    print("  git commit -m 'backup openclaw skills'")
    print("  git push origin main")


if __name__ == '__main__':
    main()
