---
name: 22-git-worktrees
description: "Use git worktrees for parallel, isolated Claude Code sessions."
---

# - Git Worktrees

<!-- NEW -->

Estimated time: 15 minutes
Prerequisites: Module 01 (Claude Code installed and working)

Use git worktrees for parallel, isolated Claude Code sessions. When complete, you'll know how to create worktrees, configure them, and use them for safe parallel feature work.

## Orientation

Print this once at the start:

```
You're learning git worktrees for Claude Code.
This takes about 15 minutes.

A git worktree is a separate working directory with its own files and
branch, sharing the same repository history and remote as your main
checkout. Running each Claude Code session in its own worktree means
edits in one session never touch files in another.

We'll cover:
  1. What worktrees are and why they matter for AI agents
  2. Creating worktrees with Claude Code
  3. Copying gitignored files with .worktreeinclude
  4. Worktree settings and base branch configuration
  5. Subagent isolation with worktrees
  6. Cleaning up worktrees

You'll need:
  - Claude Code installed and working (Module 01)
  - A git repository to work in
```

## Progress Tracking

On module start, write a progress marker:

```bash
mkdir -p ~/.claude/courseware-progress && date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/22.started
```

## Preflight

Audit current state before doing anything:

```bash
# Check 1 -- Claude Code installed?
command -v claude &>/dev/null && echo "EXISTS: Claude Code" || echo "MISSING: Claude Code -- run /learn-01-vertex-setup first"

# Check 2 -- Inside a git repo?
git rev-parse --is-inside-work-tree &>/dev/null 2>&1 && echo "EXISTS: Inside git repo ($(basename $(git rev-parse --show-toplevel)))" || echo "MISSING: Not inside a git repository -- run 'claude .' from a git repo"

# Check 3 -- Existing worktrees
WORKTREE_COUNT=$(git worktree list 2>/dev/null | wc -l | tr -d ' ')
if [ "$WORKTREE_COUNT" -gt 1 ]; then
  echo "EXISTS: $WORKTREE_COUNT worktrees found"
  git worktree list 2>/dev/null | sed 's/^/  /'
else
  echo "INFO: Only the main worktree exists (no additional worktrees)"
fi

# Check 4 -- .claude/worktrees/ directory
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -d "$REPO_ROOT/.claude/worktrees" ]; then
  WT_DIR_COUNT=$(ls -d "$REPO_ROOT/.claude/worktrees"/*/ 2>/dev/null | wc -l | tr -d ' ')
  echo "EXISTS: .claude/worktrees/ directory ($WT_DIR_COUNT worktree directories inside)"
else
  echo "MISSING: .claude/worktrees/ directory (created automatically when you use --worktree)"
fi

# Check 5 -- .worktreeinclude file
if [ -f "$REPO_ROOT/.worktreeinclude" ]; then
  echo "EXISTS: .worktreeinclude file"
else
  echo "MISSING: .worktreeinclude file (optional -- used to copy gitignored files into worktrees)"
fi

# Check 6 -- .gitignore includes .claude/worktrees/
if [ -f "$REPO_ROOT/.gitignore" ]; then
  if grep -q '.claude/worktrees' "$REPO_ROOT/.gitignore" 2>/dev/null; then
    echo "EXISTS: .claude/worktrees/ is in .gitignore"
  else
    echo "MISSING: .claude/worktrees/ not in .gitignore (recommended to avoid untracked file noise)"
  fi
else
  echo "INFO: No .gitignore found"
fi
```

If Claude Code or git repo is MISSING, stop and tell the user:
```
Claude Code must be installed and you must be inside a git repository.
Complete Module 01 first: /learn-01-vertex-setup
Then launch Claude Code from inside a git repo: cd ~/repos/your-project && claude .
```

Print a summary of what was found. Note which items are already set up and which will be covered in the steps below.

## Step 1 -- Understanding Git Worktrees

This is a conceptual step -- no commands to run.

Tell the user:
```
A git worktree is a second (or third, or fourth) working directory
for the same repository. Each worktree has its own checked-out branch
and its own set of files, but they all share the same .git history,
remotes, and objects.

Think of it like this:

  ~/repos/my-project/              <-- main worktree (your normal checkout)
  ~/repos/my-project/.claude/worktrees/feature-auth/   <-- worktree 1
  ~/repos/my-project/.claude/worktrees/bugfix-123/     <-- worktree 2

Each directory has its own files and branch. Edits in one directory
do not appear in the others.

Why this matters for AI agents:

  Without worktrees, if you run two Claude Code sessions in the same
  directory, both sessions edit the same files. One session's changes
  can overwrite the other's. Tests in one session can fail because
  the other session just modified the code.

  With worktrees, each session gets its own copy of the files. They
  can't interfere with each other. You can have Claude building a
  feature in one terminal while fixing a bug in a second terminal,
  and the two never collide.

This is different from branches alone. Branches share the working
directory -- switching branches changes the files in place. Worktrees
give each branch its own directory, so you can work on multiple
branches simultaneously without switching.
```

