---
name: token-saver
description: |
  Token consumption optimization for OpenClaw sessions. Use when:
  1) Context is getting too long and consuming excessive tokens
  2) Need to optimize memory retrieval to reduce token usage
  3) Want to search memory efficiently without loading full files
  4) Need guidance on context management and pruning strategies
  5) Need automatic alerts when token usage is high
  6) Want to optimize tool results and batch processing
  
  Provides: memory_search + memory_get workflow, tool result truncation,
  session health monitoring, batch task optimization, and automatic alerts.
---

# Token Saver

Optimize token consumption in OpenClaw sessions through intelligent context management and monitoring.

## When to Use This Skill

- **Long sessions**: Context growing beyond 50K tokens
- **Memory lookups**: Need to search MEMORY.md without loading entire files
- **Tool results**: Large JSON responses consuming too many tokens
- **Token audit**: Want to identify what's consuming tokens in your context
- **Batch tasks**: Processing many items efficiently
- **Monitoring**: Automatic alerts for high token usage
- **Optimization**: Setting up efficient context management from the start

## Quick Start

```bash
# Audit current token usage
python3 scripts/token_audit.py

# Check session health
python3 scripts/session_health.py

# Truncate large tool results
python3 scripts/smart_truncate.py <file.json> --max-tokens 1000

# Optimize batch processing
python3 scripts/batch_optimizer.py --tasks 100 --strategy chunked
```

---

## 1. Memory Search + Get (Searchable Memory Access)

The most token-efficient way to access memory:

### Step 1: Search (Semantic Query)

```javascript
memory_search({
  query: "what was decided about the database choice",
  maxResults: 5
})
```

Returns top matches with path and line numbers. **Token cost: minimal** (embedding search).

### Step 2: Get (Targeted Read)

```javascript
memory_get({
  path: "memory/2026-03-20.md",
  from: 45,
  lines: 20
})
```

Reads only the relevant snippet. **Token cost: ~200-500 tokens** vs 5000+ for full file.

---

## 2. Smart Tool Result Truncation (工具结果智能截断)

### Problem
Tool results like `gateway config.get` or `feishu_bitable_list_records` return large JSONs consuming thousands of tokens.

### Solution: Truncate Before Display

```javascript
// ❌ Bad: Returns full config (5000+ tokens)
gateway({ action: "config.get" })

// ✅ Good: Use helper to truncate
truncate_tool_result(
  gateway({ action: "config.get" }),
  { maxTokens: 1000, preserve: ['agents.defaults.model'] }
)
```

### Manual Truncation Script

```bash
# Truncate JSON to max 1000 tokens, keep only key fields
python3 scripts/smart_truncate.py result.json \
  --max-tokens 1000 \
  --preserve agents.defaults,models.providers \
  --summarize-arrays 5
```

### Best Practices

| Tool | Typical Size | Recommended Action |
|------|-------------|-------------------|
| `gateway config.get` | 3000-5000 tokens | Truncate to 1000, preserve `agents.defaults` |
| `feishu_bitable_list_records` | 2000+ tokens | Paginate (page_size: 10), request specific fields |
| `sessions_history` | 1000+ per 10 messages | Limit to 5 messages, use `offset` |
| Large file `read` | Variable | Use `offset` + `limit`, or `head` command |

---

## 3. Session Health Monitor (会话健康监控)

### Automatic Alerts

Run `scripts/session_health.py` to check:

```bash
python3 scripts/session_health.py
```

Output:
```
🔍 Session Health Report
========================
📊 Current Context: ~12,500 tokens
🔄 Message Count: 15 rounds
⏱️  Session Age: 45 minutes
⚠️  Status: HEALTHY

Recommendations:
- Consider /reset after 25 rounds (current: 15)
- Tool results averaging 800 tokens (good)
- No large bootstrap files detected
```

