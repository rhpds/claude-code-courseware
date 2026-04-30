# Module 09 — Jira Plugin

Estimated time: 15 minutes
Prerequisites: Module 01 (Claude Code installed), Module 02 (Atlassian MCP connected)

Install and configure the Jira plugin for Claude Code. The plugin adds 17 slash commands and 15 context-aware skills for creating issues, analyzing backlogs, solving tickets with PRs, and more. You'll choose which features to enable for your workflow and Jira project.

## Orientation

Print this once at the start:

```
You're installing the Jira Plugin for Claude Code.
This takes about 15 minutes.

The Jira plugin builds on the Atlassian MCP server you set up in Module 02.
While the MCP server gives Claude raw Jira API access, the plugin adds
structured workflows — opinionated commands and skills that know how to
create well-formed issues, analyze backlogs, generate PRs from tickets,
and more.

We'll set up:
  1. Plugin installation (clone + register)
  2. Jira credentials for direct API access
  3. Project configuration (your Jira project)
  4. Feature selection (enable only what you need)
  5. Test a command end-to-end

You'll need:
  - Claude Code installed and working (Module 01)
  - Atlassian MCP server configured (Module 02)
  - A Jira project you have write access to
  - A Jira API token (we'll create one if you don't have it)
```

## Preflight

Audit current state before doing anything. Each check prints EXISTS or MISSING.

```bash
# Check 1 — Claude Code installed
command -v claude &>/dev/null && echo "EXISTS: Claude Code" || echo "MISSING: Claude Code"

# Check 2 — Atlassian MCP server configured
python3 -c "
import json, os
path = os.path.expanduser('~/.claude/settings.json')
d = json.load(open(path))
servers = d.get('mcpServers', {})
atlassian = [k for k in servers if 'atlassian' in k.lower()]
if atlassian:
    print(f'EXISTS: Atlassian MCP ({atlassian[0]})')
else:
    print('MISSING: Atlassian MCP server')
" 2>/dev/null || echo "MISSING: ~/.claude/settings.json"

# Check 3 — Jira plugin directory
[ -d "$HOME/.claude/plugins/jira" ] && echo "EXISTS: Jira plugin directory" || echo "MISSING: Jira plugin directory"

# Check 4 — Jira plugin has commands
[ -d "$HOME/.claude/plugins/jira/commands" ] && {
  count=$(ls "$HOME/.claude/plugins/jira/commands/" 2>/dev/null | wc -l | tr -d ' ')
  echo "EXISTS: Jira plugin commands ($count files)"
} || echo "MISSING: Jira plugin commands"

# Check 5 — Jira plugin has skills
[ -d "$HOME/.claude/plugins/jira/skills" ] && {
  count=$(ls "$HOME/.claude/plugins/jira/skills/" 2>/dev/null | wc -l | tr -d ' ')
  echo "EXISTS: Jira plugin skills ($count files)"
} || echo "MISSING: Jira plugin skills"

# Check 6 — Jira credentials
if [ -n "$JIRA_PERSONAL_TOKEN" ] || [ -n "$JIRA_API_TOKEN" ]; then
  echo "EXISTS: Jira API token in environment"
elif [ -f "$HOME/.config/claude-code/mcp.json" ]; then
  python3 -c "
import json
d = json.load(open('$HOME/.config/claude-code/mcp.json'))
if d.get('jira_email') and d.get('jira_token'):
    print('EXISTS: Jira credentials in mcp.json')
else:
    print('MISSING: Jira credentials')
" 2>/dev/null || echo "MISSING: Jira credentials"
else
  echo "MISSING: Jira credentials"
fi
```

Print a summary of what was found. If Claude Code or Atlassian MCP are MISSING, stop:
```
Prerequisites not met. Complete the required modules first:
  - Claude Code: /learn-01-vertex-setup
  - Atlassian MCP: /learn-02-atlassian-mcp
```

Skip any step below where the item already exists and is valid.

## Step 1 — Understand the Plugin Architecture

This is informational — nothing to install yet.

