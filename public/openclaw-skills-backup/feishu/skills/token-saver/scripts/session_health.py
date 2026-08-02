#!/usr/bin/env python3
"""
Session Health Monitor - Token usage monitoring and alerts
会话健康监控 - Token 使用监控和预警
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta

def estimate_tokens(text):
    """Rough estimate: ~4 chars per token for mixed content"""
    if isinstance(text, (dict, list)):
        text = json.dumps(text, ensure_ascii=False)
    return len(text) // 4

def get_session_store_path():
    """Get OpenClaw session store path"""
    config_path = Path.home() / '.openclaw' / 'openclaw.json'
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
            store_path = config.get('session', {}).get('store')
            if store_path:
                return Path(store_path)
        except:
            pass
    return Path.home() / '.openclaw' / 'sessions.json'

def analyze_bootstrap_files():
    """Analyze workspace bootstrap files"""
    workspace = Path.home() / '.openclaw' / 'workspace'
    bootstrap_files = [
        'AGENTS.md', 'SOUL.md', 'USER.md', 'MEMORY.md',
        'IDENTITY.md', 'TOOLS.md', 'MODEL_GUIDE.md'
    ]
    
    total_tokens = 0
    file_info = []
    
    for filename in bootstrap_files:
        filepath = workspace / filename
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                tokens = estimate_tokens(content)
                total_tokens += tokens
                file_info.append({
                    'name': filename,
                    'tokens': tokens,
                    'lines': content.count('\n') + 1
                })
            except:
                pass
    
    return total_tokens, file_info

def get_config_info():
    """Get relevant config for token optimization"""
    config_path = Path.home() / '.openclaw' / 'openclaw.json'
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        defaults = config.get('agents', {}).get('defaults', {})
        session = config.get('session', {})
        
        return {
            'bootstrapMaxChars': defaults.get('bootstrapMaxChars', 20000),
            'bootstrapTotalMaxChars': defaults.get('bootstrapTotalMaxChars', 150000),
            'compactionMode': defaults.get('compaction', {}).get('mode', 'default'),
            'compactionModel': defaults.get('compaction', {}).get('model', 'default'),
            'parentForkMaxTokens': session.get('parentForkMaxTokens', 0)
        }
    except:
        return {}

def check_health(bootstrap_tokens, config):
    """Check overall health and generate alerts"""
    alerts = []
    warnings = []
    
    # Bootstrap file checks
    max_bootstrap = config.get('bootstrapTotalMaxChars', 150000) // 4
    if bootstrap_tokens > max_bootstrap:
        alerts.append(f"⚠️  Bootstrap files exceed limit: {bootstrap_tokens:,} > {max_bootstrap:,} tokens")
    elif bootstrap_tokens > max_bootstrap * 0.6:
        warnings.append(f"⚡ Bootstrap files approaching limit: {bootstrap_tokens:,} tokens ({bootstrap_tokens/max_bootstrap*100:.0f}%)")
    
    # Config optimization checks
    if config.get('compactionMode') != 'safeguard':
        warnings.append("💡 Consider setting compaction.mode to 'safeguard' for better token management")
    
    if not config.get('compactionModel') or config.get('compactionModel') == 'default':
        warnings.append("💡 Consider setting compaction.model to local model for cost savings")
    
    if config.get('parentForkMaxTokens', 0) == 0:
        warnings.append("💡 Consider setting session.parentForkMaxTokens to prevent runaway sessions")
    
    return alerts, warnings

def main():
    parser = argparse.ArgumentParser(description='Session Health Monitor')
    parser.add_argument('--quiet', action='store_true', help='Only output alerts')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()
    
    # Gather data
    bootstrap_tokens, bootstrap_files = analyze_bootstrap_files()
    config = get_config_info()
    alerts, warnings = check_health(bootstrap_tokens, config)
    
    if args.json:
        output = {
            'bootstrap': {
                'total_tokens': bootstrap_tokens,
                'files': bootstrap_files
            },
            'config': config,
            'alerts': alerts,
            'warnings': warnings,
            'status': 'CRITICAL' if alerts else ('WARNING' if warnings else 'HEALTHY')
        }
        print(json.dumps(output, indent=2))
        return
    
    if args.quiet:
        if alerts or warnings:
            for alert in alerts:
                print(alert)
            for warning in warnings:
                print(warning)
        return
    
    # Full report
    print("🔍 Session Health Report")
    print("=" * 50)
    
    print("\n📁 Bootstrap Files:")
    print("-" * 30)
    for f in bootstrap_files:
        print(f"  {f['name']:20} {f['tokens']:>6,} tokens ({f['lines']:>4} lines)")
    print(f"  {'TOTAL':20} {bootstrap_tokens:>6,} tokens")
    
    limit = config.get('bootstrapTotalMaxChars', 150000) // 4
    pct = (bootstrap_tokens / limit * 100) if limit else 0
    status_icon = "✅" if pct < 60 else ("⚡" if pct < 90 else "⚠️")
    print(f"\n  {status_icon} Bootstrap usage: {pct:.0f}% of limit ({limit:,} tokens)")
    
    print("\n⚙️  Configuration:")
    print("-" * 30)
    print(f"  bootstrapMaxChars:        {config.get('bootstrapMaxChars', 'default (20000)')}")
    print(f"  bootstrapTotalMaxChars:   {config.get('bootstrapTotalMaxChars', 'default (150000)')}")
    print(f"  compaction.mode:          {config.get('compactionMode', 'default')}")
    print(f"  compaction.model:         {config.get('compactionModel', 'default')}")
    print(f"  parentForkMaxTokens:      {config.get('parentForkMaxTokens', 'not set')}")
    
    if alerts or warnings:
        print("\n🚨 Alerts & Warnings:")
        print("-" * 30)
        for alert in alerts:
            print(f"  {alert}")
        for warning in warnings:
            print(f"  {warning}")
    else:
        print("\n✅ All checks passed! Token usage is healthy.")
    
    print("\n💡 Recommendations:")
    print("-" * 30)
    print("  1. Use 'memory_search' + 'memory_get' for memory access")
    print("  2. Run '/reset' when sessions get long (20+ rounds)")
    print("  3. Use sub-agents for token-heavy tasks")
    print("  4. Check 'MODEL_GUIDE.md' for model selection")

if __name__ == '__main__':
    main()
