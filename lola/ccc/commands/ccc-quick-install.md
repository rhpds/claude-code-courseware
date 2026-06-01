---
description: "Install MCP servers and plugins without taking a tutorial module."
---

# Quick Install

Install MCP servers and plugins without taking a tutorial module.

## Processing Flow

1. **Status Detection** -- detect what is already installed
2. **Menu Display** -- show menu, user picks items
3. **Execution Mode** -- user picks attended or unattended (skip for dry-run)
4. **Prerequisite Resolution** -- auto-detect and install Node.js, Python if needed
5. **Install Procedures** -- process each selected item per Batch Processing Rules
6. **Consolidated Post-Install** -- one results table, one restart notice

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

Pick items to install:
  Numbers:     "2, 4" or "1-6"
  Groups:      "all MCP" or "all plugins"
  Everything:  "all"
  Preview:     prefix with "dry-run" (e.g. "dry-run all MCP")
```

Wait for the user to pick items.

### Dry-Run Mode

If the user prefixes their selection with "dry-run", show what WOULD be installed without executing anything. Skip Execution Mode, Prerequisite Resolution, and Install Procedures. Just print the list of items that would be processed and exit.

### Execution Mode

After the user picks items (and the selection is NOT a dry-run), ask:

```
How should I run the installs?

  [U] Unattended -- runs everything automatically with zero interaction.
      This may install system packages via Homebrew (Node.js, Python,
      Podman) if they are missing. No prompts, no approvals, no stops.

  [A] Attended   -- I'll ask before each system-modifying command (default)

Pick U or A:
```

Wait for the user to respond. Default to Attended if the user just presses enter or says anything other than "U" or "unattended".

Set an internal flag for the rest of this session:

- **UNATTENDED = true**: This means ZERO interaction from this point forward until the Consolidated Post-Install summary prints. Specifically:
  - Run ALL commands as direct bash blocks (no `!` prefix). This includes `brew install`, `npm install -g`, `pip install`, and `claude plugin add`.
  - Do NOT ask "shall I continue?", "would you like me to proceed?", "ready for the next item?", or any other confirmation question.
  - Do NOT pause between items for any reason.
  - Do NOT print per-item summaries, explanations, or informational messages. Just execute and record results silently.
  - The ONLY output before the final summary should be brief progress lines like "Installing Memory MCP... done." for each item.
  - If something fails, record it and move on. Do NOT stop to explain the failure or ask what to do.
- **UNATTENDED = false** (default): Use `! command` prefix for system-modifying commands. Print informational messages for each item. Read-only checks always run directly regardless of mode.

## Prerequisite Resolution

Before starting installs, scan the selected items and resolve missing prerequisites. Only check prerequisites relevant to the selected items.

### Node.js + npm (needed for items 1, 2, 4)

If any npm-mcp items (1, 2, or 4) are selected, check Node.js:

```bash
if command -v node &>/dev/null; then
  NODE_VER=$(node --version)
  NODE_MAJOR=$(echo "$NODE_VER" | sed 's/v//' | cut -d. -f1)
  if [ "$NODE_MAJOR" -ge 18 ]; then
    echo "PREREQ_PASS: Node.js $NODE_VER"
  else
    echo "PREREQ_FAIL: Node.js $NODE_VER is too old (need 18+)"
  fi
else
  echo "PREREQ_FAIL: Node.js not found"
fi
command -v npm &>/dev/null && echo "PREREQ_PASS: npm $(npm --version)" || echo "PREREQ_FAIL: npm not found"
command -v npx &>/dev/null && echo "PREREQ_PASS: npx found" || echo "PREREQ_FAIL: npx not found"
```

If any PREREQ_FAIL for Node.js or npm:

```bash
echo "PLATFORM: $(uname -s)"
```

**On macOS (Darwin):**

If UNATTENDED = true, run directly:
```bash
brew install node
```

If UNATTENDED = false, tell the user:
```
Node.js 18+ is required for MCP servers. Install it now:

  ! brew install node
```

After the install completes, re-run the Node.js check to verify:
```bash
command -v node &>/dev/null && echo "PREREQ_PASS: Node.js $(node --version) installed" || echo "PREREQ_FAIL: Node.js install failed"
command -v npm &>/dev/null && echo "PREREQ_PASS: npm $(npm --version)" || echo "PREREQ_FAIL: npm not found after install"
command -v npx &>/dev/null && echo "PREREQ_PASS: npx found" || echo "PREREQ_FAIL: npx not found after install"
```

If still failing after install, stop and tell the user to troubleshoot their Homebrew installation.

**On Linux:**

```
Node.js 18+ is required but not installed. Install for your distribution:

  Fedora/RHEL:   sudo dnf install nodejs npm
  Ubuntu/Debian: sudo apt install nodejs npm
  Or visit:      https://nodejs.org

