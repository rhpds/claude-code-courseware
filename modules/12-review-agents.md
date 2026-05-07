# Module 12 — Review Agents

Estimated time: 15 minutes
Prerequisites: Module 01 (Claude Code installed and working), Module 09 recommended (Writing Custom Skills)

Use Claude Code's built-in agent system to run specialized code reviews, and create custom review agent definitions. When complete, you'll know how to spawn review agents, write your own agent definitions, and coordinate multiple agents for comprehensive reviews.

## Orientation

Print this once at the start:

```
You're learning to use Claude Code's review agent system.
This takes about 15 minutes.

Claude Code can spawn specialized subagents — isolated agents that
focus on a specific review area and return structured findings. The
system includes built-in agents for common review types, and you can
define custom agents for your own needs.

We'll cover:
  1. How the agent system works
  2. Running a built-in security review
  3. Creating a custom review agent definition
  4. Running the custom agent
  5. Coordinating multiple agents in parallel

Built-in review agents available:
  security-reviewer              — Python, React, SQL, container, K8s/OCP security
  patternfly-ui-ux-reviewer      — PatternFly components, accessibility, UX
  devops-platform-engineer       — Docker, Podman, K8s/OCP, CI/CD
  container-specialist           — Container build, run, debug, registry ops

Custom agents live in .claude/agents/ directories and extend the system
with project-specific or team-specific review capabilities.
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

# Check for the custom agent we'll create in this module
if [ -f ".claude/agents/code-quality-reviewer.md" ]; then
  echo "EXISTS: code-quality-reviewer agent definition"
else
  echo "MISSING: code-quality-reviewer agent (will be created in Step 3)"
fi
```

If Claude Code is MISSING, stop and tell the user:
```
Claude Code is not installed. Complete Module 01 first:
  /learn-01-vertex-setup
```

Print a summary of what was found. Skip steps where the config already exists.

## Step 1 — Understand the agent system

This step is informational — nothing to install.

Explain:
```
Claude Code's agent system lets you spawn subagents — isolated
instances that run a focused task and return their findings to the
main conversation. This is the same mechanism used by skills with
"agent: true", but applied specifically to code review.

How it works:
  1. The main conversation spawns a subagent with a specific type
  2. The subagent runs in its own context window
  3. It has access to tools (file reading, search, bash, MCP)
  4. It returns structured findings when done
  5. The main conversation receives only the results, not the
     intermediate work — saving context and cost

Built-in agent types:

  security-reviewer
    Focus: authentication, injection, secrets, container security,
    RBAC, dependency vulnerabilities, unsafe deserialization
    Tools: file search, bash, MCP servers
    Use when: reviewing PRs for security issues, auditing a codebase

  patternfly-ui-ux-reviewer
    Focus: PatternFly component usage, accessibility (WCAG),
    responsive design, UX patterns, design consistency
    Tools: file search, PatternFly MCP, Playwright MCP
    Use when: reviewing frontend code, checking accessibility

  devops-platform-engineer
    Focus: Dockerfiles, CI/CD pipelines, K8s/OCP manifests,
    resource limits, deployment strategies, infra-as-code
    Tools: file search, bash, Podman MCP, OCI Registry MCP
    Use when: reviewing infrastructure changes, deployment configs

  container-specialist
    Focus: container build optimization, runtime debugging,
    image size, layer caching, registry operations
    Tools: Podman MCP, OCI Registry MCP, bash
    Use when: debugging containers, reviewing Dockerfiles

Custom agents:
  You can define your own agents by creating markdown files in
  .claude/agents/ directories. These extend the built-in set with
  project-specific or team-specific review capabilities.

  Custom agent locations:
    .claude/agents/NAME.md       — project-scoped (this repo only)
    ~/.claude/agents/NAME.md     — user-scoped (all your repos)
```

## Step 2 — Run a built-in security review

Explain:
```
Let's run a security review against this repository using the
built-in security-reviewer agent. This demonstrates how subagents
work in practice.

The Agent tool takes two key parameters:
  - prompt: what you want the agent to do (be specific)
  - subagent_type: which agent type to use

The security-reviewer will scan the codebase, look for common
vulnerability patterns, and return structured findings.
```

