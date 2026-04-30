# Module 02 — Atlassian MCP Server (Jira)

Estimated time: 5 minutes
Prerequisites: Module 01 (Claude Code installed and working)

Connect Claude Code to Jira via the Atlassian Rovo MCP server. When complete, you can search issues, create tickets, add comments, and transition workflows — all from inside Claude Code. No containers or local server required.

## Orientation

Print this once at the start:

```
You're connecting Claude Code to Jira using the Atlassian Rovo MCP server.
This takes about 5 minutes.

MCP (Model Context Protocol) lets Claude Code talk to external tools.
The Atlassian Rovo MCP server is cloud-hosted by Atlassian — no Podman,
Docker, or local server needed.

We'll set up:
  1. MCP server configuration
  2. OAuth authentication with your Red Hat Atlassian account
  3. Connection test

You'll need your Red Hat Atlassian credentials (your @redhat.com identity
on redhat.atlassian.net).
```

## Preflight

Check prerequisites and current state:

```bash
# Claude Code installed?
command -v claude &>/dev/null && echo "EXISTS: Claude Code" || echo "MISSING: Claude Code — run /learn-01-vertex-setup first"

# Check for existing Atlassian MCP config in user-level settings
if [ -f "$HOME/.claude/settings.json" ]; then
  python3 -c "
import json
try:
    d = json.load(open('$HOME/.claude/settings.json'))
    servers = d.get('mcpServers', {})
    if 'mcp-atlassian-prod' in servers:
        print('EXISTS: mcp-atlassian-prod in ~/.claude/settings.json')
    else:
        print('MISSING: mcp-atlassian-prod not in ~/.claude/settings.json')
except:
    print('MISSING: could not parse ~/.claude/settings.json')
" 2>/dev/null
else
  echo "MISSING: ~/.claude/settings.json does not exist"
fi

# Check for project-level .mcp.json
[ -f ".mcp.json" ] && python3 -c "
import json
d = json.load(open('.mcp.json'))
servers = d.get('mcpServers', {})
if 'mcp-atlassian-prod' in servers:
    print('EXISTS: mcp-atlassian-prod in project .mcp.json')
" 2>/dev/null || true
```

If Claude Code is MISSING, stop and tell the user:
```
Claude Code is not installed. Complete Module 01 first:
  /learn-01-vertex-setup
```

Print a summary of what was found. Skip steps where the config already exists.

## Step 1 — Configure the MCP server

Skip if `mcp-atlassian-prod` already exists in either user-level or project-level config.

Explain:
```
The Atlassian Rovo MCP server is cloud-hosted. We just need to tell Claude Code
where to find it. We'll add it to your user-level settings so it's available in
every project, not just this one.
```

Check if `~/.claude/settings.json` exists and has content:

```bash
if [ -f "$HOME/.claude/settings.json" ]; then
  echo "File exists — will merge the MCP server entry"
  cat "$HOME/.claude/settings.json"
else
  echo "File does not exist — will create it"
fi
```

If the file exists, read it and merge the `mcpServers` entry using Python:

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

settings["mcpServers"]["mcp-atlassian-prod"] = {
    "type": "http",
    "url": "https://mcp.atlassian.com/v1/mcp"
}

with open(path, "w") as f:
    json.dump(settings, f, indent=2)

print("mcp-atlassian-prod added to ~/.claude/settings.json")
PYEOF
```

Verify:
```bash
python3 -c "
import json
d = json.load(open('$HOME/.claude/settings.json'))
if 'mcp-atlassian-prod' in d.get('mcpServers', {}):
    print('PASS: mcp-atlassian-prod configured')
    url = d['mcpServers']['mcp-atlassian-prod']['url']
    print(f'  URL: {url}')
else:
    print('FAIL: mcp-atlassian-prod not found')
"
```

## Step 2 — Authenticate with Atlassian

Tell the user:

```
Now authenticate with your Red Hat Atlassian account.

IMPORTANT: Claude Code needs to be restarted to pick up the new MCP server.

1. Exit this Claude Code session (Ctrl+C or type /exit)
2. Relaunch Claude Code: claude .
3. Type: /mcp
4. Select mcp-atlassian-prod and click Authenticate
5. Sign in with your @redhat.com account in the browser
6. Grant access when prompted
7. Return to Claude Code — the MCP tools are now available
8. Re-run this module: /learn-02-atlassian-mcp