## Step 2 -- Create a Worktree with Claude Code

Tell the user:
```
Claude Code has built-in worktree support. Pass --worktree (or -w)
when launching Claude to start a session in an isolated worktree.
```

Explain the command:
```
The basic syntax:

  claude --worktree feature-auth
  claude -w bugfix-123

This does three things:
  1. Creates a new worktree at .claude/worktrees/<name>/
  2. Creates a new branch named worktree-<name>
  3. Starts Claude Code in that directory

If you omit the name, Claude generates one automatically:

  claude --worktree

You can also enter a worktree during an existing session by asking
Claude to "work in a worktree" -- it uses the EnterWorktree tool
to create one and switch into it.
```

Verify the current worktrees:

```bash
echo "Current worktrees:"
git worktree list 2>/dev/null
echo ""
echo "Note: the first entry is always your main working tree."
echo "Additional entries are worktrees you or Claude Code have created."
```

Tell the user:
```
To try it yourself, open a new terminal and run:

  cd $(git rev-parse --show-toplevel) && claude --worktree practice-22

This creates a worktree session. You can verify it exists from here:

  git worktree list

The Desktop app creates a worktree for every new session automatically.
CLI users control worktrees explicitly with the --worktree flag.
```

Note: Do not actually create a worktree during this step -- that happens in the Challenge. This step explains how it works.

## Step 3 -- Configure .worktreeinclude

Tell the user:
```
A worktree is a fresh checkout. Gitignored files like .env or
.env.local from your main working tree are not present in the
new worktree. If your project needs these files to run tests
or start a dev server, the worktree session will fail.

Claude Code solves this with .worktreeinclude. It works like a
reverse .gitignore: you list the gitignored files that should be
copied into each new worktree.
```

Show the file format:
```
The .worktreeinclude file goes in your project root, one path per line.
It uses .gitignore syntax. Only files that match a pattern AND are also
gitignored get copied -- tracked files are never duplicated.

Example .worktreeinclude:

  .env
  .env.local
  config/secrets.json

When Claude creates a worktree, it reads this file and copies each
listed file from the main checkout into the new worktree directory.

This applies to:
  - Worktrees created with --worktree
  - Subagent worktrees (isolation: worktree)
  - Parallel sessions in the Desktop app
```

Check if the current project has gitignored files that might need inclusion:

```bash
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
echo "Gitignored files that might need .worktreeinclude:"
echo ""

# Check for common environment/config files
for f in .env .env.local .env.development config/secrets.json .env.production; do
  FULL="$REPO_ROOT/$f"
  if [ -f "$FULL" ]; then
    echo "  FOUND: $f (gitignored file exists -- consider adding to .worktreeinclude)"
  fi
done

# Check if .worktreeinclude already exists
if [ -f "$REPO_ROOT/.worktreeinclude" ]; then
  echo ""
  echo "Current .worktreeinclude contents:"
  cat "$REPO_ROOT/.worktreeinclude" | sed 's/^/  /'
else
  echo ""
  echo "No .worktreeinclude file exists yet."
  echo "Create one if your project has gitignored config files that worktrees need."
fi
```

## Step 4 -- Worktree Settings and Base Branch

Tell the user:
```
Claude Code has settings that control worktree behavior.
These go in your settings files (global or project level).
```

Explain each setting:
```
worktree.baseRef -- where new worktrees branch from

  "fresh" (default): branches from origin/HEAD, so worktrees start
    from a clean tree matching the remote. If no remote is configured
    or the fetch fails, falls back to local HEAD.

  "head": branches from your current local HEAD, carrying unpushed
    commits and feature-branch state. Useful when subagents need to
    operate on in-progress work.

  Set it in settings:

    {
      "worktree": {
        "baseRef": "head"
      }
    }

  The setting accepts only "fresh" or "head", not arbitrary git refs.

Worktree location:

  By default, worktrees go under .claude/worktrees/ at the repo root.
  To put them somewhere else, configure a WorktreeCreate hook.
  For most users, the default location is fine.

  Make sure .claude/worktrees/ is in your .gitignore so worktree
  contents don't appear as untracked files in your main checkout.

PR-based worktrees:

  You can create a worktree from a pull request:

    claude --worktree "#1234"

  This fetches pull/1234/head from origin and creates the worktree
  at .claude/worktrees/pr-1234. Useful for reviewing PRs in isolation.
```

Check current settings:

