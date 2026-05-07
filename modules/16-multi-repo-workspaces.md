# Module 16 — Multi-Repo Workspaces

Estimated time: 15 minutes
Prerequisites: Module 01 (Claude Code installed and working)

Configure Claude Code to work across multiple repositories in a single workspace, with shared and project-specific instructions.

## Orientation

Print this once at the start:

```
You're learning multi-repo workspace configuration.
This takes about 15 minutes.

We'll cover:
  1. Workspace vs project CLAUDE.md hierarchy
  2. Shared instructions across repos
  3. Project-specific overrides
  4. MCP server scoping

You'll need:
  - Claude Code installed and working (Module 01)
  - At least two git repositories in a parent directory
```

## Preflight

Audit current state:

```bash
# Check 1 — Claude Code installed?
command -v claude &>/dev/null && echo "EXISTS: Claude Code" || echo "MISSING: Claude Code — run /learn-01-vertex-setup first"

# Check 2 — Current directory structure
echo "INFO: Current directory: $(pwd)"
echo "INFO: Parent directory: $(dirname $(pwd))"

# Check 3 — Sibling repos (other git repos at the same level)
PARENT=$(dirname $(pwd))
SIBLING_COUNT=$(find "$PARENT" -maxdepth 2 -name ".git" -type d 2>/dev/null | wc -l | tr -d ' ')
echo "INFO: $SIBLING_COUNT git repo(s) found under $PARENT"

# Check 4 — Workspace CLAUDE.md exists?
if [ -f "$PARENT/CLAUDE.md" ]; then
  echo "EXISTS: Workspace CLAUDE.md at $PARENT/CLAUDE.md"
else
  echo "MISSING: No workspace CLAUDE.md at $PARENT/CLAUDE.md"
fi

# Check 5 — Project CLAUDE.md exists?
if [ -f "CLAUDE.md" ]; then
  echo "EXISTS: Project CLAUDE.md in current repo"
else
  echo "MISSING: No project CLAUDE.md in current repo"
fi

# Check 6 — Per-project .claude/ directories
PROJECT_CLAUDE_DIRS=$(find "$PARENT" -maxdepth 2 -name ".claude" -type d 2>/dev/null | wc -l | tr -d ' ')
echo "INFO: $PROJECT_CLAUDE_DIRS project(s) have .claude/ directories"
```

Print a summary.

## Step 1 — Understanding the CLAUDE.md Hierarchy

Tell the user:
```
Claude Code loads CLAUDE.md files in a hierarchy:

  ~/repos/CLAUDE.md              <-- Workspace level
  ~/repos/project-a/CLAUDE.md    <-- Project level
  ~/repos/project-a/src/CLAUDE.md  <-- Subdirectory level

When you launch Claude Code from ~/repos/project-a/:
  1. It reads ~/repos/CLAUDE.md (workspace — shared)
  2. It reads ~/repos/project-a/CLAUDE.md (project — specific)
  3. Both are loaded into every message

The workspace CLAUDE.md sets shared conventions.
The project CLAUDE.md adds project-specific details.

Neither "overrides" the other — both are always present.
If they conflict, Claude sees both instructions and must
choose. Make them complementary, not contradictory.
```

## Step 2 — Writing a Workspace CLAUDE.md

Tell the user:
```
A workspace CLAUDE.md goes in the parent directory of your repos.
It contains instructions that apply to ALL projects:

  - Team conventions (commit style, test patterns)
  - Shared MCP servers (Memory, Git, Jira)
  - Writing rules
  - Common workflows
```

Show them the structure to use:
```
A good workspace CLAUDE.md has these sections:

  ## Workspace Overview
  What this workspace contains, which repos are active.

  ## Key Conventions
  Rules that apply everywhere: commit style, test patterns,
  no emojis, etc.

  ## MCP Servers
  Servers available across all projects, with tool prefixes
  and when to use each one.

  ## Workflow Rules
  Auto-test after edits, git workflow, deploy verification.

  ## Preferences
  User preferences that apply everywhere.
```

If no workspace CLAUDE.md exists, offer to help create one:
```
You don't have a workspace CLAUDE.md yet. Want me to help
you create a starter one at the parent directory?

I'll look at your existing project CLAUDE.md files to extract
shared patterns, then draft a workspace-level file.
```

If the user agrees, read any existing CLAUDE.md files in sibling repos and draft a workspace CLAUDE.md with common patterns extracted.

## Step 3 — Project-Specific Configuration

Tell the user:
```
Each project's CLAUDE.md should only contain what's unique to
that project:

  - Repository structure (files, directories)
  - Project-specific MCP servers
  - Build and test commands for this project
  - Project-specific agents (if any)
  - Current focus areas or active work

Don't repeat workspace-level instructions. If the workspace
CLAUDE.md says "use pytest," the project CLAUDE.md doesn't
need to say it again.
```

