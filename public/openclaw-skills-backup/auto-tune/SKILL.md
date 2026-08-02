---
name: auto-tune
description: |
  Auto Tune & AlgoMate 项目管理专家。管理 auto_tune 和 algomate 两个项目的迭代开发。
  
  触发方式：
  - `/at` - 查看项目状态和待办事项
  - `/at status` - 查看两个项目的当前状态
  - `/at todo` - 列出待办事项
  - `/at plan <项目>` - 制定迭代计划
  - `/at code <项目>` - 代码审查和建议
  
  管理范围：
  - auto_tune: /home/scc/.openclaw/workspace/auto_tune/
  - algomate: /home/scc/sccWork/devData/sccDisk/algomate/
---

# Auto Tune / AlgoMate 项目管理

专门用于管理 auto_tune 和 algomate 两个项目的迭代开发。

## 项目路径

- **auto_tune**: `/home/scc/.openclaw/workspace/auto_tune/`
  - 自动调参 Agent，基于文件交互架构
  - 主要文件：state_machine.py, autoTune/, agents/, docs/
  
- **algomate**: `/home/scc/sccWork/devData/sccDisk/algomate/`
  - AlgoMate 框架，支持 Markdown Skill
  - 主要文件：src/algomate/, skills/, agents/, docs/

## 命令

### 查看状态
```
/at
/at status
```
查看两个项目的当前状态：
- Git 状态（分支、未提交更改）
- 最近修改的文件
- 待办事项（从 TODO.md 或代码中的 TODO 注释提取）

### 列出待办
```
/at todo
/at todo auto_tune
/at todo algomate
```
列出项目中的待办事项：
- 从 TODO.md 读取
- 从代码中的 TODO/FIXME 注释提取
- 从 GitHub issues 提取（如果有）

### 制定计划
```
/at plan auto_tune
/at plan algomate
```
为指定项目制定迭代计划：
1. 分析当前代码状态和架构
2. 识别下一步需要完成的功能
3. 生成迭代计划文档

### 代码审查
```
/at code auto_tune
/at code algomate
```
对项目进行代码审查：
- 检查代码质量
- 识别潜在问题
- 提供改进建议

### 执行迭代
```
/at run auto_tune <任务>
/at run algomate <任务>
```
执行具体的迭代任务，使用 subagent 完成。

## 工作流

### 日常检查
```
用户: /at
我: 📊 项目状态概览

auto_tune:
- 分支: main
- 未提交: 3 个文件
- 最近修改: state_machine.py
- TODO: 2 项待办

algomate:
- 分支: main
- 未提交: 1 个文件
- 最近修改: skills/markdown/executor.py
- TODO: 1 项待办
```

### 迭代规划
```
用户: /at plan auto_tune
我: 📝 为 auto_tune 制定迭代计划...

[分析代码结构]
[识别下一步功能]
[生成计划文档]

迭代计划已保存到 auto_tune/docs/iteration_plan_001.md
```

### 执行开发
```
用户: /at run auto_tune 实现 checkpoint 恢复功能
我: 🚀 启动 subagent 执行任务...

[subagent 执行具体开发任务]
[生成代码、测试、文档]
[提交更改]
```

## 与其他命令的区别

| 命令 | 用途 |
|------|------|
| `/at` | 管理 auto_tune & algomate 项目迭代 |
| `/pa` | 个人助理，处理日常事务 |
| `/wiki` | 查询 LLM Wiki 知识库 |
| `/token-monitor` | Token 使用监控 |

## 实现方式

- **Markdown Skill** - 本文件定义工作流程
- **Subagent 执行** - 具体任务通过 `sessions_spawn` 分配给子代理
- **文件管理** - 计划、文档保存在项目目录中

## Agent 执行指南

当用户调用 `/at` 时：

1. **解析命令**：识别子命令（status/todo/plan/code/run）
2. **确定项目**：auto_tune 或 algomate
3. **收集信息**：使用 `read`、`exec` 工具获取项目状态
4. **制定计划**：如有需要，生成迭代计划
5. **分配任务**：使用 `sessions_spawn` 启动 subagent 执行

## 文件位置

- Skill: `~/.openclaw/workspace/skills/auto-tune/SKILL.md`
- auto_tune: `~/sccWork/devData/sccDisk/auto_tune/` (Git 仓库)
- algomate: `~/sccWork/devData/sccDisk/algomate/` (Git 仓库)
