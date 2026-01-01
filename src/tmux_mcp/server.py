import subprocess, time, uuid, re, json, logging, os
from typing import List, Dict, Any, Optional, Literal
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
mcp = FastMCP("Tmux Sidecar")

def run_tmux(args: List[str]) -> str:
    try:
        res = subprocess.run(["tmux"] + args, capture_output=True, text=True, check=False)
        return res.stdout.strip() if res.returncode == 0 else f"Error: {res.stderr.strip()}"
    except Exception as e: return f"System Error: {str(e)}"

def get_active_target():
    val = run_tmux(["show-options", "-g", "-v", "@mcp_active_target"])
    return val if val and not val.startswith("Error") else None

@mcp.tool()
def set_active_target(pane_id: str):
    run_tmux(["set-option", "-g", "@mcp_active_target", pane_id])
    return f"✅ Locked on {pane_id}."

@mcp.tool()
def get_current_status():
    t = get_active_target()
    return f"Connected to {t}" if t else "Idle"

@mcp.tool()
def list_active_panes():
    cur = run_tmux(["display", "-p", "#{pane_id}"])
    tgt = get_active_target()
    raw = run_tmux(["list-panes", "-a", "-F", "#{pane_id}|#{session_name}:#{window_index}.#{pane_index}|#{pane_title}|#{pane_current_command}"])
    res = []
    for line in raw.splitlines():
        pid, name, title, cmd = line.split("|")
        if pid == cur: continue
        p_raw = run_tmux(["capture-pane", "-t", pid, "-p", "-S", "-10"])
        res.append({"id": pid, "target": (pid == tgt), "name": name, "title": title, "cmd": cmd, "preview": p_raw.splitlines()})
    return json.dumps(res, indent=2)

@mcp.tool()
def execute_in_pane_explicit(pane_id: str, command: str, timeout: int = 30):
    rid = uuid.uuid4().hex[:8]
    start, end = f"SM_{rid}", f"EM_{rid}"
    run_tmux(["send-keys", "-t", pane_id, f" echo '{start}'; {command}; echo '{end}_'$? ", "C-m"])
    st = time.time()
    while time.time() - st < timeout:
        cap = run_tmux(["capture-pane", "-t", pane_id, "-p", "-S", "-2000"])
        if end in cap:
            m = re.search(re.escape(start)+r'(.*?)'+re.escape(end)+r'_(\d+)', cap, re.DOTALL)
            if m:
                out, code = m.group(1).strip(), m.group(2)
                return f"EXIT: {code} {'✅' if code=='0' else '❌'}\n{out}"
        time.sleep(0.5)
    return "TIMEOUT"

@mcp.tool()
def run_shell(command: str):
    t = get_active_target()
    return execute_in_pane_explicit(t, command) if t else "No target locked."

@mcp.tool()
def smart_wait(pane_id: str, pattern: str, timeout: int = 60):
    st, rex = time.time(), re.compile(pattern)
    while time.time() - st < timeout:
        if rex.search(run_tmux(["capture-pane", "-t", pane_id, "-p", "-S", "-100"])):
            return f"✅ Found: {pattern}"
        time.sleep(1)
    return "❌ Timeout"

@mcp.tool()
def inspect_pane(pane_id: str, lines: int = 100):
    return run_tmux(["capture-pane", "-t", pane_id, "-p", "-S", f"-{lines}"])

@mcp.tool()
def create_session(name: str): return run_tmux(["new-session", "-d", "-s", name])

@mcp.tool()
def create_window(target_session: str, name: str):
    return run_tmux(["new-window", "-t", target_session, "-n", name])

@mcp.tool()
def split_window(pane_id: str, direction: str):
    f = "-h" if direction == "horizontal" else "-v"
    return run_tmux(["split-window", f, "-t", pane_id, "-P", "-F", "#{pane_id}"])

@mcp.tool()
def kill_window(target: str):
    return run_tmux(["kill-window", "-t", target])

@mcp.tool()
def kill_pane(pane_id: str): return run_tmux(["kill-pane", "-t", pane_id])

@mcp.tool()
def rename_window(target: str, new_name: str):
    return run_tmux(["rename-window", "-t", target, new_name])

@mcp.tool()
def resize_pane(pane_id: str, direction: str, amount: int = 5):
    return run_tmux(["resize-pane", "-t", pane_id, f"-{direction}", str(amount)])

@mcp.tool()
def select_layout(target_window: str, layout: str):
    return run_tmux(["select-layout", "-t", target_window, layout])

@mcp.tool()
def rotate_window(target_window: str):
    return run_tmux(["rotate-window", "-t", target_window])

def main(): mcp.run()
if __name__ == "__main__": main()