The preflight will show your auth status when you return.
```

Note: This step requires the user to restart Claude Code. The module is designed to handle this — when re-run, the preflight will detect the existing config and skip Step 1.

## Step 3 — Test the connection

After authentication, test the MCP connection:

```
Let's verify the connection works. I'll call the Atlassian MCP to check your identity.
```

Use the `atlassianUserInfo` MCP tool to get the user's account info. If the tool is available, call it directly. If it returns a valid account ID and email, the connection is working.

If the tool is not available or returns an error:
```
The MCP tools aren't available yet. This usually means:
  - You haven't authenticated yet (see Step 2)
  - The OAuth token has expired — run /mcp and re-authenticate
  - Claude Code needs a restart to pick up the MCP config
```

Report the result:
```
Connection verified:
  Account: <display name>
  Email: <email>
  Account ID: <account_id>
```

## Step 4 — (Optional) API Token for Long-Lived Sessions

Tell the user:

```
OAuth tokens expire after a few hours. For long-running sessions or automation,
you can set up an API token instead. This is optional — OAuth works fine for
most use cases.

Skip this step if OAuth is sufficient for you.
```

If the user wants to proceed:

1. Direct them to create a token:
```
Create a Rovo MCP-scoped API token:
https://id.atlassian.com/manage-profile/security/api-tokens?autofillToken&expiryDays=max&appId=mcp&selectedScopes=all
```

2. Ask for their email and token, then tell them to encode and set it:
```
Base64 encode your credentials:

  ! echo -n "your.email@redhat.com:YOUR_API_TOKEN" | base64 | tr -d '\n'

Copy the output, then add it to your shell config:

  ! echo 'export ATLASSIAN_MCP_TOKEN="<base64 output>"' >> ~/.zshrc
  ! source ~/.zshrc
```

3. Update the MCP config to use the auth header:
```bash
python3 << 'PYEOF'
import json, os

path = os.path.expanduser("~/.claude/settings.json")
with open(path) as f:
    settings = json.load(f)

settings["mcpServers"]["mcp-atlassian-prod"] = {
    "type": "http",
    "url": "https://mcp.atlassian.com/v1/mcp",
    "headers": {
        "Authorization": "Basic ${ATLASSIAN_MCP_TOKEN}"
    }
}

with open(path, "w") as f:
    json.dump(settings, f, indent=2)

print("Auth header added to mcp-atlassian-prod config")
PYEOF
```

## Verification

Run the connection check:

```
I'll verify the Atlassian MCP connection by calling atlassianUserInfo.
```

Call the `atlassianUserInfo` MCP tool. If it returns a valid response with an account ID and email at `@redhat.com`, the module is complete.

If it fails:
```
Troubleshooting:

  401 Unauthorized:
    OAuth: Token expired — run /mcp and re-authenticate
    API token: Check ATLASSIAN_MCP_TOKEN is set: echo $ATLASSIAN_MCP_TOKEN

  403 Forbidden:
    Your account doesn't have permission for the requested project.
    Contact the project admin.

  MCP tools not available:
    1. Check ~/.claude/settings.json has mcp-atlassian-prod entry
    2. Restart Claude Code to reload MCP config
    3. Run /mcp to check server status
```

## Challenge

```
Let's use the Atlassian MCP to do something real.

Find all open Jira issues assigned to you in the RHDPOPS project.

Tell me:
  1. How many open issues are assigned to you?
  2. What is the key of the most recently created one?

Hint: you can ask me to search using JQL, or try asking in natural language.
```

## Challenge Verification

The user should provide:
1. A count of their open issues in RHDPOPS
2. The issue key of the most recent one (e.g. `RHDPOPS-1234`)

To verify, use the `searchJiraIssuesUsingJql` MCP tool with:
- JQL: `project = RHDPOPS AND assignee = currentUser() AND status != Done ORDER BY created DESC`
- Check the total count matches what the user reported
- Check the first result's key matches what the user reported

If the user has zero assigned issues, that's a valid result — acknowledge it and suggest an alternative challenge:
```
You don't have any issues assigned in RHDPOPS right now. That's fine.

Alternative challenge: Find the 5 most recently created issues in RHDPOPS
(assigned to anyone) and tell me the keys and summaries.
```

If successful, print:
```
Module 02 complete.

Claude Code is connected to Jira via the Atlassian Rovo MCP server.
You can now:
  - Search issues with JQL
  - Create and update issues
  - Add comments
  - Transition workflows
  - Look up users and projects

All from inside Claude Code, across any project.

Next module: /learn-03-memory-mcp
```