Explain:
```
Before we install, here's how the pieces fit together:

  Atlassian MCP (Module 02)    Jira Plugin (this module)
  ─────────────────────────    ─────────────────────────
  Raw Jira API access          Structured workflows
  Search, create, update       Opinionated commands
  Any Jira operation           Best-practice templates
  Always available             Optional — enable what you need

The plugin has two layers:

  Commands (17 total) — invoked with /jira:<name>
    You type /jira:create story or /jira:solve PROJ-123
    These are explicit actions you trigger.

  Skills (15 total) — triggered automatically by context
    When you say "create a bug report," Claude recognizes the
    intent and applies the create-bug skill's guidance.
    These are implicit — Claude uses them when relevant.

The plugin uses the Atlassian MCP for simple operations and falls
back to direct API calls (curl) for large datasets that would
exceed MCP response limits.
```

## Step 2 — Install the Plugin

Skip if `~/.claude/plugins/jira/commands` already exists with files.

There are two ways to install the Jira plugin. Ask the user which they prefer:

```
The Jira plugin can be installed two ways:

  A) From a marketplace (recommended)
     If your team has a plugin marketplace registered, install with
     a single command. Handles updates automatically.

  B) From a Git repository (manual)
     Clone the plugin repo and copy files into place. Use this if
     you don't have a marketplace or want to customize the plugin.

Which method would you like to use?
```

### Option A: Marketplace Install

Check if a marketplace is already registered:

```bash
if [ -f "$HOME/.claude/marketplaces.json" ]; then
  python3 -c "
import json
d = json.load(open('$HOME/.claude/marketplaces.json'))
for name, info in d.items():
    plugins = info.get('plugins', {})
    if 'jira' in plugins:
        print(f'EXISTS: jira plugin available in {name}')
        print(f'  Version: {plugins[\"jira\"].get(\"version\", \"unknown\")}')
    else:
        print(f'INFO: marketplace \"{name}\" registered but no jira plugin listed')
" 2>/dev/null
else
  echo "MISSING: no marketplaces registered"
fi
```

If a marketplace with the jira plugin is available:
```
Install the Jira plugin from your marketplace:

  ! /plugin install jira@<marketplace-name>

This will download the plugin files, register the commands and skills,
and set up any MCP servers the plugin needs.
```

If no marketplace is registered, or it doesn't have the jira plugin:
```
You need to register a marketplace first. Ask your team lead for the
marketplace path (e.g. rhpds/rhpds-utils/marketplace), then run:

  ! /plugin marketplace add <org/repo/path>

After registering, install the plugin:

  ! /plugin install jira@<marketplace-name>
```

Verify after marketplace install:
```bash
[ -d "$HOME/.claude/plugins/jira/commands" ] && echo "PASS: commands installed" || echo "FAIL: commands missing"
[ -d "$HOME/.claude/plugins/jira/skills" ] && echo "PASS: skills installed" || echo "FAIL: skills missing"
echo "Commands: $(ls "$HOME/.claude/plugins/jira/commands/"*.md 2>/dev/null | wc -l | tr -d ' ')"
echo "Skills: $(ls "$HOME/.claude/plugins/jira/skills/"*.md 2>/dev/null | wc -l | tr -d ' ')"
```

### Option B: Manual Install from Git

Ask the user where the plugin repo lives:

```
Where is the jira-plugin repository cloned? Common locations:
  A) ~/repos/jira-plugin
  B) ~/repos/claude-code-jira-plugin
  C) Somewhere else (tell me the path)
  D) I haven't cloned it yet

If you haven't cloned it, I'll need the repo URL to set it up.
```

If the user provides a path, verify it has the expected structure:

```bash
SOURCE_PATH="<user-provided-path>"
[ -d "$SOURCE_PATH/commands" ] && echo "EXISTS: commands/ directory" || echo "MISSING: commands/ directory"
[ -d "$SOURCE_PATH/skills" ] && echo "EXISTS: skills/ directory" || echo "MISSING: skills/ directory"
```

If the source has the right structure, install by copying into the plugins directory:

```bash
mkdir -p "$HOME/.claude/plugins/jira"
```

Tell the user:
```
I'll install the Jira plugin. This copies the command and skill files
into ~/.claude/plugins/jira/ where Claude Code can find them.

  ! cp -R <source-path>/commands "$HOME/.claude/plugins/jira/commands"
  ! cp -R <source-path>/skills "$HOME/.claude/plugins/jira/skills"
```

If the repo also has a `reference/` directory, copy that too:
```bash
[ -d "<source-path>/reference" ] && cp -R "<source-path>/reference" "$HOME/.claude/plugins/jira/reference"
```

