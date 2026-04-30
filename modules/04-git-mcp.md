# Module 04 — Git MCP

Estimated time: 10 minutes
Prerequisites: Module 01 (Claude Code installed and working)

Use Git operations from inside Claude Code via the Git MCP server. When complete, Claude can check status, read history, diff branches, and manage branches — all through structured MCP tools instead of parsing shell output.

## Orientation

Print this once at the start:

```
You're connecting Claude Code to Git via the Git MCP server.
This takes about 10 minutes.

The Git MCP server gives Claude Code structured access to Git repositories.
Instead of parsing shell output from `git log` or `git diff`, Claude gets
clean, typed data it can reason about directly.

We'll set up:
  1. Git MCP server configuration
  2. Status and diff operations
  3. History and commit inspection
  4. Branch operations

Why use Git MCP instead of shell commands?
  Claude can run `git status` in a shell, but the MCP server returns
  structured data — no parsing needed, fewer errors, and it's the
  recommended approach in most CLAUDE.md configurations.
```

## Preflight

Audit current state before doing anything:

```bash
# Claude Code installed?
command -v claude &>/dev/null && echo "EXISTS: Claude Code" || echo "MISSING: Claude Code — run /learn-01-vertex-setup first"

# Git installed?
command -v git &>/dev/null && echo "EXISTS: Git $(git --version | cut -d' ' -f3)" || echo "MISSING: Git"

# Node.js (required to run the MCP server)
command -v node &>/dev/null && echo "EXISTS: Node.js $(node --version)" || echo "MISSING: Node.js"

# Inside a git repo?
git rev-parse --is-inside-work-tree &>/dev/null 2>&1 && echo "EXISTS: Inside git repo ($(basename $(git rev-parse --show-toplevel)))" || echo "MISSING: Not inside a git repository"

# Check for Git MCP in user settings
if [ -f "$HOME/.claude/settings.json" ]; then
  python3 -c "
import json
try:
    d = json.load(open('$HOME/.claude/settings.json'))
    servers = d.get('mcpServers', {})
    found = False
    for name, cfg in servers.items():
        args = ' '.join(cfg.get('args', []))
        if name == 'git' or 'server-git' in args:
            print(f'EXISTS: Git MCP server \"{name}\" in ~/.claude/settings.json')
            found = True
            break
    if not found:
        print('MISSING: No Git MCP server in ~/.claude/settings.json')
except:
    print('MISSING: could not parse ~/.claude/settings.json')
" 2>/dev/null
else
  echo "MISSING: ~/.claude/settings.json does not exist"
fi

# Check for project-level git MCP config
if [ -f ".mcp.json" ]; then
  python3 -c "
import json
d = json.load(open('.mcp.json'))
servers = d.get('mcpServers', {})
for name, cfg in servers.items():
    args = ' '.join(cfg.get('args', []))
    if name == 'git' or 'server-git' in args:
        print(f'EXISTS: Git MCP server \"{name}\" in project .mcp.json')
        break
" 2>/dev/null || true
fi
```

If Claude Code or Git is MISSING, stop and tell the user:
```
Claude Code or Git is not installed. Complete Module 01 first:
  /learn-01-vertex-setup
```

Print a summary of what was found. Skip steps where the config already exists.

## Step 1 — Configure the Git MCP server

Skip if a Git MCP server is already configured in user settings or project config.

Explain:
```
The Git MCP server runs locally via npx. It provides structured access
to any Git repository on your machine. We'll add it to your user-level
settings so it's available across all projects.
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

Add the Git MCP server:

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

settings["mcpServers"]["git"] = {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-git"]
}

with open(path, "w") as f:
    json.dump(settings, f, indent=2)

print("Git MCP server added to ~/.claude/settings.json")
PYEOF
```

Verify:
```bash
python3 -c "
import json
d = json.load(open('$HOME/.claude/settings.json'))
if 'git' in d.get('mcpServers', {}):
    cfg = d['mcpServers']['git']
    print('PASS: Git MCP server configured')
    print(f'  Command: {cfg[\"command\"]} {\" \".join(cfg[\"args\"])}')
else:
    print('FAIL: git not found in mcpServers')
"
```

Tell the user:
```
IMPORTANT: Claude Code needs to be restarted to pick up the new MCP server.

1. Exit this Claude Code session (Ctrl+C or type /exit)
2. Relaunch Claude Code: claude .
3. Re-run this module: /learn-04-git-mcp

The preflight will detect the config and skip Step 1 on re-entry.
```

Note: If the user needed to restart, the module resumes from Step 2 when re-run.

## Step 2 — Check repository status

This step uses the Git MCP tools directly. If the tools are not available, tell the user to restart Claude Code (see Step 1).

Explain:
```
Let's start with the most common operation: checking repository status.
git_status shows the current branch, staged changes, unstaged changes,
and untracked files — same as `git status` but as structured data.
```

Use the `git_status` MCP tool with `repo_path` set to the current working directory.

Show the result:
```
Repository: <repo name>
  Branch: <current branch>
  Staged: <list or "none">
  Unstaged: <list or "none">
  Untracked: <list or "none">
```

