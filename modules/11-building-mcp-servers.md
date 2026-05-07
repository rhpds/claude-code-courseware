# Module 11 — Building MCP Servers

Estimated time: 30 minutes
Prerequisites: Module 01 (Claude Code installed and working), Module 04 recommended (Git MCP — as a reference implementation)

Build a custom MCP server in Python that exposes tools Claude Code can call, then register and use it from inside a Claude Code session.

## Orientation

Print this once at the start:

```
You're building your own MCP server from scratch and connecting it to Claude Code.
This takes about 30 minutes.

An MCP (Model Context Protocol) server is a process that speaks JSON-RPC over
stdin/stdout. Claude Code launches it as a subprocess and calls its tools the
same way it calls Git MCP or Jira MCP tools. You define the tools — Claude
calls them.

We'll build:
  1. A Python MCP server with two tools
  2. A project structure with dependency management
  3. Registration in Claude Code's settings
  4. Live tool invocation from a Claude Code session

After this module you'll know how to extend Claude Code with any custom
tool you need — file utilities, API wrappers, internal services, anything.

You'll need:
  - Python 3.10+ installed
  - pip or uv for package management
  - Claude Code installed and working (Module 01)
```

## Progress Tracking

On module start, write a progress marker:

```bash
mkdir -p ~/.claude/courseware-progress && date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/11.started
```

## Preflight

Audit current state before doing anything:

```bash
# Claude Code installed?
command -v claude &>/dev/null && echo "EXISTS: Claude Code" || echo "MISSING: Claude Code — run /learn-01-vertex-setup first"

# Python 3.10+?
if command -v python3 &>/dev/null; then
  PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
  PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
  PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
  if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 10 ]; then
    echo "EXISTS: Python $PY_VERSION"
  else
    echo "MISSING: Python 3.10+ required (found $PY_VERSION)"
  fi
else
  echo "MISSING: Python 3 — install Python 3.10 or later"
fi

# pip available?
python3 -m pip --version &>/dev/null && echo "EXISTS: pip $(python3 -m pip --version | awk '{print $2}')" || echo "MISSING: pip — install with: python3 -m ensurepip"

# Project directory already exists?
[ -d "$HOME/repos/my-mcp-server" ] && echo "EXISTS: ~/repos/my-mcp-server directory" || echo "MISSING: ~/repos/my-mcp-server directory (will create in Step 2)"

# server.py already written?
[ -f "$HOME/repos/my-mcp-server/server.py" ] && echo "EXISTS: server.py" || echo "MISSING: server.py (will create in Step 3)"

# mcp SDK installed?
python3 -c "import mcp" &>/dev/null 2>&1 && echo "EXISTS: mcp Python SDK" || echo "MISSING: mcp Python SDK (will install in Step 2)"

# MCP server already registered?
if [ -f "$HOME/.claude/settings.json" ]; then
  python3 -c "
import json
try:
    d = json.load(open('$HOME/.claude/settings.json'))
    servers = d.get('mcpServers', {})
    if 'my-server' in servers:
        print('EXISTS: my-server registered in ~/.claude/settings.json')
    else:
        print('MISSING: my-server not in ~/.claude/settings.json (will register in Step 5)')
except:
    print('MISSING: could not parse ~/.claude/settings.json')
" 2>/dev/null
else
  echo "MISSING: ~/.claude/settings.json does not exist"
fi
```

If Claude Code or Python is MISSING, stop and tell the user:
```
Claude Code or Python 3.10+ is not installed.
  - Claude Code: complete Module 01 first (/learn-01-vertex-setup)
  - Python: install from https://www.python.org or via your package manager
```

Print a summary of what was found. Skip steps where the item already exists and is valid.

## Step 1 — Understand MCP server architecture

This step is informational. No commands to run.

