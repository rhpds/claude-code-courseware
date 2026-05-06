# Robust MCP Install Pattern

Date: 2026-05-06

## Problem

MCP modules (06-Playwright, 03-Memory, 04-Git) use a "write config and pray" pattern: they add an entry to `~/.claude/settings.json` using bare `npx` as the command, tell the user to restart Claude Code, and hope the server starts. When it doesn't, the user has no diagnostic path.

Beta testing of Module 06 confirmed the failure mode: after completing the module and restarting, the Playwright MCP server never appeared in `/mcp`. The user tried installing npm/npx and adjusting PATH with no success. Claude Code itself could see the config in settings.json but couldn't explain why the server wasn't starting.

### Root causes

1. **No smoke test**: Modules never verify the MCP server process can actually launch before writing config.
2. **Bare `npx` in config**: `"command": "npx"` relies on PATH resolution at Claude Code startup time. Claude Code's shell environment often has a different PATH than the user's terminal (Homebrew, nvm, fnm, nix all wire PATH differently via shell profile files that may not run in Claude Code's context).
3. **No pre-install**: `npx` may need to download the package at startup, which can fail silently due to network, registry, or cache issues.
4. **No post-restart verification**: On re-entry, the preflight only checks "is config in the file?" not "are the MCP tools actually available in this session?"
5. **No diagnostic ladder**: When things fail, the user has no structured troubleshooting path.

## Solution: Four-Phase MCP Install Pattern

Every MCP module preflight adopts a four-phase structure. Each phase must pass before proceeding to the next.

### Phase 1 -- Dependency Check

Verify the runtime exists, is the right version, and is reachable from Claude Code's shell.

**Shared checks (all Node-based MCP servers):**

```bash
# Node.js
NODE_PATH=$(command -v node 2>/dev/null)
if [ -z "$NODE_PATH" ]; then
  echo "MISSING: Node.js — install from https://nodejs.org or via Homebrew: brew install node"
  # STOP
else
  echo "EXISTS: Node.js $(node --version) at $NODE_PATH"
fi

# npm
NPM_PATH=$(command -v npm 2>/dev/null)
if [ -z "$NPM_PATH" ]; then
  echo "MISSING: npm — should come with Node.js, reinstall Node"
  # STOP
else
  echo "EXISTS: npm $(npm --version) at $NPM_PATH"
fi

# npx
NPX_PATH=$(command -v npx 2>/dev/null)
if [ -z "$NPX_PATH" ]; then
  echo "MISSING: npx — should come with npm, reinstall Node"
  # STOP
else
  echo "EXISTS: npx at $NPX_PATH"
fi

# PATH consistency check
# Compare Claude Code's PATH with what a login shell resolves
LOGIN_PATH=$(zsh -l -c 'echo $PATH' 2>/dev/null || bash -l -c 'echo $PATH' 2>/dev/null)
if echo "$LOGIN_PATH" | tr ':' '\n' | grep -q "$(dirname "$NODE_PATH")"; then
  echo "PASS: Node directory is in login shell PATH"
else
  echo "WARNING: $(dirname "$NODE_PATH") is not in login shell PATH"
  echo "  Claude Code may not find node/npx on restart."
  echo "  Add this to ~/.zshrc or ~/.zprofile:"
  echo "    export PATH=\"$(dirname "$NODE_PATH"):\$PATH\""
  # STOP — user must fix PATH before continuing
fi
```

**Server-specific checks added per module:**

- Module 06 (Playwright): Chrome installed at `/Applications/Google Chrome.app` (macOS) or `which google-chrome` (Linux)
- Module 03 (Memory): No additional dependencies
- Module 04 (Git): Git installed

### Phase 2 -- Package Install + Smoke Test

Pre-install the package globally so npx never needs to download at runtime, then prove the server actually starts.

```bash
# Install globally
echo "Installing MCP server package..."
npm install -g <PACKAGE_NAME>
# Verify install succeeded
npm list -g <PACKAGE_NAME> --depth=0 2>/dev/null
if [ $? -ne 0 ]; then
  echo "FAIL: npm install failed"
  echo "  Try: sudo npm install -g <PACKAGE_NAME>"
  echo "  Or use a prefix: npm install -g --prefix ~/.npm-global <PACKAGE_NAME>"
  # STOP
fi
echo "PASS: <PACKAGE_NAME> installed globally"
```

```bash
# Smoke test — spawn server, confirm it starts, kill it
# Note: macOS lacks GNU timeout. Use perl one-liner as portable alternative.
echo "Smoke test: launching server process..."
NPX_FULL=$(command -v npx)
$NPX_FULL <PACKAGE_NAME> <SERVER_ARGS> &
SERVER_PID=$!
sleep 3
if kill -0 $SERVER_PID 2>/dev/null; then
  echo "PASS: Server process started (PID $SERVER_PID)"
  kill $SERVER_PID 2>/dev/null
  wait $SERVER_PID 2>/dev/null
else
  wait $SERVER_PID 2>/dev/null
  EXIT_CODE=$?
  echo "FAIL: Server process exited immediately (exit code $EXIT_CODE)"
  echo "  Possible causes:"
  echo "    - Missing dependency (Chrome for Playwright, etc.)"
  echo "    - Permission error"
  echo "    - Port conflict"
  echo "  Re-run with stderr: $NPX_FULL <PACKAGE_NAME> <SERVER_ARGS> 2>&1"
  # STOP
fi
```

**Package and args per module:**

| Module | npm Package | npx Args (for config) | Server-Specific Deps |
|--------|-------------|----------------------|---------------------|
| 06 Playwright | `@playwright/mcp` | `["@playwright/mcp@latest", "--browser", "chrome"]` | Chrome |
| 03 Memory | `@modelcontextprotocol/server-memory` | `["-y", "@modelcontextprotocol/server-memory"]` | None |
| 04 Git | `@modelcontextprotocol/server-git` | `["-y", "@modelcontextprotocol/server-git"]` | Git |

### Phase 3 -- Config Write with Full Paths

Write to `~/.claude/settings.json` using the **fully resolved path** to npx, not the bare command name. This makes the config immune to PATH differences between shells.

```python
import json, os, subprocess

path = os.path.expanduser("~/.claude/settings.json")
try:
    with open(path) as f:
        settings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}

if "mcpServers" not in settings:
    settings["mcpServers"] = {}

# Resolve full path to npx
import shutil
npx_path = shutil.which("npx")
if not npx_path:
    # Fallback: ask the shell
    npx_path = subprocess.check_output(
        "command -v npx", shell=True, text=True
    ).strip()

settings["mcpServers"]["<SERVER_NAME>"] = {
    "command": npx_path,  # e.g., "/opt/homebrew/bin/npx"
    "args": [<SERVER_ARGS>]
}

with open(path, "w") as f:
    json.dump(settings, f, indent=2)

print(f"Config written with npx path: {npx_path}")
```

**Verification:** Read the file back and confirm the command is an absolute path, not bare `npx`.

### Phase 4 -- Post-Restart Verification

On re-entry after restart, the preflight does two things:

1. **Config check**: Is the server entry in settings.json? (existing check)
2. **Live tool check**: Are the MCP tools actually available in this session?

The live tool check is done by the module's Claude Code skill — it attempts to list MCP tools or recognizes that `mcp__playwright__*` (or `mcp__memory__*`, `mcp__git__*`) tools are available in the session.

If config exists but tools aren't available, run the **diagnostic ladder**:

```bash
# Step 1: Is the npx path in config still valid?
NPX_IN_CONFIG=$(python3 -c "
import json
d = json.load(open('$HOME/.claude/settings.json'))
print(d['mcpServers']['<NAME>']['command'])
")
if [ ! -x "$NPX_IN_CONFIG" ]; then
  echo "FAIL: npx path in config ($NPX_IN_CONFIG) is not executable"
  echo "  Node.js may have been reinstalled to a different location."
  echo "  Current npx: $(command -v npx)"
  # Offer to update config with current path
fi

# Step 2: Can we launch the server manually?
timeout 5 $NPX_IN_CONFIG <PACKAGE_ARGS> &
SERVER_PID=$!
sleep 2
if kill -0 $SERVER_PID 2>/dev/null; then
  echo "Server launches fine — Claude Code may need another restart"
  kill $SERVER_PID 2>/dev/null
else
  echo "Server fails to launch — checking stderr..."
  $NPX_IN_CONFIG <PACKAGE_ARGS> 2>&1 | head -20
fi

# Step 3 (Playwright only): Is Chrome reachable?
if [ "$(uname)" = "Darwin" ]; then
  if [ -d "/Applications/Google Chrome.app" ]; then
    echo "PASS: Chrome installed at /Applications/Google Chrome.app"
  else
    echo "FAIL: Chrome not found — install from https://www.google.com/chrome/"
  fi
else
  command -v google-chrome &>/dev/null && echo "PASS: Chrome found" || echo "FAIL: Chrome not found"
fi

# Step 4: macOS permissions (screen recording, accessibility)
if [ "$(uname)" = "Darwin" ]; then
  echo "If the server starts but browser operations fail, check:"
  echo "  System Settings > Privacy & Security > Screen Recording"
  echo "  System Settings > Privacy & Security > Accessibility"
  echo "  Grant access to your terminal app (Terminal, iTerm2, etc.)"
fi
```

The module prints exactly what's wrong and what to do. The user is never stuck with "it should work but doesn't."

## Module-Specific Changes

### Module 06 -- Playwright MCP

**Preflight additions:**
- Chrome detection: `ls "/Applications/Google Chrome.app"` (macOS), `which google-chrome` (Linux)
- If Chrome missing: print install instructions and stop
- macOS quarantine check: `xattr -l $(which npx)` for com.apple.quarantine flag

**Step 1 becomes three sub-steps:**
- 1a: `npm install -g @playwright/mcp` with output
- 1b: Smoke test with `--browser chrome` arg, 5-second timeout
- 1c: Full-path config write

**Restart instruction:**
```
Restart Claude Code, then re-run /learn-06-playwright-mcp.
On re-entry, we'll verify the server is live before continuing.
If it isn't, we'll diagnose why — you won't be left stuck.
```

**Steps 2-4:** Unchanged (browser navigation, interaction, screenshots).

**Verification gate:** Before running the five-operation check, confirm Playwright MCP tools are in the session. If not, run diagnostic ladder instead.

### Module 03 -- Memory MCP

**Preflight:** Replace naive config-exists check with four-phase pattern.
- Phase 1: node, npm, npx + PATH check
- Phase 2: `npm install -g @modelcontextprotocol/server-memory` + smoke test
- Phase 3: Full-path config write with `MEMORY_FILE_PATH` env var
- Phase 4: Post-restart check for memory tools

**Step 1:** Same three sub-steps as Module 06 (install, smoke test, config write).

### Module 04 -- Git MCP

**Preflight:** Replace naive config-exists check with four-phase pattern.
- Phase 1: node, npm, npx, git + PATH check
- Phase 2: `npm install -g @modelcontextprotocol/server-git` + smoke test
- Phase 3: Full-path config write
- Phase 4: Post-restart check for git tools

**Step 1:** Same three sub-steps.

## Build-Module Skill Update

Add an **MCP Module Variant** section to `.claude/commands/build-module.md` that activates when the new module involves an MCP server. It injects:

1. The four-phase preflight template with placeholders:
   - `<PACKAGE_NAME>`: npm package name
   - `<SERVER_NAME>`: key in mcpServers object
   - `<SERVER_ARGS>`: args array for the server
   - `<TOOL_PREFIX>`: expected MCP tool prefix (e.g., `mcp__playwright__`)
   - `<EXTRA_DEPS>`: server-specific dependencies (e.g., Chrome)
2. The smoke test template
3. The full-path config write template
4. The diagnostic ladder template
5. The restart-with-verification-contract wording

When `build-module` detects the module is MCP-related (user says so, or module name contains "mcp"), it generates the preflight using this template instead of the generic EXISTS/MISSING pattern.

## TEMPLATE.md Update

Add an MCP variant section to `modules/TEMPLATE.md` that shows the four-phase pattern as a reference. Module authors who aren't using `build-module` can copy from the template directly.

## Files Changed

| File | Change |
|------|--------|
| `modules/06-playwright-mcp.md` | Rewrite preflight and Step 1 with four-phase pattern, add diagnostic ladder |
| `modules/03-memory-mcp.md` | Replace preflight and Step 1 with four-phase pattern |
| `modules/04-git-mcp.md` | Replace preflight and Step 1 with four-phase pattern |
| `modules/TEMPLATE.md` | Add MCP module variant section |
| `.claude/commands/build-module.md` | Add MCP module variant with templates |

## Success Criteria

1. A user with no prior MCP servers can complete Module 06 and have a working Playwright MCP on re-entry
2. If any dependency is missing, the module tells them exactly what to install and how
3. If the server fails to start, the module diagnoses why and gives actionable next steps
4. The user is never stuck in a "config exists but nothing works" state
5. Modules 03 and 04 use the same pattern
6. Future MCP modules built with `build-module` get the pattern automatically