Spawn the security-reviewer agent with a prompt like:
```
Review the current repository for security issues. Focus on:
1. Any hardcoded secrets, API keys, or credentials
2. Unsafe file operations or command injection risks
3. Dependencies with known vulnerabilities
4. Insecure configuration patterns

Report your findings as a numbered list with file paths and line
numbers where applicable.
```

After the agent returns, show the results and explain:
```
The security-reviewer ran in its own context. Here's what happened:

  1. It scanned the repository structure
  2. It read files looking for vulnerability patterns
  3. It checked for common security anti-patterns
  4. It returned structured findings

Notice that the main conversation only received the summary —
all the file reading and analysis the agent did stays in the
agent's context, not ours. This saves context space for our
ongoing conversation.

When to use the security-reviewer:
  - Before merging a PR with sensitive changes
  - When onboarding to an unfamiliar codebase
  - As part of a periodic security audit
  - After adding new dependencies or API integrations
```

## Step 3 — Create a custom review agent

Explain:
```
Built-in agents cover common review areas, but every team has
specific standards. Custom agent definitions let you codify your
team's review criteria into a reusable agent.

Agent definitions are markdown files in .claude/agents/ with a
simple structure:
  - Frontmatter with name and description
  - Instructions that define the agent's focus and output format

Let's create a code quality reviewer focused on naming, complexity,
duplication, test coverage, and error handling.
```

Create the agents directory if it does not exist:

```bash
mkdir -p .claude/agents
```

Write the custom agent definition:

```bash
cat > .claude/agents/code-quality-reviewer.md << 'AGENTEOF'
---
name: code-quality-reviewer
description: Reviews code for quality, naming conventions, complexity, and test coverage
---

You are a code quality reviewer. Examine the repository and report on:

1. Naming -- Are variables, functions, and classes named clearly and consistently?
2. Complexity -- Are functions too long or deeply nested? Flag anything over 50 lines or 4 levels deep.
3. Duplication -- Is there repeated code that could be consolidated into shared functions?
4. Test coverage -- Are there tests for the main code paths? Are edge cases covered?
5. Error handling -- Are errors handled appropriately? Are there bare except/catch blocks?

For each finding, report:
- File and line number
- What you found
- Suggested improvement

Be specific. Only report real issues, not style nitpicks. Prioritize
findings by impact: bugs and missing error handling first, then
complexity, then naming.

Output format:

## Code Quality Review

### Critical (bugs, missing error handling)
- ...

### Major (complexity, duplication)
- ...

### Minor (naming, conventions)
- ...

### Summary
- Total findings: N
- Files reviewed: N
- Recommendation: PASS / PASS WITH NOTES / NEEDS WORK
AGENTEOF
```

Verify:
```bash
if [ -f ".claude/agents/code-quality-reviewer.md" ]; then
  echo "PASS: code-quality-reviewer.md created"
  echo "  Location: .claude/agents/code-quality-reviewer.md"
  wc -l ".claude/agents/code-quality-reviewer.md" | awk '{print "  Lines: " $1}'
else
  echo "FAIL: agent definition not found"
fi
```

Show the file content and explain the structure:
```
The agent definition has two parts:

  Frontmatter (between --- markers):
    name         — identifier used to reference the agent
    description  — one-line summary of what the agent does

  Body (after the frontmatter):
    The instructions Claude follows when running as this agent.
    This is where you define:
      - What to examine
      - What criteria to apply
      - What output format to use

The output format matters most. A well-structured output format
makes it easy to act on the findings. The template above uses
severity tiers (Critical / Major / Minor) so the most important
issues surface first.
```

## Step 4 — Run the custom agent

Explain:
```
Now let's run the custom code-quality-reviewer against this
repository. Custom agents defined in .claude/agents/ become
available as subagent types, just like the built-in ones.
```

Spawn the code-quality-reviewer agent with a prompt like:
```
Review the code in this repository for quality issues. Follow
your instructions for what to examine and how to format findings.
Focus on the modules/ directory and any scripts/ directory.
```