Explain:
```
How MCP servers work:

  1. An MCP server is a standalone process — a Python script, a Node.js app,
     or any executable that speaks the MCP protocol.

  2. Communication happens over stdio (stdin/stdout) using JSON-RPC messages.
     Claude Code launches the server as a subprocess and sends tool-call
     requests over stdin. The server sends results back over stdout.

  3. A server registers tools — functions that Claude can call with typed
     arguments and that return typed results. Optionally, a server can also
     expose resources (read-only data Claude can access).

  4. The mcp Python SDK handles all the protocol plumbing. You define tools
     as decorated Python functions, and the SDK handles serialization,
     validation, and the JSON-RPC transport.

  The pattern looks like this:

     Claude Code                    Your MCP server
     ----------                    ---------------
     Launches server via stdio  -> Server starts, registers tools
     Sends tool call request    -> Server runs your function
     Receives structured result <- Server returns the result

  This is the same pattern used by the Git MCP, Jira MCP, Memory MCP, and
  every other MCP server you've used in this courseware.
```

## Step 2 — Create the project structure

Skip if `~/repos/my-mcp-server/requirements.txt` already exists with `mcp[cli]` in it.

Explain:
```
We'll create a minimal project with two files:

  ~/repos/my-mcp-server/
    server.py           — the MCP server (tools live here)
    requirements.txt    — Python dependencies

The only dependency is the mcp SDK with its CLI extras.
```

Tell the user:
```
Create the project directory and install the dependency:

  ! mkdir -p ~/repos/my-mcp-server
  ! echo 'mcp[cli]' > ~/repos/my-mcp-server/requirements.txt
  ! python3 -m pip install -r ~/repos/my-mcp-server/requirements.txt
```

Verify:
```bash
# Directory exists?
[ -d "$HOME/repos/my-mcp-server" ] && echo "PASS: project directory exists" || echo "FAIL: ~/repos/my-mcp-server not found"

# requirements.txt has mcp?
grep -q 'mcp' "$HOME/repos/my-mcp-server/requirements.txt" 2>/dev/null && echo "PASS: requirements.txt contains mcp" || echo "FAIL: requirements.txt missing or does not contain mcp"

# mcp SDK importable?
python3 -c "import mcp; print(f'PASS: mcp SDK version {mcp.__version__}')" 2>/dev/null || echo "FAIL: mcp SDK not importable — run pip install again"
```

## Step 3 — Write a simple MCP server

Skip if `~/repos/my-mcp-server/server.py` already exists and contains `FastMCP`.

Explain:
```
The server defines tools using the @mcp.tool() decorator. Each tool is a
regular Python function with type annotations. The SDK uses the function
name, docstring, and type hints to generate the tool schema that Claude sees.

We'll create two tools:
  - greet(name)       — returns a greeting string (a "hello world" for MCP)
  - summarize_file(path) — reads a file and returns its line count and first lines
```

Tell the user:
```
Create server.py with the following content:

  ! cat > ~/repos/my-mcp-server/server.py << 'PYEOF'
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")


@mcp.tool()
def greet(name: str) -> str:
    """Return a greeting for the given name."""
    return f"Hello, {name}! This response came from your custom MCP server."


@mcp.tool()
def summarize_file(path: str) -> str:
    """Read a file and return its line count and first 10 lines."""
    try:
        with open(path) as f:
            lines = f.readlines()
    except FileNotFoundError:
        return f"File not found: {path}"
    except PermissionError:
        return f"Permission denied: {path}"

    total = len(lines)
    preview = "".join(lines[:10])
    if total > 10:
        preview += f"\n... ({total - 10} more lines)"

    return f"File: {path}\nLines: {total}\n\n{preview}"


if __name__ == "__main__":
    mcp.run()
PYEOF
```

