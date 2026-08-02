#!/usr/bin/env python3
"""
DuckDuckGo Search - Free web search without API keys
"""

import json
import sys
import argparse
import urllib.request
import urllib.parse
import re
from html.parser import HTMLParser

class TextExtractor(HTMLParser):
    """Extract text from HTML"""
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False
        
    def handle_starttag(self, tag, attrs):
        if tag in ['script', 'style', 'nav', 'footer']:
            self.skip = True
            
    def handle_endtag(self, tag):
        if tag in ['script', 'style', 'nav', 'footer']:
            self.skip = False
            
    def handle_data(self, data):
        if not self.skip:
            self.text.append(data)
            
    def get_text(self):
        return ' '.join(self.text)

def search_duckduckgo(query, max_results=10):
    """
    Search DuckDuckGo using ddgs package
    """
    try:
        # Try using ddgs package (new name for duckduckgo-search)
        try:
            from ddgs import DDGS
            with DDGS() as ddgs:
                results = []
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        'title': r.get('title', ''),
                        'url': r.get('href', ''),
                        'snippet': r.get('body', '')
                    })
                return results
        except ImportError:
            pass
        
        # Try old package name
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = []
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        'title': r.get('title', ''),
                        'url': r.get('href', ''),
                        'snippet': r.get('body', '')
                    })
                return results
        except ImportError:
            pass
        
        # Fallback: Simple HTML scraping
        encoded_query = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0'
        }
        
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
        
        # Parse results
        results = []
        
        # Find result blocks
        result_pattern = r'<div class="result[^"]*"[^>]*>.*?<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?<a[^>]*class="result__snippet"[^>]*>(.*?)</a>.*?</div>'
        matches = re.findall(result_pattern, html, re.DOTALL)
        
        for url, title_html, snippet_html in matches[:max_results]:
            # Clean HTML tags
            title = re.sub(r'<[^>]+>', '', title_html)
            snippet = re.sub(r'<[^>]+>', '', snippet_html)
            
            # Decode HTML entities
            title = title.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            snippet = snippet.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            
            results.append({
                'title': title.strip(),
                'url': url.strip(),
                'snippet': snippet.strip()
            })
        
        return results
        
    except Exception as e:
        return [{'error': str(e)}]

def main():
    parser = argparse.ArgumentParser(description='DuckDuckGo Search')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--max', '-m', type=int, default=5, help='Max results (default: 5)')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    parser.add_argument('--type', '-t', choices=['web', 'news'], default='web', help='Search type')
    
    args = parser.parse_args()
    
    results = search_duckduckgo(args.query, args.max)
    
    output = {
        'query': args.query,
        'type': args.type,
        'results': results,
        'total': len(results)
    }
    
    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(f"🔍 Search: {args.query}")
        print(f"{'='*60}")
        for i, r in enumerate(results, 1):
            if 'error' in r:
                print(f"❌ Error: {r['error']}")
                continue
            print(f"\n{i}. {r['title']}")
            print(f"   URL: {r['url']}")
            print(f"   {r['snippet'][:150]}...")

if __name__ == '__main__':
    main()
