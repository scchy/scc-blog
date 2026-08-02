#!/usr/bin/env python3
"""
Tiered Search - Local 7B filter + Cloud Kimi analysis
分层搜索 - 本地7B筛选 + 云端Kimi深度分析
"""

import json
import sys
import argparse
import subprocess
from pathlib import Path

def run_search(query, max_results=5):
    """Run basic DuckDuckGo search"""
    script_path = Path(__file__).parent / "search.py"
    
    result = subprocess.run(
        [sys.executable, str(script_path), query, "--json", "--max", str(max_results)],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        return {"error": result.stderr}
    
    return json.loads(result.stdout)

def generate_local_extract_prompt(query, search_results):
    """Generate prompt for local 7B extraction"""
    results_text = json.dumps(search_results, indent=2, ensure_ascii=False)
    
    prompt = f'''请分析以下搜索结果，为查询"{query}"提取最相关的信息。

搜索结果：
{results_text}

请完成以下任务：
1. 从搜索结果中选择3个最相关的链接
2. 对每个链接提供：
   - 标题
   - URL
   - 一句话说明为什么它相关
3. 推荐最佳的一个链接用于深入分析

请以JSON格式输出：
{{
  "top_3": [
    {{"title": "...", "url": "...", "reason": "..."}},
    {{"title": "...", "url": "...", "reason": "..."}},
    {{"title": "...", "url": "...", "reason": "..."}}
  ],
  "recommended": "推荐理由..."
}}'''
    
    return prompt

def generate_kimi_analysis_prompt(query, selected_result):
    """Generate prompt for cloud Kimi deep analysis"""
    prompt = f'''请深入分析以下主题：{query}

参考资源：
- 标题：{selected_result.get('title', '')}
- 链接：{selected_result.get('url', '')}
- 相关性：{selected_result.get('reason', '')}

请提供：
1. **核心概念**：用简洁的语言解释关键概念
2. **实践指导**：具体的操作步骤或最佳实践
3. **代码示例**（如适用）：提供实用的代码片段
4. **注意事项**：常见陷阱和建议
5. **扩展资源**：推荐进一步学习的方向

请用中文回答，结构清晰。'''
    
    return prompt

def generate_sessions_spawn_code(task, model):
    """Generate sessions_spawn code"""
    escaped_task = task.replace('"', '\\"').replace('\n', '\\n')
    
    code = f'''sessions_spawn({{
  task: "{escaped_task}",
  model: "{model}",
  mode: "run"
}})'''
    
    return code

def main():
    parser = argparse.ArgumentParser(description='Tiered Search: Local filter + Cloud analysis')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--max', '-m', type=int, default=5, help='Max search results (default: 5)')
    parser.add_argument('--mode', choices=['quick', 'research', 'code'], default='research',
                       help='Processing mode')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    print(f"🔍 Tiered Search: {args.query}")
    print(f"{'='*60}")
    
    # Step 1: Search
    print("\n📡 Step 1: Searching DuckDuckGo...")
    search_results = run_search(args.query, args.max)
    
    if "error" in search_results:
        print(f"❌ Search failed: {search_results['error']}")
        sys.exit(1)
    
    print(f"✅ Found {search_results.get('total', 0)} results")
    
    # Step 2: Generate Local 7B prompt
    print("\n🤖 Step 2: Generating Local 7B extraction task...")
    local_prompt = generate_local_extract_prompt(args.query, search_results)
    
    local_code = generate_sessions_spawn_code(local_prompt, "local-vllm-instruct/qwen2.5-7B")
    
    print("✅ Local 7B task ready")
    print(f"   Estimated tokens: ~{len(local_prompt) // 4}")
    
    # Step 3: Example of Tier 2 (Kimi) - would be executed after Local 7B returns
    print("\n☁️  Step 3: Cloud Kimi analysis (after Local 7B result)...")
    
    # Example selected result (placeholder)
    example_selected = {
        "title": "Example Result Title",
        "url": "https://example.com",
        "reason": "Most relevant to the query"
    }
    kimi_prompt = generate_kimi_analysis_prompt(args.query, example_selected)
    kimi_code = generate_sessions_spawn_code(kimi_prompt, "kimi-coding/k2p5")
    
    print("✅ Cloud Kimi task template ready")
    
    # Output
    output = {
        "query": args.query,
        "mode": args.mode,
        "step1_search": search_results,
        "step2_local_7b": {
            "prompt": local_prompt,
            "model": "local-vllm-instruct/qwen2.5-7B",
            "spawn_code": local_code
        },
        "step3_cloud_kimi": {
            "prompt_template": kimi_prompt,
            "model": "kimi-coding/k2p5",
            "spawn_code_template": kimi_code
        },
        "workflow": [
            "1. Run step2_local_7b to filter results",
            "2. Use filtered results to populate step3_cloud_kimi",
            "3. Run step3_cloud_kimi for deep analysis"
        ]
    }
    
    if args.json:
        print("\n" + json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print("\n" + "="*60)
        print("📋 EXECUTION PLAN:")
        print("="*60)
        print("\n【Step 2 - Local 7B Extraction】")
        print(local_code)
        print("\n【Step 3 - Cloud Kimi Analysis】(run after Step 2)")
        print("# Replace {{selected_result}} with actual output from Step 2")
        print(kimi_code)
        print("\n" + "="*60)
        print("💡 Tip: Run Step 2 first, then use its output for Step 3")

if __name__ == '__main__':
    main()
