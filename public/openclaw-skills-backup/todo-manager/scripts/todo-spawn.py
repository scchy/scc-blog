#!/usr/bin/env python3
"""
Todo Spawn Wrapper - Execute todo operations using local 7B model
待办执行包装器 - 使用本地7B模型执行待办操作
"""

import subprocess
import sys
import json
from pathlib import Path

def run_todo_command(args):
    """Run todo.py command and return result"""
    script_path = Path(__file__).parent / "todo.py"
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)] + args,
            capture_output=True,
            text=True,
            check=True
        )
        return {
            "success": True,
            "output": result.stdout.strip(),
            "error": None
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "output": e.stdout.strip() if e.stdout else "",
            "error": e.stderr.strip() if e.stderr else str(e)
        }

def generate_spawn_code(operation, args):
    """Generate sessions_spawn code for the operation"""
    
    # Map operations to commands
    command_map = {
        "set": ["add"] + args,
        "done": ["done-task"] + args,
        "done-index": ["done-index"] + args,
        "list": ["list"]
    }
    
    cmd_args = command_map.get(operation, [operation] + args)
    cmd_str = " ".join(f'"{a}"' if " " in a else a for a in cmd_args)
    
    code = f'''// Execute via local 7B model
sessions_spawn({{
  task: "Run: python3 todo.py {cmd_str}",
  model: "local-vllm-instruct/qwen2.5-7B",
  mode: "run"
}})'''
    
    return code

def main():
    if len(sys.argv) < 2:
        print("Usage: todo-spawn.py <operation> [args...]")
        print("")
        print("Operations:")
        print("  set <task> [priority] [due]    - Add todo (uses local 7B)")
        print("  done <task>                    - Complete by name")
        print("  done-index <index>             - Complete by index")
        print("  list                          - List todos")
        print("")
        print("Examples:")
        print('  todo-spawn.py set "完成周报" high "今天"')
        print('  todo-spawn.py done "周报"')
        print('  todo-spawn.py list')
        sys.exit(1)
    
    operation = sys.argv[1]
    args = sys.argv[2:]
    
    # Map operations
    if operation == "set":
        cmd_args = ["add"] + args
    elif operation == "done":
        cmd_args = ["done-task"] + args
    elif operation == "done-index":
        cmd_args = ["done-index"] + args
    elif operation == "list":
        cmd_args = ["list"]
    else:
        cmd_args = [operation] + args
    
    # Run the command
    result = run_todo_command(cmd_args)
    
    # Generate spawn code
    spawn_code = generate_spawn_code(operation, args)
    
    output = {
        "operation": operation,
        "args": args,
        "success": result["success"],
        "output": result["output"],
        "error": result["error"],
        "model_used": "local-vllm-instruct/qwen2.5-7B",
        "spawn_code": spawn_code
    }
    
    print(json.dumps(output, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
