# Module NN — TITLE

Estimated time: X minutes
Prerequisites: LIST OR "None"

ONE SENTENCE: what this module does and what the user will have when done.

## Orientation

Print this once at the start:

```
You're setting up TOPIC.
This takes about X minutes.

We'll set up:
  1. First thing
  2. Second thing
  3. Third thing

You'll need: LIST WHAT THE USER NEEDS BEFORE STARTING.
```

## Preflight

Audit current state before doing anything. Each check prints EXISTS or MISSING.

```bash
# Check 1 — DESCRIPTION
COMMAND && echo "EXISTS: LABEL" || echo "MISSING: LABEL"

# Check 2 — DESCRIPTION
COMMAND && echo "EXISTS: LABEL" || echo "MISSING: LABEL"
```

Print a summary of what was found. Skip any step below where the item already exists and is valid.

## Step 1 — STEP TITLE

Skip if CONDITION.

EXPLANATION OF WHAT THIS STEP DOES AND WHY.

If missing, tell the user:
```
INSTRUCTIONS FOR THE USER.
For system-modifying commands, prefix with !

  ! COMMAND_USER_RUNS
```

Verify:
```bash
VERIFICATION_COMMAND
```

## Step 2 — STEP TITLE

REPEAT PATTERN: skip condition, explanation, user instructions, verification.

## Verification

Run all preflight checks again as PASS/FAIL:

```bash
PASS=0
TOTAL=N

COMMAND && { echo "PASS: LABEL"; PASS=$((PASS+1)); } || echo "FAIL: LABEL"
# repeat for each check

echo ""
echo "$PASS/$TOTAL checks passed."
```

If all pass, print:
```
All checks passed. SUMMARY OF WHAT IS NOW CONFIGURED.
```

If any fail, tell the user which step to re-run.

## Challenge

```
DESCRIBE A HANDS-ON TASK USING REAL TEAM DATA.

Tell me:
  1. First thing to report
  2. Second thing to report
```

## Challenge Verification

DESCRIBE HOW TO VERIFY THE USER'S ANSWERS.
Use MCP tools, bash commands, or ask the user to show output.

If successful, print:
```
Module NN complete.

SUMMARY OF WHAT THE USER CAN NOW DO.

Next module: /learn-NN+1-NEXT-TOPIC
```

---

## MCP Module Variant

Use this section when the module installs an MCP server. Replace the generic Preflight and Step 1 above with the four-phase pattern below. Fill in the placeholders.

**Placeholders:**
- `<PACKAGE_NAME>`: npm package name (e.g., `@playwright/mcp`)
- `<SERVER_NAME>`: key in the mcpServers object (e.g., `playwright`)
- `<SERVER_ARGS>`: npx args array as JSON (e.g., `["@playwright/mcp@latest", "--browser", "chrome"]`)
- `<TOOL_PREFIX>`: expected MCP tool prefix (e.g., `mcp__playwright__`)
- `<EXTRA_DEPS>`: server-specific dependency checks (e.g., Chrome detection)
- `<MODULE_COMMAND>`: the `/learn-NN-TOPIC` command to re-run

### Phase 1 — Dependency Check (in Preflight)

```bash
# Node.js
NODE_PATH=$(command -v node 2>/dev/null)
if [ -z "$NODE_PATH" ]; then
  echo "MISSING: Node.js — install from https://nodejs.org or via Homebrew: brew install node"
else
  echo "EXISTS: Node.js $(node --version) at $NODE_PATH"
fi

# npm
NPM_PATH=$(command -v npm 2>/dev/null)
if [ -z "$NPM_PATH" ]; then
  echo "MISSING: npm — should come with Node.js, reinstall Node"
else
  echo "EXISTS: npm $(npm --version) at $NPM_PATH"
fi

# npx
NPX_PATH=$(command -v npx 2>/dev/null)
if [ -z "$NPX_PATH" ]; then
  echo "MISSING: npx — should come with npm, reinstall Node"
else
  echo "EXISTS: npx at $NPX_PATH"
fi

# PATH consistency
LOGIN_PATH=$(zsh -l -c 'echo $PATH' 2>/dev/null || bash -l -c 'echo $PATH' 2>/dev/null)
NODE_DIR=$(dirname "$(command -v node)")
if echo "$LOGIN_PATH" | tr ':' '\n' | grep -q "$NODE_DIR"; then
  echo "PASS: Node directory ($NODE_DIR) is in login shell PATH"
else
  echo "WARNING: $NODE_DIR is not in login shell PATH"
  echo "  Claude Code may not find node/npx on restart."
  echo "  Add this to ~/.zshrc or ~/.zprofile:"
  echo "    export PATH=\"$NODE_DIR:\$PATH\""
fi

# <EXTRA_DEPS> — add server-specific checks here
```

### Phase 2 — Package Install + Smoke Test (Step 1a + 1b)

```bash
# Step 1a: Global install
npm install -g <PACKAGE_NAME>
npm list -g <PACKAGE_NAME> --depth=0 2>/dev/null
if [ $? -ne 0 ]; then
  echo "FAIL: npm install failed"
else
  echo "PASS: <PACKAGE_NAME> installed globally"
fi

# Step 1b: Smoke test
NPX_FULL=$(command -v npx)
$NPX_FULL <SERVER_ARGS_FOR_LAUNCH> &
SERVER_PID=$!
sleep 3
if kill -0 $SERVER_PID 2>/dev/null; then
  echo "PASS: Server process started (PID $SERVER_PID)"
  kill $SERVER_PID 2>/dev/null
  wait $SERVER_PID 2>/dev/null
else
  wait $SERVER_PID 2>/dev/null
  echo "FAIL: Server process exited immediately"
fi
```

### Phase 3 — Config Write with Full Paths (Step 1c)

```bash
python3 << 'PYEOF'
import json, os, shutil, subprocess

path = os.path.expanduser("~/.claude/settings.json")
try:
    with open(path) as f:
        settings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}

if "mcpServers" not in settings:
    settings["mcpServers"] = {}

npx_path = shutil.which("npx")
if not npx_path:
    npx_path = subprocess.check_output(
        "command -v npx", shell=True, text=True
    ).strip()

settings["mcpServers"]["<SERVER_NAME>"] = {
    "command": npx_path,
    "args": <SERVER_ARGS>
}

with open(path, "w") as f:
    json.dump(settings, f, indent=2)

print(f"<SERVER_NAME> MCP server added with npx path: {npx_path}")
PYEOF
```

### Phase 4 — Post-Restart Verification

On re-entry, check if `<TOOL_PREFIX>*` tools are available. If not, run the diagnostic ladder:

```bash
# Is the npx path in config still valid?
NPX_IN_CONFIG=$(python3 -c "
import json, os
d = json.load(open(os.path.expanduser('~/.claude/settings.json')))
print(d['mcpServers']['<SERVER_NAME>']['command'])
")
[ -x "$NPX_IN_CONFIG" ] && echo "PASS: npx path valid" || echo "FAIL: npx path ($NPX_IN_CONFIG) not executable"

# Can we launch manually?
$NPX_IN_CONFIG <SERVER_ARGS_FOR_LAUNCH> &
SERVER_PID=$!
sleep 3
if kill -0 $SERVER_PID 2>/dev/null; then
  echo "Server launches — try restarting Claude Code again"
  kill $SERVER_PID 2>/dev/null
  wait $SERVER_PID 2>/dev/null
else
  echo "FAIL: Server won't start. Debug: $NPX_IN_CONFIG <SERVER_ARGS_FOR_LAUNCH> 2>&1"
fi
```