Verify:
```bash
# File exists?
[ -f "$HOME/repos/my-mcp-server/server.py" ] && echo "PASS: server.py exists" || echo "FAIL: server.py not found"

# Valid Python syntax?
python3 -c "import ast; ast.parse(open('$HOME/repos/my-mcp-server/server.py').read()); print('PASS: server.py has valid Python syntax')" 2>/dev/null || echo "FAIL: server.py has syntax errors"

# Contains FastMCP?
grep -q 'FastMCP' "$HOME/repos/my-mcp-server/server.py" 2>/dev/null && echo "PASS: server.py uses FastMCP" || echo "FAIL: server.py does not contain FastMCP"

# Contains both tools?
grep -c '@mcp.tool()' "$HOME/repos/my-mcp-server/server.py" 2>/dev/null | {
  read count
  if [ "$count" -ge 2 ]; then
    echo "PASS: server.py defines $count tools"
  else
    echo "FAIL: expected at least 2 @mcp.tool() decorators, found $count"
  fi
}
```

## Step 4 — Test the server locally

Skip if the server has already been tested (proceed to Step 5).

Explain:
```
Before registering with Claude Code, verify the server starts without errors.
When you run it directly, it waits for JSON-RPC input on stdin — that's
expected behavior. We just need to confirm it launches cleanly.
```

Tell the user:
```
Test that the server starts without import or syntax errors:

  ! cd ~/repos/my-mcp-server && timeout 3 python3 server.py 2>&1 || true

The command will exit after 3 seconds (or you can press Ctrl+C). What
matters is that there are no ImportError or SyntaxError messages.

If the mcp CLI is available, you can also test interactively:

  ! cd ~/repos/my-mcp-server && mcp dev server.py

This opens a browser-based inspector where you can call your tools.
Press Ctrl+C to stop when done.
```

Verify:
```bash
# Attempt to start the server — capture stderr for errors
cd "$HOME/repos/my-mcp-server"
OUTPUT=$(timeout 3 python3 -c "
import importlib.util, sys
spec = importlib.util.spec_from_file_location('server', 'server.py')
mod = importlib.util.module_from_spec(spec)
# Just import — don't run mcp.run()
sys.modules['server'] = mod
try:
    spec.loader.exec_module(mod)
except SystemExit:
    pass
print('OK')
" 2>&1)

if echo "$OUTPUT" | grep -q "OK"; then
  echo "PASS: server.py imports without errors"
else
  echo "FAIL: server.py has import errors:"
  echo "$OUTPUT"
fi
```

## Step 5 — Register with Claude Code

Skip if `my-server` is already registered in `~/.claude/settings.json`.

Explain:
```
Claude Code discovers MCP servers from its settings file. We'll register
your server so Claude Code launches it automatically on startup.

The registration tells Claude Code:
  - The command to run (python3)
  - The full path to the server script
  - The server name (used as a prefix for tool names)
```

Tell the user:
```
Register the server with Claude Code:

  ! claude mcp add my-server -- python3 $HOME/repos/my-mcp-server/server.py

This adds an entry to ~/.claude/settings.json under mcpServers.
```

Verify:
```bash
if [ -f "$HOME/.claude/settings.json" ]; then
  python3 -c "
import json
d = json.load(open('$HOME/.claude/settings.json'))
servers = d.get('mcpServers', {})
if 'my-server' in servers:
    cfg = servers['my-server']
    cmd = cfg.get('command', '')
    args = ' '.join(cfg.get('args', []))
    print('PASS: my-server registered in ~/.claude/settings.json')
    print(f'  Command: {cmd} {args}')
else:
    print('FAIL: my-server not found in mcpServers')
" 2>/dev/null
else
  echo "FAIL: ~/.claude/settings.json does not exist"
fi
```

Tell the user:
```
IMPORTANT: Claude Code needs to be restarted to load the new MCP server.

  1. Exit this Claude Code session (Ctrl+C or type /exit)
  2. Relaunch Claude Code: claude .
  3. Re-run this module: /learn-11-building-mcp-servers

The preflight will detect the registration and skip Steps 1-5 on re-entry.
```

Note: If the user needed to restart, the module resumes from Step 6 when re-run.

## Step 6 — Use the tools from Claude Code

