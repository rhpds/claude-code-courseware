# Module 14 — Agent Teams vs Superpowers

Estimated time: 20 minutes
Prerequisites: Module 01 (Claude Code installed and working), Module 12 recommended (Review Agents)

Compare two approaches to multi-agent coordination in Claude Code: the agent review team pattern (a team-lead dispatches specialist subagents) and the superpowers plugin pattern (fresh subagent per task with two-stage review). When complete, you'll understand both patterns, know when to reach for each, and have run them both against real code.

## Orientation

Print this once at the start:

```
You're comparing two multi-agent patterns in Claude Code.
This takes about 20 minutes.

Pattern A — Agent Review Team
  A coordinator (team lead) reads changed files, decides which
  specialist agents to spawn, and consolidates findings.
  Each specialist runs in its own context: security, UI/UX,
  DevOps, code quality, etc.

Pattern B — Superpowers (Subagent-Driven Development)
  A controller dispatches a fresh subagent per task from a plan.
  Each subagent implements, then two review subagents check the
  work: first for spec compliance, then for code quality.

We'll cover:
  1. How each pattern works (architecture and flow)
  2. Hands-on: build a minimal agent team
  3. Hands-on: run a superpowers-style review
  4. Side-by-side comparison on the same codebase
  5. Decision framework — when to use which

You'll need:
  - Claude Code installed (Module 01)
  - A git repository to review (this courseware repo works)
  - Basic familiarity with agents (Module 12 recommended)
```

## Preflight

Audit current state before doing anything:

```bash
# Claude Code installed?
command -v claude &>/dev/null && echo "EXISTS: Claude Code" || echo "MISSING: Claude Code — run /learn-01-vertex-setup first"

# Inside a git repo?
git rev-parse --is-inside-work-tree &>/dev/null 2>&1 && echo "EXISTS: Inside git repo ($(basename $(git rev-parse --show-toplevel)))" || echo "MISSING: Not inside a git repository"

# Check for .claude/agents/ directory in this project
if [ -d ".claude/agents" ]; then
  count=$(ls .claude/agents/*.md 2>/dev/null | wc -l | tr -d ' ')
  echo "EXISTS: .claude/agents/ directory ($count agent definitions)"
  for f in .claude/agents/*.md; do
    [ -f "$f" ] || continue
    echo "  - $(basename "$f" .md)"
  done
else
  echo "MISSING: .claude/agents/ directory (will be created)"
fi

# Superpowers plugin installed?
if [ -d "$HOME/.claude/plugins/cache/claude-plugins-official/superpowers" ]; then
  version=$(ls "$HOME/.claude/plugins/cache/claude-plugins-official/superpowers/" 2>/dev/null | head -1)
  echo "EXISTS: Superpowers plugin (v$version)"
else
  echo "INFO: Superpowers plugin not installed (optional — we'll explain the pattern regardless)"
fi

# Check for team-lead agent from Module 12
if [ -f ".claude/agents/review-coordinator.md" ] || [ -f ".claude/agents/team-lead.md" ]; then
  echo "EXISTS: Team coordinator agent definition found"
else
  echo "MISSING: Team coordinator agent (will be created in Step 2)"
fi
```

If Claude Code is MISSING, stop and tell the user:
```
Claude Code is not installed. Complete Module 01 first:
  /learn-01-vertex-setup
```

Print a summary of what was found. Skip steps where the config already exists.

## Step 1 — Understand both patterns

This step is informational — nothing to install.

