# Module 10 — Hooks

Estimated time: 15 minutes
Prerequisites: Module 01 (Claude Code installed and working)

Create pre- and post-command hooks that run automatically when Claude Code executes tools, giving you guardrails and automation.

## Orientation

Print this once at the start:

```
You're learning Claude Code hooks.
This takes about 15 minutes.

We'll cover:
  1. What hooks are and when they fire
  2. Writing a pre-tool hook (guardrail)
  3. Writing a post-tool hook (automation)
  4. Hook configuration in settings.json

You'll need:
  - Claude Code installed and working (Module 01)
```

## Progress Tracking

On module start, write a progress marker:

```bash
mkdir -p ~/.claude/courseware-progress && date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/10.started
```

## Preflight

Audit current state before doing anything. Each check prints EXISTS or MISSING.

```bash
# Check 1 — Claude Code installed?
command -v claude &>/dev/null && echo "EXISTS: Claude Code" || echo "MISSING: Claude Code — run /learn-01-vertex-setup first"

# Check 2 — Existing hooks configured?
if [ -f "$HOME/.claude/settings.json" ]; then
  HOOK_COUNT=$(python3 -c "
import json
d = json.load(open('$HOME/.claude/settings.json'))
hooks = d.get('hooks', {})
count = 0
for event in hooks:
  if isinstance(hooks[event], list):
    count += len(hooks[event])
print(count)
" 2>/dev/null)
  if [ "$HOOK_COUNT" -gt 0 ] 2>/dev/null; then
    echo "EXISTS: $HOOK_COUNT hook(s) already configured"
  else
    echo "INFO: No hooks configured yet (expected — we'll create some)"
  fi
else
  echo "INFO: No settings.json found — will create hooks in project settings"
fi

# Check 3 — Project .claude/settings.local.json exists?
if [ -f ".claude/settings.local.json" ]; then
  echo "EXISTS: Project-local settings file"
else
  echo "INFO: No project-local settings — hooks can go in user or project settings"
fi
```

Print a summary of what was found.

If Claude Code is MISSING, stop:
```
Claude Code is not installed. Complete Module 01 first:
  /learn-01-vertex-setup
```

## Step 1 — Understanding Hooks

Hooks are shell commands that Claude Code runs automatically before or after tool calls. They let you add guardrails, logging, and automation without modifying Claude's behavior directly.

Tell the user:
```
Claude Code hooks fire at specific events:

  PreToolUse     — runs BEFORE a tool is executed
                   Can block the action (exit non-zero = blocked)

  PostToolUse    — runs AFTER a tool completes
                   Gets the tool result, can log or react

  Notification   — runs when Claude sends a notification
                   (e.g., background task complete)

  Stop           — runs when Claude finishes a response

  SubagentStop   — runs when a subagent completes

Hook config goes in:
  ~/.claude/settings.json          (global — all projects)
  .claude/settings.json            (project — this repo only)
  .claude/settings.local.json      (project-local — gitignored)

Each hook has:
  - matcher: which tool to match (regex or exact)
  - command: shell command to run
  - timeout: max execution time (ms, default 60000)
```

## Step 2 — Write a PreToolUse Hook (Guardrail)

This hook prevents destructive git operations by blocking force-push and hard-reset commands.

Tell the user:
```
Let's create a safety hook that blocks dangerous git commands.
This is a PreToolUse hook that inspects Bash tool calls and
blocks "git push --force" and "git reset --hard".

The hook script receives tool input as JSON on stdin. It reads
the command being run and checks for dangerous patterns.
```

Create the hook script:

```bash
mkdir -p .claude/hooks

cat > .claude/hooks/guard-git.sh << 'HOOKEOF'
#!/bin/bash
# PreToolUse hook: block destructive git commands
# Receives tool input as JSON on stdin

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_name',''))" 2>/dev/null)

if [ "$TOOL_NAME" != "Bash" ]; then
  exit 0
fi

COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null)

# Block dangerous patterns
if echo "$COMMAND" | grep -qE 'git\s+push\s+.*--force|git\s+reset\s+--hard|git\s+clean\s+-fd'; then
  echo "BLOCKED: Destructive git command detected: $COMMAND"
  echo "Use the standard git workflow instead."
  exit 2
fi

exit 0
HOOKEOF

chmod +x .claude/hooks/guard-git.sh
echo "PASS: Guard hook created at .claude/hooks/guard-git.sh"
```

Now register it in settings. Tell the user:
```
Now we need to register this hook. I'll add it to the project's
local settings so it only applies here.
```

```bash
python3 << 'PYEOF'
import json, os

path = ".claude/settings.local.json"
try:
    with open(path) as f:
        settings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}

if "hooks" not in settings:
    settings["hooks"] = {}

if "PreToolUse" not in settings["hooks"]:
    settings["hooks"]["PreToolUse"] = []

# Check if hook already exists
existing = [h for h in settings["hooks"]["PreToolUse"] if "guard-git" in h.get("command", "")]
if not existing:
    settings["hooks"]["PreToolUse"].append({
        "matcher": "Bash",
        "command": "bash .claude/hooks/guard-git.sh",
        "timeout": 5000
    })

with open(path, "w") as f:
    json.dump(settings, f, indent=2)

print("PASS: PreToolUse hook registered in .claude/settings.local.json")
PYEOF
```

## Step 3 — Write a PostToolUse Hook (Logging)

This hook logs all file modifications to a local audit trail.

Tell the user:
```
Now let's create a PostToolUse hook that logs every file
Claude Code modifies. This creates an audit trail you can
review later.
```

