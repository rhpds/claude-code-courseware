# Module 14 — Debugging and Troubleshooting

Estimated time: 15 minutes
Prerequisites: Module 01 (Claude Code installed and working)

Learn what to do when things go wrong — MCP server failures, tool errors, context issues, and common gotchas.

## Orientation

Print this once at the start:

```
You're learning to debug Claude Code issues.
This takes about 15 minutes.

We'll cover:
  1. MCP server diagnostic ladder
  2. Tool and permission errors
  3. Context and session problems
  4. The "restart and re-check" pattern

You'll need:
  - Claude Code installed and working (Module 01)
```

## Preflight

Audit current state — this module is about diagnosis, so we start by checking the health of the current setup.

```bash
# Check 1 — Claude Code installed?
command -v claude &>/dev/null && echo "EXISTS: Claude Code $(claude --version 2>/dev/null | head -1)" || echo "MISSING: Claude Code — run /learn-01-vertex-setup first"

# Check 2 — Settings file exists?
[ -f "$HOME/.claude/settings.json" ] && echo "EXISTS: ~/.claude/settings.json" || echo "MISSING: ~/.claude/settings.json"

# Check 3 — Count configured MCP servers
if [ -f "$HOME/.claude/settings.json" ]; then
  MCP_COUNT=$(python3 -c "
import json
d = json.load(open('$HOME/.claude/settings.json'))
print(len(d.get('mcpServers', {})))
" 2>/dev/null)
  echo "INFO: $MCP_COUNT MCP server(s) configured"
fi

# Check 4 — Node.js and npx available?
command -v node &>/dev/null && echo "EXISTS: Node.js $(node --version)" || echo "INFO: Node.js not installed"
command -v npx &>/dev/null && echo "EXISTS: npx at $(command -v npx)" || echo "INFO: npx not available"

# Check 5 — Check for common problem indicators
if [ -d "$HOME/.claude/logs" ]; then
  RECENT_ERRORS=$(find "$HOME/.claude/logs" -name "*.log" -newer "$HOME/.claude/settings.json" 2>/dev/null | wc -l | tr -d ' ')
  echo "INFO: $RECENT_ERRORS log file(s) newer than settings.json"
fi
```

Print a summary of what was found.

## Step 1 — MCP Server Diagnostic Ladder

MCP server failures are the most common issue. When a server doesn't load, work through this ladder.

Tell the user:
```
When an MCP server fails to load, debug in this order:

LEVEL 1 — Is the binary reachable?
  Check that the command in settings.json exists and is executable.

LEVEL 2 — Does the process start?
  Try launching the server manually to see startup errors.

LEVEL 3 — Is the path correct?
  Claude Code's PATH may differ from your shell's PATH.
  Use absolute paths in settings.json to avoid this.

LEVEL 4 — Does it respond to MCP protocol?
  Some servers start but fail to handle MCP handshake.

Let's walk through each level with a real server.
```

Demonstrate the diagnostic ladder with whatever MCP server the user has configured:

```bash
# Pick the first configured MCP server to diagnose
python3 << 'PYEOF'
import json, os

path = os.path.expanduser("~/.claude/settings.json")
d = json.load(open(path))
servers = d.get("mcpServers", {})

if not servers:
    print("No MCP servers configured — skipping live demo.")
else:
    name = list(servers.keys())[0]
    config = servers[name]
    cmd = config.get("command", "unknown")
    args = config.get("args", [])

    print(f"Diagnosing server: {name}")
    print(f"  Command: {cmd}")
    print(f"  Args: {' '.join(args)}")
    print()

    # Level 1: Binary exists?
    import shutil
    if shutil.which(cmd):
        print(f"  LEVEL 1 PASS: {cmd} found at {shutil.which(cmd)}")
    else:
        print(f"  LEVEL 1 FAIL: {cmd} not found in PATH")
        print(f"    Fix: Use absolute path. Find it with: command -v {cmd}")

    # Level 2: Check if it's an absolute path
    if os.path.isabs(cmd):
        if os.path.isfile(cmd) and os.access(cmd, os.X_OK):
            print(f"  PATH CHECK PASS: Absolute path is executable")
        else:
            print(f"  PATH CHECK FAIL: {cmd} not executable")
    else:
        print(f"  PATH NOTE: Using relative command '{cmd}' — consider absolute path for reliability")
PYEOF
```

Explain:
```
The most common fix: replace the command in settings.json with
an absolute path. Instead of "npx", use the output of:
  command -v npx

This prevents PATH mismatch between your shell and Claude Code's
runtime environment.
```

