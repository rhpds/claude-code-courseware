# Module 06 — Playwright MCP

Estimated time: 10 minutes
Prerequisites: Module 01 (Claude Code installed and working)

Use browser automation from inside Claude Code via the Playwright MCP server. When complete, Claude can navigate to pages, take screenshots, click elements, fill forms, and inspect page content — all through structured MCP tools.

## Orientation

Print this once at the start:

```
You're connecting Claude Code to a browser via the Playwright MCP server.
This takes about 10 minutes.

The Playwright MCP server gives Claude Code direct browser control.
Instead of asking you to open a URL and describe what you see, Claude
can navigate, read page content, click buttons, fill forms, and take
screenshots on its own.

We'll set up:
  1. Playwright MCP server configuration
  2. Page navigation and snapshots
  3. Interacting with page elements
  4. Taking screenshots

Use cases:
  - Visual testing — verify a deployed app looks right
  - Form filling — automate repetitive web tasks
  - Page inspection — read structured page content for analysis
  - Screenshot capture — document UI state for reviews
```

## Preflight

Audit current state before doing anything:

```bash
# Claude Code installed?
command -v claude &>/dev/null && echo "EXISTS: Claude Code" || echo "MISSING: Claude Code — run /learn-01-vertex-setup first"
```

If Claude Code is MISSING, stop and tell the user:
```
Claude Code is not installed. Complete Module 01 first:
  /learn-01-vertex-setup
```

### Phase 1 — Dependency Check

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
```

If any of Node.js, npm, or npx are MISSING, stop and tell the user what to install.

```bash
# PATH consistency — ensure Claude Code can find node on restart
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
```

If PATH consistency fails, stop and tell the user to fix their PATH before continuing. This is the most common cause of "config exists but server won't start."

```bash
# Chrome (required for Playwright with --browser chrome)
if [ "$(uname)" = "Darwin" ]; then
  if [ -d "/Applications/Google Chrome.app" ]; then
    echo "EXISTS: Chrome at /Applications/Google Chrome.app"
  else
    echo "MISSING: Chrome — install from https://www.google.com/chrome/"
  fi
else
  command -v google-chrome &>/dev/null && echo "EXISTS: Chrome ($(google-chrome --version 2>/dev/null))" || echo "MISSING: Chrome — install from https://www.google.com/chrome/"
fi
```

If Chrome is MISSING, stop and tell the user to install it before continuing.

```bash
# Check for Playwright MCP already configured in user settings
if [ -f "$HOME/.claude/settings.json" ]; then
  python3 -c "
import json
try:
    d = json.load(open('$HOME/.claude/settings.json'))
    servers = d.get('mcpServers', {})
    found = False
    for name, cfg in servers.items():
        args = ' '.join(cfg.get('args', []))
        if 'playwright' in name.lower() or 'playwright' in args.lower():
            cmd = cfg.get('command', '')
            print(f'EXISTS: Playwright MCP server \"{name}\" in ~/.claude/settings.json')
            print(f'  Command: {cmd}')
            if cmd == 'npx':
                print(f'  WARNING: Config uses bare \"npx\" — should be a full path.')
                print(f'  Step 1 will fix this.')
            found = True
            break
    if not found:
        print('MISSING: No Playwright MCP server in ~/.claude/settings.json')
except:
    print('MISSING: could not parse ~/.claude/settings.json')
" 2>/dev/null
else
  echo "MISSING: ~/.claude/settings.json does not exist"
fi

# Check for project-level Playwright MCP config
if [ -f ".mcp.json" ]; then
  python3 -c "
import json
d = json.load(open('.mcp.json'))
servers = d.get('mcpServers', {})
for name, cfg in servers.items():
    args = ' '.join(cfg.get('args', []))
    if 'playwright' in name.lower() or 'playwright' in args.lower():
        print(f'EXISTS: Playwright MCP server \"{name}\" in project .mcp.json')
        break
