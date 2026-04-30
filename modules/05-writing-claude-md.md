# Module 05 — Writing CLAUDE.md

Estimated time: 15 minutes
Prerequisites: Module 01 (Claude Code installed and working)

Learn how to write a CLAUDE.md file that shapes Claude Code's behavior in any project. When complete, you'll know how to give Claude persistent project instructions covering conventions, tool preferences, cost-saving patterns, and workflow rules.

## Orientation

Print this once at the start:

```
You're learning to write effective CLAUDE.md files.
This takes about 15 minutes.

CLAUDE.md is the single most impactful file you can add to a project.
It's read by Claude Code at the start of every session and shapes how
Claude approaches your code — what tools it uses, what patterns it
follows, what it avoids, and how it manages cost and context.

We'll cover:
  1. What CLAUDE.md is and where it goes
  2. The key sections every CLAUDE.md should have
  3. Cost-saving patterns (subagents, preferred tools, session discipline)
  4. Write a real CLAUDE.md for a project

You'll need: Claude Code installed and at least one project directory.
```

## Preflight

Audit current state before doing anything:

```bash
# Claude Code installed?
command -v claude &>/dev/null && echo "EXISTS: Claude Code" || echo "MISSING: Claude Code — run /learn-01-vertex-setup first"

# Does the user have any CLAUDE.md files already?
CLAUDE_COUNT=$(find ~/repos -maxdepth 2 -name "CLAUDE.md" 2>/dev/null | wc -l | tr -d ' ')
if [ "$CLAUDE_COUNT" -gt 0 ]; then
  echo "EXISTS: Found $CLAUDE_COUNT CLAUDE.md file(s) in ~/repos"
  find ~/repos -maxdepth 2 -name "CLAUDE.md" 2>/dev/null | head -5
else
  echo "INFO: No CLAUDE.md files found in ~/repos — that's fine, we'll create one"
fi

# Does this courseware repo have a CLAUDE.md?
[ -f "$HOME/repos/claude-code-courseware/CLAUDE.md" ] && echo "EXISTS: CLAUDE.md in claude-code-courseware" || echo "MISSING: CLAUDE.md in claude-code-courseware"

# Does the workspace-level CLAUDE.md exist?
[ -f "$HOME/repos/CLAUDE.md" ] && echo "EXISTS: Workspace CLAUDE.md at ~/repos/CLAUDE.md" || echo "INFO: No workspace CLAUDE.md at ~/repos/CLAUDE.md"

# Is the cost-saving reference repo available?
[ -d "$HOME/repos/claude-cost-saving" ] && echo "EXISTS: claude-cost-saving reference repo" || echo "INFO: claude-cost-saving repo not found (optional reference)"
```

If Claude Code is MISSING, stop and tell the user:
```
Claude Code is not installed. Complete Module 01 first:
  /learn-01-vertex-setup
```

Print a summary of what was found.

## Step 1 — Understand CLAUDE.md

No installation needed — this step is conceptual.

Explain:
```
CLAUDE.md is a Markdown file that Claude Code reads automatically at
the start of every session. It acts as persistent project instructions —
like onboarding a new developer who reads the project README before
touching any code.

Where CLAUDE.md files can live (Claude reads all of them):

  ~/repos/CLAUDE.md              Workspace-level — applies to all projects
                                 in ~/repos when Claude is launched there

  ~/repos/my-project/CLAUDE.md   Project-level — applies to this project only

  ~/repos/my-project/            Subdirectory — applies when Claude reads
    src/CLAUDE.md                files in that directory

Claude merges instructions from all levels. Workspace-level sets
shared conventions; project-level overrides or adds specifics.

Key principle: CLAUDE.md is for instructions that DON'T belong in code.
Things like "use pytest not unittest," "always run lint after edits,"
or "this project uses PatternFly 6, not 5." If it's a project fact that
a new developer would need to know, it belongs in CLAUDE.md.
```

## Step 2 — Learn the key sections

No installation needed — this step walks through the anatomy of a good CLAUDE.md.

