#!/usr/bin/env python3
"""
Wiki Spawn - Subagent wrapper for OpenClaw.
Spawns wiki operations as subagent tasks.
"""

import sys
import os

# Add skill scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from wiki_manager import WikiManager


def main():
    """Entry point for OpenClaw subagent."""
    # Read operation from environment or args
    operation = os.environ.get("WIKI_OPERATION", sys.argv[1] if len(sys.argv) > 1 else "lint")
    wiki_root = os.environ.get("WIKI_ROOT", sys.argv[2] if len(sys.argv) > 2 else ".")
    
    manager = WikiManager(wiki_root)
    
    if operation == "ingest":
        source_file = os.environ.get("WIKI_SOURCE", sys.argv[3] if len(sys.argv) > 3 else "")
        if not source_file:
            print("Error: No source file specified for ingest")
            sys.exit(1)
        result = manager.ingest(source_file)
        print(result)
    
    elif operation == "query":
        question = os.environ.get("WIKI_QUESTION", sys.argv[3] if len(sys.argv) > 3 else "")
        if not question:
            print("Error: No question specified for query")
            sys.exit(1)
        result = manager.query(question)
        print(result)
    
    elif operation == "lint":
        result = manager.lint()
        print(result)
    
    else:
        print(f"Unknown operation: {operation}")
        print("Supported: ingest, query, lint")
        sys.exit(1)


if __name__ == "__main__":
    main()