" 2>/dev/null || true
fi
```

Print a summary of what was found. If all Phase 1 checks pass and Playwright MCP is already configured with a full path, skip to Step 2.

## Step 1 — Install and configure the Playwright MCP server

Skip if Playwright MCP is already configured with a full path to npx (not bare `npx`). If configured with bare `npx`, this step will fix it.

### Step 1a — Install the package globally

Explain:
```
We install the Playwright MCP package globally so npx never needs to
download it at runtime. This eliminates silent download failures that
can prevent the server from starting.
```

```bash
echo "Installing @playwright/mcp globally..."
npm install -g @playwright/mcp
npm list -g @playwright/mcp --depth=0 2>/dev/null
if [ $? -ne 0 ]; then
  echo "FAIL: npm install failed"
  echo "  Try: sudo npm install -g @playwright/mcp"
  echo "  Or configure a user prefix: npm config set prefix ~/.npm-global"
  echo "  Then add ~/.npm-global/bin to your PATH"
else
  echo "PASS: @playwright/mcp installed globally"
fi
```

### Step 1b — Smoke test the server

Explain:
```
Before writing any config, we verify the server actually starts.
We'll launch it, wait a few seconds, and check if the process is alive.
```

```bash
NPX_FULL=$(command -v npx)
echo "Smoke test: launching server with $NPX_FULL..."
$NPX_FULL @playwright/mcp@latest --browser chrome &
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
  echo "    - Chrome is not installed or not found"
  echo "    - Permission error (macOS Screen Recording or Accessibility)"
  echo "    - Port conflict"
  echo "  Debug with: $NPX_FULL @playwright/mcp@latest --browser chrome 2>&1"
fi
```

If the smoke test fails, stop and help the user diagnose. Do not write config for a server that cannot start.

### Step 1c — Write config with full npx path

Explain:
```
Now we write the MCP server config to ~/.claude/settings.json using the
fully resolved path to npx. This makes the config immune to PATH
differences between your terminal and Claude Code's shell environment.
```

Check if `~/.claude/settings.json` exists:

```bash
if [ -f "$HOME/.claude/settings.json" ]; then
  echo "File exists — will merge the MCP server entry"
  cat "$HOME/.claude/settings.json"
else
  echo "File does not exist — will create it"
fi
```

Write the config:

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

# Resolve full path to npx — never use bare "npx"
npx_path = shutil.which("npx")
if not npx_path:
    npx_path = subprocess.check_output(
        "command -v npx", shell=True, text=True
    ).strip()

if not npx_path:
    print("FAIL: Cannot find npx. Install Node.js first.")
    raise SystemExit(1)

settings["mcpServers"]["playwright"] = {
    "command": npx_path,
    "args": ["@playwright/mcp@latest", "--browser", "chrome"]
}

with open(path, "w") as f:
    json.dump(settings, f, indent=2)

print(f"Playwright MCP server added to ~/.claude/settings.json")
print(f"  npx path: {npx_path}")
PYEOF
```

Verify the config was written correctly:

```bash
python3 -c "
import json, os
d = json.load(open(os.path.expanduser('~/.claude/settings.json')))
if 'playwright' in d.get('mcpServers', {}):
    cfg = d['mcpServers']['playwright']
    cmd = cfg['command']
    print('PASS: Playwright MCP server configured')
    print(f'  Command: {cmd} {\" \".join(cfg[\"args\"])}')
    if '/' in cmd:
        print(f'  PASS: Command uses full path')
    else:
        print(f'  FAIL: Command is bare \"{cmd}\" — should be a full path')
else:
    print('FAIL: playwright not found in mcpServers')
"
```

Tell the user:
```
IMPORTANT: Claude Code needs to be restarted to pick up the new MCP server.

1. Exit this Claude Code session (Ctrl+C or type /exit)
2. Relaunch Claude Code: claude .
3. Re-run this module: /learn-06-playwright-mcp

On re-entry, we'll verify the server is live before continuing.
If it isn't, we'll diagnose why — you won't be left stuck.
```

Note: If the user needed to restart, the module resumes from Step 2 when re-run.

### Post-Restart Verification

On re-entry after restart, verify the Playwright MCP tools are actually available in this session before continuing to Step 2.

Check if any `mcp__playwright__*` tools are available. If they are:
```
PASS: Playwright MCP tools are live in this session.
Continuing to Step 2.
```

If config exists but tools are NOT available, run the diagnostic ladder:

```bash
# Diagnostic Step 1: Is the npx path in config still valid?
NPX_IN_CONFIG=$(python3 -c "
import json, os
d = json.load(open(os.path.expanduser('~/.claude/settings.json')))
print(d['mcpServers']['playwright']['command'])
")
if [ -x "$NPX_IN_CONFIG" ]; then
  echo "PASS: npx path in config ($NPX_IN_CONFIG) is executable"
else
  echo "FAIL: npx path in config ($NPX_IN_CONFIG) is not executable"
  echo "  Node.js may have been reinstalled to a different location."
  echo "  Current npx: $(command -v npx)"
  echo "  Fix: re-run Step 1c to update the config path."
fi
```

```bash
# Diagnostic Step 2: Can we launch the server manually?
NPX_IN_CONFIG=$(python3 -c "
import json, os
d = json.load(open(os.path.expanduser('~/.claude/settings.json')))
print(d['mcpServers']['playwright']['command'])
")
echo "Attempting manual server launch..."
$NPX_IN_CONFIG @playwright/mcp@latest --browser chrome &
SERVER_PID=$!
sleep 3
if kill -0 $SERVER_PID 2>/dev/null; then
  echo "Server launches fine — Claude Code may need another restart."
  echo "Try: exit and run 'claude .' again."
  kill $SERVER_PID 2>/dev/null
  wait $SERVER_PID 2>/dev/null
else
  wait $SERVER_PID 2>/dev/null
  echo "FAIL: Server fails to launch. Checking stderr..."
  $NPX_IN_CONFIG @playwright/mcp@latest --browser chrome 2>&1 | head -20
fi
```

```bash
# Diagnostic Step 3: Is Chrome reachable?
if [ "$(uname)" = "Darwin" ]; then
  if [ -d "/Applications/Google Chrome.app" ]; then
    echo "PASS: Chrome installed at /Applications/Google Chrome.app"
  else
    echo "FAIL: Chrome not found — install from https://www.google.com/chrome/"
  fi
else
  command -v google-chrome &>/dev/null && echo "PASS: Chrome found" || echo "FAIL: Chrome not found — install from https://www.google.com/chrome/"
fi
```

```bash
# Diagnostic Step 4: macOS permissions
if [ "$(uname)" = "Darwin" ]; then
  echo "If the server starts but browser operations fail, check:"
  echo "  System Settings > Privacy & Security > Screen Recording"
  echo "  System Settings > Privacy & Security > Accessibility"
  echo "  Grant access to your terminal app (Terminal, iTerm2, etc.)"
fi
```

Print exactly what is wrong and what to do next. The user should never be stuck in a "config exists but nothing works" state.

## Step 2 — Navigate to a page and take a snapshot

This step uses the Playwright MCP tools directly. If the tools are not available, tell the user to restart Claude Code (see Step 1).

Explain:
```
Let's start with the most fundamental operation: opening a web page
and reading its content. A "snapshot" returns the page's accessibility
tree — a structured view of all the elements Claude can see and interact
with. This is more useful than a screenshot because Claude can reason
about the elements directly.
```

Use `browser_navigate` to open `https://www.redhat.com`:

Show the result:
```
Navigated to: https://www.redhat.com
Page title: <title from navigation result>
```

Then use `browser_snapshot` to capture the page structure:

```
The snapshot shows the page's accessibility tree — headings, links,
buttons, images, and text content. Each element has a reference that
Claude can use to interact with it (click, type, etc.).

Think of it as "what a screen reader sees" — structured, actionable,
and much richer than raw HTML.
```

Show a brief summary of what the snapshot contains (number of links, headings, key content areas).

## Step 3 — Interact with page elements

Explain:
```
Now let's interact with the page. Claude can click links, type into
search boxes, hover over elements, and fill forms — all using element
references from the snapshot.
```

Use `browser_snapshot` to get the current page state, then find the search or navigation element.

Walk through an interaction sequence:
1. Find a clickable element in the snapshot (a main navigation link or search icon)
2. Use `browser_click` on that element
3. Use `browser_snapshot` again to see the updated page

Show the result:
```
Clicked: <element description>
New page state: <brief summary of what changed>
```