Explain:
```
Both patterns use the same Claude Code Agent tool to spawn subagents.
The difference is in how they organize and coordinate the work.

PATTERN A: Agent Review Team
------------------------------
Architecture:
  You (or a team-lead agent)
    |-- spawns --> security-reviewer
    |-- spawns --> patternfly-ui-ux-reviewer
    |-- spawns --> devops-platform-engineer
    |-- spawns --> code-quality-reviewer (custom)
    |-- spawns --> docs-reviewer (custom)
    |
    Collects all findings --> consolidated report

How it works:
  1. A coordinator reads the changed files (git diff, git status)
  2. Based on file types and change scope, it decides which
     specialists are relevant
  3. It spawns only the relevant specialists in parallel
  4. Each specialist runs independently in its own context
  5. The coordinator collects findings and returns a single report

Key characteristics:
  - Review-oriented (reads code, reports findings)
  - Smart routing (only spawns relevant agents)
  - Parallel execution (agents don't depend on each other)
  - Consolidated output (one report with all findings)

Real-world example:
  The RHDP ops-hub project uses this pattern. When you say
  "review" or "run the team", the ops-hub-team-lead agent
  analyzes changed files and dispatches the right specialists.


PATTERN B: Superpowers (Subagent-Driven Development)
------------------------------------------------------
Architecture:
  Controller (you)
    |-- reads plan
    |-- for each task:
    |     |-- spawns --> implementer subagent
    |     |-- spawns --> spec-compliance reviewer
    |     |-- spawns --> code-quality reviewer
    |     |-- marks task complete
    |-- after all tasks:
          |-- spawns --> final reviewer

How it works:
  1. A plan defines discrete tasks (from the writing-plans skill)
  2. For each task, a fresh implementer subagent is dispatched
  3. The implementer writes code, tests, and commits
  4. A spec-compliance reviewer checks: did the code match the spec?
  5. A code-quality reviewer checks: is the implementation clean?
  6. If either reviewer finds issues, the implementer fixes them
  7. Only after both reviews pass does the next task begin

Key characteristics:
  - Implementation-oriented (writes code, not just reviews)
  - Sequential tasks (one at a time, dependencies respected)
  - Two-stage review gate (spec then quality)
  - Fresh context per task (no cross-contamination)
  - Plan-driven (follows a written implementation plan)
```

## Step 2 — Build a minimal agent review team

Explain:
```
Let's build a 3-agent review team for this repository:
  1. A team coordinator that decides which agents to spawn
  2. A structure reviewer that checks module consistency
  3. A link checker that validates cross-references

You already know how to create individual agents from Module 12.
The new concept here is the coordinator — an agent that spawns
other agents based on what it finds.
```

Create the agents directory if it does not exist:

```bash
mkdir -p .claude/agents
```

Write the structure reviewer agent:

```bash
cat > .claude/agents/structure-reviewer.md << 'AGENTEOF'
---
name: structure-reviewer
description: Checks that courseware modules follow the standard template structure
---

You are a structure reviewer for courseware modules. Check each module file
in the modules/ directory against the standard structure:

Required sections (in order):
  1. Title line: "# Module NN — TITLE"
  2. Metadata: "Estimated time:" and "Prerequisites:"
  3. ## Orientation — with a print block
  4. ## Preflight — with EXISTS/MISSING bash checks
  5. ## Step N — at least one step with skip condition and verification
  6. ## Verification — PASS/FAIL checks with counter
  7. ## Challenge — hands-on task
  8. ## Challenge Verification — how to verify answers

For each module, report:
- File name
- Which required sections are present or missing
- Any sections out of order

Output format:

## Structure Review

### Issues
- module-file.md: [description of issue]

### Summary
- Modules checked: N
- Fully compliant: N
- Issues found: N
AGENTEOF
```

Write the link checker agent:

```bash
cat > .claude/agents/link-checker.md << 'AGENTEOF'
---
name: link-checker
description: Validates cross-references between modules, skills, and dispatchers
---

You are a link checker for the courseware repository. Verify that:

1. Every module in modules/ has a matching skill dispatcher in skills/learn-*/SKILL.md
2. Every module in modules/ has a matching clone-mode dispatcher in .claude/commands/learn-*.md
3. Every skill dispatcher references the correct module file path
4. The courseware catalog (skills/courseware/SKILL.md and .claude/commands/courseware.md)
   lists all available modules
5. "Next module" links at the end of each module point to a module that exists

For each broken reference, report:
- Source file and line
- What it references
- Whether the target exists

Output format:

## Link Check

### Broken References
- [source] references [target]: NOT FOUND

### Missing Dispatchers
- [module] has no skill dispatcher / command dispatcher

### Catalog Gaps
- [module] not listed in courseware catalog

### Summary
- References checked: N
- Broken: N
- Missing dispatchers: N
AGENTEOF
```

Write the team coordinator:

```bash
cat > .claude/agents/courseware-team-lead.md << 'AGENTEOF'
---
name: courseware-team-lead
description: Coordinates specialist review agents for comprehensive courseware review
---

You are the courseware review team coordinator. Your job is to dispatch
the right specialist agents and consolidate their findings.

Available specialists:
  structure-reviewer  — checks module template compliance
  link-checker        — validates cross-references and dispatchers
  security-reviewer   — checks for secrets, injection, unsafe operations (built-in)

Workflow:
  1. Run `git diff --name-only HEAD~3` to see recently changed files
  2. Run `ls modules/` and `ls skills/` to understand scope
  3. Decide which specialists to spawn:
     - If module files changed: spawn structure-reviewer
     - If any files changed: spawn link-checker (always useful)
     - If scripts/ or setup code changed: spawn security-reviewer
  4. Spawn the selected specialists in PARALLEL using the Agent tool
  5. Collect their findings
  6. Return a consolidated report

Output format:

## Team Review Report

### Specialists Dispatched
- [name]: [reason for inclusion]

### Findings by Specialist

#### [specialist-name]
[paste their findings]

### Combined Summary
- Total issues: N
- Critical: N
- Recommendation: PASS / NEEDS WORK
AGENTEOF
```

Verify all three files exist:
```bash
for agent in structure-reviewer link-checker courseware-team-lead; do
  if [ -f ".claude/agents/$agent.md" ]; then
    echo "PASS: $agent.md created ($(wc -l < ".claude/agents/$agent.md") lines)"
  else
    echo "FAIL: $agent.md not found"
  fi
done
```

Explain the team lead pattern:
```
The coordinator is the key difference from running agents manually.
Instead of you deciding which agents to run, the coordinator:

  1. Inspects the situation (changed files, repo structure)
  2. Decides which specialists are relevant
  3. Spawns only those specialists
  4. Consolidates findings into one report

This scales better than manual dispatch because the coordinator
makes routing decisions automatically. Add a new specialist agent
and the coordinator can learn to use it without changing your workflow.
```

## Step 3 — Run the agent team

Explain:
```
Let's run the courseware-team-lead against this repository. The
coordinator will analyze the repo, decide which specialists to
spawn, and return a consolidated report.

Watch what happens — the team lead should dispatch at least the
structure-reviewer and link-checker, and possibly the security-reviewer
if there are scripts in the recent changes.
```

Spawn the courseware-team-lead agent:
```
Review the courseware repository. Analyze recently changed files,
decide which specialist agents to dispatch, run them, and return
a consolidated report with all findings.
```

After the agent returns, explain the results:
```
The team lead pattern in action:

  1. It checked what changed recently
  2. It decided which specialists were relevant
  3. It spawned them (possibly in parallel)
  4. It collected and consolidated the findings

Notice that you gave one command — "review" — and got a structured
report covering multiple review dimensions. The coordinator handled
the routing.

This is the same pattern the RHDP ops-hub uses for PR reviews:
  "review" --> ops-hub-team-lead --> dispatches specialists --> report
```

## Step 4 — Understand the superpowers approach

Explain:
```
Now let's look at the superpowers pattern. This is fundamentally
different from the agent review team because it's about BUILDING,
not just REVIEWING.

The superpowers plugin provides a structured workflow:

  1. Brainstorming — collaborative design of what to build
  2. Writing Plans — detailed implementation plan with tasks
  3. Subagent-Driven Development — execute the plan task by task:
     - Fresh implementer subagent per task
     - Spec-compliance review after each task
     - Code-quality review after each task
     - Both reviews must pass before moving on

The review step in superpowers is embedded in the build process.
Every piece of code gets reviewed twice before the next task starts.

Comparison:

  Agent Review Team               Superpowers
  ─────────────────               ───────────
  Reviews existing code           Builds AND reviews new code
  Runs on demand ("review")       Runs as part of implementation
  Specialists run in parallel     Tasks run sequentially
  One-shot analysis               Iterative (fix + re-review loops)
  Manual dispatch or coordinator  Controller manages full lifecycle
  Good for: PR reviews, audits    Good for: feature implementation
```