This step requires the MCP server to be running (loaded after restart). If the tools are not available, tell the user to restart Claude Code (see Step 5).

Explain:
```
After restarting, Claude Code should have launched your server automatically.
Your tools are now available alongside Git MCP, Memory MCP, and the others.

Let's verify the server is running and call both tools.
```

First, check that the server is loaded:
```
Check the MCP server status. You can run:

  /mcp

Look for "my-server" in the list. It should show as connected with 2 tools.
If it's not listed or shows an error, check:
  - The path in ~/.claude/settings.json points to the correct server.py
  - Python 3 is available on your PATH
  - The mcp SDK is installed in the Python environment Claude Code uses
```

Then call the tools to demonstrate they work:

1. Call the `greet` tool:
```
Ask Claude to greet you by name. For example:

  "Use the greet tool to say hello to me"

Expected result: a greeting string from your custom server.
```

2. Call the `summarize_file` tool:
```
Ask Claude to summarize a file. For example:

  "Use the summarize_file tool on ~/repos/my-mcp-server/server.py"

Expected result: the line count and first 10 lines of server.py.
```

Explain:
```
Your tools work exactly like the built-in MCP tools. Claude sees the
function name, docstring, and parameter types, then calls them with
structured arguments and receives structured results.

Key points:
  - Tool names come from the Python function names
  - Docstrings become the tool descriptions Claude reads
  - Type annotations define the parameter schema
  - Return values are sent back as tool results
```

## Verification

Run all checks and report:

```bash
PASS_COUNT=0
TOTAL=6

# 1. server.py exists and has valid syntax
if python3 -c "import ast; ast.parse(open('$HOME/repos/my-mcp-server/server.py').read())" 2>/dev/null; then
  echo "PASS: server.py exists with valid Python syntax"
  PASS_COUNT=$((PASS_COUNT+1))
else
  echo "FAIL: server.py missing or has syntax errors"
fi

# 2. requirements.txt exists with mcp dependency
if grep -q 'mcp' "$HOME/repos/my-mcp-server/requirements.txt" 2>/dev/null; then
  echo "PASS: requirements.txt contains mcp dependency"
  PASS_COUNT=$((PASS_COUNT+1))
else
  echo "FAIL: requirements.txt missing or does not contain mcp"
fi

# 3. mcp SDK is installed
if python3 -c "import mcp" 2>/dev/null; then
  echo "PASS: mcp Python SDK is installed"
  PASS_COUNT=$((PASS_COUNT+1))
else
  echo "FAIL: mcp Python SDK not importable"
fi

# 4. server.py uses FastMCP and defines at least 2 tools
TOOL_COUNT=$(grep -c '@mcp.tool()' "$HOME/repos/my-mcp-server/server.py" 2>/dev/null || echo 0)
if [ "$TOOL_COUNT" -ge 2 ]; then
  echo "PASS: server.py defines $TOOL_COUNT tools"
  PASS_COUNT=$((PASS_COUNT+1))
else
  echo "FAIL: server.py defines $TOOL_COUNT tools (expected at least 2)"
fi

# 5. Server is registered in settings.json
if python3 -c "
import json
d = json.load(open('$HOME/.claude/settings.json'))
assert 'my-server' in d.get('mcpServers', {})
" 2>/dev/null; then
  echo "PASS: my-server registered in ~/.claude/settings.json"
  PASS_COUNT=$((PASS_COUNT+1))
else
  echo "FAIL: my-server not found in ~/.claude/settings.json"
fi

# 6. Server script is importable (no runtime errors)
if python3 -c "
import importlib.util, sys
spec = importlib.util.spec_from_file_location('server', '$HOME/repos/my-mcp-server/server.py')
mod = importlib.util.module_from_spec(spec)
sys.modules['server'] = mod
try:
    spec.loader.exec_module(mod)
except SystemExit:
    pass
" 2>/dev/null; then
  echo "PASS: server.py imports without errors"
  PASS_COUNT=$((PASS_COUNT+1))
else
  echo "FAIL: server.py has import errors"
fi

echo ""
echo "$PASS_COUNT/$TOTAL checks passed."
```