If the page has a search box or text field:
1. Use `browser_type` to enter text
2. Use `browser_snapshot` to see the results

```
The pattern is always: snapshot -> find element -> act -> snapshot again.
Claude uses the accessibility tree to understand page state, just like
a screen reader user would navigate the web.

Available interaction tools:
  browser_click      — click any element
  browser_type       — type text into inputs
  browser_hover      — hover over elements (triggers menus, tooltips)
  browser_select_option — choose from dropdowns
  browser_fill_form  — fill multiple form fields at once
  browser_press_key  — press keyboard keys (Enter, Tab, Escape, etc.)
```

## Step 4 — Take screenshots

Explain:
```
Screenshots capture the visual state of the page. Use them for
documentation, visual testing, or sharing with teammates.

Snapshots (accessibility tree) are better for Claude to reason about.
Screenshots are better for humans to review.
```

Use `browser_take_screenshot` with `type` set to `png`:

```
Screenshot saved. This captures exactly what the browser shows —
useful for visual verification and documentation.
```

Then demonstrate a full-page screenshot:

Use `browser_take_screenshot` with `fullPage` set to `true`:

```
Full-page screenshot captures the entire scrollable content,
not just the visible viewport. Useful for long pages.

When to use each:
  browser_snapshot      — Claude needs to read or interact with the page
  browser_take_screenshot — you need a visual record of what the page looks like
```

Close the browser:

Use `browser_close` to clean up.

```
Always close the browser when you're done to free up resources.
```

## Verification

Open a fresh page and run through all operations:

1. `browser_navigate` to `https://example.com` — confirm navigation succeeds
2. `browser_snapshot` — confirm it returns page content
3. `browser_click` on a link — confirm the page changes
4. `browser_take_screenshot` — confirm a screenshot is captured
5. `browser_close` — confirm cleanup

Print:
```
PASS: browser_navigate — loaded https://example.com
PASS: browser_snapshot — returned page accessibility tree
PASS: browser_click — interacted with page element
PASS: browser_take_screenshot — captured screenshot
PASS: browser_close — browser cleaned up

All Playwright MCP operations verified.
```

If any fail:
```
Troubleshooting:

  Tools not available:
    Playwright MCP server may not be running. Run /mcp to check server status.
    If not listed, verify ~/.claude/settings.json and restart Claude Code.

  Browser fails to launch:
    Chrome must be installed. On macOS it's usually at:
      /Applications/Google Chrome.app
    The MCP server uses Chrome by default. Install Chrome if missing.

  Permission errors:
    macOS may prompt for screen recording or accessibility permissions.
    Grant them in System Settings > Privacy & Security.
```

## Challenge

```
Use the Playwright MCP to complete these tasks:

1. Navigate to this repository's GitHub page:
   https://github.com/rhpds/claude-code-courseware

2. Take a snapshot and tell me:
   - How many files/folders are shown in the repository root
   - What the repository description says

3. Click into the "modules" folder and take a snapshot:
   - List all the module files you can see

4. Take a screenshot of the modules folder view and save it

5. Close the browser

Tell me:
  - The repo description from GitHub
  - The list of module files
  - Where the screenshot was saved
```

## Challenge Verification

The user should report:
1. The repository description from the GitHub page
2. A list of module files found in the modules/ folder
3. A screenshot file path

To verify, use the Playwright MCP tools to independently check the GitHub page.
Compare the user's answers with what the tools return.

If the answers are reasonable (the repo may be private — accept descriptions of what they found or any access error they encountered), print:
```
Module 06 complete.

Claude Code can now automate browser interactions via Playwright MCP.
You can:
  - Navigate to any URL (browser_navigate)
  - Read page content as structured data (browser_snapshot)
  - Click, type, hover, and fill forms (browser_click, browser_type, etc.)
  - Take screenshots for documentation (browser_take_screenshot)
  - Run custom Playwright code (browser_run_code)

Common workflows:
  Visual testing  — navigate to deployed app, snapshot, verify elements
  Form automation — navigate, fill_form, submit, verify result
  Documentation   — navigate, take_screenshot, save for review
  Web scraping    — navigate, snapshot, extract structured data

Next module: /learn-07-writing-custom-skills
```
