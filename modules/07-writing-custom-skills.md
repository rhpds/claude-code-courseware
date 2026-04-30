# Module 07 — Writing Custom Skills

Estimated time: 20 minutes
Prerequisites: Module 01 (Claude Code installed and working)

Create Claude Code skills — reusable, shareable instructions that run as slash commands or get triggered automatically. When complete, you'll have written, installed, and tested your own skill.

## Orientation

Print this once at the start:

```
You're learning to write Claude Code skills.
This takes about 20 minutes.

A skill is a markdown file (SKILL.md) that teaches Claude Code how to
perform a specific task. Skills can:
  - Run as slash commands (when installed in .claude/commands/)
  - Get triggered by keywords in conversation (when installed in ~/.claude/skills/)
  - Run as subagents to save context and cost (agent: true)
  - Route to cheaper models for mechanical tasks (model: sonnet/haiku)

We'll cover:
  1. Skill anatomy — SKILL.md frontmatter and body
  2. Installation locations
  3. Subagent delegation for cost savings
  4. Writing and testing your own skill

Real-world examples:
  - The courseware modules you've been using are skills
  - The team's hivemind-write and hivemind-query are skills
  - The red-hat-quick-deck presentation generator is a skill
  - The claude-cost-saving repo has 10 utility skills
```

## Preflight

Audit current state before doing anything:

```bash
# Claude Code installed?
command -v claude &>/dev/null && echo "EXISTS: Claude Code" || echo "MISSING: Claude Code — run /learn-01-vertex-setup first"

# Check for user-level skills directory
if [ -d "$HOME/.claude/skills" ]; then
  count=$(find "$HOME/.claude/skills" -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')
  echo "EXISTS: ~/.claude/skills/ directory ($count skills installed)"
  find "$HOME/.claude/skills" -name "SKILL.md" -exec dirname {} \; 2>/dev/null | while read d; do
    name=$(basename "$d")
    echo "  - $name"
  done
else
  echo "MISSING: ~/.claude/skills/ directory (will be created)"
fi

# Check for project-level commands
if [ -d ".claude/commands" ]; then
  count=$(ls .claude/commands/*.md 2>/dev/null | wc -l | tr -d ' ')
  echo "EXISTS: .claude/commands/ directory ($count commands)"
else
  echo "MISSING: .claude/commands/ directory"
fi

# Check for claude-cost-saving repo (reference skills)
if [ -d "$HOME/repos/claude-cost-saving/skills" ]; then
  count=$(ls -d "$HOME/repos/claude-cost-saving/skills"/*/ 2>/dev/null | wc -l | tr -d ' ')
  echo "EXISTS: claude-cost-saving repo ($count reference skills)"
else
  echo "INFO: claude-cost-saving repo not found (optional reference material)"
fi
```

If Claude Code is MISSING, stop and tell the user:
```
Claude Code is not installed. Complete Module 01 first:
  /learn-01-vertex-setup
```

Print a summary of what was found.

## Step 1 — Understand skill anatomy

Explain:
```
Every skill is a directory containing a SKILL.md file. The file has two
parts: YAML frontmatter (metadata) and the body (instructions).
```

Show this annotated example:

```
Here's the anatomy of a SKILL.md file:

  ---
  name: my-skill                    # identifier (kebab-case)
  description: >                    # what triggers this skill
    One-line summary of when Claude should use this skill.
    Include trigger phrases the user might say.
  agent: true                       # run as subagent (isolates context)
  model: sonnet                     # route to cheaper model (optional)
  ---

  # Skill Title

  Instructions for Claude go here. Write them as if briefing a
  colleague who needs to accomplish the task.

  ## Step 1: Do the thing
  ...

Frontmatter fields:
  name         — required, kebab-case identifier
  description  — required, tells Claude when to activate the skill
  agent        — optional, true = run in a subagent (saves context/cost)
  model        — optional, sonnet or haiku (only works with agent: true)
```

Then show real examples from the user's system:

```bash
# Show the frontmatter of an installed skill (if any exist)
if [ -f "$HOME/.claude/skills/hivemind-write/SKILL.md" ]; then
  echo "=== hivemind-write (team skill) ==="
  head -10 "$HOME/.claude/skills/hivemind-write/SKILL.md"
  echo ""
fi
```

```bash
# Show a courseware dispatcher for comparison
echo "=== courseware dispatcher (project command) ==="
cat .claude/commands/learn-04-git-mcp.md
```

Explain the difference:
```
Two types of skills:

  Project commands (.claude/commands/*.md)
    - Invoked with slash commands: /learn-04-git-mcp
    - Scoped to the project — only work in this repo
    - No frontmatter needed (the filename is the command name)
    - Good for: project-specific workflows, module dispatchers

  Global skills (~/.claude/skills/NAME/SKILL.md)
    - Triggered by keywords in conversation
    - Available across all projects
    - Use frontmatter for name, description, agent, model
    - Good for: reusable utilities, team-wide tools
```

## Step 2 — Installation locations

Explain:
```
Skills can be installed in two places, and they behave differently:
```

Show the directory structure:
```
  ~/.claude/skills/                    # Global skills (all projects)
    hivemind-write/
      SKILL.md
    hivemind-query/
      SKILL.md
      references/
        search-strategy.md

  ~/repos/my-project/
    .claude/commands/                  # Project commands (this repo only)
      my-command.md
      deploy.md

Skills can include reference files alongside SKILL.md. The skill can
read these with relative paths (e.g., references/search-strategy.md).
```

Show how skills get installed:

```bash
# Check if any skills are symlinked (common pattern)
find "$HOME/.claude/skills" -type l 2>/dev/null | while read link; do
  target=$(readlink "$link")
  echo "SYMLINK: $(basename $link) -> $target"
done
```

Explain:
```
Common installation patterns:

  1. Direct copy — copy the skill directory into ~/.claude/skills/
     cp -r my-skill/ ~/.claude/skills/my-skill/

  2. Symlink from a repo — keep the skill in version control
     ln -s ~/repos/my-repo/.claude/skills/my-skill ~/.claude/skills/my-skill

  3. Project commands — just add .md files to .claude/commands/
     No installation needed, they're part of the repo.

The symlink pattern is recommended for team skills — everyone pulls
the repo and symlinks, so the skill stays in sync.
```

## Step 3 — Subagent delegation

Explain:
```
The most powerful skill feature is subagent delegation. When a skill
has "agent: true", it runs in a separate context window. This means:

  - The skill's work doesn't fill up the main conversation context
  - You can route it to a cheaper model (Sonnet or Haiku)
  - The parent only sees the final result, not every intermediate step

This is the primary cost-saving mechanism for Claude Code.
```

Show the model routing tiers:

```
Model routing for subagent skills:

  model: haiku    — cheapest, fastest
    Use for: mechanical tasks, text extraction, formatting
    Examples: parse a PDF, format a log, extract data

  model: sonnet   — mid-tier, good reasoning
    Use for: analysis, code review, search, summarization
    Examples: explore codebase, review diff, research topic

  (no model line) — uses parent model (Opus)
    Use for: complex reasoning, planning, architecture
    Examples: brainstorming, writing specs, debugging
```

If the claude-cost-saving repo exists, show a concrete example:

```bash
if [ -f "$HOME/repos/claude-cost-saving/skills/review-diff/SKILL.md" ]; then
  echo "=== review-diff skill (subagent example) ==="
  cat "$HOME/repos/claude-cost-saving/skills/review-diff/SKILL.md"
fi
```

Explain:
```
Notice the pattern:
  1. Frontmatter sets agent: true and model: sonnet
  2. The body describes inputs, steps, and the exact output format
  3. The output format is minimal — only what the parent needs

The output format matters most. A subagent that returns the full diff
defeats the purpose — you want it to return only the structured findings.
```

## Step 4 — Write your own skill

Explain:
```
Let's write a skill together. We'll create a utility that summarizes
the current git session — recent commits, changed files, and branch
status — as a quick status report.
```

