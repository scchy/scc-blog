#!/usr/bin/env python3
"""
Quick Model Command Handler
Handles /local and /kimi shortcuts
"""

import sys
import json

def parse_command(message):
    """Parse /local or /kimi command from message"""
    message = message.strip()
    
    if message.startswith('/local '):
        task = message[7:].strip()  # Remove '/local '
        return {
            'command': 'local',
            'task': task,
            'model': 'local-vllm-instruct/qwen2.5-7B'
        }
    elif message.startswith('/kimi '):
        task = message[6:].strip()  # Remove '/kimi '
        return {
            'command': 'kimi',
            'task': task,
            'model': 'kimi-coding/k2p5'
        }
    
    return None

def generate_spawn_code(parsed):
    """Generate sessions_spawn code"""
    if not parsed:
        return None
    
    code = f'''sessions_spawn({{
  task: "{parsed['task']}",
  model: "{parsed['model']}",
  mode: "run"
}})'''
    return code

def main():
    if len(sys.argv) < 2:
        print("Usage: handler.py '<message>'")
        sys.exit(1)
    
    message = sys.argv[1]
    parsed = parse_command(message)
    
    if parsed:
        code = generate_spawn_code(parsed)
        print(json.dumps({
            'detected': True,
            'command': parsed['command'],
            'task': parsed['task'],
            'model': parsed['model'],
            'spawn_code': code
        }, indent=2))
    else:
        print(json.dumps({
            'detected': False
        }))

if __name__ == '__main__':
    main()