If all pass, print:
```
All checks passed. Your custom MCP server is built, registered, and available.
```

If any fail:
```
Troubleshooting:

  server.py syntax errors:
    Run: python3 ~/repos/my-mcp-server/server.py
    Fix any import or syntax errors reported.

  mcp SDK not installed:
    Run: python3 -m pip install mcp[cli]

  Server not registered:
    Run: claude mcp add my-server -- python3 ~/repos/my-mcp-server/server.py

  Tools not available after restart:
    Run /mcp to check server status. If the server shows an error,
    check the command path in ~/.claude/settings.json.
```

## Challenge

```
Add a third tool to your MCP server: search_files

The tool should:
  - Accept two parameters: directory (str) and pattern (str)
  - Use Python's glob module to find files matching the pattern
    in the given directory (recursively)
  - Return the list of matching file paths, one per line
  - Handle errors (directory not found, permission denied)
  - Include a clear docstring so Claude knows what the tool does

Example usage:
  search_files(directory="~/repos/my-mcp-server", pattern="*.py")
  should return: /Users/you/repos/my-mcp-server/server.py

Steps:
  1. Edit ~/repos/my-mcp-server/server.py to add the new tool
  2. Restart Claude Code to reload the server
  3. Test the tool by asking Claude to search for files

Tell me:
  - The full source of your search_files function
  - The result of searching this courseware repo for *.md files
```

## Challenge Verification

Verify the challenge by checking:

1. `server.py` now defines at least 3 tools:
```bash
TOOL_COUNT=$(grep -c '@mcp.tool()' "$HOME/repos/my-mcp-server/server.py" 2>/dev/null || echo 0)
if [ "$TOOL_COUNT" -ge 3 ]; then
  echo "PASS: server.py defines $TOOL_COUNT tools (including search_files)"
else
  echo "FAIL: expected at least 3 tools, found $TOOL_COUNT"
fi
```

2. The search_files function exists and uses glob:
```bash
grep -q 'def search_files' "$HOME/repos/my-mcp-server/server.py" 2>/dev/null && echo "PASS: search_files function defined" || echo "FAIL: search_files function not found"
grep -q 'glob' "$HOME/repos/my-mcp-server/server.py" 2>/dev/null && echo "PASS: uses glob module" || echo "FAIL: glob module not referenced"
```

3. The server still imports without errors:
```bash
python3 -c "import ast; ast.parse(open('$HOME/repos/my-mcp-server/server.py').read()); print('PASS: server.py has valid syntax')" 2>/dev/null || echo "FAIL: syntax errors in server.py"
```

4. If the MCP tools are available, call `search_files` on the courseware repo to confirm it returns `.md` files.

Write the completion marker:

```bash
date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/11.done
```

If all checks pass, print:
```
Module 11 complete.

You can now build custom MCP servers for Claude Code.
You know how to:
  - Create an MCP server using the mcp Python SDK and FastMCP
  - Define tools with @mcp.tool(), typed parameters, and docstrings
  - Register a server with claude mcp add
  - Test and debug servers locally and through Claude Code

Architecture recap:
  Claude Code  --stdio-->  Your server  --JSON-RPC-->  Your tools
  (subprocess)             (FastMCP)                   (Python functions)

Ideas for your next server:
  - Wrap an internal API (Jira, ServiceNow, custom services)
  - Add file-processing utilities (CSV parsing, log analysis)
  - Build a database query tool (PostgreSQL, SQLite)
  - Create a deployment helper (check pod status, tail logs)

To remove the practice server later:
  claude mcp remove my-server
  rm -rf ~/repos/my-mcp-server

Next module: /learn-12-review-agents

Questions or feedback? https://github.com/rhpds/claude-code-courseware/issues
```