After installing Node.js, re-run /ccc-quick-install to continue.
```

On Linux, stop processing and exit (package managers need sudo which cannot run unattended).

### npm global packages (needed for items 1, 2, 4)

After Node.js is confirmed available, install the npm packages needed for selected items.

Build the package list based on selection:

| Item | Package |
|------|---------|
| 1 (Memory MCP) | `@modelcontextprotocol/server-memory` |
| 2 (Git MCP) | `@modelcontextprotocol/server-git` |
| 4 (Playwright MCP) | `@playwright/mcp` |

Install all selected packages in one command.

If UNATTENDED = true, run directly:
```bash
npm install -g PACKAGE_LIST
```

If UNATTENDED = false, tell the user:
```
Installing npm packages for selected MCP servers:

  ! npm install -g PACKAGE_LIST
```

Where PACKAGE_LIST is the space-separated list of packages for the selected items (e.g., `@modelcontextprotocol/server-memory @modelcontextprotocol/server-git` if items 1 and 2 are selected).

After install, verify each package:
```bash
npm list -g PACKAGE_NAME --depth=0 2>/dev/null | grep -q PACKAGE_NAME && echo "PREREQ_PASS: PACKAGE_NAME installed" || echo "PREREQ_FAIL: PACKAGE_NAME not found after install"
```

If any package fails to install, record that item as FAILED and exclude it from further processing. Continue with remaining items.

### Chrome browser (needed for item 4 only)

If item 4 (Playwright MCP) is selected, check for Chrome:

```bash
if [ "$(uname)" = "Darwin" ]; then
  [ -d "/Applications/Google Chrome.app" ] && echo "PREREQ_PASS: Chrome found" || echo "PREREQ_WARN: Chrome not found"
else
  command -v google-chrome &>/dev/null && echo "PREREQ_PASS: Chrome found" || echo "PREREQ_WARN: Chrome not found"
fi
```

If Chrome is missing, print a warning but do NOT block the install:
```
Chrome browser not detected. Playwright MCP will install and configure,
but browser automation requires Chrome. Install it when ready:
  https://www.google.com/chrome/
```

Continue with the Playwright install. Mark it with a note in the results: `INSTALLED (Chrome not detected)`.

### Git (needed for item 2 only)

If item 2 (Git MCP) is selected:
```bash
command -v git &>/dev/null && echo "PREREQ_PASS: git $(git --version | head -1)" || echo "PREREQ_FAIL: git not found"
```

If git is missing, tell the user:
```
Git is required for Git MCP. Install it:
  macOS: xcode-select --install
  Linux: sudo dnf install git (or sudo apt install git)
```

Skip item 2 and record as SKIPPED.

After all prerequisite checks pass (or auto-installs complete), proceed to Install Procedures.

## Install Procedures

### Batch Processing Rules

When processing the selected items, follow these rules:

1. **Sequential processing**: Process items in numerical order (1, 2, 3, ..., 14). This ensures dependencies are met.

2. **Skip already-installed items**: If status detection showed an item as "installed", skip it silently. Record it as `ALREADY INSTALLED` for the summary.

3. **Suppress per-item restart notices**: Do NOT print restart notices after each individual item. Collect the names of all items that require a restart.

4. **Continue on success**: After each item completes successfully, immediately proceed to the next selected item. Do NOT stop, do NOT suggest restarting, do NOT wait for user input between items.

5. **Continue on failure**: If an item fails, record it as `FAILED` and continue to the next item. Only abort the entire batch if a prerequisite failure makes ALL remaining items impossible.

6. **Track results**: Maintain a results list with one of these statuses per item:
   - `INSTALLED` -- newly installed this session
   - `ALREADY INSTALLED` -- skipped, was already present
   - `FAILED` -- attempted but failed (include reason)
   - `SKIPPED` -- not attempted (dependency missing)
   - `INFO` -- informational only (Notion, Container)

7. **Consolidated restart notice**: After ALL items are processed, print ONE restart notice listing everything that needs restart. See Consolidated Post-Install below.

8. **Execution mode**: Read-only commands (checks, verifications) always run directly. System-modifying commands respect the UNATTENDED flag:
   - UNATTENDED = true: run as direct bash blocks
   - UNATTENDED = false: present with `!` prefix for user approval

### npm-mcp (Memory, Git, Playwright)

For items 1, 2, and 4. Prerequisites and npm packages are already resolved in Prerequisite Resolution. This procedure handles config writing only.

**Registry:**

| Item | Server Name | npx Args | Env |
|------|-------------|----------|-----|
| 1 - Memory MCP | `memory` | `["-y", "@modelcontextprotocol/server-memory"]` | `MEMORY_FILE_PATH: ~/.claude/memory/memory.json` |
| 2 - Git MCP | `git` | `["-y", "@modelcontextprotocol/server-git"]` | none |
| 4 - Playwright MCP | `playwright` | `["@playwright/mcp@latest", "--browser", "chrome"]` | none |

**Step 1 -- Verify package installed:**

```bash
npm list -g PACKAGE_NAME --depth=0 2>/dev/null | grep -q PACKAGE_NAME && echo "PASS: PACKAGE_NAME installed" || echo "FAIL: PACKAGE_NAME not found"
```

If FAIL, record as `FAILED` and proceed to next item.

**Step 2 -- Config write:**

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

print(f"PASS: SERVER_NAME configured with npx at {npx_path}")
PYEOF
```

