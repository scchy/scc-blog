---
name: quick-model
description: |
  Quick model switching commands for OpenClaw. Use when:
  1) User types /local followed by task to run with local 7B model
  2) User types /kimi followed by task to run with cloud Kimi model
  3) Need quick sub-agent spawning without writing full sessions_spawn code
  
  Provides shortcuts: /local, /kimi for instant model-specific task execution.
---

# Quick Model Commands

Quick shortcuts to run tasks with specific models via sub-agents.

## Commands

### /local <task>

Run task with **local 7B model** (fast, free, private).

**Usage:**
```
/local 总结这段文字
/local 翻译成英文：你好世界
/local 给这段文字起3个标题
/local 格式化这段JSON
```

**What it does:**
```javascript
sessions_spawn({
  task: "<your task>",
  model: "local-vllm-instruct/qwen2.5-7B",
  mode: "run"
})
```

**Best for:**
- Text summarization
- Translation
- Formatting/JSON cleanup
- Simple classification
- Privacy-sensitive data
- Quick questions

---

### /kimi task

Run task with **cloud Kimi model** (powerful, reasoning, coding).

**Usage:**
```
/kimi 写个Python快速排序
/kimi 设计一个微服务架构
/kimi 分析这段代码的bug
/kimi 帮我写一封正式邮件
```

**What it does:**
```javascript
sessions_spawn({
  task: "your task",
  model: "kimi-coding/k2p5",
  mode: "run"
})
```

**Best for:**
- Code writing/debugging
- Architecture design
- Complex reasoning
- Creative writing
- Long-context tasks

---

## Command Detection

Trigger on message patterns:
- `^/local\s+(.+)` → Local 7B model
- `^/kimi\s+(.+)` → Cloud Kimi model

**Note:** These run in isolated sub-agents, so they don't affect current session context.

---

## Examples

### Example 1: Quick Summary
```
User: /local 总结这段新闻：【粘贴新闻内容】
→ Spawns sub-agent with local 7B
→ Returns summary
```

### Example 2: Code Help
```
User: /kimi 帮我优化这段Python代码
→ Spawns sub-agent with Kimi
→ Returns optimized code
```

### Example 3: Privacy Processing
```
User: /local 从这份邮件提取待办事项
→ Processes locally (no cloud)
→ Returns action items
```

---

## Comparison

| Command | Model | Speed | Cost | Best For |
|---------|-------|-------|------|----------|
| /local | 本地7B | Fast | Free | Simple tasks, privacy |
| /kimi | 云端Kimi | Normal | API | Complex tasks, code |

---

## Scripts

- `scripts/handler.py` - Command parsing and execution logic
