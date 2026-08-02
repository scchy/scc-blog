---
name: wiki-manager
description: |
  LLM Wiki management subagent for OpenClaw.
  Use when:
  1) Ingesting documents into LLM Wiki (ingest)
  2) Querying knowledge from LLM Wiki (query)
  3) Health checking the wiki (lint)
  
  Manages a structured knowledge base using the Karpathy LLM Wiki pattern.
---

# Wiki Manager

Subagent for managing LLM Wiki - structured knowledge base that compounds over time.

## Overview

Based on Karpathy's LLM Wiki pattern (https://gist.github.com/karpathy/...):
- **Raw Sources** (immutable): Articles, papers, notes you add
- **The Wiki** (AI-maintained): Structured markdown with entities, concepts, cross-references
- **Operations**: Ingest → Query → Lint (health check)

## Directory Structure

```
LLM_wiki/
├── raw/              # Your sources (you add)
├── wiki/             # AI-maintained knowledge
│   ├── sources/      # Source summaries
│   ├── entities/     # People, companies, products
│   ├── concepts/     # Technologies, theories
│   ├── index.md      # Content catalog
│   └── log.md        # Operation log
└── WIKI_SCHEMA.md    # Configuration
```

## Commands

### Ingest (摄取)

Add a document to the wiki.

```javascript
wiki_ingest({
  wiki_root: "/path/to/LLM_wiki",
  source_file: "article.md",  // relative to raw/
  llm_model: "kimi"  // optional: kimi/local
})
```

**What it does:**
1. Reads raw/article.md
2. Analyzes content (entities, concepts, key points)
3. Creates wiki/sources/article.md
4. Creates/updates wiki/entities/*.md
5. Creates/updates wiki/concepts/*.md
6. Updates wiki/index.md
7. Appends to wiki/log.md

**Example:**
```javascript
wiki_ingest({
  wiki_root: "/home/scc/sccWork/devData/sccDisk/algomate/LLM_wiki",
  source_file: "transformer_paper.pdf"
})
```

---

### Query (查询)

Query the wiki for knowledge.

```javascript
wiki_query({
  wiki_root: "/path/to/LLM_wiki",
  question: "What is Transformer architecture?",
  llm_model: "kimi"
})
```

**What it does:**
1. Reads wiki/index.md to find relevant pages
2. Reads specific pages (sources/entities/concepts)
3. Synthesizes answer with citations
4. Returns structured response

**Example:**
```javascript
wiki_query({
  wiki_root: "/home/scc/sccWork/devData/sccDisk/algomate/LLM_wiki",
  question: "对比 Transformer 和 RNN 的优缺点"
})
```

---

### Lint (健康检查)

Health check the wiki.

```javascript
wiki_lint({
  wiki_root: "/path/to/LLM_wiki"
})
```

**What it checks:**
- Orphan pages (no inbound links)
- Missing cross-references
- Contradictions between pages
- Index completeness

**Output:**
```javascript
{
  issues: [
    { type: "orphan", page: "gpt-4.md" },
    { type: "missing_ref", from: "transformer.md", to: "attention.md" }
  ],
  stats: {
    total_pages: 15,
    sources: 5,
    entities: 8,
    concepts: 2
  }
}
```

---

## Implementation

Each operation spawns a subagent:

```javascript
// Ingest
sessions_spawn({
  task: `Ingest ${source_file} into wiki at ${wiki_root}`,
  agentId: "wiki-manager",
  mode: "run",
  model: llm_model || "kimi"
})

// Query
sessions_spawn({
  task: `Query wiki at ${wiki_root}: ${question}`,
  agentId: "wiki-manager",
  mode: "run",
  model: llm_model || "kimi"
})

// Lint
sessions_spawn({
  task: `Lint wiki at ${wiki_root}`,
  agentId: "wiki-manager",
  mode: "run"
})
```

## Workflow

### Daily Knowledge Capture
```javascript
// Morning - ingest overnight reading
wiki_ingest({
  wiki_root: "~/LLM_wiki",
  source_file: "attention_is_all_you_need.pdf"
})

// Afternoon - query for project
wiki_query({
  wiki_root: "~/LLM_wiki",
  question: "How does self-attention work?"
})

// Weekly - health check
wiki_lint({ wiki_root: "~/LLM_wiki" })
```

### Research Project
```javascript
// Week 1: Build knowledge base
wiki_ingest({ source_file: "paper1.pdf" })
wiki_ingest({ source_file: "paper2.pdf" })
wiki_ingest({ source_file: "survey.md" })

// Week 2: Query for synthesis
wiki_query({ question: "What are the current SOTA methods?" })
wiki_query({ question: "Compare approach A vs B" })

// Final: Generate report from wiki
```

## Why This Works

| Problem | Solution |
|---------|----------|
| Knowledge scattered | Centralized in wiki/ |
| Re-derive every time | Compiled once, kept current |
| Manual maintenance | AI does cross-referencing |
| Chat history lost | Persistent markdown files |

## Files

- `SKILL.md` - This documentation
- `scripts/wiki_manager.py` - Core wiki operations
- `scripts/wiki-spawn.py` - Subagent wrapper

## Integration with AlgoMate

The same WikiManager can be used:
1. **Standalone**: Direct subagent calls (this skill)
2. **In AlgoMate**: As `WikiManagerAgent` in the agent framework

Both share the same directory structure and operations.