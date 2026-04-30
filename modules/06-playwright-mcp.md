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

# Node.js (required to run the MCP server)
command -v node &>/dev/null && echo "EXISTS: Node.js $(node --version)" || echo "MISSING: Node.js"

# npx available?
command -v npx &>/dev/null && echo "EXISTS: npx" || echo "MISSING: npx"

# Check for Playwright MCP in user settings
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
            print(f'EXISTS: Playwright MCP server \"{name}\" in ~/.claude/settings.json')
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

If Claude Code is MISSING, stop and tell the user:
```
Claude Code is not installed. Complete Module 01 first:
  /learn-01-vertex-setup
```

Print a summary of what was found. Skip steps where the config already exists.

## Step 1 — Configure the Playwright MCP server

Skip if a Playwright MCP server is already configured.

Explain:
```
The Playwright MCP server runs locally via npx. It launches a Chrome
browser that Claude can control programmatically. We'll add it to your
user-level settings so it's available across all projects.
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

Add the Playwright MCP server:

```bash
python3 << 'PYEOF'
import json, os

path = os.path.expanduser("~/.claude/settings.json")
try:
    with open(path) as f:
        settings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}

if "mcpServers" not in settings:
    settings["mcpServers"] = {}

settings["mcpServers"]["playwright"] = {
    "command": "npx",
    "args": ["@playwright/mcp@latest", "--browser", "chrome"]
}

with open(path, "w") as f:
    json.dump(settings, f, indent=2)

print("Playwright MCP server added to ~/.claude/settings.json")
PYEOF
```

Verify:
```bash
python3 -c "
import json
d = json.load(open('$HOME/.claude/settings.json'))
if 'playwright' in d.get('mcpServers', {}):
    cfg = d['mcpServers']['playwright']
    print('PASS: Playwright MCP server configured')
    print(f'  Command: {cfg[\"command\"]} {\" \".join(cfg[\"args\"])}')
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

The preflight will detect the config and skip Step 1 on re-entry.
```

Note: If the user needed to restart, the module resumes from Step 2 when re-run.

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
