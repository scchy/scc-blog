---
title: 'OpenClaw 技能库备份与整理（2026-08-02）'
description: '记录个人 OpenClaw 助手技能库的 weekly backup，包含技能分类、用途与自动化计划。'
pubDate: 2026-08-02
tags: ['openclaw', 'skills', 'backup', 'workflow']
canonical_url: https://scchy.github.io/scc-blog/blog/openclaw-skills-backup-2026-08-02/
---

> 每周把 `~/.openclaw/workspace/skills` 和 `~/.openclaw/extensions` 下的技能整理一次，避免本地环境翻车导致丢失。

## 本周备份概况

- **备份时间**：2026-08-02
- **技能总数**：24 个
- **文件总数**：62 个
- **占用空间**：约 347.7 KB

## 技能分类

### 其他（12 个）

| 技能 | 用途 |
|------|------|
| `"ab-test-setup"` |  |
| `"analytics-tracking"` |  |
| `auto-research` | 自动调研触发器。当用户输入包含"调研"、"研究一下"、"查查"等关键词时， 自动执行：搜索 → 7B筛选 → Kimi分析 的完整流程。 触发词：调研, 研究一下, 查查, 搜索, 找一下 --- |
| `brainstorming` |  |
| `duckduckgo-search` |  |
| `kaoyan-hdu` | 在职考研杭电（杭州电子科技大学）学习管理工具。 触发方式：用户输入 `/ky` 或包含"杭电考研""在职考研""考研打卡""考研答疑"等关键词。 支持：学习打卡、状态查看、计划管理、智能生成计划、周报生成、计划调整、学科答疑。 用 `/ky` 激活后，可跟以下子命令： - `/ky 打卡 [科目] [内容] [时长]` — 记录今日学习 - `/ky 状态` — 查看本周进度与学习统计 - `/ky 计划` 或 `/ky 进度` — 智能生成或更新学习计划 - `/ky 周报` — 生成本周学习周报 - `/ky 调整 [内容]` — 修改计划安排 - `/ky 问 [科目] [题目/问题]` — 学科答疑 - `/ky help` — 显示帮助 --- |
| `karpathy-guidelines` |  |
| `n8n` |  |
| `prd` |  |
| `superpowers` |  |
| `wiki-manager` | LLM Wiki management subagent for OpenClaw. Use when: 1) Ingesting documents into LLM Wiki (ingest) 2) Querying knowledge from LLM Wiki (query) 3) Health checking the wiki (lint) Manages a structured knowledge base using the Karpathy LLM Wiki pattern. --- |
| `writing-plans` |  |

### 搜索与效率类（3 个）

| 技能 | 用途 |
|------|------|
| `auto-tune` | Auto Tune & AlgoMate 项目管理专家。管理 auto_tune 和 algomate 两个项目的迭代开发。 触发方式： - `/at` - 查看项目状态和待办事项 - `/at status` - 查看两个项目的当前状态 - `/at todo` - 列出待办事项 - `/at plan <项目>` - 制定迭代计划 - `/at code <项目>` - 代码审查和建议 管理范围： - auto_tune: /home/scc/.openclaw/workspace/auto_tune/ - algomate: /home/scc/sccWork/devData/sccDisk/algomate/ --- |
| `duckduckgo-search` | Free web search using DuckDuckGo with intelligent tiered processing. Use when you need to search the web without API costs. Features: - Basic search with result limiting - Two-tier processing: Local 7B filters, Kimi analyzes - Automatic token management for long results - Completely free, no API key required --- |
| `token-saver` | Token consumption optimization for OpenClaw sessions. Use when: 1) Context is getting too long and consuming excessive tokens 2) Need to optimize memory retrieval to reduce token usage 3) Want to search memory efficiently without loading full files 4) Need guidance on context management and pruning strategies 5) Need automatic alerts when token usage is high 6) Want to optimize tool results and batch processing Provides: memory_search + memory_get workflow, tool result truncation, session health monitoring, batch task optimization, and automatic alerts. --- |

### 飞书工具类（5 个）

| 技能 | 用途 |
|------|------|
| `feishu-doc` | Feishu document read/write operations. Activate when user mentions Feishu docs, cloud docs, or docx links. --- |
| `feishu-drive` | Feishu cloud storage file management. Activate when user mentions cloud space, folders, drive. --- |
| `feishu-perm` | Feishu permission management for documents and files. Activate when user mentions sharing, permissions, collaborators. --- |
| `feishu-wiki` | Feishu knowledge base navigation. Activate when user mentions knowledge base, wiki, or wiki links. --- |
| `success-moment-logger` | 记录今日成功时刻到飞书文档。 触发方式：用户说"记录今日成功时刻 [内容]" 会将内容追加到飞书文档：https://my.feishu.cn/docx/ABqhdBCaLoazpkxJGHec9Cvmn1c --- |

### 模型管理类（4 个）

| 技能 | 用途 |
|------|------|
| `quick-model` | Quick model switching commands for OpenClaw. Use when: 1) User types /local followed by task to run with local 7B model 2) User types /kimi followed by task to run with cloud Kimi model 3) Need quick sub-agent spawning without writing full sessions_spawn code Provides shortcuts: /local, /kimi for instant model-specific task execution. --- |
| `smart-router` | Intelligent task routing to automatically select the best model for each task. Use when you want to run a task without manually choosing between local 7B and cloud Kimi models. Analyzes task complexity, content type, and requirements to route to: - local-vllm-instruct/qwen2.5-7B for simple, fast, private tasks - kimi-coding/k2p5 for complex, coding, reasoning tasks Simply describe your task and let the router decide the optimal model. --- |
| `todo-manager` | Simple todo management for OpenClaw sessions using local 7B model. Use when: 1) Setting a new todo item for the session 2) Marking a todo as complete 3) Listing current todos 4) Managing session-level tasks without cloud API calls All operations use local-vllm-instruct/qwen2.5-7B model for privacy and speed. --- |
| `todo-manager` | Simple todo management for OpenClaw sessions using local 7B model. Use when: 1) Setting a new todo item for the session 2) Marking a todo as complete 3) Listing current todos 4) Managing session-level tasks without cloud API calls All operations use local-vllm-instruct/qwen2.5-7B model for privacy and speed. --- |

## 为什么做这件事

OpenClaw 的技能都是 Markdown + 可选脚本，结构简单但数量会越来越多。每周备份一次可以：

1. **防丢失**：本地环境重装或误删时能快速恢复
2. **可追溯**：通过 Git 历史查看技能演进
3. **可分享**：整理成博客后，方便给他人参考

## 自动备份脚本

备份脚本已放在仓库 `scripts/backup-openclaw-skills.py`，运行后会：

1. 扫描 `~/.openclaw/workspace/skills` 和 `~/.openclaw/extensions`
2. 将 SKILL.md 及相关脚本复制到 `public/openclaw-skills-backup/`
3. 在 `src/content/blog/` 生成本周汇总文章

```bash
python3 scripts/backup-openclaw-skills.py
```

## 相关链接

- 博客源码：[github.com/scchy/scc-blog](https://github.com/scchy/scc-blog)
- 站点地址：[https://scchy.github.io/scc-blog](https://scchy.github.io/scc-blog)
