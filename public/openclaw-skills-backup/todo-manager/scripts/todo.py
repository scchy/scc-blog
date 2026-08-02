#!/usr/bin/env python3
"""
Todo Manager - Simple todo management using local 7B model
待办管理 - 使用本地7B模型的简单待办管理
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

def get_todo_dir():
    """Get todo storage directory"""
    todo_dir = Path.home() / '.openclaw' / 'workspace' / 'memory'
    todo_dir.mkdir(parents=True, exist_ok=True)
    return todo_dir

def load_todos():
    """Load active todos"""
    todo_file = get_todo_dir() / 'session-todos.json'
    if todo_file.exists():
        with open(todo_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def load_completed():
    """Load completed todos"""
    todo_file = get_todo_dir() / 'session-todos-completed.json'
    if todo_file.exists():
        with open(todo_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_todos(todos):
    """Save active todos"""
    todo_file = get_todo_dir() / 'session-todos.json'
    with open(todo_file, 'w', encoding='utf-8') as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)

def save_completed(todos):
    """Save completed todos"""
    todo_file = get_todo_dir() / 'session-todos-completed.json'
    with open(todo_file, 'w', encoding='utf-8') as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)

def add_todo(task, priority="medium", due=None):
    """Add a new todo"""
    todos = load_todos()
    
    todo = {
        "id": len(todos) + 1,
        "task": task,
        "priority": priority,
        "due": due,
        "created": datetime.now().isoformat(),
        "status": "active"
    }
    
    todos.append(todo)
    save_todos(todos)
    
    return todo

def complete_todo_by_task(task_name):
    """Complete todo by task name"""
    todos = load_todos()
    completed = load_completed()
    
    for i, todo in enumerate(todos):
        if task_name in todo["task"]:
            todo["completed_at"] = datetime.now().isoformat()
            todo["status"] = "completed"
            completed.append(todo)
            todos.pop(i)
            
            save_todos(todos)
            save_completed(completed)
            return todo
    
    return None

def complete_todo_by_index(index):
    """Complete todo by index (1-based)"""
    todos = load_todos()
    completed = load_completed()
    
    if 1 <= index <= len(todos):
        todo = todos.pop(index - 1)
        todo["completed_at"] = datetime.now().isoformat()
        todo["status"] = "completed"
        completed.append(todo)
        
        save_todos(todos)
        save_completed(completed)
        return todo
    
    return None

def list_all_todos():
    """List all todos"""
    todos = load_todos()
    completed = load_completed()
    return todos, completed

def format_todo_list(todos, completed):
    """Format todo list for display"""
    lines = []
    
    # Active todos
    lines.append(f"📋 待办事项 ({len(todos)}):")
    if todos:
        for i, todo in enumerate(todos, 1):
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(todo.get("priority", "medium"), "🟡")
            due_str = f" (截止: {todo['due']})" if todo.get("due") else ""
            lines.append(f"  {i}. [ ] {priority_icon} {todo['task']}{due_str}")
    else:
        lines.append("  (无待办事项)")
    
    lines.append("")
    
    # Completed todos
    lines.append(f"✅ 已完成 ({len(completed)}):")
    if completed:
        # Show last 5 completed
        for todo in completed[-5:]:
            lines.append(f"  ✓ {todo['task']}")
        if len(completed) > 5:
            lines.append(f"  ... 还有 {len(completed) - 5} 项")
    else:
        lines.append("  (无已完成事项)")
    
    return "\n".join(lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: todo.py <command> [args...]")
        print("")
        print("Commands:")
        print("  add <task> [priority] [due]     - Add new todo")
        print("  done-task <task_name>          - Complete by task name")
        print("  done-index <index>             - Complete by index (1-based)")
        print("  list                           - List all todos")
        print("")
        print("Examples:")
        print('  todo.py add "完成周报" high "今天"')
        print('  todo.py done-task "周报"')
        print('  todo.py done-index 1')
        print('  todo.py list')
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "add":
        if len(sys.argv) < 3:
            print("Error: Task required")
            sys.exit(1)
        
        task = sys.argv[2]
        priority = sys.argv[3] if len(sys.argv) > 3 else "medium"
        due = sys.argv[4] if len(sys.argv) > 4 else None
        
        todo = add_todo(task, priority, due)
        print(f"✅ 已添加待办: {todo['task']}")
        print(f"   优先级: {todo['priority']}")
        if due:
            print(f"   截止: {due}")
    
    elif command == "done-task":
        if len(sys.argv) < 3:
            print("Error: Task name required")
            sys.exit(1)
        
        task_name = sys.argv[2]
        todo = complete_todo_by_task(task_name)
        
        if todo:
            print(f"✅ 已完成: {todo['task']}")
        else:
            print(f"❌ 未找到待办: {task_name}")
    
    elif command == "done-index":
        if len(sys.argv) < 3:
            print("Error: Index required")
            sys.exit(1)
        
        try:
            index = int(sys.argv[2])
        except ValueError:
            print("Error: Index must be a number")
            sys.exit(1)
        
        todo = complete_todo_by_index(index)
        
        if todo:
            print(f"✅ 已完成: {todo['task']}")
        else:
            print(f"❌ 无效序号: {index}")
    
    elif command == "list":
        todos, completed = list_all_todos()
        print(format_todo_list(todos, completed))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()