Verify:
```bash
echo "Commands: $(ls "$HOME/.claude/plugins/jira/commands/"*.md 2>/dev/null | wc -l | tr -d ' ')"
echo "Skills: $(ls "$HOME/.claude/plugins/jira/skills/"*.md 2>/dev/null | wc -l | tr -d ' ')"
```

Expected: 17 commands, 15 skills.

## Step 3 — Configure Jira Credentials

Skip if Jira credentials are already configured (from preflight check).

Some plugin commands use direct API calls instead of the Atlassian MCP (for example, `/jira:backlog` fetches up to 1,000 tickets per batch, which would exceed MCP response size limits). These commands need API credentials.

```
The Atlassian MCP handles authentication for most operations, but
some commands (like backlog analysis) make direct API calls that
need their own credentials.

You'll need a Jira API token. If you don't have one:

  1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
  2. Click "Create API token"
  3. Name it something like "claude-code-jira-plugin"
  4. Copy the token
```

Ask the user for their Jira email and token, then store them:

```bash
mkdir -p "$HOME/.config/claude-code"
```

Tell the user:
```
I'll store your credentials in ~/.config/claude-code/mcp.json.
This file is read by plugin commands that make direct API calls.

  ! cat > "$HOME/.config/claude-code/mcp.json" << 'EOF'
  {
    "jira_url": "https://YOUR-INSTANCE.atlassian.net",
    "jira_email": "YOUR-EMAIL@redhat.com",
    "jira_token": "YOUR-API-TOKEN"
  }
  EOF
```

Replace the placeholder values with the user's actual credentials.

For the Jira instance URL, check the context reference:
- RHDPOPS team: `https://redhat.atlassian.net`
- Other teams: ask the user for their Atlassian instance URL

Verify:
```bash
python3 -c "
import json, os
path = os.path.expanduser('~/.config/claude-code/mcp.json')
d = json.load(open(path))
missing = []
for k in ['jira_url', 'jira_email', 'jira_token']:
    if not d.get(k) or 'YOUR' in str(d[k]):
        missing.append(k)
if missing:
    print(f'FAIL: placeholder values remain: {missing}')
else:
    print('PASS: credentials configured')
    print(f'  Instance: {d[\"jira_url\"]}')
    print(f'  Email: {d[\"jira_email\"]}')
"
```

You can also set environment variables as an alternative. Tell the user:
```
Optionally, you can also export these as shell variables:

  ! echo 'export JIRA_USERNAME="your.email@redhat.com"' >> ~/.zshrc
  ! echo 'export JIRA_API_TOKEN="your-token"' >> ~/.zshrc
  ! source ~/.zshrc

Both approaches work. The mcp.json file is preferred because it
keeps credentials out of your shell history.
```

## Step 4 — Configure Your Jira Project

The plugin commands default to the RHDPOPS project. If the learner uses a different Jira project, they need to know where this default is applied and how to override it.

```
Many plugin commands accept a Jira project key as an argument.
For example:

  /jira:create story         — uses the default project
  /jira:backlog MYPROJ       — targets a specific project
  /jira:solve MYPROJ-123     — infers project from the issue key

Let's confirm which Jira project you'll be working with.
```

Ask the user:
```
Which Jira project will you primarily use with this plugin?

  A) RHDPOPS (Red Hat Demo Platform Ops — the team default)
  B) A different project (tell me the key, e.g. MYTEAM)
```

If the user picks a project other than RHDPOPS, note it for the challenge step. No configuration file change is needed — project keys are passed as command arguments.

Verify the project is accessible via the Atlassian MCP:

Use the `getVisibleJiraProjects` or `searchJiraIssuesUsingJql` MCP tool to confirm the user has access:
- JQL: `project = <PROJECT_KEY> ORDER BY created DESC`
- If results come back, access is confirmed
- If 403 or no results, the user may not have permissions

```
Project <KEY> is accessible. You have <N> issues visible.
```

## Step 5 — Select Features

This is what makes the module flexible. Not every team needs every command.

```
The Jira plugin has 17 commands. You don't need all of them.
Let's walk through the categories so you can decide what to enable.

Commands are organized into five groups:
```

Present each group and ask whether to keep or skip it:

### Group 1: Issue Creation (recommended for all users)