For Memory MCP, also create the memory directory and add env:
```bash
mkdir -p ~/.claude/memory
```

Add to the config: `"env": {"MEMORY_FILE_PATH": os.path.expanduser("~/.claude/memory/memory.json")}`

**Step 3 -- Record and continue:**

Record as `INSTALLED` and proceed to the next item. Do NOT print a restart notice.

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

Record as `INSTALLED (requires restart + OAuth)` and proceed.

### built-in (Notion)

For item 5:

In unattended mode, print only: `Notion MCP... built-in, no install needed.`

In attended mode, print:
```
Notion MCP is built into Claude Code -- no installation needed.
To activate, use any Notion tool (e.g. search). Claude Code will
prompt you to authenticate via browser OAuth on first use.
```

Record as `INFO: built-in` and proceed.

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

If no runtime found AND **UNATTENDED = true** AND macOS (`uname -s` = Darwin):

Auto-install Podman via Homebrew:

```bash
echo "Installing Podman via Homebrew..."
brew install podman
```

After install, re-check:

```bash
if command -v podman &>/dev/null; then
  echo "PASS: podman installed ($(podman --version 2>/dev/null | head -1))"
else
  echo "FAIL: podman install failed"
fi
```

Record as `INSTALLED` if podman is now available, or `FAILED` if not. Proceed either way.

If no runtime found AND **UNATTENDED = true** AND Linux:

Record as `SKIPPED (no container runtime, manual install required on Linux)`. Proceed.

If no runtime found AND **UNATTENDED = false** (attended mode):

```
No container runtime detected. Install Podman or Docker first:
  - Podman: brew install podman (macOS) or dnf install podman (Fedora)
  - Docker: https://docs.docker.com/get-docker/

Run /learn-08-container-podman-mcp for the full walkthrough.
```

Record as `INFO` and proceed.

If runtime found:

In unattended mode, print only: `Container MCP... runtime detected.`

In attended mode, print:
```
Container runtime detected. Claude Code can run container commands
directly via shell (podman run, podman build, etc.).

Run /learn-08-container-podman-mcp for the full walkthrough.
```

Record as `INFO` and proceed.

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

If found in a marketplace:

If UNATTENDED = true, run directly:
```bash
claude plugin add github:SOURCE_REPO
```

If UNATTENDED = false, tell the user:
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

Record as `SKIPPED: not in marketplace` and proceed.

After plugin install, verify:
```bash
CACHE="$HOME/.claude/plugins/cache/claude-plugins-official/PLUGIN_NAME"
if [ -d "$CACHE" ]; then
  echo "PASS: PLUGIN_NAME installed"
else
  echo "FAIL: PLUGIN_NAME not found in cache"
fi
```

Record as `INSTALLED` (plugins are active immediately, no restart needed) and proceed.

### Convenience Groups

These shortcuts expand to item lists:

| Shortcut | Items | Processing Order |
|----------|-------|-----------------|
| `all MCP` | 1-6 | numerical (1, 2, 3, 4, 5, 6) |
| `all plugins` | 7-11 | numerical (7, 8, 9, 10, 11) |
| `all` | 1-11 | MCP first (1-6), then plugins (7-11) |

When a group is selected, expand it to the full item list and apply Batch Processing Rules. Skip already-installed items within the group.

## Consolidated Post-Install

After ALL selected items have been processed, print the results.

### Results Table

```
Install Results
===============
  [1]  Memory MCP              RESULT
  [2]  Git MCP                 RESULT
  ...
```

Only list items that were selected. Use the result recorded during processing: `INSTALLED`, `ALREADY INSTALLED`, `FAILED: reason`, `SKIPPED: reason`, or `INFO: detail`.

### Consolidated Restart Notice

If ANY installed items require a restart (MCP servers: items 1-4, 6), print ONE restart notice:

```
The following items need a Claude Code restart to activate:

  - Memory MCP
  - Git MCP
  - Playwright MCP
  ...

Restart now:
  1. Exit this session (Ctrl+C or /exit)
  2. Relaunch Claude Code

After restart, the new MCP servers will be available.
```

If Atlassian MCP (item 3) was installed, add:
```
Note: Atlassian MCP will prompt for OAuth authentication on first use after restart.
```

If NO items require a restart (only plugins were installed, or everything was already installed):
```
All installed items are active immediately. No restart needed.
```

### Next Steps

```
Next steps:
  - Run /ccc-courseware for tutorial modules on any of these tools
  - Run /ccc-preflight to verify your full environment
```

## Reference

Use `../skills/references/context.md` for server configuration values.
