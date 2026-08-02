#!/usr/bin/env python3
"""
Batch Optimizer - Optimize batch processing to save tokens
批量任务优化器 - 批量处理优化以节省 Token
"""

import json
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any

def estimate_tokens(text):
    """Rough estimate: ~4 chars per token"""
    if isinstance(text, (dict, list)):
        text = json.dumps(text, ensure_ascii=False)
    return len(text) // 4

def chunk_items(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split items into chunks"""
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]

def generate_subagent_plan(tasks: List[Dict], strategy: str, chunk_size: int) -> Dict:
    """Generate execution plan for batch processing"""
    
    if strategy == 'individual':
        # One sub-agent per task
        plans = []
        for i, task in enumerate(tasks):
            plans.append({
                'index': i,
                'task': task.get('description', f'Task {i+1}'),
                'model': task.get('model', 'local-vllm-instruct/qwen2.5-7B'),
                'mode': 'run',
                'estimated_tokens': estimate_tokens(task) * 2  # Input + output estimate
            })
        return {
            'strategy': 'individual',
            'total_tasks': len(tasks),
            'subagents': len(plans),
            'plans': plans,
            'total_estimated_tokens': sum(p['estimated_tokens'] for p in plans)
        }
    
    elif strategy == 'chunked':
        # Group tasks into chunks
        chunks = chunk_items(tasks, chunk_size)
        plans = []
        for i, chunk in enumerate(chunks):
            plans.append({
                'index': i,
                'tasks_in_chunk': len(chunk),
                'task': f'Process batch of {len(chunk)} items',
                'model': 'local-vllm-instruct/qwen2.5-7B',
                'mode': 'run',
                'attachments': [{
                    'name': f'batch_{i+1}.json',
                    'content': json.dumps(chunk, ensure_ascii=False)
                }],
                'estimated_tokens': estimate_tokens(chunk) * 2
            })
        return {
            'strategy': 'chunked',
            'total_tasks': len(tasks),
            'chunk_size': chunk_size,
            'chunks': len(chunks),
            'plans': plans,
            'total_estimated_tokens': sum(p['estimated_tokens'] for p in plans)
        }
    
    elif strategy == 'stream':
        # Stream processing - no history retention
        return {
            'strategy': 'stream',
            'total_tasks': len(tasks),
            'recommendation': 'Use streaming mode with no history retention',
            'model': 'local-vllm-instruct/qwen2.5-7B',
            'estimated_tokens': estimate_tokens(tasks) * 1.5
        }
    
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

def generate_code_example(plan: Dict) -> str:
    """Generate executable code example"""
    
    if plan['strategy'] == 'individual':
        code = '''
# Process tasks individually with sub-agents
results = []
for i, task in enumerate(tasks):
    result = sessions_spawn({
        task: task['description'],
        model: task.get('model', 'local-vllm-instruct/qwen2.5-7B'),
        mode: 'run'
    })
    results.append(result)
    # Only summary comes back to main context
'''
    
    elif plan['strategy'] == 'chunked':
        code = '''
# Process tasks in chunks
chunks = [tasks[i:i + ''' + str(plan.get('chunk_size', 10)) + '''] for i in range(0, len(tasks), ''' + str(plan.get('chunk_size', 10)) + ''')]
summaries = []

for i, chunk in enumerate(chunks):
    result = sessions_spawn({
        task: f"Process batch {i+1} of ''' + str(plan.get('chunks', 'N')) + '''",
        model: "local-vllm-instruct/qwen2.5-7B",
        mode: "run",
        attachments: [{
            name: f"batch_{i+1}.json",
            content: JSON.stringify(chunk)
        }]
    })
    summaries.append(result.summary)  # Only summary to main context
'''
    
    else:
        code = '''
# Stream processing - minimal context retention
for task in tasks:
    sessions_spawn({
        task: task['description'],
        model: "local-vllm-instruct/qwen2.5-7B",
        mode: "run",
        cleanup: "delete"  # Delete after completion
    })
'''
    
    return code.strip()

def main():
    parser = argparse.ArgumentParser(description='Batch Task Optimizer')
    parser.add_argument('--tasks', '-n', type=int, help='Number of tasks')
    parser.add_argument('--input', '-i', help='Input JSON file with tasks array')
    parser.add_argument('--strategy', '-s', choices=['individual', 'chunked', 'stream'], 
                       default='chunked', help='Processing strategy')
    parser.add_argument('--chunk-size', '-c', type=int, default=10, help='Chunk size for chunked strategy')
    parser.add_argument('--estimate-only', '-e', action='store_true', help='Only show estimates')
    parser.add_argument('--output', '-o', help='Output execution plan to file')
    
    args = parser.parse_args()
    
    # Load tasks
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
    elif args.tasks:
        # Generate sample tasks for estimation
        tasks = [{'description': f'Task {i+1}', 'data': f'Sample data {i}'} for i in range(args.tasks)]
    else:
        print("Error: Provide --tasks N or --input file.json")
        sys.exit(1)
    
    # Calculate baseline (processing in main session)
    baseline_tokens = estimate_tokens(tasks) * 2  # Input + accumulated output
    
    # Generate plan
    plan = generate_subagent_plan(tasks, args.strategy, args.chunk_size)
    
    # Calculate savings
    savings = baseline_tokens - plan['total_estimated_tokens']
    savings_pct = (savings / baseline_tokens * 100) if baseline_tokens > 0 else 0
    
    # Output
    if args.estimate_only:
        print(f"📊 Token Estimation")
        print(f"=" * 40)
        print(f"Strategy: {args.strategy}")
        print(f"Tasks: {len(tasks)}")
        if args.strategy == 'chunked':
            print(f"Chunk size: {args.chunk_size}")
            print(f"Chunks: {plan['chunks']}")
        print(f"-" * 40)
        print(f"Baseline (main session): ~{baseline_tokens:,} tokens")
        print(f"Optimized (sub-agents):  ~{plan['total_estimated_tokens']:,} tokens")
        print(f"Savings:                 ~{savings:,} tokens ({savings_pct:.1f}%)")
        return
    
    # Full output
    output = {
        'baseline_tokens': baseline_tokens,
        'optimized_tokens': plan['total_estimated_tokens'],
        'savings': savings,
        'savings_percent': savings_pct,
        'plan': plan,
        'code_example': generate_code_example(plan)
    }
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"Plan saved to {args.output}")
    else:
        print(json.dumps(output, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