After the agent returns, show the results and compare:
```
Compare the two reviews we ran:

  security-reviewer (built-in):
    - Focused on vulnerabilities and security anti-patterns
    - Looks for secrets, injection, unsafe operations
    - Good for: pre-merge security checks

  code-quality-reviewer (custom):
    - Focused on maintainability and code health
    - Looks for complexity, duplication, naming issues
    - Good for: ongoing code quality, onboarding reviews

Each agent brings a different lens to the same codebase. That's
the power of the system — you define what matters for your team
and codify it as an agent.
```

Explain how custom agents become available:
```
Custom agent availability:

  .claude/agents/NAME.md in a project:
    Available when Claude Code is running in that project.
    No restart needed — new agent files are picked up automatically.

  ~/.claude/agents/NAME.md (user-level):
    Available across all your projects.
    Same as project-level but scoped to your user.

  Naming: the filename (without .md) becomes the agent reference.
    code-quality-reviewer.md  -->  code-quality-reviewer
```

## Step 5 — Coordinate multiple agents

Explain:
```
The real power of the agent system comes from running multiple
agents in parallel. Each runs independently and returns its own
set of findings.

Three patterns for multi-agent reviews:

  1. Direct parallel — spawn 2+ agents at the same time
     Each agent runs independently with its own focus area.
     You get separate findings from each.

  2. Team lead pattern — a coordinator agent dispatches specialists
     One agent reads the changed files, decides which specialists
     are relevant, and spawns only those. This avoids running
     agents that have nothing to review (e.g., no UI code means
     skip the PatternFly reviewer).

  3. Sequential pipeline — one agent's output feeds the next
     First agent identifies risk areas, second agent deep-dives
     into those specific areas. Good for large codebases where
     you want to focus effort.
```

Demonstrate the direct parallel pattern:

Spawn both agents at the same time:
- security-reviewer: "Review the repository for security issues. Return a numbered list of findings with severity."
- code-quality-reviewer: "Review the repository for code quality issues. Follow your standard output format."

After both return, show the combined results:
```
Two agents ran in parallel:

  security-reviewer: <N> findings
  code-quality-reviewer: <N> findings

Each ran in its own context window. Neither saw the other's work.
The main conversation received both sets of findings without
spending context on the intermediate analysis.

This is the same pattern the team uses for comprehensive PR
reviews — the ops-hub-team-lead agent coordinates specialists
based on what files changed.
```

Explain the team lead pattern in more detail:
```
The team lead pattern (used in ops-hub):

  .claude/agents/ops-hub-team-lead.md
    - Reads the list of changed files
    - Decides which specialists to spawn based on file types:
        *.py files         --> security-reviewer
        *.tsx files        --> patternfly-ui-ux-reviewer
        Dockerfile, k8s/  --> devops-platform-engineer
    - Collects findings from each specialist
    - Returns a consolidated report

This avoids wasting tokens on irrelevant reviews. If a PR only
touches Python files, there's no need to run the UI reviewer.

You can create your own team lead for this repo:
  .claude/agents/review-coordinator.md

The coordinator is just another agent definition that knows about
the other agents and when to use each one.
```

## Verification

Run all checks and report:

```bash
PASS=0
TOTAL=4

# 1. Claude Code running
command -v claude &>/dev/null && { echo "PASS: Claude Code installed"; PASS=$((PASS+1)); } || echo "FAIL: Claude Code not installed"

# 2. .claude/agents/ directory exists
[ -d ".claude/agents" ] && { echo "PASS: .claude/agents/ directory exists"; PASS=$((PASS+1)); } || echo "FAIL: .claude/agents/ directory missing"

# 3. code-quality-reviewer agent definition exists and has required fields
if [ -f ".claude/agents/code-quality-reviewer.md" ]; then
  python3 -c "
import re
with open('.claude/agents/code-quality-reviewer.md') as f:
    content = f.read()
has_name = bool(re.search(r'^name:', content, re.MULTILINE))
has_desc = bool(re.search(r'^description:', content, re.MULTILINE))
if has_name and has_desc:
    print('PASS: code-quality-reviewer.md has valid frontmatter')
else:
    missing = []
    if not has_name: missing.append('name')
    if not has_desc: missing.append('description')
    print(f'FAIL: code-quality-reviewer.md missing: {', '.join(missing)}')
" 2>/dev/null && PASS=$((PASS+1))
else
  echo "FAIL: code-quality-reviewer.md not found"
fi

# 4. Agent file contains review instructions
if [ -f ".claude/agents/code-quality-reviewer.md" ]; then
  python3 -c "
with open('.claude/agents/code-quality-reviewer.md') as f:
    content = f.read()
body = content.split('---', 2)[-1] if content.startswith('---') else content
if len(body.strip()) > 100:
    print('PASS: agent definition has review instructions (' + str(len(body.strip())) + ' chars)')
else:
    print('FAIL: agent definition body is too short — needs review instructions')
" 2>/dev/null && PASS=$((PASS+1))
else
  echo "FAIL: cannot check agent body — file missing"
fi

echo ""
echo "$PASS/$TOTAL checks passed."
```