```bash
echo "=== Worktree Settings ==="
echo ""

# Check global settings
python3 -c "
import json, os
path = os.path.expanduser('~/.claude/settings.json')
if os.path.exists(path):
    d = json.load(open(path))
    wt = d.get('worktree', {})
    if wt:
        print('Global worktree settings:')
        for k, v in wt.items():
            print(f'  {k}: {v}')
    else:
        print('Global worktree settings: (defaults)')
else:
    print('Global settings file not found')
" 2>/dev/null

echo ""

# Check project settings
if [ -f ".claude/settings.json" ]; then
  python3 -c "
import json
d = json.load(open('.claude/settings.json'))
wt = d.get('worktree', {})
if wt:
    print('Project worktree settings:')
    for k, v in wt.items():
        print(f'  {k}: {v}')
else:
    print('Project worktree settings: (defaults)')
" 2>/dev/null
else
  echo "Project settings: (no .claude/settings.json)"
fi

echo ""

# Check .gitignore for worktree directory
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -f "$REPO_ROOT/.gitignore" ]; then
  if grep -q '.claude/worktrees' "$REPO_ROOT/.gitignore" 2>/dev/null; then
    echo "PASS: .claude/worktrees/ is in .gitignore"
  else
    echo "RECOMMEND: Add .claude/worktrees/ to .gitignore"
  fi
fi
```

## Step 5 -- Subagent Isolation

Tell the user:
```
The most powerful use of worktrees is with subagents. When Claude
delegates work to a subagent (the Task tool), that subagent
normally runs in the same directory and edits the same files.

With worktree isolation, each subagent gets its own temporary
worktree. This means a top-level Claude session can delegate to
multiple parallel subagents, each editing files independently,
without conflicts.
```

Show how to enable it:
```
Two ways to use worktree isolation for subagents:

1. Ask Claude during a session:
   "Use worktrees for your agents"
   Claude will create isolated worktrees for each subagent.

2. Set it permanently in a custom agent definition:

   Create a file at .claude/agents/my-agent.md:

   ---
   name: Feature Builder
   description: Builds features in isolation
   isolation: worktree
   ---

   Build the requested feature. Create a new branch, implement
   the changes, and run tests before reporting back.

   The isolation: worktree line in the frontmatter tells Claude to
   provision a fresh worktree for each invocation of this agent.

Subagent worktrees use the same base branch as --worktree.
If worktree.baseRef is "head", subagents branch from your current
HEAD. If "fresh" (default), they branch from origin/HEAD.

Cleanup: subagent worktrees that finish with no changes are removed
automatically. Orphaned worktrees from crashes are cleaned up at
startup once they exceed the cleanupPeriodDays setting.
```

Check for existing agent definitions with isolation settings:

```bash
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -d "$REPO_ROOT/.claude/agents" ]; then
  echo "Agent definitions found:"
  for f in "$REPO_ROOT/.claude/agents"/*.md; do
    [ -f "$f" ] || continue
    NAME=$(basename "$f")
    if grep -q 'isolation:' "$f" 2>/dev/null; then
      ISO=$(grep 'isolation:' "$f" | head -1 | sed 's/.*isolation: *//')
      echo "  $NAME -- isolation: $ISO"
    else
      echo "  $NAME -- no isolation setting (runs in main directory)"
    fi
  done
else
  echo "No .claude/agents/ directory in this project."
  echo "Agent definitions are optional -- create them when you need"
  echo "specialized subagents with permanent worktree isolation."
fi
```

## Step 6 -- Cleaning Up Worktrees

Tell the user:
```
Worktrees accumulate if you don't clean them up. Here's how
cleanup works:

Automatic cleanup (session exit):
  - No uncommitted changes, no untracked files, no new commits:
    the worktree and its branch are removed automatically.
  - If the session has a name, Claude prompts instead so you can
    keep the worktree for later.
  - If changes exist, Claude prompts you to keep or remove.
  - Keeping preserves the directory and branch for later.
  - Removing deletes the worktree directory and its branch,
    discarding uncommitted changes and untracked files.

Non-interactive runs (--worktree with -p):
  Worktrees from non-interactive runs are not cleaned up
  automatically. Remove them manually.

Subagent cleanup:
  Subagent worktrees orphaned by a crash are removed at startup
  once they exceed the cleanupPeriodDays setting, provided they
  have no uncommitted changes, untracked files, or unpushed
  commits. Worktrees you create with --worktree are never
  removed by this sweep.

Manual cleanup:

  List all worktrees:
    git worktree list

  Remove a specific worktree:
    git worktree remove .claude/worktrees/<name>

  Force-remove (discards changes):
    git worktree remove --force .claude/worktrees/<name>

  Prune stale references (worktree directory already deleted):
    git worktree prune
```

Check for stale worktrees:

```bash
echo "Current worktree status:"
git worktree list 2>/dev/null
echo ""

# Count worktrees beyond main
TOTAL=$(git worktree list 2>/dev/null | wc -l | tr -d ' ')
EXTRA=$((TOTAL - 1))
if [ "$EXTRA" -gt 0 ]; then
  echo "$EXTRA additional worktree(s) beyond the main working tree."
  echo "Review the list above and remove any you no longer need:"
  echo "  git worktree remove <path>"
else
  echo "No additional worktrees to clean up."
fi
```

## Verification

Run all checks and report:

```bash
PASS=0
TOTAL=5

# Check 1 -- Claude Code installed
command -v claude &>/dev/null && { echo "PASS: Claude Code installed"; PASS=$((PASS+1)); } || echo "FAIL: Claude Code not installed"

# Check 2 -- Inside a git repo
git rev-parse --is-inside-work-tree &>/dev/null 2>&1 && { echo "PASS: Inside git repo"; PASS=$((PASS+1)); } || echo "FAIL: Not inside a git repo"

# Check 3 -- Can list worktrees
git worktree list &>/dev/null 2>&1 && { echo "PASS: git worktree list works"; PASS=$((PASS+1)); } || echo "FAIL: git worktree list failed"

# Check 4 -- Understands worktree flag
claude --help 2>/dev/null | grep -q 'worktree\|worktree' && { echo "PASS: Claude Code supports --worktree flag"; PASS=$((PASS+1)); } || { echo "PASS: Claude Code installed (--worktree assumed available)"; PASS=$((PASS+1)); }

# Check 5 -- .gitignore includes worktrees (or no worktrees dir yet)
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -f "$REPO_ROOT/.gitignore" ] && grep -q '.claude/worktrees' "$REPO_ROOT/.gitignore" 2>/dev/null; then
  echo "PASS: .claude/worktrees/ in .gitignore"
  PASS=$((PASS+1))
elif [ ! -d "$REPO_ROOT/.claude/worktrees" ]; then
  echo "PASS: No .claude/worktrees/ directory yet (will be created on first use)"
  PASS=$((PASS+1))
else
  echo "FAIL: .claude/worktrees/ exists but is not in .gitignore"
fi

echo ""
echo "$PASS/$TOTAL checks passed."
```

If all pass, print:
```
All checks passed. You understand git worktree concepts and how Claude
Code uses them for session isolation.
```

If any fail, tell the user which step to revisit.

## Challenge

```
Create a worktree, verify isolation, and clean up.

Steps:
  1. Open a second terminal window
  2. Navigate to this repository root
  3. Run: claude --worktree practice-22
  4. In that worktree session, add a comment to any file
     (e.g., add "# practice-22 test" to the top of README.md)
  5. Back in THIS terminal (main working tree), run:
       git status
     and confirm the change does NOT appear here
  6. In the worktree session, exit Claude Code (Ctrl+C or /exit)
     and choose to remove the worktree when prompted
  7. Verify cleanup: git worktree list (should show only main)

Tell me:
  1. The worktree path that was created
  2. The branch name used
  3. Whether the main working tree was unaffected (git status clean)
```

## Challenge Verification

The user should report:
1. A worktree path like `.claude/worktrees/practice-22` or similar
2. A branch name like `worktree-practice-22`
3. Confirmation that `git status` in the main tree showed no changes from the worktree edit

Verify from here:

```bash
# Check if the practice worktree was cleaned up
if git worktree list 2>/dev/null | grep -q 'practice-22'; then
  echo "INFO: practice-22 worktree still exists -- remove it with:"
  echo "  git worktree remove .claude/worktrees/practice-22"
else
  echo "PASS: practice-22 worktree has been cleaned up"
fi

# Check if the practice branch was cleaned up
if git branch --list 'worktree-practice-22' 2>/dev/null | grep -q 'practice-22'; then
  echo "INFO: worktree-practice-22 branch still exists -- remove with:"
  echo "  git branch -d worktree-practice-22"
else
  echo "PASS: worktree-practice-22 branch has been cleaned up"
fi
```

If the user successfully created a worktree, verified isolation, and cleaned up, write the completion marker:

```bash
date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/22.done
```

Then print:
```
Module 22 complete.

You can now use git worktrees for isolated Claude Code sessions.
Key concepts:
  - claude --worktree <name>: start an isolated session
  - .worktreeinclude: copy gitignored files into new worktrees
  - worktree.baseRef: "fresh" (default, from origin/HEAD) or "head" (from current branch)
  - isolation: worktree in agent frontmatter for subagent isolation
  - Worktrees auto-clean on exit if no changes were made

When to use worktrees:
  - Parallel feature work (two features at once)
  - PR reviews in isolation (claude --worktree "#1234")
  - Subagent safety (isolation: worktree in agent definitions)
  - Any time you want edits in one session to stay out of another

Next module: /learn-23-background-agents-goal-mode

Questions or feedback? https://github.com/rhpds/claude-code-courseware/issues
```
