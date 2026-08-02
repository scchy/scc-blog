---
name: auto-research
description: |
  自动调研触发器。当用户输入包含"调研"、"研究一下"、"查查"等关键词时，
  自动执行：搜索 → 7B筛选 → Kimi分析 的完整流程。
  
  触发词：调研, 研究一下, 查查, 搜索, 找一下
---

# Auto Research 自动调研

智能识别用户的调研需求，自动执行完整的调研流程。

## 触发机制

当用户输入包含以下关键词时，自动触发调研流程：
- **调研** - "调研50GB显存可部署什么模型"
- **研究一下** - "研究一下最新的AI框架"
- **查查** - "查查Python异步编程"
- **搜索** - "搜索vLLM部署教程"
- **找一下** - "找一下深度学习相关资料"

## 完整流程

```
用户输入: "调研50GB显存可部署什么int4模型"
    ↓
检测触发词: "调研"
    ↓
提取搜索词: "50GB显存可部署什么int4模型"
    ↓
[1] DuckDuckGo搜索 → 获取Top5结果
    ↓
[2] 本地7B筛选 → 选出Top3最相关链接
    ↓
[3] Kimi深度分析 → 浏览内容并总结
    ↓
输出调研报告
```

## 使用示例

### 示例1: 技术调研
```
用户: 调研50GB显存可部署什么int4模型
系统: 
  1. 搜索"50GB VRAM int4 model deployment"
  2. 7B筛选出最相关的3个技术文章
  3. Kimi分析并给出可部署模型列表和vLLM配置建议
```

### 示例2: 产品调研
```
用户: 研究一下当前最好的开源LLM
系统:
  1. 搜索"best open source LLM 2024"
  2. 7B筛选官方文档和技术评测
  3. Kimi对比分析各模型优缺点
```

## 实现方式

触发检测脚本:
```bash
python3 scripts/trigger.py "用户输入文本"
# 返回: {"trigger": true, "trigger_word": "调研", "query": "..."}
```

完整调研脚本:
```bash
python3 scripts/research.py "搜索关键词"
```

Agent端集成:
```javascript
// 检测触发
const triggerCheck = exec({
  command: "python3 skills/auto-research/scripts/trigger.py '用户输入'"
});

if (triggerCheck.trigger) {
  // 执行完整调研流程
  const research = await sessions_spawn({
    task: `执行调研流程: ${triggerCheck.query}`,
    model: "local-vllm-instruct/qwen2.5-7B",  // Step 1+2
    mode: "run"
  });
  
  const analysis = await sessions_spawn({
    task: `深度分析调研结果: ${research}`,
    model: "kimi-coding/k2p5",  // Step 3
    mode: "run"
  });
}
```

## 优势

| 特性 | 说明 |
|------|------|
| 自动触发 | 无需手动说"搜索"，说"调研"即可 |
| 分层处理 | 7B过滤+Kimi分析，节省token |
| 免费搜索 | DuckDuckGo无API费用 |
| 隐私保护 | 初步筛选在本地完成 |