If all pass:
```
All review agent checks passed.
```

If any fail:
```
Troubleshooting:

  Agent definition not found:
    The file should be at .claude/agents/code-quality-reviewer.md
    Run Step 3 again to create it.

  Missing frontmatter fields:
    Every agent definition needs at minimum:
      ---
      name: agent-name
      description: what this agent does
      ---

  Agent not recognized:
    Custom agents in .claude/agents/ are picked up automatically.
    Make sure the file has the .md extension and valid frontmatter.
    If issues persist, restart Claude Code.
```

## Challenge

```
Create a documentation review agent and run it.

1. Create .claude/agents/docs-reviewer.md with:
   - Frontmatter: name and description
   - Instructions to check for:
     a. Missing or incomplete docstrings on functions and classes
     b. Outdated comments that reference things that no longer exist
     c. README accuracy — does the README match what the code does?
     d. Broken or missing links in markdown files
     e. Inconsistent terminology across documentation
   - A structured output format with severity levels

2. Run the docs-reviewer agent against this courseware repository

3. Tell me:
   - The full path where you saved the agent definition
   - How many findings the agent reported
   - The most significant finding
```

## Challenge Verification

The user should report:
1. Path: `.claude/agents/docs-reviewer.md` in the current project
2. A count of findings from the agent
3. The most significant finding from the review

To verify:
```bash
# Check the file exists
[ -f ".claude/agents/docs-reviewer.md" ] && echo "PASS: docs-reviewer.md exists" || echo "FAIL: docs-reviewer.md not found"

# Check frontmatter
if [ -f ".claude/agents/docs-reviewer.md" ]; then
  python3 -c "
import re
with open('.claude/agents/docs-reviewer.md') as f:
    content = f.read()
checks = {
    'name': bool(re.search(r'^name:', content, re.MULTILINE)),
    'description': bool(re.search(r'^description:', content, re.MULTILINE)),
}
for field, ok in checks.items():
    print(f'  {\"PASS\" if ok else \"FAIL\"}: frontmatter has {field}')

# Check body has documentation-specific instructions
body = content.split('---', 2)[-1] if content.startswith('---') else content
doc_terms = ['docstring', 'comment', 'README', 'link', 'documentation']
found = [t for t in doc_terms if t.lower() in body.lower()]
if len(found) >= 3:
    print(f'  PASS: body covers documentation topics ({', '.join(found)})')
else:
    print(f'  FAIL: body should cover documentation topics (found: {', '.join(found)})')
" 2>/dev/null
fi
```

If the answers match, print:
```
Module 12 complete.

You can now use Claude Code's review agent system.
Key concepts:
  - Built-in agents: security-reviewer, patternfly-ui-ux-reviewer,
    devops-platform-engineer, container-specialist
  - Custom agents: .claude/agents/NAME.md with frontmatter and instructions
  - Agent definitions need: name, description (frontmatter) + review
    instructions with structured output format (body)
  - Agents run in isolated context — findings return to the main
    conversation without consuming context for intermediate work
  - Multiple agents can run in parallel for comprehensive reviews

Review patterns:
  Direct parallel   — spawn 2+ agents, get independent findings
  Team lead          — coordinator dispatches relevant specialists
  Sequential         — one agent identifies areas, next deep-dives

When to use agents vs manual review:
  Agents     — repeatable checks, standard criteria, large codebases
  Manual     — nuanced judgment, architectural decisions, trade-offs

Next module: /learn-13-agent-teams-vs-superpowers
```