Explain:
```
A well-structured CLAUDE.md has these sections. You don't need all of
them — start with what matters most for your project.

1. PROJECT OVERVIEW
   What the project does, in 2-3 sentences. Claude uses this to
   understand intent behind your requests.

   Example:
     ## What This Repo Does
     Interactive learning modules for the RHDP operations team,
     delivered as Claude Code skills.

2. KEY CONVENTIONS
   Coding standards, naming patterns, framework versions. Anything
   Claude should follow when writing or editing code.

   Example:
     ## Conventions
     - Use PatternFly 6 components (not 5)
     - Python: follow PEP 8, use type hints
     - No conventional-commit prefixes in commit messages
     - No emojis in any written output

3. TOOL AND MCP USAGE
   Which MCP servers are available, when to use them, and any
   priority rules.

   Example:
     ## MCP Servers
     | Server | Use For |
     |--------|---------|
     | Memory | Persist findings across sessions |
     | Git    | Read operations (status, log, diff) |
     | Jira   | Link work to tickets |

4. WORKFLOW RULES
   What Claude should do automatically after certain actions.

   Example:
     ## After ANY code change
     1. Run git status and git diff
     2. Run the project's test suite
     3. Fix failures before reporting completion

5. PREFERENCES
   Style, tone, and behavior preferences.

   Example:
     ## Preferences
     - Keep changes minimal and focused
     - Prefer editing existing files over creating new ones
     - Check Memory MCP at the start of each session
```

## Step 3 — Cost-saving patterns

No installation needed — this step covers patterns from the cost-saving reference bundle.

Skip this step if the user is already familiar with subagent delegation and model routing.

Explain:
```
Three patterns from the claude-cost-saving bundle that belong in
CLAUDE.md. These reduce token usage and keep sessions lean.

PATTERN 1: SUBAGENT DELEGATION

  Tell Claude when to spawn subagents and which model tier to use:

    ## Subagents
    Spawn subagents to isolate context or parallelize work.
    Pick the cheapest model that can do the subtask:
      Haiku  — bulk mechanical work, no judgment
      Sonnet — scoped research, code exploration
      Opus   — subtasks needing planning or tradeoffs

  Why it saves: subagent context is isolated. A 5000-line file read
  in a subagent doesn't bloat the parent session. On Opus 4.6 this
  can cut 20-50% of token usage on multi-step tasks.

PATTERN 2: PREFERRED TOOLS

  Tell Claude which tools to prefer for common operations:

    ## Preferred Tools
    - PDFs: use pdftotext, not the Read tool (Read rasterizes PDFs)
    - Large files: run wc -l, head, grep first — don't full-read
    - Web pages: use WebFetch for static, agent-browser for dynamic

  Why it saves: the Read tool on a PDF loads it as images (~1.5K
  tokens per page). pdftotext returns plain text at a fraction.

PATTERN 3: SESSION DISCIPLINE

  Tell Claude when to compact and clear:

    ## Session Discipline
    - /compact at ~50% context or after each completed task
    - /clear between unrelated pieces of work
    - /rewind when a turn went sideways

  Why it saves: compaction preserves the important context and
  drops the raw tool output. Doing it proactively avoids the
  expensive auto-compact at the context limit.
```

## Step 4 — Write a CLAUDE.md for a project

This is the hands-on step. The user will create or edit a real CLAUDE.md.

Explain:
```
Now you'll write a CLAUDE.md for one of your own projects. If you
don't have a preference, we'll use a practice file in this courseware
repo.

Pick a project you work on regularly. A good CLAUDE.md for it should
answer these questions:

  1. What does this project do? (2-3 sentences)
  2. What conventions should Claude follow? (language, framework, style)
  3. What tools or MCP servers should Claude use?
  4. What should Claude do automatically after code changes?
  5. Any preferences for how Claude communicates or works?
```

Tell the user:
```
Create a CLAUDE.md in one of your projects. Start with the sections
that matter most — you can always add more later.

If you want to practice first, create one here:

  Open a new file at ~/repos/claude-code-courseware/my-claude-md-practice.md

Write at least these three sections:
  1. A "What This Repo Does" overview
  2. A "Conventions" section with 3+ rules
  3. One cost-saving pattern (subagents, preferred tools, or session discipline)

Don't overthink it — a 20-line CLAUDE.md that covers the basics is
more valuable than a 200-line one you never finish.
```

Verify:
```bash
# Check if the user created a practice file or has an existing CLAUDE.md
if [ -f "$HOME/repos/claude-code-courseware/my-claude-md-practice.md" ]; then
  LINES=$(wc -l < "$HOME/repos/claude-code-courseware/my-claude-md-practice.md")
  echo "PASS: Practice file created ($LINES lines)"
elif [ -f "$HOME/repos/claude-code-courseware/CLAUDE.md" ]; then
  LINES=$(wc -l < "$HOME/repos/claude-code-courseware/CLAUDE.md")
  echo "PASS: CLAUDE.md exists ($LINES lines)"
else
  echo "INFO: No practice file found — you can write one during the challenge"
fi
```

## Step 5 — Examine a real CLAUDE.md