### Alert Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Context size | 30K tokens | 50K tokens | Alert /reset |
| Message rounds | 20 rounds | 30 rounds | Alert new session |
| Single tool result | 2K tokens | 5K tokens | Alert truncation |
| Bootstrap files | 30K tokens | 50K tokens | Alert file cleanup |

### Integration with Heartbeat

Add to `HEARTBEAT.md`:

```markdown
- Run token health check: `python3 scripts/session_health.py --quiet`
- If warning, suggest session reset to user
```

---

## 4. Batch Task Optimization (批量任务优化)

### Problem
Processing 100+ items in a loop causes context to grow linearly with each iteration.

### Solution: Chunked Sub-agents

```javascript
// ❌ Bad: Loop in main session (context grows)
for (const item of items) {
  await process(item)  // Each result adds to context
}

// ✅ Good: Chunk into sub-agents
python3 scripts/batch_optimizer.py --input tasks.json \
  --chunk-size 10 \
  --model local-vllm-instruct/qwen2.5-7B \
  --summarize-results
```

### Strategies

| Strategy | Use Case | Token Savings |
|----------|----------|---------------|
| `subagent` | Independent tasks | 100% (isolated sessions) |
| `chunked` | Related items | 90% (summarized results) |
| `stream` | Real-time output | 80% (no history retention) |

### Example: Process 100 Records

```javascript
// Split into 10 batches of 10
const batches = chunk(records, 10);

for (const batch of batches) {
  const result = await sessions_spawn({
    task: `Process ${batch.length} records`,
    model: "local-vllm-instruct/qwen2.5-7B",
    mode: "run",
    attachments: [{ name: "batch.json", content: JSON.stringify(batch) }]
  });
  
  // Only summary comes back to main context
  summaries.push(result.summary);
}
```

---

## 5. Token Optimization Strategies

### 1. Prefer Search + Get Over Full Reads

❌ Inefficient:
```javascript
read({ file_path: "MEMORY.md" })  // Loads entire file
```

✅ Efficient:
```javascript
memory_search({ query: "database decision" })  // Find relevant section
memory_get({ path: "MEMORY.md", from: 120, lines: 15 })  // Read just that part
```

### 2. Use Sub-agents for Heavy Tasks

Offload token-heavy work to isolated sessions:

```javascript
sessions_spawn({
  task: "Analyze this 10MB log file",
  model: "local-vllm-instruct/qwen2.5-7B",  // Use local model
  mode: "run"
})
```

### 3. Periodic Session Reset

For very long conversations, use `/reset` or start fresh sessions.

### 4. Compact Bootstrap Files

Keep workspace bootstrap files (AGENTS.md, SOUL.md, etc.) concise:
- Target: < 1000 lines total
- Remove redundant examples
- Move detailed docs to references/

---

## Quick Reference

| Situation | Action | Token Savings |
|-----------|--------|---------------|
| Looking for past decision | `memory_search` + `memory_get` | 80-90% |
| Large tool result | `smart_truncate.py` | 70-90% |
| Processing many items | `batch_optimizer.py` | 90-100% |
| Long conversation | `/reset` or new session | 100% history |
| High token usage alert | Run `session_health.py` | Preventive |

---

## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `token_audit.py` | Audit workspace token usage | `python3 token_audit.py` |
| `session_health.py` | Monitor session health | `python3 session_health.py [--quiet]` |
| `smart_truncate.py` | Truncate large JSON results | `python3 smart_truncate.py <file> --max-tokens 1000` |
| `batch_optimizer.py` | Optimize batch processing | `python3 batch_optimizer.py --tasks 100` |

---

## Configuration

Recommended OpenClaw config for token efficiency:

```json
{
  "agents": {
    "defaults": {
      "bootstrapMaxChars": 8000,
      "bootstrapTotalMaxChars": 50000,
      "compaction": {
        "mode": "safeguard",
        "model": "local-vllm-instruct/qwen2.5-7B"
      }
    }
  },
  "session": {
    "parentForkMaxTokens": 80000
  }
}
```
