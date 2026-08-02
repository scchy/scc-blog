---
name: duckduckgo-search
description: |
  Free web search using DuckDuckGo with intelligent tiered processing.
  Use when you need to search the web without API costs.
  
  Features:
  - Basic search with result limiting
  - Two-tier processing: Local 7B filters, Kimi analyzes
  - Automatic token management for long results
  - Completely free, no API key required
---

# DuckDuckGo Search with Tiered Processing

Free web search with intelligent local + cloud processing.

## Quick Start

### Basic Search (Local 7B)

```bash
python3 scripts/search.py "OpenClaw AI" --max 3
```

### Tiered Processing (Local + Cloud)

```bash
# Search → Local filter → Cloud analyze
python3 scripts/tiered_search.py "Python asyncio tutorial" --depth full
```

## Tiered Processing Workflow

### Tier 1: Local 7B - Filter & Extract

Fast, free preprocessing of search results:

```javascript
// Step 1: Search and get raw results
const searchResults = exec({
  command: "python3 scripts/search.py 'Python asyncio' --json --max 5"
});

// Step 2: Local 7B extracts key information
const summary = await sessions_spawn({
  task: `从以下搜索结果中提取3个最相关的链接：
  要求：
  1. 选择最权威/官方的链接
  2. 提取标题和URL
  3. 一句话说明为什么选它
  
  搜索结果：${searchResults}`,
  model: "local-vllm-instruct/qwen2.5-7B",
  mode: "run"
});
```

**Local 7B handles:**
- Filtering irrelevant results
- Extracting key metadata
- Ranking by relevance
- Token count: ~500-1000

### Tier 2: Cloud Kimi - Deep Analysis

Powerful analysis when needed:

```javascript
// Step 3: Cloud Kimi analyzes selected content
const analysis = await sessions_spawn({
  task: `深入分析这个主题：${summary.selected_topic}
  
  请提供：
  1. 核心概念解释
  2. 代码示例（如有）
  3. 最佳实践
  4. 常见陷阱
  
  参考链接：${summary.url}`,
  model: "kimi-coding/k2p5",
  mode: "run"
});
```

**Cloud Kimi handles:**
- Deep content analysis
- Code generation
- Complex reasoning
- Long-context understanding

## Usage Examples

### Example 1: Quick Overview

```bash
# Local 7B only - fast, free
python3 scripts/search.py "OpenClaw" --max 3
```

Output: 3 results with titles and snippets

### Example 2: Research Mode

```bash
# Full tiered processing
python3 scripts/tiered_search.py "asyncio best practices" --mode research
```

Process:
1. Search for "asyncio best practices" (5 results)
2. Local 7B filters to top 3 relevant links
3. Cloud Kimi analyzes the best link in depth

### Example 3: Code Lookup

```bash
# Find code examples
python3 scripts/tiered_search.py "Python decorator example" --mode code
```

Process:
1. Search for decorator examples
2. Local 7B identifies code-focused results
3. Cloud Kimi extracts and explains code patterns

## Scripts

| Script | Purpose | Model |
|--------|---------|-------|
| `search.py` | Basic search | None (just API) |
| `tiered_search.py` | Full pipeline | Local 7B + Kimi |
| `extract.py` | Local extraction | Local 7B |

## Token Management

### Local 7B Context (24K limit)

```
Search results (5 items)     ~2,000 tokens
↓
Local 7B extracts/filter     ~500 tokens input
↓
Summary output               ~300 tokens output
```

### Cloud Kimi Context (262K limit)

```
Filtered summary             ~300 tokens
+ User query                 ~100 tokens
↓
Kimi analysis               ~2,000 tokens output
```

## Comparison

| Mode | Speed | Cost | Use Case |
|------|-------|------|----------|
| Basic (`search.py`) | Fast | Free | Quick lookup |
| Tiered (`tiered_search.py`) | Medium | Low (only tier 2) | Research |
| Direct Kimi | Slow | High | Deep analysis only |

## Why Tiered?

1. **Save Money**: 80% of tasks solved by free local 7B
2. **Save Time**: Local filtering reduces cloud tokens
3. **Better Results**: Cloud focuses on best content, not noise
4. **Privacy**: Initial filtering happens locally

## Installation

```bash
pip install ddgs
```

No API key needed!
