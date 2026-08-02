#!/usr/bin/env python3
"""
Token Audit Script for OpenClaw Sessions
Analyzes workspace files and estimates token consumption
"""

import os
import sys
import json
from pathlib import Path

def estimate_tokens(text):
    """Rough estimate: ~4 chars per token for CJK, ~4 for English"""
    return len(text) // 4

def analyze_file(filepath):
    """Analyze a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        tokens = estimate_tokens(content)
        lines = content.count('\n') + 1
        return {
            'path': str(filepath),
            'tokens': tokens,
            'lines': lines,
            'size_bytes': len(content.encode('utf-8'))
        }
    except Exception as e:
        return {
            'path': str(filepath),
            'error': str(e)
        }

def main():
    workspace = Path.home() / '.openclaw' / 'workspace'
    
    print("🔍 Token Audit Report")
    print("=" * 50)
    
    total_tokens = 0
    files_analyzed = []
    
    # Bootstrap files that load on every session
    bootstrap_files = [
        'AGENTS.md',
        'SOUL.md', 
        'USER.md',
        'MEMORY.md',
        'IDENTITY.md',
        'TOOLS.md',
        'MODEL_GUIDE.md'
    ]
    
    print("\n📁 Bootstrap Files (loaded every session):")
    print("-" * 50)
    
    for filename in bootstrap_files:
        filepath = workspace / filename
        if filepath.exists():
            info = analyze_file(filepath)
            if 'error' not in info:
                total_tokens += info['tokens']
                files_analyzed.append(info)
                print(f"  {filename:20} {info['tokens']:>6} tokens ({info['lines']:>4} lines)")
    
    # Memory directory
    memory_dir = workspace / 'memory'
    if memory_dir.exists():
        print("\n🧠 Memory Files (loaded selectively):")
        print("-" * 50)
        for memfile in sorted(memory_dir.glob('*.md')):
            info = analyze_file(memfile)
            if 'error' not in info:
                print(f"  {memfile.name:20} {info['tokens']:>6} tokens ({info['lines']:>4} lines)")
    
    print("\n" + "=" * 50)
    print(f"📊 Total Bootstrap Tokens: ~{total_tokens:,}")
    print(f"📊 Recommended Limit: 50,000 tokens")
    
    if total_tokens > 50000:
        print(f"⚠️  WARNING: Bootstrap exceeds recommended limit!")
        print(f"   Consider trimming files to reduce token usage.")
    else:
        print(f"✅ Bootstrap size is healthy")
    
    # Tips
    print("\n💡 Optimization Tips:")
    print("  1. Use 'memory_search' + 'memory_get' instead of loading full files")
    print("  2. Trim AGENTS.md to essential instructions only")
    print("  3. Archive old daily memory files")
    print("  4. Use sub-agents for token-heavy tasks")

if __name__ == '__main__':
    main()