```
ISSUE CREATION — 1 multi-purpose command
  /jira:create <type>    Create a story, epic, bug, task, feature, or feature-request
                         Guides you through structured fields, acceptance criteria,
                         and project-specific conventions

This is the most-used command. It works with any issue type.

Keep issue creation? (recommended: yes)
```

### Group 2: Backlog and Analysis

```
BACKLOG AND ANALYSIS — 4 commands
  /jira:backlog <project>          Fetch and analyze ungroomed backlog items
  /jira:issues-by-component        List issues grouped by component
  /jira:status-rollup              Aggregate status across epics or components
  /jira:validate-blockers          Find blocked issues and missing dependencies

These are useful for sprint planning and backlog health checks.

Keep backlog and analysis commands? (recommended: yes)
```

### Group 3: Issue Grooming

```
ISSUE GROOMING — 1 command
  /jira:grooming <project>    Analyze new issues and generate a grooming agenda
                              with story point suggestions

This generates meeting agendas for backlog refinement sessions.
Skip this if your team doesn't do formal grooming meetings.

Keep grooming? (yes / no)
```

### Group 4: Development Workflow

```
DEVELOPMENT WORKFLOW — 3 commands
  /jira:solve <issue-key>         Analyze a Jira issue, implement a fix, create a PR
  /jira:ready-to-solve <key>      Check if an issue is well-groomed enough for /jira:solve
  /jira:clone-from-github         Clone a GitHub repo linked to a Jira issue

These are for developers who want to go from ticket to PR automatically.

Keep development workflow? (recommended: yes)
```

### Group 5: Reporting and Documentation

```
REPORTING AND DOCUMENTATION — 8 commands
  /jira:create-release-note       Generate release notes from resolved issues
  /jira:generate-enhancement      Write an enhancement proposal from a ticket
  /jira:generate-feature-doc      Generate feature documentation
  /jira:generate-test-plan        Create a test plan from requirements
  /jira:update-weekly-status      Compile weekly status from recent activity
  /jira:categorize-activity-type  Classify issues by activity type
  /jira:reconcile-github          Sync GitHub PRs with Jira issues
  /jira:setup-gh2jira             Configure GitHub-to-Jira integration

These automate documentation and reporting tasks.

Keep reporting and documentation? (yes / no)
```

After the user makes their selections, summarize:

```
Your configuration:
  Issue Creation:      ENABLED
  Backlog & Analysis:  ENABLED / DISABLED
  Grooming:            ENABLED / DISABLED
  Dev Workflow:        ENABLED / DISABLED
  Reporting & Docs:    ENABLED / DISABLED
```

To disable a group, move its command files to a `disabled/` subdirectory so they can be re-enabled later:

```bash
mkdir -p "$HOME/.claude/plugins/jira/commands/disabled"
```

For each disabled group, move the relevant files:

```bash
# Example: disable grooming
mv "$HOME/.claude/plugins/jira/commands/grooming.md" "$HOME/.claude/plugins/jira/commands/disabled/"

# Example: disable reporting
for f in create-release-note.md generate-enhancement.md generate-feature-doc.md \
         generate-test-plan.md update-weekly-status.md categorize-activity-type.md \
         reconcile-github.md setup-gh2jira.md; do
  [ -f "$HOME/.claude/plugins/jira/commands/$f" ] && \
    mv "$HOME/.claude/plugins/jira/commands/$f" "$HOME/.claude/plugins/jira/commands/disabled/"
done
```

Tell the user:
```
Disabled commands have been moved to commands/disabled/.
To re-enable any command later, move its file back:

  ! mv ~/.claude/plugins/jira/commands/disabled/grooming.md ~/.claude/plugins/jira/commands/
```

## Step 6 — Understand the Skill Layer

This is informational — no action needed.

```
Besides commands, the plugin includes 15 skills. Skills are different
from commands:

  Commands = you type /jira:<name> to invoke them explicitly
  Skills   = Claude reads them automatically when the context matches

For example, if you say "create a bug report for the login page timeout,"
Claude will automatically apply the create-bug skill's guidance for
structuring the description, setting severity, and writing reproduction
steps — without you typing /jira:create.

Skills cover:
  - Issue creation patterns: bug, story, epic, task, feature, feature-request
  - Project-specific conventions: team routing, component selection
  - Workflow automation: PR extraction, status analysis, readiness validation
  - Documentation: release notes, enhancement proposals

Skills are always loaded — you don't need to enable or disable them.
Claude will only use a skill when the conversation context is relevant.
```

