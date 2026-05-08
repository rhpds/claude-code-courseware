# Quick Install

Install MCP servers and plugins without taking a tutorial module.

## Status Detection

Run this silently to detect what is already installed:

```bash
echo "=== MCP SERVER STATUS ==="

# Parse settings.json for MCP servers
SETTINGS="$HOME/.claude/settings.json"
if [ -f "$SETTINGS" ]; then
  python3 -c "
import json
with open('$SETTINGS') as f:
    s = json.load(f)
servers = s.get('mcpServers', {})
for name in ['memory', 'git', 'mcp-atlassian-prod', 'playwright']:
    status = 'installed' if name in servers else 'not installed'
    print(f'MCP:{name}:{status}')
# Container: check for any podman/docker/container server
container_found = any(k for k in servers if any(w in k.lower() for w in ['podman', 'docker', 'container']))
print(f'MCP:container:{\"installed\" if container_found else \"not installed\"}')
" 2>/dev/null
else
  echo "MCP:memory:not installed"
  echo "MCP:git:not installed"
  echo "MCP:mcp-atlassian-prod:not installed"
  echo "MCP:playwright:not installed"
  echo "MCP:container:not installed"
fi

# Notion is built-in, check differently
echo "MCP:notion:check session"

echo ""
echo "=== PLUGIN STATUS ==="

# Check plugin cache directories
CACHE="$HOME/.claude/plugins/cache/claude-plugins-official"
for plugin in superpowers atlassian playwright frontend-design pyright-lsp; do
  if [ -d "$CACHE/$plugin" ]; then
    version=$(ls "$CACHE/$plugin/" 2>/dev/null | head -1)
    echo "PLUGIN:$plugin:installed:$version"
  else
    echo "PLUGIN:$plugin:not installed"
  fi
done

echo ""
echo "=== TEAM TOOLS STATUS ==="

# RHDP-Flow MCP server
SETTINGS="$HOME/.claude/settings.json"
flow_configured=false
if [ -f "$SETTINGS" ]; then
  python3 -c "
import json
with open('$SETTINGS') as f:
    s = json.load(f)
if 'rhdp-flow' in s.get('mcpServers', {}):
    print('configured')
else:
    print('not configured')
" 2>/dev/null | grep -q configured && flow_configured=true
fi
if python3 -c "import rhdp_flow_mcp" 2>/dev/null && [ "$flow_configured" = true ]; then
  echo "TEAM:rhdp-flow-mcp:installed"
elif python3 -c "import rhdp_flow_mcp" 2>/dev/null; then
  echo "TEAM:rhdp-flow-mcp:package only (not in settings.json)"
elif [ "$flow_configured" = true ]; then
  echo "TEAM:rhdp-flow-mcp:config only (package not installed)"
else
  echo "TEAM:rhdp-flow-mcp:not installed"
fi

# RHDP-Flow Skills
found=0
for skill in flow-deploy flow-qa flow-ops flow-status flow-bulk flow-report; do
  if find "$HOME/.claude/skills" "$HOME/.claude/plugins" -name "$skill.md" -path "*/skills/*" 2>/dev/null | grep -q .; then
    found=$((found + 1))
  fi
done
if [ "$found" -eq 6 ]; then
  echo "TEAM:rhdp-flow-skills:installed"
elif [ "$found" -gt 0 ]; then
  echo "TEAM:rhdp-flow-skills:partial ($found/6)"
else
  echo "TEAM:rhdp-flow-skills:not installed"
fi

# RHDP-Flow Agents
found=0
for agent in flow-csv-validator flow-deployment-auditor flow-pre-event-checklist; do
  if find "$HOME/.claude/agents" "$HOME/.claude/plugins" -name "$agent.md" -path "*/agents/*" 2>/dev/null | grep -q .; then
    found=$((found + 1))
  fi
done
if [ "$found" -eq 3 ]; then
  echo "TEAM:rhdp-flow-agents:installed"
elif [ "$found" -gt 0 ]; then
  echo "TEAM:rhdp-flow-agents:partial ($found/3)"
else
  echo "TEAM:rhdp-flow-agents:not installed"
fi
```