Create the skill directory:

```bash
mkdir -p "$HOME/.claude/skills/session-summary"
```

Guide the user through writing the SKILL.md. Present this as the target:

```
We'll create a "session-summary" skill that:
  - Runs as a subagent (agent: true) to save context
  - Uses Sonnet (model: sonnet) since it's analysis work
  - Gathers git status, recent commits, and branch info
  - Returns a concise summary to the parent

Here's the SKILL.md we'll write:
```

Write the skill file:

```markdown
---
name: session-summary
description: >
  Summarize the current working session: recent commits, changed files,
  branch status, and what was accomplished. Trigger on: "session summary",
  "what did I do", "summarize my session", "status report".
agent: true
model: sonnet
---

# Session Summary

Generate a concise summary of the current working session.

## Steps

1. Get the current branch and repo name:
   ```bash
   basename $(git rev-parse --show-toplevel)
   git branch --show-current
   ```

2. Get recent commits (last 10):
   ```bash
   git log --oneline -10
   ```

3. Get working directory status:
   ```bash
   git status --short
   ```

4. Get recent file changes:
   ```bash
   git diff --stat HEAD~5..HEAD 2>/dev/null || git diff --stat
   ```

## Output Format

Return ONLY this structure to the parent:

**Session Summary — <repo name>**
- Branch: <branch name>
- Recent commits: <count> commits in the last session
- Key changes: <2-3 bullet points summarizing what changed>
- Working directory: <clean / N files modified / N files untracked>

Do not return raw command output. Synthesize it into the summary above.
```

Verify the file was created:
```bash
if [ -f "$HOME/.claude/skills/session-summary/SKILL.md" ]; then
  echo "PASS: session-summary skill created"
  echo "  Location: ~/.claude/skills/session-summary/SKILL.md"
  wc -l "$HOME/.claude/skills/session-summary/SKILL.md" | awk '{print "  Lines: " $1}'
else
  echo "FAIL: SKILL.md not found"
fi
```

Tell the user:
```
The skill is installed. To test it, you'll need to restart Claude Code
so it picks up the new skill. But first, let's verify everything else.
```

## Step 5 — Examine the skill ecosystem

Explain:
```
Let's look at how skills are organized across the team. Understanding
the ecosystem helps you know what already exists and where to contribute.
```

List all available skills:

```bash
echo "=== Global skills (~/.claude/skills/) ==="
find "$HOME/.claude/skills" -name "SKILL.md" -exec dirname {} \; 2>/dev/null | while read d; do
  name=$(basename "$d")
  # Extract the description from frontmatter
  desc=$(python3 -c "
import re
with open('$d/SKILL.md') as f:
    content = f.read()
m = re.search(r'description:\s*>?\s*\n?\s*(.+?)(?:\n[a-z]|\n---)', content, re.DOTALL)
if m:
    print(m.group(1).strip()[:80])
else:
    print('(no description)')
" 2>/dev/null || echo "(could not parse)")
  echo "  $name — $desc"
done

echo ""
echo "=== Project commands (.claude/commands/) ==="
for f in .claude/commands/*.md; do
  [ -f "$f" ] || continue
  name=$(basename "$f" .md)
  echo "  /$name"
done
```

Explain:
```
Skill design guidelines:

  1. One skill, one job — don't combine unrelated tasks
  2. Clear trigger phrases — list them in the description
  3. Minimal output — subagents should return structured results, not raw data
  4. Include references — put supporting data in references/ alongside SKILL.md
  5. Version control — keep skills in a git repo, symlink to ~/.claude/skills/
  6. Test before sharing — run the skill yourself before pushing to the team
```

## Verification

Run all checks and report:

```bash
# 1. Skills directory exists
[ -d "$HOME/.claude/skills" ] && echo "PASS: ~/.claude/skills/ exists" || echo "FAIL: missing skills directory"

# 2. Session-summary skill exists
[ -f "$HOME/.claude/skills/session-summary/SKILL.md" ] && echo "PASS: session-summary skill created" || echo "FAIL: session-summary SKILL.md not found"

# 3. Frontmatter has required fields
if [ -f "$HOME/.claude/skills/session-summary/SKILL.md" ]; then
  python3 -c "
import re
with open('$HOME/.claude/skills/session-summary/SKILL.md') as f:
    content = f.read()
checks = {
    'name': bool(re.search(r'^name:', content, re.MULTILINE)),
    'description': bool(re.search(r'^description:', content, re.MULTILINE)),
    'agent: true': bool(re.search(r'^agent:\s*true', content, re.MULTILINE)),
    'model: sonnet': bool(re.search(r'^model:\s*sonnet', content, re.MULTILINE)),
}
for field, ok in checks.items():
    print(f'  {\"PASS\" if ok else \"FAIL\"}: frontmatter has {field}')
" 2>/dev/null
fi

# 4. Project commands exist
count=$(ls .claude/commands/*.md 2>/dev/null | wc -l | tr -d ' ')
echo "PASS: $count project commands in .claude/commands/"
```

Print:
```
All skill authoring checks passed.
```

If any fail:
```
Troubleshooting:

  SKILL.md not found:
    Make sure the file is at ~/.claude/skills/session-summary/SKILL.md
    The directory name must match the skill name.

  Missing frontmatter fields:
    Every SKILL.md needs: name, description
    Subagent skills also need: agent: true
    Model routing needs: model: sonnet (or haiku)

  Skill not showing up:
    Restart Claude Code after adding new skills.
    Check that the SKILL.md is valid YAML frontmatter (--- delimiters).
```

## Challenge

```
Create a second skill called "file-stats" that:

1. Has proper frontmatter (name, description, agent: true, model: haiku)
2. Takes a directory path as input
3. Returns a summary: number of files, total lines of code, top 5 largest
   files, and breakdown by file extension
4. Uses model: haiku (this is a mechanical counting task)
5. Lives in ~/.claude/skills/file-stats/SKILL.md

Write the SKILL.md, then tell me:
  - The full path where you saved it
  - What model you chose and why
  - The trigger phrases you put in the description
```

## Challenge Verification

The user should report:
1. Path: `~/.claude/skills/file-stats/SKILL.md`
2. Model: `haiku` (because counting files and lines is mechanical)
3. Trigger phrases in the description

To verify:
```bash
# Check the file exists
[ -f "$HOME/.claude/skills/file-stats/SKILL.md" ] && echo "PASS: file exists" || echo "FAIL: file not found"

# Check frontmatter
if [ -f "$HOME/.claude/skills/file-stats/SKILL.md" ]; then
  python3 -c "
import re
with open('$HOME/.claude/skills/file-stats/SKILL.md') as f:
    content = f.read()
checks = {
    'name: file-stats': bool(re.search(r'^name:\s*file-stats', content, re.MULTILINE)),
    'description': bool(re.search(r'^description:', content, re.MULTILINE)),
    'agent: true': bool(re.search(r'^agent:\s*true', content, re.MULTILINE)),
    'model: haiku': bool(re.search(r'^model:\s*haiku', content, re.MULTILINE)),
}
for field, ok in checks.items():
    print(f'  {\"PASS\" if ok else \"FAIL\"}: {field}')
" 2>/dev/null
fi
```

If the answers match, print:
```
Module 07 complete.

You can now write and install Claude Code skills.
Key concepts:
  - SKILL.md = frontmatter (metadata) + body (instructions)
  - Project commands: .claude/commands/*.md (slash commands, repo-scoped)
  - Global skills: ~/.claude/skills/NAME/SKILL.md (keyword-triggered, all repos)
  - Subagent delegation: agent: true isolates context, saves cost
  - Model routing: model: haiku|sonnet for cheaper execution

Cost-saving tiers:
  haiku   — mechanical tasks (parse, format, count, extract)
  sonnet  — analysis tasks (review, search, summarize, explore)
  opus    — complex reasoning (plan, debug, architect, brainstorm)

Next module: /learn-08-hivemind-knowledge-base
```
