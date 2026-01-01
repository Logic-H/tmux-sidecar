#!/usr/bin/env python3
import sys
import time
import re
import os

# 将源码路径加入 path 以便直接导入测试
sys.path.append(os.path.expanduser("~/.config/tmux/tmux-mcp/src"))
from tmux_mcp.server import (
    set_active_target, 
    run_shell, 
    smart_wait, 
    inspect_pane, 
    split_window, 
    kill_pane,
    send_keys_active
)

TARGET_PANE = "%10"

print(f"🎯 开始测试 Tmux Sidecar Capability on {TARGET_PANE}...
")

# 1. 测试锁定
print(f"[1] Locking Target...")
print(set_active_target(TARGET_PANE))

# 2. 测试同步执行
print(f"\n[2] Testing Synchronous Execution (run_shell)...")
output = run_shell("echo 'Hello MCP World'")
print(f"Result:\n{output}")

# 3. 测试智能等待 (Smart Wait)
print(f"\n[3] Testing Smart Wait...")
# 先在后台发送一个延迟命令
run_shell("sleep 2 && echo 'Server Started' &")
print("Waiting for 'Server Started' pattern...")
wait_result = smart_wait(TARGET_PANE, "Server Started", timeout_seconds=5)
print(f"Wait Result: {wait_result}")

# 4. 测试上下文回溯 (Inspect)
print(f"\n[4] Testing Inspect Pane...")
logs = inspect_pane(TARGET_PANE, lines=3)
print(f"Last 3 lines:\n{logs}")

# 5. 测试管理能力 (Split & Kill)
print(f"\n[5] Testing Layout Management (Split)...")
split_res = split_window(TARGET_PANE, "vertical")
print(split_res)

# 提取新 Pane ID
match = re.search(r"%[0-9]+", split_res)
if match:
    new_pane = match.group(0)
    print(f"New pane created: {new_pane}")
    
    # 在新分屏里做点事
    run_shell(f"tmux send-keys -t {new_pane} 'echo I am a temporary pane' C-m")
    time.sleep(1)
    
    print(f"Killing {new_pane}...")
    print(kill_pane(new_pane))
else:
    print("Failed to parse new pane ID")

print(f"\n✅ All tests completed.")