## Menu Display

After running the status detection, display the menu. Use the detected status to tag each item as `installed` or `not installed`. For Notion, check if any `mcp__claude_ai_Notion__*` tools are available in the current session.

Print:

```
Quick Install
=============

  --- MCP Servers ---

  [1]  Memory MCP                STATUS
  [2]  Git MCP                   STATUS
  [3]  Atlassian MCP (Jira)      STATUS
  [4]  Playwright MCP            STATUS
  [5]  Notion MCP                STATUS
  [6]  Container MCP             STATUS

  --- Plugins ---

  [7]  superpowers               STATUS
  [8]  atlassian                 STATUS
  [9]  playwright (plugin)       STATUS
  [10] frontend-design           STATUS
  [11] pyright-lsp               STATUS

  --- Team Tools ---

  [12] RHDP-Flow MCP (Python)    STATUS
  [13] RHDP-Flow Skills (6)      STATUS
  [14] RHDP-Flow Agents (3)      STATUS

Pick items to install (e.g. "2, 4" or "all MCP" or "all plugins" or "all team tools").
Add "dry-run" to preview without changes (e.g. "dry-run 2, 4"):
```

Wait for the user to pick items. Then run the install procedure for each selected item.

### Dry-Run Mode

If the user prefixes their selection with "dry-run", do NOT execute any install commands. Instead, for each selected item:

1. Run the dependency check (Phase 1) as normal -- this is read-only
2. Print what would be installed and configured, including:
   - The npm package or config entry that would be written
   - The exact settings.json changes that would be made
   - Any directories that would be created
   - Post-install steps (restart, authenticate, etc.)
3. Prefix each action with `[dry-run]` so it's clear nothing was changed

After the dry-run summary, print:
```
No changes were made. To install for real, re-run /quick-install and pick the same items without "dry-run".
```

## Install Procedures

### npm-mcp (Memory, Git, Playwright)

For items 1, 2, and 4 -- follow this four-phase pattern:

**Registry:**

| Item | Package | Server Name | Args | Env | Extra Dep |
|------|---------|-------------|------|-----|-----------|
| Memory MCP | `@modelcontextprotocol/server-memory` | `memory` | `["-y", "@modelcontextprotocol/server-memory"]` | `MEMORY_FILE_PATH: ~/.claude/memory/memory.json` | none |
| Git MCP | `@modelcontextprotocol/server-git` | `git` | `["-y", "@modelcontextprotocol/server-git"]` | none | `git` |
| Playwright MCP | `@playwright/mcp` | `playwright` | `["@playwright/mcp@latest", "--browser", "chrome"]` | none | Chrome browser |

**Phase 1 -- Dependency check:**
```bash
command -v node &>/dev/null && echo "PASS: node $(node --version)" || echo "FAIL: node not found"
command -v npm &>/dev/null && echo "PASS: npm $(npm --version)" || echo "FAIL: npm not found"
command -v npx &>/dev/null && echo "PASS: npx found at $(which npx)" || echo "FAIL: npx not found"
```

For Playwright, also check Chrome:
```bash
if [ "$(uname)" = "Darwin" ]; then
  [ -d "/Applications/Google Chrome.app" ] && echo "PASS: Chrome found" || echo "FAIL: Chrome not found"
else
  command -v google-chrome &>/dev/null && echo "PASS: Chrome found" || echo "FAIL: Chrome not found"
fi
```

For Git MCP, also check git:
```bash
command -v git &>/dev/null && echo "PASS: git $(git --version | head -1)" || echo "FAIL: git not found"
```

If any FAIL, stop and tell the user what to install first.

**Phase 2 -- Package install + smoke test:**

Tell the user:
```
Installing PACKAGE_NAME...

  ! npm install -g PACKAGE_NAME
```

After install, verify:
```bash
npm list -g PACKAGE_NAME --depth=0 2>/dev/null | grep PACKAGE_NAME && echo "PASS: package installed" || echo "FAIL: package not found"
```