This step uses the courseware repo's own CLAUDE.md as a worked example.

Explain:
```
Let's look at the CLAUDE.md in this courseware repo as a real example.

Key things to notice:
  - It starts with what the repo does
  - It describes the repository structure
  - It explains how modules work (so Claude follows the pattern)
  - It lists key conventions
  - It's concise — under 50 lines

A good CLAUDE.md is specific to the project. Generic advice like
"write clean code" doesn't help — Claude already tries to do that.
Instead, tell Claude things it can't figure out from the code alone:
  - "Challenges use real team data from the RHDPOPS Jira project"
  - "Preflight checks use the EXISTS/MISSING pattern"
  - "No conventional-commit prefixes"

These are the kind of instructions that prevent Claude from guessing
wrong on the first try.
```

Tell the user:
```
Read the CLAUDE.md in this repo:

  cat ~/repos/claude-code-courseware/CLAUDE.md

Notice how every section answers a specific question that Claude
would otherwise have to guess about.
```

## Verification

Run all checks and report:

```bash
PASS=0
TOTAL=3

# 1. Claude Code installed
command -v claude &>/dev/null && { echo "PASS: Claude Code installed"; PASS=$((PASS+1)); } || echo "FAIL: Claude Code not installed"

# 2. Understands CLAUDE.md placement (check that at least one exists in repos)
CLAUDE_COUNT=$(find ~/repos -maxdepth 2 -name "CLAUDE.md" 2>/dev/null | wc -l | tr -d ' ')
[ "$CLAUDE_COUNT" -gt 0 ] && { echo "PASS: Found $CLAUDE_COUNT CLAUDE.md file(s) in ~/repos"; PASS=$((PASS+1)); } || echo "FAIL: No CLAUDE.md files found in ~/repos"

# 3. Practice file or evidence of hands-on work
if [ -f "$HOME/repos/claude-code-courseware/my-claude-md-practice.md" ]; then
  LINES=$(wc -l < "$HOME/repos/claude-code-courseware/my-claude-md-practice.md")
  [ "$LINES" -ge 5 ] && { echo "PASS: Practice file has content ($LINES lines)"; PASS=$((PASS+1)); } || echo "FAIL: Practice file is too short (< 5 lines)"
else
  echo "PASS: Skipped practice file (existing CLAUDE.md knowledge assumed)"
  PASS=$((PASS+1))
fi

echo ""
echo "$PASS/$TOTAL checks passed."
```

If all pass, print:
```
All checks passed. You understand how to write effective CLAUDE.md files.
```

If any fail, tell the user which step to re-run.

## Challenge

```
Write a CLAUDE.md for a real project you work on.

Pick any project in ~/repos that doesn't already have a CLAUDE.md,
or improve an existing one. Your CLAUDE.md should include:

  1. A project overview (what does it do?)
  2. At least 3 conventions Claude should follow
  3. At least one cost-saving pattern (subagent delegation,
     preferred tools, or session discipline)
  4. At least one workflow rule (what to do after code changes)

After writing it:
  1. Launch Claude Code in that project directory
  2. Ask Claude a question about the project
  3. Notice how Claude's behavior reflects your CLAUDE.md instructions

Tell me:
  - Which project you wrote the CLAUDE.md for
  - How many sections it has
  - Which cost-saving pattern you included
  - Whether Claude's behavior changed when you tested it
```

## Challenge Verification

The user should report:
1. A project name (any project is valid)
2. A section count (minimum 3-4 sections for a useful CLAUDE.md)
3. A cost-saving pattern (subagents, preferred tools, or session discipline)
4. Confirmation that they tested it (even a brief observation counts)

To verify, ask the user to share the contents of their CLAUDE.md or confirm the section count. Any reasonable CLAUDE.md with project-specific content passes.

If successful, print:
```
Module 05 complete.

You can now write CLAUDE.md files that shape Claude Code's behavior.
Key things to remember:
  - CLAUDE.md is read at session start — changes take effect next session
  - Workspace-level CLAUDE.md applies to all projects below it
  - Project-level CLAUDE.md overrides or extends workspace instructions
  - Be specific — "use pytest" beats "write good tests"
  - Include cost-saving patterns: subagent delegation, preferred tools,
    session discipline (/compact, /clear, /rewind)
  - Start small and iterate — a 20-line CLAUDE.md is better than none

Common CLAUDE.md sections:
  - Project overview
  - Repository structure
  - Conventions and style rules
  - MCP server usage
  - Workflow rules (auto-test, auto-lint)
  - Cost-saving patterns
  - Preferences

Next module: /learn-06-playwright-mcp
```