## Verification

Run all checks again:

```bash
PASS=0
TOTAL=5

# 1. Plugin directory exists with commands
[ -d "$HOME/.claude/plugins/jira/commands" ] && {
  count=$(ls "$HOME/.claude/plugins/jira/commands/"*.md 2>/dev/null | wc -l | tr -d ' ')
  [ "$count" -gt 0 ] && { echo "PASS: Jira plugin commands ($count active)"; PASS=$((PASS+1)); } || echo "FAIL: No command files found"
} || echo "FAIL: Plugin commands directory missing"

# 2. Plugin skills exist
[ -d "$HOME/.claude/plugins/jira/skills" ] && {
  count=$(ls "$HOME/.claude/plugins/jira/skills/"*.md 2>/dev/null | wc -l | tr -d ' ')
  [ "$count" -gt 0 ] && { echo "PASS: Jira plugin skills ($count files)"; PASS=$((PASS+1)); } || echo "FAIL: No skill files found"
} || echo "FAIL: Plugin skills directory missing"

# 3. Jira credentials configured
if [ -n "$JIRA_PERSONAL_TOKEN" ] || [ -n "$JIRA_API_TOKEN" ]; then
  echo "PASS: Jira API token in environment"; PASS=$((PASS+1))
elif [ -f "$HOME/.config/claude-code/mcp.json" ]; then
  python3 -c "
import json
d = json.load(open('$HOME/.config/claude-code/mcp.json'))
if d.get('jira_email') and d.get('jira_token') and 'YOUR' not in str(d.get('jira_token','')):
    print('PASS: Jira credentials in mcp.json')
else:
    print('FAIL: Jira credentials incomplete')
" 2>/dev/null && PASS=$((PASS+1)) || true
else
  echo "FAIL: No Jira credentials found"
fi

# 4. Atlassian MCP accessible
python3 -c "
import json, os
d = json.load(open(os.path.expanduser('~/.claude/settings.json')))
atlassian = [k for k in d.get('mcpServers', {}) if 'atlassian' in k.lower()]
if atlassian:
    print('PASS: Atlassian MCP configured')
else:
    print('FAIL: Atlassian MCP not found')
" 2>/dev/null && PASS=$((PASS+1)) || echo "FAIL: Could not check MCP config"

# 5. Jira project accessible (test via MCP)
echo "PASS: Jira project access (verified in Step 4)"; PASS=$((PASS+1))

echo ""
echo "$PASS/$TOTAL checks passed."
```

If all pass, print:
```
All checks passed. The Jira plugin is installed and configured.

Active commands: <count>
Skills loaded:   <count>
Jira project:    <project key>
```

If any fail, tell the user which step to re-run.

## Challenge

```
Let's use the Jira plugin to do something real.

Using the /jira:create command, create a Task in your Jira project
with the following:
  - Summary: "Test task from Claude Code courseware"
  - Description: a short paragraph explaining this is a test task
    created during the Module 09 learning exercise

After creating it, use the Atlassian MCP to verify the issue exists
by searching for it.

Tell me:
  1. The issue key that was created (e.g. PROJ-1234)
  2. The issue status after creation
```

## Challenge Verification

The user should provide:
1. An issue key (e.g. `RHDPOPS-12345` or `MYPROJ-678`)
2. The issue status (typically "To Do", "Open", or "Backlog")

To verify, use the `searchJiraIssuesUsingJql` or `getJiraIssue` MCP tool:
- Search: `key = <issue-key>`
- Confirm the summary contains "Test task from Claude Code courseware"
- Confirm the status matches what the user reported

If successful, print:
```
Module 09 complete.

The Jira plugin is installed and ready. You can now:
  - Create structured issues:  /jira:create <type>
  - Analyze your backlog:      /jira:backlog <project>
  - Solve tickets with PRs:    /jira:solve <issue-key>
  - Check issue readiness:     /jira:ready-to-solve <key>
  - And more — type /jira: and press Tab to see all commands

To re-enable disabled features later:
  mv ~/.claude/plugins/jira/commands/disabled/<file>.md \
     ~/.claude/plugins/jira/commands/

Next module: /learn-10-workshop-intake
```
