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

Pick items to install (e.g. "2, 4" or "all MCP" or "all plugins"):
```

Wait for the user to pick items. Then run the install procedure for each selected item.

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
  - Run /courseware for tutorial modules on any of these tools
```

## Reference

Use `.claude/commands/references/context.md` for server configuration values.