Smoke test -- launch the server briefly to confirm it starts:
```bash
NPX_PATH=$(which npx)
$NPX_PATH ARGS &
PID=$!
sleep 3
if kill -0 $PID 2>/dev/null; then
  echo "PASS: server starts successfully"
  kill $PID 2>/dev/null
else
  echo "FAIL: server did not stay running -- check dependencies"
fi
```

If FAIL, stop and print diagnostics.

**Phase 3 -- Config write:**

Write to `~/.claude/settings.json` using the full npx path:
```bash
python3 << 'PYEOF'
import json, os, shutil

path = os.path.expanduser("~/.claude/settings.json")
settings = json.load(open(path)) if os.path.exists(path) else {}
if "mcpServers" not in settings:
    settings["mcpServers"] = {}

npx_path = shutil.which("npx")
if not npx_path:
    print("FAIL: cannot resolve npx path")
    exit(1)

# SERVER_NAME, ARGS, and ENV are filled from the registry above
settings["mcpServers"]["SERVER_NAME"] = {
    "command": npx_path,
    "args": ARGS
}
# Add env if needed (Memory MCP)

with open(path, "w") as f:
    json.dump(settings, f, indent=2)

print(f"PASS: {SERVER_NAME} configured with npx at {npx_path}")
PYEOF
```

For Memory MCP, also create the memory directory:
```bash
mkdir -p ~/.claude/memory
```

**Phase 4 -- Restart notice:**
```
SERVER_NAME is installed and configured.

Restart Claude Code to activate:
  1. Exit this session (Ctrl+C or /exit)
  2. Relaunch Claude Code

After restart, verify by running any SERVER_NAME tool.
```

### http-mcp (Atlassian)

For item 3:

Write the HTTP config entry to `~/.claude/settings.json`:
```bash
python3 << 'PYEOF'
import json, os

path = os.path.expanduser("~/.claude/settings.json")
settings = json.load(open(path)) if os.path.exists(path) else {}
if "mcpServers" not in settings:
    settings["mcpServers"] = {}

settings["mcpServers"]["mcp-atlassian-prod"] = {
    "type": "http",
    "url": "https://mcp.atlassian.com/v1/mcp"
}

with open(path, "w") as f:
    json.dump(settings, f, indent=2)

print("PASS: mcp-atlassian-prod configured")
PYEOF
```

Then print:
```
Atlassian MCP is configured.

Restart Claude Code, then authenticate:
  1. Exit and relaunch Claude Code
  2. After restart, Claude will prompt you to authenticate via browser
  3. Sign in with your Atlassian account to complete setup
```

### built-in (Notion)

For item 5:

```
Notion MCP is built into Claude Code -- no installation needed.

To activate, use any Notion tool (e.g. search). Claude Code will
prompt you to authenticate via browser OAuth on first use.

Try it now: ask Claude to search Notion for something.
```

### variable (Container)

For item 6:

```bash
# Detect container runtime
if command -v podman &>/dev/null; then
  echo "RUNTIME: podman $(podman --version 2>/dev/null | head -1)"
elif command -v docker &>/dev/null; then
  echo "RUNTIME: docker $(docker --version 2>/dev/null | head -1)"
else
  echo "RUNTIME: none found"
fi
```

If no runtime found:
```
No container runtime detected. Install Podman or Docker first:
  - Podman: brew install podman (macOS) or dnf install podman (Fedora)
  - Docker: https://docs.docker.com/get-docker/

After installing a runtime, re-run /quick-install and select Container MCP.
```

If runtime found:
```
Container runtime detected. The container MCP ecosystem is still maturing.

For now, Claude Code can run container commands directly via shell:
  podman run, podman build, podman ps, podman logs, etc.

Run /learn-08-container-podman-mcp for the full walkthrough on
container workflows with Claude Code.
```

### plugin (superpowers, atlassian, playwright, frontend-design, pyright-lsp)

For items 7-11:

First, check if the plugin source is in a known marketplace:

```bash
# Check known marketplaces for the plugin
MARKETPLACES="$HOME/.claude/plugins/known_marketplaces.json"
if [ -f "$MARKETPLACES" ]; then
  python3 -c "
import json
with open('$MARKETPLACES') as f:
    data = json.load(f)
# Search all marketplace entries for the plugin name
for marketplace_name, marketplace_data in data.items():
    plugins = marketplace_data.get('plugins', {})
    if 'PLUGIN_NAME' in plugins:
        source = marketplace_data.get('source', 'unknown')
        print(f'FOUND:PLUGIN_NAME:{marketplace_name}:{source}')
        exit(0)
print('NOT_FOUND:PLUGIN_NAME')
" 2>/dev/null
else
  echo "NOT_FOUND:PLUGIN_NAME"
fi
```

If found in a marketplace, tell the user:
```
Installing PLUGIN_NAME from MARKETPLACE_NAME...

  ! claude plugin add github:SOURCE_REPO
```

If NOT found in a known marketplace:
```
PLUGIN_NAME is not in your configured marketplaces.

To install, run /install inside Claude Code and search for "PLUGIN_NAME".
This will let you browse available marketplaces and find the plugin.
```

After plugin install, verify:
```bash
CACHE="$HOME/.claude/plugins/cache/claude-plugins-official/PLUGIN_NAME"
if [ -d "$CACHE" ]; then
  echo "PASS: PLUGIN_NAME installed"
else
  echo "FAIL: PLUGIN_NAME not found in cache"
fi
```

### python-mcp (RHDP-Flow MCP)

For item 12:

**Phase 1 -- Dependency check:**
```bash
python3 --version 2>&1 | grep -E "3\.(1[0-9]|[2-9][0-9])" && echo "PASS: Python 3.10+" || echo "FAIL: Python 3.10+ required"
command -v pip3 &>/dev/null && echo "PASS: pip3 found" || echo "FAIL: pip3 not found"
```

If any FAIL, stop and tell the user what to install first.

**Phase 2 -- Locate source and install:**

Resolve the package source from the courseware plugin:
```bash
FLOW_MCP_PATH="$HOME/.claude/plugins/claude-code-courseware/repo/rhdp-flow-mcp"
if [ -d "$FLOW_MCP_PATH" ]; then
  echo "FOUND: $FLOW_MCP_PATH"
else
  echo "NOT_FOUND"
fi
```

If FOUND:
```
Installing rhdp-flow-mcp from courseware plugin...

  ! pip install -e $FLOW_MCP_PATH
```

If NOT_FOUND:
```
rhdp-flow-mcp source not found. The courseware plugin must be installed first.

Run /quick-install and install the courseware plugin, or provide the path
to your rhdp-flow-mcp directory.
```

After install, verify:
```bash
python3 -c "import rhdp_flow_mcp; print('PASS: rhdp_flow_mcp importable')" 2>/dev/null || echo "FAIL: import failed"
```

**Phase 3 -- Config write:**

Ask the user for their Flow API URL. Default: `http://localhost:8000`. Accept any URL they provide.

Write to `~/.claude/settings.json`:
```bash
python3 << 'PYEOF'
import json, os

path = os.path.expanduser("~/.claude/settings.json")
settings = json.load(open(path)) if os.path.exists(path) else {}
if "mcpServers" not in settings:
    settings["mcpServers"] = {}

# FLOW_URL is the user-provided URL or the default
settings["mcpServers"]["rhdp-flow"] = {
    "type": "stdio",
    "command": "python3",
    "args": ["-m", "rhdp_flow_mcp"],
    "env": {
        "FLOW_API_URL": "FLOW_URL"
    }
}

with open(path, "w") as f:
    json.dump(settings, f, indent=2)

print("PASS: rhdp-flow MCP server configured")
PYEOF
```

**Phase 4 -- Restart notice:**
```
RHDP-Flow MCP is installed and configured.

Restart Claude Code to activate:
  1. Exit this session (Ctrl+C or /exit)
  2. Relaunch Claude Code
  3. Verify: ask Claude "check flow health" -- it should call flow_health

For the full walkthrough, run /learn-23-rhdp-flow-mcp.
```

### skills-copy (RHDP-Flow Skills)

For item 13:

**Prerequisite:** RHDP-Flow MCP should be installed first (item 12). Warn but don't block if missing.

