---
name: todo-manager
description: |
  Simple todo management for OpenClaw sessions using local 7B model.
  Use when:
  1) Setting a new todo item for the session
  2) Marking a todo as complete
  3) Listing current todos
  4) Managing session-level tasks without cloud API calls
  
  All operations use local-vllm-instruct/qwen2.5-7B model for privacy and speed.
---

# Todo Manager

Lightweight todo management using local 7B model. Fast, private, no API costs.

## Commands

### Set Todo (添加待办)

```javascript
set_todo({
  task: "完成周报",
  priority: "high",  // optional: high/medium/low
  due: "今天下班前"  // optional
})
```

**What it does:**
- Adds todo to session memory
- Uses local 7B model for categorization/tagging
- No cloud API call

**Examples:**
```
set_todo({ task: "完成周报" })
set_todo({ task: "回复邮件", priority: "high" })
set_todo({ task: "整理文档", due: "明天下午" })
```

---

### Complete Todo (完成待办)

```javascript
complete_todo({
  task: "完成周报"  // or use index: 1
})
```

**What it does:**
- Marks todo as complete
- Moves to completed list
- Uses local 7B for summary generation

**Examples:**
```
complete_todo({ task: "完成周报" })
complete_todo({ index: 2 })  // complete 2nd item
```

---

### List Todos (列出待办)

```javascript
list_todos()
```

**Output:**
```
📋 待办事项 (3):
  1. [ ] 完成周报 (高优先级)
  2. [ ] 回复邮件 (今天)
  3. [ ] 整理文档

✅ 已完成 (5):
  1. 安装OpenClaw
  2. 配置Token优化
```

---

## Storage

Todos are stored in session memory file:
- Active: `memory/session-todos.json`
- Completed: `memory/session-todos-completed.json`

**Privacy:** All processing uses local 7B model - no data leaves your machine.

---

## Scripts

- `scripts/todo.py` - Core todo management logic
- `scripts/todo-spawn.py` - Sub-agent wrapper for local execution

## Implementation

All operations spawn sub-agents with local 7B model:

```javascript
// Set todo
sessions_spawn({
  task: "Parse and store todo: 完成周报",
  model: "local-vllm-instruct/qwen2.5-7B",
  mode: "run"
})

// Complete todo
sessions_spawn({
  task: "Mark todo complete: 完成周报",
  model: "local-vllm-instruct/qwen2.5-7B",
  mode: "run"
})
```

## Why Local Model?

| Aspect | Local 7B | Cloud API |
|--------|----------|-----------|
| Speed | Fast | Network latency |
| Cost | Free | API charges |
| Privacy | 100% local | Data to cloud |
| Complexity | Simple tasks only | Complex reasoning |

Todo management is simple categorization - perfect for local 7B.

---

## Examples

### Daily Standup Style
```javascript
// Morning - set todos
set_todo({ task: "Review PRs", priority: "high" })
set_todo({ task: "Update documentation" })
set_todo({ task: "Team meeting", due: "14:00" })

// Check list
list_todos()

// Afternoon - complete
complete_todo({ task: "Review PRs" })
```

### Project Milestones
```javascript
set_todo({ task: "Phase 1: Setup environment", priority: "high" })
set_todo({ task: "Phase 2: Core features" })
set_todo({ task: "Phase 3: Testing" })
set_todo({ task: "Phase 4: Deployment" })
```