Then demonstrate the diff tools. If there are unstaged changes, use `git_diff_unstaged`. If there are staged changes, use `git_diff_staged`. If the repo is clean:
```
Your working directory is clean — no changes to diff right now.
We'll see diffs in the next step using commit history.
```

Explain:
```
Three diff tools cover different needs:
  git_diff_unstaged  — changes not yet staged (working directory vs index)
  git_diff_staged    — changes staged for commit (index vs HEAD)
  git_diff           — compare any two branches, tags, or commits
```

## Step 3 — Read commit history

Explain:
```
git_log returns recent commits with hashes, authors, dates, and messages.
This is what Claude uses to understand recent changes and follow commit
message conventions when writing new commits.
```

Use `git_log` with `repo_path` set to the current directory and `max_count` of 5.

Show the results:
```
Recent commits (last 5):
  <short hash>  <date>  <message>
  <short hash>  <date>  <message>
  ...
```

Then pick the most recent commit and use `git_show` to display its full details:

```
Let's inspect the most recent commit in detail.
```

Show the commit: author, date, message, and the diff (files changed with their modifications).

```
git_show gives you the full commit: metadata, message, and the complete diff.
This is how Claude understands what a commit actually changed — not just
what its message claims.
```

## Step 4 — Compare branches and commits

Explain:
```
git_diff compares two points in history — branches, tags, or commit hashes.
This is essential for understanding what changed between two states of
the codebase.
```

First, use `git_branch` with `branch_type` set to `local` to list available branches.

If there are multiple branches, use `git_diff` to compare the current branch to another:
```
Comparing <current branch> to <other branch>:
  <summary of files changed and line counts>
```

If there's only one branch, compare the earliest and latest commits from the log:
```
Only one branch exists. Let's compare the first and latest commits instead
to see how the repo evolved.
```

Show the diff summary (files changed, insertions, deletions).

```
git_diff is the tool to use when reviewing what a branch adds, what changed
between releases, or understanding a pull request.
```

## Step 5 — Branch operations

Explain:
```
The Git MCP also handles branch management: listing, creating, and
switching branches. Let's create a practice branch to demonstrate.
```

Use `git_create_branch` to create a branch named `learn-04-practice` from the current branch.

Verify by using `git_branch` with `branch_type` set to `local`:
```
Branches:
  * <current branch>
    learn-04-practice
```

Then clean up — tell the user:
```
The practice branch demonstrates the tool. Let's remove it:

  ! git branch -d learn-04-practice
```

Verify:
```bash
git branch --list learn-04-practice | grep -q learn-04-practice && echo "STILL EXISTS" || echo "PASS: practice branch deleted"
```

## Verification

Run all operations and report:

1. `git_status` — confirm it returns valid status for the current repo
2. `git_log` with `max_count` of 3 — confirm it returns commit history
3. `git_show` with the latest commit hash from the log — confirm it returns commit details
4. `git_branch` with `branch_type` of `local` — confirm it lists branches

Print:
```
PASS: git_status — returned status for <repo name> on branch <branch>
PASS: git_log — returned <N> commits
PASS: git_show — displayed commit <short hash>
PASS: git_branch — listed <N> local branches

All Git MCP operations verified.
```

If any fail:
```
Troubleshooting:

  Tools not available:
    Git MCP server may not be running. Run /mcp to check server status.
    If not listed, verify ~/.claude/settings.json and restart Claude Code.

  "Not a git repository":
    Make sure you launched Claude Code from inside a git repo:
      cd ~/repos/claude-code-courseware && claude .

  Permission errors:
    The Git MCP server needs read access to the repository directory.
```

## Challenge

```
Use the Git MCP to answer these questions about this courseware repository:

1. How many commits are in this repository?
   (Use git_log with a high max_count, e.g. 100)

2. Who authored the first (oldest) commit, and what was its message?

3. What files were changed in the commit that added Module 02?
   (Find it in the log by its message, then use git_show)

Tell me:
  - Total commit count
  - First commit's author and message
  - List of files changed in the Module 02 commit
```

## Challenge Verification

The user should report:
1. A commit count (use `git_log` with `max_count` 100 and count results)
2. The first commit's author and message (use `git_show` on the oldest hash)
3. Files from the Module 02 commit (find it by message, then `git_show`)

To verify, use the Git MCP tools:
- `git_log` with `max_count` 100 — count the entries
- `git_show` on the earliest commit hash — check author and message
- Search the log for a commit mentioning "Module 02" or "atlassian-mcp" and `git_show` it — list changed files

If the answers match, print:
```
Module 04 complete.

Claude Code can now use Git MCP for repository operations.
You can:
  - Check status and diffs (git_status, git_diff_unstaged, git_diff_staged)
  - Read history (git_log, git_show)
  - Compare branches and commits (git_diff)
  - Manage branches (git_branch, git_create_branch, git_checkout)
  - Stage and commit (git_add, git_commit)

When to use Git MCP vs shell commands:
  Git MCP  — read operations (status, log, diff, show, branch listing)
  Shell    — interactive operations (rebase -i, merge conflicts, push, pull)

Next module: /learn-05-writing-claude-md
```
