#!/usr/bin/env python3
"""
Smart Router - Automatic task routing to optimal model
智能路由 - 自动选择最适合的模型
"""

import sys
import json
import re

# Keywords that indicate complex tasks (route to Kimi)
KIMI_KEYWORDS = [
    # Code related
    '代码', '编程', 'program', 'code', 'bug', 'debug', '修复',
    'python', 'javascript', 'java', 'go', 'rust', 'c++', 'sql',
    '函数', '类', '算法', '数据结构', 'api', '接口',
    
    # Complex analysis
    '架构', '设计', 'design', 'architecture',
    '优化', '性能', '效率', 'complexity',
    '分析', 'analyze', '分析', '诊断', '排查',
    
    # Creative/Reasoning
    '写作', '创作', 'write', 'create',
    '解释', '原理', '原理', '机制',
    '方案', '策略', '规划', 'plan',
    
    # Math/Logic
    '数学', '计算', '算法', 'formula',
    '逻辑', '推理', '证明', '推导',
    
    # Multi-step
    '步骤', '流程', '实现', 'implement',
    '构建', '搭建', '部署', 'develop'
]

# Keywords that indicate simple tasks (route to Local 7B)
LOCAL_KEYWORDS = [
    '总结', 'summarize', 'summary', '概括',
    '翻译', 'translate', 'translation',
    '格式化', 'format', '整理', '清理',
    '分类', '归类', '标签', 'tag',
    '关键词', 'keyword', '提取', 'extract',
    '标题', 'headline', '命名', 'name',
    '情绪', '情感', 'sentiment', 'mood',
    '排序', 'sort', '列表', 'list',
]

# Privacy-related keywords (force local)
PRIVACY_KEYWORDS = [
    '密码', 'password', '密钥', 'secret', 'key',
    '私密', 'private', '隐私', 'privacy',
    '邮件', 'email', '日志', 'log',
    '内部', 'internal', '机密', 'confidential'
]

def analyze_task(task):
    """Analyze task and determine optimal model"""
    task_lower = task.lower()
    
    # Check for privacy keywords first (force local)
    for keyword in PRIVACY_KEYWORDS:
        if keyword in task_lower or keyword in task:
            return {
                'model': 'local-vllm-instruct/qwen2.5-7B',
                'reason': 'privacy-sensitive content',
                'confidence': 'high'
            }
    
    # Count keyword matches
    kimi_score = 0
    local_score = 0
    
    for keyword in KIMI_KEYWORDS:
        if keyword in task_lower or keyword in task:
            kimi_score += 1
    
    for keyword in LOCAL_KEYWORDS:
        if keyword in task_lower or keyword in task:
            local_score += 1
    
    # Check for code blocks
    has_code_block = '```' in task or '`' in task
    if has_code_block:
        kimi_score += 2
    
    # Check task length (longer tasks tend to be more complex)
    task_length = len(task)
    if task_length > 200:
        kimi_score += 1
    elif task_length < 50:
        local_score += 1
    
    # Decision
    if kimi_score > local_score:
        return {
            'model': 'kimi-coding/k2p5',
            'reason': f'complex task detected (coding/analysis keywords: {kimi_score})',
            'confidence': 'high' if kimi_score > 2 else 'medium'
        }
    elif local_score > kimi_score:
        return {
            'model': 'local-vllm-instruct/qwen2.5-7B',
            'reason': f'simple task detected (formatting/summary keywords: {local_score})',
            'confidence': 'high' if local_score > 2 else 'medium'
        }
    else:
        # Default to local for speed when uncertain
        return {
            'model': 'local-vllm-instruct/qwen2.5-7B',
            'reason': 'defaulting to fast local model (uncertain complexity)',
            'confidence': 'low'
        }

def generate_spawn_code(task, model):
    """Generate sessions_spawn code"""
    # Escape quotes in task
    escaped_task = task.replace('"', '\\"')
    
    code = f'''sessions_spawn({{
  task: "{escaped_task}",
  model: "{model}",
  mode: "run"
}})'''
    return code

def main():
    if len(sys.argv) < 2:
        print("Usage: router.py '\u003ctask\u003e' [model_override]")
        print("")
        print("Examples:")
        print("  router.py '\u603b\u7ed3\u8fd9\u6bb5\u6587\u5b57'")
        print("  router.py '\u5199\u4e2aPython\u6392\u5e8f\u7b97\u6cd5'")
        print("  router.py '\u603b\u7ed3' 'kimi-coding/k2p5'  # force model")
        sys.exit(1)
    
    task = sys.argv[1]
    
    # Check for model override
    if len(sys.argv) >= 3:
        result = {
            'model': sys.argv[2],
            'reason': 'user override',
            'confidence': 'forced'
        }
    else:
        result = analyze_task(task)
    
    # Generate code
    spawn_code = generate_spawn_code(task, result['model'])
    
    output = {
        'task': task,
        'routed_to': result['model'],
        'reason': result['reason'],
        'confidence': result['confidence'],
        'is_local': result['model'] == 'local-vllm-instruct/qwen2.5-7B',
        'spawn_code': spawn_code
    }
    
    print(json.dumps(output, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
