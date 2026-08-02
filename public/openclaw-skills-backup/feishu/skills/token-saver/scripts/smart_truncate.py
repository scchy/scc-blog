#!/usr/bin/env python3
"""
Smart Truncate - Intelligent JSON truncation for tool results
智能截断 - 工具结果的智能 JSON 截断
"""

import json
import sys
import argparse
from pathlib import Path

def estimate_tokens(text):
    """Rough estimate: ~4 chars per token"""
    if isinstance(text, (dict, list)):
        text = json.dumps(text, ensure_ascii=False)
    return len(text) // 4

def truncate_value(value, max_depth=3, current_depth=0, max_array_items=5, max_string_length=200):
    """Recursively truncate a value"""
    if current_depth >= max_depth:
        if isinstance(value, dict):
            return f"<dict:{len(value)} keys>"
        elif isinstance(value, list):
            return f"<array:{len(value)} items>"
        elif isinstance(value, str) and len(value) > max_string_length:
            return value[:max_string_length] + "..."
        return value
    
    if isinstance(value, dict):
        result = {}
        for k, v in value.items():
            result[k] = truncate_value(v, max_depth, current_depth + 1, max_array_items, max_string_length)
        return result
    
    elif isinstance(value, list):
        if len(value) > max_array_items:
            truncated = [truncate_value(v, max_depth, current_depth + 1, max_array_items, max_string_length) 
                        for v in value[:max_array_items]]
            truncated.append(f"<... {len(value) - max_array_items} more items>")
            return truncated
        else:
            return [truncate_value(v, max_depth, current_depth + 1, max_array_items, max_string_length) 
                   for v in value]
    
    elif isinstance(value, str) and len(value) > max_string_length:
        return value[:max_string_length] + "..."
    
    return value

def preserve_paths(data, paths):
    """Preserve specific paths from truncation"""
    if not paths:
        return data
    
    preserved = {}
    for path in paths:
        keys = path.split('.')
        value = data
        try:
            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key)
                elif isinstance(value, list) and key.isdigit():
                    value = value[int(key)]
                else:
                    value = None
                    break
            if value is not None:
                preserved[path] = value
        except:
            pass
    
    return preserved

def smart_truncate(data, max_tokens=1000, preserve_paths_list=None, summarize_arrays=5):
    """Smart truncate JSON data to fit within token limit"""
    current_tokens = estimate_tokens(data)
    
    if current_tokens <= max_tokens:
        return data, current_tokens, 0
    
    # Start with preserving specified paths
    preserved = preserve_paths(data, preserve_paths_list or [])
    
    # Calculate how much we need to reduce
    target_reduction = (current_tokens - max_tokens) / current_tokens
    
    # Determine truncation depth based on reduction needed
    if target_reduction < 0.3:
        max_depth = 4
        max_string = 300
    elif target_reduction < 0.6:
        max_depth = 3
        max_string = 200
    else:
        max_depth = 2
        max_string = 100
    
    # Truncate
    truncated = truncate_value(data, max_depth=max_depth, max_array_items=summarize_arrays, max_string_length=max_string)
    
    # Restore preserved paths
    for path, value in preserved.items():
        keys = path.split('.')
        target = truncated
        try:
            for key in keys[:-1]:
                if isinstance(target, dict):
                    target = target.get(key, {})
                elif isinstance(target, list) and key.isdigit():
                    target = target[int(key)]
            if isinstance(target, dict) and keys[-1] in target:
                target[keys[-1]] = value
        except:
            pass
    
    new_tokens = estimate_tokens(truncated)
    saved = current_tokens - new_tokens
    
    return truncated, new_tokens, saved

def main():
    parser = argparse.ArgumentParser(description='Smart JSON Truncation for Token Saving')
    parser.add_argument('input', nargs='?', help='Input JSON file (or stdin)')
    parser.add_argument('--max-tokens', '-t', type=int, default=1000, help='Maximum tokens (default: 1000)')
    parser.add_argument('--preserve', '-p', action='append', help='Preserve path (can use multiple times)')
    parser.add_argument('--summarize-arrays', '-a', type=int, default=5, help='Max array items to show (default: 5)')
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    parser.add_argument('--stats', '-s', action='store_true', help='Show statistics only')
    
    args = parser.parse_args()
    
    # Read input
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)
    
    # Truncate
    truncated, new_tokens, saved = smart_truncate(
        data,
        max_tokens=args.max_tokens,
        preserve_paths_list=args.preserve,
        summarize_arrays=args.summarize_arrays
    )
    
    if args.stats:
        original_tokens = estimate_tokens(data)
        print(f"Original: {original_tokens:,} tokens")
        print(f"Truncated: {new_tokens:,} tokens")
        print(f"Saved: {saved:,} tokens ({saved/original_tokens*100:.1f}%)")
        return
    
    # Output
    output = json.dumps(truncated, indent=2, ensure_ascii=False)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Truncated to {new_tokens:,} tokens (saved {saved:,})")
    else:
        print(output)
        if saved > 0:
            print(f"\n# Truncated: {new_tokens:,} tokens (saved {saved:,})", file=sys.stderr)

if __name__ == '__main__':
    main()
