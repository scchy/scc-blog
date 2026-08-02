#!/usr/bin/env python3
"""
智能调研触发器
当检测到"调研"关键词时，自动执行：搜索 → 7B筛选 → Kimi分析
"""
import sys
import json
import re

# 触发词列表
TRIGGER_WORDS = ['调研', '研究一下', '查查', '搜索', '找一下']

def should_trigger(text):
    """检查是否应该触发调研流程"""
    for word in TRIGGER_WORDS:
        if word in text:
            return True, word
    return False, None

def extract_query(text, trigger_word):
    """提取搜索关键词"""
    # 移除触发词
    query = text.replace(trigger_word, '').strip()
    # 移除标点
    query = re.sub(r'[，。？！,.?!]', '', query)
    return query

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({"trigger": False, "reason": "No input"}))
        sys.exit(0)
    
    text = sys.argv[1]
    triggered, word = should_trigger(text)
    
    if triggered:
        query = extract_query(text, word)
        print(json.dumps({
            "trigger": True,
            "trigger_word": word,
            "query": query
        }))
    else:
        print(json.dumps({"trigger": False}))
