# Module 07 — Notion MCP

Estimated time: 15 minutes
Prerequisites: Module 01 (Claude Code installed and working)

Connect Claude Code to Notion so you can search, read, create, and update pages and databases directly from the CLI.

## Orientation

Print this once at the start:

```
You're connecting Claude Code to Notion.
This takes about 15 minutes.

We'll set up:
  1. Notion MCP server via Claude's built-in integration
  2. OAuth authentication with your Notion workspace
  3. Basic page and database operations

You'll need:
  - Claude Code installed and working (Module 01)
  - A Notion workspace you have access to
  - A web browser for OAuth
```

## Progress Tracking

On module start, write a progress marker:

```bash
mkdir -p ~/.claude/courseware-progress && date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/07.started
```

## Preflight

Audit current state before doing anything. Each check prints EXISTS or MISSING.

```bash
# Check 1 — Claude Code installed?
command -v claude &>/dev/null && echo "EXISTS: Claude Code" || echo "MISSING: Claude Code — run /learn-01-vertex-setup first"

# Check 2 — Notion MCP tools available?
# The Notion MCP is a cloud-hosted integration, not a local package.
# We check if the tools are already accessible in the current session.
if claude --print-system-prompt 2>/dev/null | grep -q "claude_ai_Notion"; then
  echo "EXISTS: Notion MCP tools detected in session"
else
  echo "INFO: Notion MCP tools not yet active — will set up in Step 1"
fi
```

Print a summary of what was found. Skip any step below where the item already exists and is valid.

If Claude Code is MISSING, stop:
```
Claude Code is not installed. Complete Module 01 first:
  /learn-01-vertex-setup
```

## Step 1 — Enable the Notion Integration

Skip if Notion MCP tools are already active.

Claude Code includes a built-in Notion integration that uses OAuth — no npm packages or local servers needed. The integration appears as `claude.ai Notion` in your MCP server list.

To enable it, you need to authenticate. Tell the user:

```
The Notion MCP server is built into Claude Code as a cloud integration.
To connect it to your workspace, we need to authenticate via OAuth.

I'll start the authentication flow now. You'll see a URL — open it
in your browser, sign in to Notion, and grant access to the workspace
you want to use.
```

Use the `mcp__claude_ai_Notion__notion-search` tool with a simple query to trigger the authentication flow. If authentication is needed, Claude Code will prompt automatically.

After authentication completes, verify:

```
Try searching for a page in your workspace. If results come back,
the connection is working.
```

## Step 2 — Search Your Workspace

Now that the connection is active, demonstrate Notion search.

Tell the user:
```
Let's try a search. Tell me a keyword or topic that exists
in your Notion workspace, and I'll search for it.
```

Use `mcp__claude_ai_Notion__notion-search` with the user's keyword. Show the results — page titles and URLs.

If the search returns results, explain:
```
The search uses semantic matching — it finds pages by content,
not just exact title matches. You can search across all pages,
databases, and connected sources.
```

## Step 3 — Read a Page

Ask the user to pick one of the search results (or provide a Notion page URL).

Use `mcp__claude_ai_Notion__notion-fetch` with the page ID or URL. Show a summary of the page content.

Explain:
```
The fetch tool returns page content in Notion-flavored Markdown.
This works for both regular pages and database entries.
You can also fetch databases to see their schema and data sources.
```

## Step 4 — Create or Update a Page

Demonstrate a write operation. Tell the user:
```
Let's create a test page to confirm write access works.
I'll create a page called "Claude Code Test" in your workspace.
You can delete it afterward.

Want me to create it as a standalone page, or under a specific
parent page? Tell me a parent page name, or say "standalone."
```

Use `mcp__claude_ai_Notion__notion-create-pages` to create a simple test page with a few lines of content.

Then use `mcp__claude_ai_Notion__notion-update-page` to add a line confirming the update worked.

Show the user the page URL so they can verify in Notion.

## Verification

Run these checks as PASS/FAIL:

```
Verify the Notion MCP connection by running each check:

1. Search — run a search query and confirm results return
2. Fetch — read a page and confirm content is returned
3. Create — confirm the test page was created successfully
4. Update — confirm the update to the test page worked
```

Use the Notion MCP tools to verify each item. Count passes.

If all pass, print:
```
All checks passed. Notion MCP is connected and working.
```

If any fail, tell the user which step to re-run. The most common issue is authentication — the OAuth token may need to be refreshed by re-running the auth flow.

## Challenge

```
Using Claude Code's Notion integration, do the following:

1. Search for a page or database in your workspace that contains
   information about a current project or team resource
2. Read that page and summarize its key points
3. Create a new page titled "Notion MCP Module Complete" with
   a brief summary of what you learned

Tell me:
  1. What page you found and its URL
  2. Your summary of the page content
  3. The URL of the new page you created
```

## Challenge Verification

Verify the user's answers by:
1. Fetching the page they found — confirm it exists and matches their summary
2. Fetching their new "Notion MCP Module Complete" page — confirm it was created

Write the completion marker:

```bash
date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/07.done
```

If successful, print:
```
Module 07 complete.

Claude Code is connected to your Notion workspace.
You can now:
  - Search pages and databases with semantic queries
  - Read page content in Markdown format
  - Create new pages (standalone or under a parent)
  - Update existing page content and properties
  - Query databases with filters and sorts
  - Add comments to pages and discussions

Common workflows:
  "Search Notion for our deployment runbook"
  "Create a meeting notes page for today"
  "Update the project status in Notion"
  "What's in the Q2 planning database?"

Next module: /learn-08-container-podman-mcp

Questions or feedback? https://github.com/rhpds/claude-code-courseware/issues
```
