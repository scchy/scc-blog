#!/usr/bin/env python3
"""
调研工作流：搜索 → 7B筛选 → Kimi分析
"""
import sys
import subprocess
import json

def search_ddg(query, max_results=5):
    """使用DuckDuckGo搜索"""
    skill_path = "~/.openclaw/extensions/feishu/skills/duckduckgo-search"
    cmd = f"cd {skill_path} && /home/scc/anaconda3/envs/LLM/bin/python scripts/search.py '{query}' --json --max {max_results}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except:
        return []

def main():
    if len(sys.argv) < 2:
        print("用法: python3 research.py '搜索关键词'")
        sys.exit(1)
    
    query = sys.argv[1]
    print(f"🔍 开始调研: {query}\n")
    
    # Step 1: 搜索
    print("Step 1: 搜索相关网页...")
    results = search_ddg(query, max_results=5)
    print(f"   找到 {len(results)} 个结果\n")
    
    # Step 2: 7B筛选 (这一步会在Agent中通过sessions_spawn完成)
    print("Step 2: 本地7B筛选Top3...")
    print("   [需要Agent调用本地模型执行]\n")
    
    # Step 3: Kimi分析
    print("Step 3: Kimi深度分析...")
    print("   [需要Agent调用Kimi执行]\n")
    
    # 输出结果供Agent处理
    print("=== 搜索结果 ===")
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
