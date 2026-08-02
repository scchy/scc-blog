---
name: smart-router
description: |
  Intelligent task routing to automatically select the best model for each task.
  Use when you want to run a task without manually choosing between local 7B and cloud Kimi models.
  
  Analyzes task complexity, content type, and requirements to route to:
  - local-vllm-instruct/qwen2.5-7B for simple, fast, private tasks
  - kimi-coding/k2p5 for complex, coding, reasoning tasks
  
  Simply describe your task and let the router decide the optimal model.
---

# Smart Router

Automatically routes tasks to the most appropriate model based on task analysis.

## Usage

```javascript
smart_route({
  task: "总结这段文字"
})
```

The router will:
1. Analyze the task type and complexity
2. Select the optimal model (local 7B or cloud Kimi)
3. Execute via sub-agent
4. Return the result

## Routing Logic

### Routes to Local 7B (Fast, Free, Private)

- Text summarization (总结)
- Translation (翻译)
- Formatting/conversion (格式化)
- Simple classification (分类)
- Keyword extraction (关键词提取)
- Title generation (起标题)
- Sentiment analysis (情绪分析)
- Data cleaning (数据清洗)
- Privacy-sensitive content (隐私数据)

Keywords: 总结, 翻译, 格式化, 分类, 关键词, 标题, 情绪, 提取, 整理

### Routes to Cloud Kimi (Powerful, Reasoning)

- Code writing/debugging (代码, 编程)
- Architecture design (架构, 设计)
- Complex reasoning (分析, 优化)
- Creative writing (创作, 写作)
- Math/logic problems (数学, 算法)
- Long-context analysis (长文档)
- Multi-step tasks (多步骤)

Keywords: 代码, 编程, bug, debug, 架构, 设计, 算法, 优化, 分析, 写作, 创作

## Examples

### Example 1: Simple Task
```javascript
smart_route({ task: "总结这段新闻" })
// → Uses local 7B (fast, free)
```

### Example 2: Complex Task
```javascript
smart_route({ task: "写个Python快速排序并解释原理" })
// → Uses cloud Kimi (coding + reasoning)
```

### Example 3: Ambiguous Task
```javascript
smart_route({ task: "分析这段代码的性能问题" })
// → Uses cloud Kimi (contains '代码' + '分析')
```

## Override (Force Specific Model)

If you want to force a specific model:

```javascript
// Force local 7B
smart_route({ 
  task: "分析代码",
  model: "local-vllm-instruct/qwen2.5-7B"
})

// Force cloud Kimi
smart_route({ 
  task: "总结文字",
  model: "kimi-coding/k2p5"
})
```

## Scripts

- `scripts/router.py` - Task analysis and routing logic
- `scripts/analyze.py` - Task complexity analyzer

## How It Works

1. **Keyword Matching**: Checks for coding/complexity keywords
2. **Length Analysis**: Longer tasks tend to need more power
3. **Context Check**: Code blocks, technical terms indicate complexity
4. **Fallback**: When uncertain, uses local 7B for speed

## Configuration

Default routing rules can be customized by editing the keyword lists in `scripts/router.py`.

## Benefits

| Benefit | Description |
|---------|-------------|
| Save Money | Simple tasks use free local model |
| Save Time | No need to decide which model to use |
| Optimal Results | Complex tasks get the power they need |
| Privacy | Sensitive data stays local automatically |