## Step 2 — Tool and Permission Errors

Tell the user:
```
When a tool call fails, you'll see an error in the conversation.
Common categories:

  PERMISSION DENIED
    Claude Code has a permission system. When you deny a tool call,
    Claude won't retry the exact same call. It needs to adjust.

    Fix: If you accidentally denied, tell Claude "go ahead" or
    "I approve that action." Or restart the session to reset.

  TOOL NOT FOUND
    The MCP server is loaded but the specific tool doesn't exist.
    This usually means the server version changed.

    Fix: Check the server's documentation for current tool names.
    Run /mcp to see available tools.

  TIMEOUT
    Tool took too long to execute (default 120s for Bash).

    Fix: For long-running commands, use run_in_background.
    For MCP tools, check if the server is hung.

  HOOK BLOCKED
    A PreToolUse hook blocked the action (exit code 2).

    Fix: Check .claude/hooks/ and settings.json for hooks.
    The hook's output message tells you why it blocked.
```

## Step 3 — Context and Session Problems

Tell the user:
```
Context-related issues:

  "I told you this already"
    Claude Code compresses old messages as context fills up.
    Information from early in a long session may be lost.

    Fix: Use /compact to compress proactively. For critical
    info, put it in CLAUDE.md or Memory MCP.

  "Claude forgot the plan"
    Same cause — context compression.

    Fix: Write plans to files, not just conversation. Use
    tasks (TaskCreate) for step tracking.

  "Session is slow / expensive"
    Context is too large. Every message sends the full context.

    Fix: Start a new session (/clear or exit+relaunch).
    Use /cost to check current session cost.

  "Claude keeps asking for permission"
    Each new command pattern needs approval.

    Fix: Add allowed patterns to settings.json permissions,
    or use the /permissions command.

  "MCP tools disappeared"
    Server crashed mid-session.

    Fix: Restart Claude Code. If it persists, run the
    diagnostic ladder from Step 1.
```

## Step 4 — The Restart-and-Recheck Pattern

Tell the user:
```
When in doubt, this sequence fixes most issues:

  1. Exit Claude Code (Ctrl+C or /exit)
  2. Check settings:  cat ~/.claude/settings.json | python3 -m json.tool
  3. Test the server:  npx <package> (or whatever the command is)
  4. Restart:  claude .
  5. Verify:  /mcp (check servers are loaded)

If that doesn't work:
  6. Check logs:  ls -la ~/.claude/logs/
  7. Try verbose:  claude --verbose .
  8. Reset MCP:  Remove the server from settings.json, restart,
     re-add it, restart again
```

## Verification

This module is conceptual — verification is based on demonstrating understanding.

Ask the user:
```
Let's verify you can diagnose issues. I'll ask you three questions:

1. An MCP server is configured but its tools don't appear after
   restart. What's the first thing you check?

2. You denied a tool call by mistake and now Claude won't retry.
   What do you do?

3. You're 45 minutes into a session and Claude seems to have
   forgotten instructions from the start. What happened and
   how do you prevent it?
```

Expected answers:
1. Check that the command path is valid and executable (Level 1 of the diagnostic ladder). Use absolute paths.
2. Tell Claude to proceed, or restart the session to reset permission state.
3. Context compression dropped early messages. Put critical info in CLAUDE.md or Memory MCP. Use /compact proactively.

Accept any reasonable phrasing that shows understanding.

If successful, print:
```
All checks passed. You understand the core debugging patterns.
```

## Challenge

```
Run a health check on your current Claude Code setup:

1. List all your configured MCP servers and check if each
   command path is valid (use the Level 1 diagnostic)
2. Check your session cost with /cost
3. Identify one thing that could be improved in your setup
   (absolute paths, missing servers, context bloat, etc.)

Tell me:
  1. How many MCP servers you have, and how many passed Level 1
  2. Your current session cost
  3. The improvement you identified
```

## Challenge Verification

Review the user's answers. Any reasonable health check results pass.

If successful, print:
```
Module 14 complete.

You now know how to debug Claude Code issues.
Diagnostic toolkit:
  MCP servers: command path → process start → absolute path → protocol
  Tool errors: permission reset, tool name check, timeout handling
  Context: /compact, /cost, CLAUDE.md for persistent instructions
  Nuclear option: restart and re-check

Key rules of thumb:
  - Always use absolute paths in MCP server configs
  - When in doubt, restart Claude Code
  - Put critical info in files, not just conversation
  - Check /cost periodically in long sessions
  - /mcp shows current server and tool status

Next module: /learn-15-cost-context-management
```
