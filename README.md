# Tmux Sidecar (tmux-sidecar)

<video src="assets/demo.mp4" controls="controls" style="max-width: 100%;">
</video>

Tmux Sidecar is a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that turns your terminal into an AI-native workspace. It allows AI agents to "sit" alongside you in your Tmux session, observing output and executing commands just like a pair programmer.

## The Sidecar Philosophy

Most AI coding tools require you to install heavy server components (Node.js, VS Code Server, etc.) on every machine you connect to. Tmux Sidecar takes a different approach: **Zero Infrastructure**.

### 1. Agent Anywhere (No Remote Server)
Because this tool operates by manipulating Tmux locally, **it works on any server you can SSH into.**
*   Connecting to a legacy production server? **It works.**
*   Jumping through a bastion host? **It works.**
*   Working in a container? **It works.**

The Agent lives on your local machine (the "Sidecar") but controls the remote environment through the SSH stream in your Tmux pane. You get full AI capabilities without installing a single file on the remote server.

### 2. Context Locking (Laser Focus)
Terminals are noisy. You might have logs scrolling in one pane, a monitor in another, and a shell in a third.
Sidecar uses a **"Context Lock"** mechanism (`set_active_target`). Once locked, the Agent focuses exclusively on that specific pane (ID), ignoring the noise from other windows. It knows exactly where to type and exactly which output belongs to its command.

### 3. The Sentinel (Smart Observation)
Standard agents "fire and forget"—they run a command and hope for the best.
Sidecar acts as a **Sentinel**. using `smart_wait`, it can execute a command (like `npm install` or `make build`) and then *watch* the stream. It waits for specific success signals ("Build Complete") or error patterns before waking up. It understands the *result*, not just the command.

## Key Capabilities

*   **Context Management**: Lock the agent to specific panes (`%1`, `%2`) for focused interaction.
*   **Robust Execution**: Run commands with marker injection to guarantee output capture (even over SSH).
*   **Layout Control**: Split panes, create windows, and organize your workspace dynamically.
*   **Deep Inspection**: Read full pane history and snapshots to understand current state.

## Prerequisites

*   **Linux/macOS**
*   **Tmux** installed and running
*   **Python 3.10+**
*   **[uv](https://github.com/astral-sh/uv)** (Recommended for installation and running)

## Installation & Usage

The easiest way to use `tmux-sidecar` is via `uv`. No cloning or manual installation is required.

### Quick Start (The Easiest Way)

Run the server instantly:

```bash
uv tool run tmux-sidecar
```

### Configuration for MCP Clients

Add this to your `claude_desktop_config.json` or equivalent:

```json
{
  "mcpServers": {
    "tmux-sidecar": {
      "command": "uv",
      "args": ["tool", "run", "tmux-sidecar"]
    }
  }
}
```

### Alternative: Install from GitHub

If you prefer to run the absolute latest version from source:

```bash
uv tool run git+https://github.com/Logic-H/tmux-sidecar.git
```


## Usage Guide

Once the server is running and connected to your AI assistant (e.g., Claude, Gemini), you can interact with Tmux using natural language.

### 1. Discovery & Connection (The "Handshake")

The first step is usually to find out what's running and "lock" onto a specific pane to work in.

*   **User:** "Show me my running tmux sessions."
*   **Tool:** `list_active_panes()`
    *   Returns a list of panes with IDs (e.g., `%1`, `%2`), titles, and a preview of their content.
*   **User:** "Connect to the 'backend' pane."
*   **Tool:** `set_active_target(pane_id="%2")`
    *   **Crucial Step:** This sets `%2` as the *default target*. Subsequent commands like `run_shell` will automatically execute here without needing the ID every time.

### 2. Reliable Command Execution

Unlike a standard terminal integration, this server uses a robust "explicit" execution mode. It injects markers to ensure it captures *exactly* the output of your command, complete with exit codes.

*   **User:** "Check the git status."
*   **Tool:** `run_shell(command="git status")`
    *   *Requires a locked target.* Executes the command in the focused pane and returns the full output.

*   **User:** "Run `ls -la` in the other window (pane %3)."
*   **Tool:** `execute_in_pane_explicit(pane_id="%3", command="ls -la")`
    *   Executes in a specific pane without changing the global lock.

### 3. Smart Observation (Wait for Output)

Perfect for long-running tasks like builds, server startups, or test runs.

*   **User:** "Restart the server and let me know when it's ready."
*   **Tool:** `run_shell(command="npm run start")` -> `smart_wait(pane_id="%2", pattern="Server listening on port")`
    *   The AI will poll the pane content until the specific regex pattern appears, then notify you.

### 4. Layout Management

You can manipulate your workspace directly.

*   **User:** "Split this window and run the monitor."
*   **Tool:** `split_window(pane_id="%2", direction="horizontal")` -> `run_shell(...)`

## Available Tools Reference

### Core & Context
*   `list_active_panes`: Lists all panes with a snapshot of their current state. **Use this first.**
*   `set_active_target(pane_id)`: Sets the global focus. **Required for `run_shell`.**
*   `get_current_status`: Checks which pane is currently locked.

### Execution
*   `run_shell(command)`: Runs a command in the *currently locked* pane. Blocks until finished.
*   `execute_in_pane_explicit(pane_id, command)`: Runs a command in a specific pane.
*   `send_keys(pane_id, keys)`: Sends raw keystrokes (e.g., `C-c`, `q`, `Up`) to control interactive apps (vim, top).

### Observation
*   `inspect_pane(pane_id)`: Reads the last N lines of a pane's history.
*   `smart_wait(pane_id, pattern)`: Blocks execution until a regex pattern appears in the pane.

### Session Management
*   `create_session(name)`: Starts a new session.
*   `create_window(target_session, name)`: Adds a window.
*   `split_window(pane_id, direction)`: Splits horizontally (`-h`) or vertically (`-v`).
*   `kill_pane(pane_id)` / `kill_window(target)`: Closes terminals.
*   `rename_window` / `resize_pane` / `select_layout`: UI adjustments.


## Development

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Logic-H/tmux-sidecar.git
    cd tmux-sidecar
    ```

2.  **Install dependencies:**
    ```bash
    uv sync
    ```

3.  **Run the test suite:**
    ```bash
    uv run test_suite.py
    ```

## License

MIT