```bash
cat > .claude/hooks/log-edits.sh << 'HOOKEOF'
#!/bin/bash
# PostToolUse hook: log file modifications
# Receives tool result as JSON on stdin

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_name',''))" 2>/dev/null)

# Only log Edit and Write tools
if [ "$TOOL_NAME" != "Edit" ] && [ "$TOOL_NAME" != "Write" ]; then
  exit 0
fi

FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('file_path','unknown'))" 2>/dev/null)
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

mkdir -p .claude/logs
echo "$TIMESTAMP | $TOOL_NAME | $FILE_PATH" >> .claude/logs/edit-audit.log

exit 0
HOOKEOF

chmod +x .claude/hooks/log-edits.sh
echo "PASS: Logging hook created at .claude/hooks/log-edits.sh"
```

Register it:

```bash
python3 << 'PYEOF'
import json

path = ".claude/settings.local.json"
with open(path) as f:
    settings = json.load(f)

if "PostToolUse" not in settings["hooks"]:
    settings["hooks"]["PostToolUse"] = []

existing = [h for h in settings["hooks"]["PostToolUse"] if "log-edits" in h.get("command", "")]
if not existing:
    settings["hooks"]["PostToolUse"].append({
        "matcher": "(Edit|Write)",
        "command": "bash .claude/hooks/log-edits.sh",
        "timeout": 5000
    })

with open(path, "w") as f:
    json.dump(settings, f, indent=2)

print("PASS: PostToolUse hook registered")
PYEOF
```

## Step 4 — Test the Hooks

Tell the user:
```
Hooks take effect on the next Claude Code session.
To test them, you'll need to restart:

1. Exit this session (Ctrl+C or /exit)
2. Relaunch: claude .
3. Re-run this module: /learn-10-hooks

On re-entry, the preflight will show the hooks are configured.
Then try:
  - Ask Claude to "run git push --force" — should be blocked
  - Ask Claude to edit any file — the audit log should capture it
```

After restart, verify hooks are active:

```bash
# Check hooks are registered
python3 -c "
import json
d = json.load(open('.claude/settings.local.json'))
hooks = d.get('hooks', {})
pre = len(hooks.get('PreToolUse', []))
post = len(hooks.get('PostToolUse', []))
print(f'PreToolUse hooks: {pre}')
print(f'PostToolUse hooks: {post}')
" 2>/dev/null

# Check if audit log exists (will exist after an edit)
if [ -f ".claude/logs/edit-audit.log" ]; then
  echo "EXISTS: Audit log has $(wc -l < .claude/logs/edit-audit.log | tr -d ' ') entries"
else
  echo "INFO: Audit log will be created after the first file edit"
fi
```

## Verification

Run all checks as PASS/FAIL:

```bash
PASS=0
TOTAL=4

# 1. Hook scripts exist
[ -x ".claude/hooks/guard-git.sh" ] && { echo "PASS: Guard hook script exists and is executable"; PASS=$((PASS+1)); } || echo "FAIL: Guard hook script missing"

# 2. Logging hook exists
[ -x ".claude/hooks/log-edits.sh" ] && { echo "PASS: Logging hook script exists and is executable"; PASS=$((PASS+1)); } || echo "FAIL: Logging hook script missing"

# 3. PreToolUse hook registered
python3 -c "
import json
d = json.load(open('.claude/settings.local.json'))
hooks = d.get('hooks', {}).get('PreToolUse', [])
assert any('guard-git' in h.get('command','') for h in hooks)
print('PASS: PreToolUse hook registered')
" 2>/dev/null && PASS=$((PASS+1)) || echo "FAIL: PreToolUse hook not registered"

# 4. PostToolUse hook registered
python3 -c "
import json
d = json.load(open('.claude/settings.local.json'))
hooks = d.get('hooks', {}).get('PostToolUse', [])
assert any('log-edits' in h.get('command','') for h in hooks)
print('PASS: PostToolUse hook registered')
" 2>/dev/null && PASS=$((PASS+1)) || echo "FAIL: PostToolUse hook not registered"

echo ""
echo "$PASS/$TOTAL checks passed."
```

If all pass, print:
```
All checks passed. Hooks are configured and ready.
```

If any fail, tell the user which step to re-run.

## Challenge

```
Create a new hook that does one of the following:

  Option A: A PreToolUse hook that warns (but doesn't block)
  when a Bash command would modify files outside the current
  project directory.

  Option B: A PostToolUse hook that automatically runs
  "git diff --stat" after every file edit.

Tell me:
  1. Which option you chose
  2. Show me your hook script
  3. Show me the settings.json entry you added
```

## Challenge Verification

Review the user's hook script and settings entry. Check:
- The script is syntactically valid bash
- The event type matches the use case (Pre for guardrail, Post for automation)
- The matcher targets the right tool(s)
- The script handles the JSON input correctly

Write the completion marker:

```bash
date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/10.done
```

If successful, print:
```
Module 10 complete.

You can now create Claude Code hooks for guardrails and automation.
Key concepts:
  - PreToolUse: runs before, exit 2 = block, exit 0 = allow
  - PostToolUse: runs after, receives tool result
  - Hooks receive JSON on stdin with tool_name and tool_input
  - Matcher uses regex to select which tools trigger the hook
  - Settings scope: global (~/.claude/), project (.claude/), local (.local)

Common hook patterns:
  - Block dangerous commands (force push, rm -rf /)
  - Audit trail of all file modifications
  - Auto-lint after code changes
  - Notify on long-running operations
  - Enforce naming conventions

Next module: /learn-11-building-mcp-servers

Questions or feedback? https://github.com/rhpds/claude-code-courseware/issues
```