If the superpowers plugin is installed, demonstrate the available skills:
```bash
# List superpowers skills if installed
if [ -d "$HOME/.claude/plugins/cache/claude-plugins-official/superpowers" ]; then
  version=$(ls "$HOME/.claude/plugins/cache/claude-plugins-official/superpowers/" | head -1)
  echo "Superpowers v$version skills:"
  for skill_dir in "$HOME/.claude/plugins/cache/claude-plugins-official/superpowers/$version/skills"/*/; do
    name=$(basename "$skill_dir")
    echo "  /superpowers:$name"
  done
else
  echo "Superpowers plugin not installed."
  echo "To install: search for 'superpowers' in the Claude Code plugin marketplace"
  echo ""
  echo "The superpowers skills include:"
  echo "  /superpowers:brainstorming"
  echo "  /superpowers:writing-plans"
  echo "  /superpowers:subagent-driven-development"
  echo "  /superpowers:executing-plans"
  echo "  /superpowers:test-driven-development"
  echo "  /superpowers:requesting-code-review"
  echo "  /superpowers:finishing-a-development-branch"
  echo "  /superpowers:using-git-worktrees"
fi
```

## Step 5 — Run a superpowers-style review

Explain:
```
Even without the full superpowers plugin, you can use the two-stage
review pattern manually. Let's run a spec-compliance review followed
by a code-quality review on a module file.

This simulates what superpowers does automatically after each
implementation task.
```

Pick a module file (suggest `modules/12-review-agents.md` or the module with the most recent changes):

First, spawn a spec-compliance reviewer:
```
Review modules/12-review-agents.md against the standard module template
(modules/TEMPLATE.md). Check:

1. Does it have all required sections in the correct order?
2. Does the Orientation print block set expectations correctly?
3. Does the Preflight use EXISTS/MISSING pattern?
4. Does each Step have a skip condition and verification?
5. Does the Verification use PASS/FAIL with a counter?
6. Does the Challenge use real team data?

Report: SPEC COMPLIANT or list specific gaps.
```

Then, spawn a code-quality reviewer:
```
Review modules/12-review-agents.md for quality:

1. Are the bash code blocks syntactically correct?
2. Are instructions clear and unambiguous?
3. Is there unnecessary repetition?
4. Are the verification commands robust (handle edge cases)?
5. Is the flow logical — does each step build on the previous?

Report findings with severity: Critical / Major / Minor.
```

After both return, compare:
```
Two-stage review results:

  Stage 1 — Spec Compliance:
    Did the module match the template? Were sections present?
    This catches structural issues — missing sections, wrong order.

  Stage 2 — Code Quality:
    Was the content well-written? Were the scripts correct?
    This catches implementation issues — bugs, unclear instructions.

In the superpowers workflow, both stages must pass before moving to
the next task. If either finds issues, the implementer fixes them
and the reviewer checks again. This loop continues until approved.

This is more rigorous than a single-pass review because each
reviewer has a narrow focus. The spec reviewer doesn't care about
code style, and the quality reviewer doesn't care about template
compliance. Separation of concerns applied to code review.
```

## Step 6 — Decision framework

Explain:
```
When to use each pattern:

USE AGENT REVIEW TEAM WHEN:
  - Reviewing a PR or existing code
  - Running periodic audits
  - You need multiple perspectives on the same code
  - The code already exists and you want feedback
  - You want a one-shot consolidated report

  Examples:
    "Review this PR for security and UI issues"
    "Audit the deployment configs before release"
    "Check all modules for template compliance"

USE SUPERPOWERS WHEN:
  - Building a new feature from a plan
  - You want implementation + review in one workflow
  - Tasks are sequential and each builds on the previous
  - You need iterative fix-and-review loops
  - Quality gates must pass before moving forward

  Examples:
    "Implement the auth system from the design spec"
    "Build all 5 API endpoints from the plan"
    "Create a new courseware module with all sections"

USE BOTH WHEN:
  - Building a feature (superpowers) then doing a final sweep
    (agent team) before merge
  - The team lead can be the "final reviewer" in the superpowers
    workflow — after all tasks complete, run the full agent team
    for a comprehensive review

  Example workflow:
    1. /superpowers:brainstorming — design the feature
    2. /superpowers:writing-plans — create the implementation plan
    3. /superpowers:subagent-driven-development — build it
    4. "run the team" — agent review team does a final sweep
    5. /superpowers:finishing-a-development-branch — wrap up

The patterns complement each other. Agent teams are best for
review-in-place. Superpowers is best for plan-driven construction.
Using both gives you implementation rigor AND review breadth.
```

## Verification

Run all checks and report:

```bash
PASS=0
TOTAL=5

# 1. Claude Code running
command -v claude &>/dev/null && { echo "PASS: Claude Code installed"; PASS=$((PASS+1)); } || echo "FAIL: Claude Code not installed"

# 2. .claude/agents/ directory exists
[ -d ".claude/agents" ] && { echo "PASS: .claude/agents/ directory exists"; PASS=$((PASS+1)); } || echo "FAIL: .claude/agents/ directory missing"

# 3. Team coordinator agent exists
if [ -f ".claude/agents/courseware-team-lead.md" ]; then
  echo "PASS: courseware-team-lead.md created"
  PASS=$((PASS+1))
else
  echo "FAIL: courseware-team-lead.md not found"
fi

# 4. Structure reviewer agent exists with valid frontmatter
if [ -f ".claude/agents/structure-reviewer.md" ]; then
  python3 -c "
import re
with open('.claude/agents/structure-reviewer.md') as f:
    content = f.read()
has_name = bool(re.search(r'^name:', content, re.MULTILINE))
has_desc = bool(re.search(r'^description:', content, re.MULTILINE))
if has_name and has_desc:
    print('PASS: structure-reviewer.md has valid frontmatter')
else:
    print('FAIL: structure-reviewer.md missing frontmatter fields')
" 2>/dev/null && PASS=$((PASS+1))
else
  echo "FAIL: structure-reviewer.md not found"
fi

# 5. Link checker agent exists with valid frontmatter
if [ -f ".claude/agents/link-checker.md" ]; then
  python3 -c "
import re
with open('.claude/agents/link-checker.md') as f:
    content = f.read()
has_name = bool(re.search(r'^name:', content, re.MULTILINE))
has_desc = bool(re.search(r'^description:', content, re.MULTILINE))
if has_name and has_desc:
    print('PASS: link-checker.md has valid frontmatter')
else:
    print('FAIL: link-checker.md missing frontmatter fields')
" 2>/dev/null && PASS=$((PASS+1))
else
  echo "FAIL: link-checker.md not found"
fi

echo ""
echo "$PASS/$TOTAL checks passed."
```

If all pass:
```
All checks passed. Your agent review team is set up and ready.
```

If any fail, tell the user which step to re-run.

## Challenge

```
Run both patterns against this courseware repository and compare:

1. Run the courseware-team-lead agent (Pattern A — agent review team)
   and note the total number of findings across all specialists.

2. Run a two-stage review (Pattern B — superpowers style) on the
   module file modules/14-agent-teams-vs-superpowers.md:
   - Stage 1: spec-compliance review against modules/TEMPLATE.md
   - Stage 2: code-quality review

3. Tell me:
   a. How many specialists did the team lead dispatch?
   b. How many total findings did the agent team report?
   c. Did the spec-compliance review pass or fail? What was missing?
   d. Which pattern gave you more actionable feedback for THIS repo?
```

## Challenge Verification

The user should provide:
1. Number of specialists dispatched (should be at least 2)
2. Total findings count from the agent team
3. Spec-compliance result for Module 14
4. Their assessment of which pattern was more useful

To verify, confirm:
- The team lead dispatched at least structure-reviewer and link-checker
- The two-stage review ran both stages
- The user can articulate why one pattern was better for this use case

Accept any reasonable answer for item 4 — both patterns have valid strengths for different situations. The point is that the user understands the trade-offs.

If successful, print:
```
Module 14 complete.

You now understand two multi-agent coordination patterns:

  Agent Review Team (Pattern A):
    - Coordinator dispatches specialist agents
    - Best for: PR reviews, audits, one-shot analysis
    - Scales by adding new specialist agent definitions
    - Agents in .claude/agents/ — project or user scoped

  Superpowers (Pattern B):
    - Fresh subagent per task with two-stage review
    - Best for: plan-driven implementation with quality gates
    - Spec-compliance then code-quality review after each task
    - Install: search for superpowers in plugin marketplace

  Combined workflow:
    Superpowers builds it --> Agent team does final sweep

Decision framework:
  Reviewing existing code?  --> Agent review team
  Building from a plan?     --> Superpowers
  Building then reviewing?  --> Both, in sequence

Agent definitions you created in this module:
  .claude/agents/courseware-team-lead.md    — team coordinator
  .claude/agents/structure-reviewer.md     — module template checker
  .claude/agents/link-checker.md           — cross-reference validator

These agents are available in this project now. You can run them
anytime by asking Claude Code to "run the courseware review team"
or by spawning individual specialists.
```