Show the relationship:
```
Example structure:

  ~/repos/CLAUDE.md
    "Use pytest for all Python projects"
    "Memory MCP: always check at session start"
    "No conventional-commit prefixes"

  ~/repos/api-service/CLAUDE.md
    "This is a FastAPI service"
    "Test command: pytest tests/ -v"
    "Health endpoint: /api/health"

  ~/repos/web-app/CLAUDE.md
    "This is a React app with PatternFly"
    "Test command: npm test"
    "Dev server: npm run dev on port 3000"

Claude sees both files. The workspace sets the rules,
the project fills in the details.
```

## Step 4 — MCP Server Scoping

Tell the user:
```
MCP servers can be scoped at different levels:

  ~/.claude/settings.json
    Global — available in every project, every session.
    Use for: Memory, Git, Jira, other always-on servers.

  .claude/settings.json (in a project repo)
    Project — only available when Claude is launched from
    this directory. Checked into git, shared with the team.
    Use for: project-specific MCP servers.

  .claude/settings.local.json (in a project repo)
    Project-local — same scope as project settings, but
    gitignored. Not shared with the team.
    Use for: personal hooks, local overrides, secrets.

For multi-repo workspaces, put shared servers in global
settings and project-specific servers in project settings.
```

Demonstrate by checking the user's current setup:

```bash
echo "=== MCP Server Scoping ==="
echo ""
echo "Global servers (~/.claude/settings.json):"
python3 -c "
import json, os
path = os.path.expanduser('~/.claude/settings.json')
d = json.load(open(path))
for name in d.get('mcpServers', {}):
    print(f'  {name}')
" 2>/dev/null || echo "  (none)"

echo ""
echo "Project servers (.claude/settings.json):"
if [ -f ".claude/settings.json" ]; then
  python3 -c "
import json
d = json.load(open('.claude/settings.json'))
for name in d.get('mcpServers', {}):
    print(f'  {name}')
" 2>/dev/null || echo "  (none)"
else
  echo "  (no project settings file)"
fi

echo ""
echo "Local overrides (.claude/settings.local.json):"
if [ -f ".claude/settings.local.json" ]; then
  python3 -c "
import json
d = json.load(open('.claude/settings.local.json'))
for name in d.get('mcpServers', {}):
    print(f'  {name}')
hooks = d.get('hooks', {})
for event in hooks:
    count = len(hooks[event]) if isinstance(hooks[event], list) else 0
    if count: print(f'  ({count} {event} hook(s))')
" 2>/dev/null || echo "  (none)"
else
  echo "  (no local settings file)"
fi
```

## Verification

Ask the user:
```
Let's verify understanding:

1. You have a team convention "always run tests after edits."
   Where does this instruction go — workspace or project CLAUDE.md?

2. Your API project uses a custom MCP server that only makes sense
   for that project. Where does the server config go?

3. You launch Claude Code from ~/repos/my-app/. Which CLAUDE.md
   files does Claude read?
```

Expected answers:
1. Workspace CLAUDE.md — it applies to all projects.
2. `.claude/settings.json` in the project repo (project-scoped MCP).
3. Both `~/repos/CLAUDE.md` (workspace) and `~/repos/my-app/CLAUDE.md` (project), plus any subdirectory CLAUDE.md files.

If successful, print:
```
All checks passed. You understand the multi-repo workspace model.
```

## Challenge

```
Set up (or audit) your workspace configuration:

1. Check if you have a workspace CLAUDE.md. If not, create
   a starter one with at least 3 shared conventions.
2. Check that your current project's CLAUDE.md doesn't
   duplicate workspace-level instructions.
3. List your MCP servers by scope (global vs project vs local).

Tell me:
  1. Whether you created or already had a workspace CLAUDE.md
  2. Any duplications you found (and removed)
  3. Your MCP server breakdown by scope
```

## Challenge Verification

Any reasonable audit results pass.

If successful, print:
```
Module 16 complete.

You can now configure multi-repo workspaces.
Key concepts:
  - Workspace CLAUDE.md: shared conventions, loaded for all projects
  - Project CLAUDE.md: project-specific details, complements workspace
  - Don't duplicate — workspace sets rules, project fills in details
  - MCP scoping: global (~/.claude/) vs project (.claude/) vs local (.local)

File hierarchy:
  ~/repos/CLAUDE.md                    Workspace (all projects)
  ~/repos/project/CLAUDE.md            Project (this repo)
  ~/repos/project/.claude/settings.json    Project MCP servers
  ~/repos/project/.claude/settings.local.json  Local overrides (gitignored)
  ~/.claude/settings.json              Global MCP servers

Next module: /learn-17-ci-cd-integration
```