**Phase 1 -- Locate source:**
```bash
FLOW_SKILLS_PATH="$HOME/.claude/plugins/claude-code-courseware/repo/rhdp-flow-skills/skills"
if [ -d "$FLOW_SKILLS_PATH" ]; then
  count=$(ls "$FLOW_SKILLS_PATH"/flow-*.md 2>/dev/null | wc -l | tr -d ' ')
  echo "FOUND: $FLOW_SKILLS_PATH ($count skill files)"
else
  echo "NOT_FOUND"
fi
```

If NOT_FOUND:
```
rhdp-flow-skills source not found. The courseware plugin must be installed first.
```

**Phase 2 -- Copy skills:**
```bash
mkdir -p "$HOME/.claude/skills"
cp "$FLOW_SKILLS_PATH"/flow-*.md "$HOME/.claude/skills/"
```

**Phase 3 -- Verify:**
```bash
installed=0
for skill in flow-deploy flow-qa flow-ops flow-status flow-bulk flow-report; do
  if [ -f "$HOME/.claude/skills/$skill.md" ]; then
    echo "PASS: $skill"
    installed=$((installed + 1))
  else
    echo "FAIL: $skill not found"
  fi
done
echo ""
echo "$installed/6 skills installed"
```

**Phase 4 -- Summary:**
```
RHDP-Flow skills are installed. No restart needed -- skills are active immediately.

Available skills: /flow-status, /flow-deploy, /flow-qa, /flow-ops, /flow-bulk, /flow-report

For the full walkthrough, run /learn-24-rhdp-flow-ops.
```

### agents-copy (RHDP-Flow Agents)

For item 14:

**Prerequisite:** RHDP-Flow MCP should be installed first (item 12). Warn but don't block if missing.

**Phase 1 -- Locate source:**
```bash
FLOW_AGENTS_PATH="$HOME/.claude/plugins/claude-code-courseware/repo/rhdp-flow-agents/agents"
if [ -d "$FLOW_AGENTS_PATH" ]; then
  count=$(ls "$FLOW_AGENTS_PATH"/flow-*.md 2>/dev/null | wc -l | tr -d ' ')
  echo "FOUND: $FLOW_AGENTS_PATH ($count agent files)"
else
  echo "NOT_FOUND"
fi
```

If NOT_FOUND:
```
rhdp-flow-agents source not found. The courseware plugin must be installed first.
```

**Phase 2 -- Copy agents:**
```bash
mkdir -p "$HOME/.claude/agents"
cp "$FLOW_AGENTS_PATH"/flow-*.md "$HOME/.claude/agents/"
```

**Phase 3 -- Verify:**
```bash
installed=0
for agent in flow-csv-validator flow-deployment-auditor flow-pre-event-checklist; do
  if [ -f "$HOME/.claude/agents/$agent.md" ]; then
    echo "PASS: $agent"
    installed=$((installed + 1))
  else
    echo "FAIL: $agent not found"
  fi
done
echo ""
echo "$installed/3 agents installed"
```

**Phase 4 -- Summary:**
```
RHDP-Flow agents are installed. No restart needed -- agents are active immediately.

Available agents: flow-csv-validator, flow-deployment-auditor, flow-pre-event-checklist

For the full walkthrough, run /learn-24-rhdp-flow-ops.
```

### all team tools (convenience group)

If the user selects "all team tools", install items 12, 13, and 14 in order:
1. RHDP-Flow MCP first (item 12) -- other items depend on it
2. RHDP-Flow Skills (item 13)
3. RHDP-Flow Agents (item 14)

## Post-Install Summary

After processing all selected items, print a summary:

```
Install Results
===============
  ITEM_NAME:    INSTALLED / ALREADY INSTALLED / FAILED / REQUIRES RESTART
  ...

Next steps:
  - If any MCP servers were installed: restart Claude Code to activate them
  - If any plugins were installed: they are active immediately
  - If team tools were installed: MCP requires restart, skills/agents are active immediately
  - Run /courseware for tutorial modules on any of these tools
```

## Reference

Use `.claude/commands/references/context.md` for server configuration values.
