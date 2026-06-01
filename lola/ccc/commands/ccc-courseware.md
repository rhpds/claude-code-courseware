---
description: "Before displaying the catalog, run the update check and progress scan."
---

# Claude Code Courseware

Before displaying the catalog, run the update check and progress scan.

## Update Check

Run this check silently before printing the catalog:

```bash
PLUGIN_REPO="$HOME/.claude/plugins/claude-code-courseware/repo"
if [ -d "$PLUGIN_REPO/.git" ]; then
  git -C "$PLUGIN_REPO" fetch origin main --quiet 2>/dev/null
  LOCAL=$(git -C "$PLUGIN_REPO" rev-parse HEAD 2>/dev/null)
  REMOTE=$(git -C "$PLUGIN_REPO" rev-parse origin/main 2>/dev/null)
  if [ -n "$LOCAL" ] && [ -n "$REMOTE" ] && [ "$LOCAL" != "$REMOTE" ]; then
    BEHIND=$(git -C "$PLUGIN_REPO" rev-list HEAD..origin/main --count 2>/dev/null)
    echo "UPDATE AVAILABLE: courseware plugin is $BEHIND commit(s) behind."
    echo "  New or updated modules may be available."
    echo "  Run /ccc-update-courseware to get the latest content."
    echo ""
  fi
fi
```

If the update check prints "UPDATE AVAILABLE", show that message to the user before the catalog. Also append:

> Run `/ccc-update-courseware` to pull the latest content before starting a module.

## Progress Scan

Run this silently to detect completion/in-progress state:

```bash
PROGRESS_DIR="$HOME/.claude/ccc-courseware-progress"
if [ -d "$PROGRESS_DIR" ]; then
  for f in ../skills/[0-9]*.md; do
    n=$(basename "$f" | grep -o '^[0-9]*')
    if [ -f "$PROGRESS_DIR/$n.done" ]; then
      echo "DONE:$n"
    elif [ -f "$PROGRESS_DIR/$n.started" ]; then
      echo "IN_PROGRESS:$n"
    fi
  done
fi
```

Use the output to add status tags to the catalog. See the tag rules below.

## Catalog

Print the catalog using markdown (NOT inside a code block).

**Tag rules** (append after the duration, in this priority order):
- If the progress scan printed `DONE:NN` for a module, show `done`
- If the progress scan printed `IN_PROGRESS:NN`, show `in progress`
- If the module is in the NEW list below, show **NEW**
- Otherwise, no tag

**NEW modules:** Scan each module file for a `<!-- NEW -->` HTML comment. If present, that module gets the **NEW** tag. This replaces the hardcoded list.

## Claude Code Courseware

### Setup & Foundation
`01`  Vertex AI Setup · 10 min
`02`  Writing CLAUDE.md · 15 min

### Core MCP Servers
`03`  Memory MCP · 10 min
`04`  Git MCP · 10 min
`05`  Atlassian MCP (Jira) · 5 min
`06`  Playwright MCP · 10 min
`07`  Notion MCP · 15 min
`08`  Container & Podman MCP · 15 min

### Skills & Customization
`09`  Writing Custom Skills · 15 min
`10`  Hooks · 15 min
`21`  Plugin Marketplace · 15 min

### Security
`24`  Security-First Development · 15 min
`25`  Security Scanning & Vulnerability Research · 20 min

### Advanced Patterns
`11`  Building MCP Servers · 30 min
`12`  Review Agents · 15 min
`13`  Agent Teams vs Superpowers · 15 min
`26`  Claude Agent SDK · 25 min

### Parallel & Autonomous Workflows
`22`  Git Worktrees · 15 min
`23`  Background Agents & Goal Mode · 15 min

### Workflow & Operations
`14`  Debugging & Troubleshooting · 15 min
`15`  Cost & Context Management · 15 min
`16`  Multi-Repo Workspaces · 15 min
`17`  CI/CD Integration · 15 min
`18`  Profile Cleanup · 15 min
`27`  Checkpointing & Session Management · 10 min
`28`  Voice, Vim & Terminal Customization · 10 min
`29`  Effort & Reasoning Control · 10 min

### Team-Customizable
`19`  Red Hat Quick Deck · 10 min
`20`  Hivemind Knowledge Base · 15 min

## Recommended Paths

After the catalog, show the role-based recommendations:

> **Not sure where to start?** Here are suggested paths by role:
>
> **Developer:** 01, 02, 03, 04, 06, 09, 24 -- environment setup, daily tools, and security-first habits.
>
> **Ops engineer:** 01, 02, 03, 05, 08, 10, 14, 24 -- Jira integration, containers, hooks, debugging, security.
>
> **Security-focused:** 01, 02, 24, 25, 10, 17 -- security modules, hooks for guardrails, CI/CD scanning.
>
> **Team lead / manager:** 01, 02, 15, 24 -- setup, project config, cost management, security awareness.
>
> **Power user (all modules):** start at 01 and go in order. Each module builds on the previous ones.

## Footer

After the recommendations, print:

> **[COUNT] modules available.** Modules marked **NEW** were recently added.
>
> Where [COUNT] is computed by counting `../skills/[0-9]*.md` files excluding TEMPLATE.md:
> ```bash
> ls ../skills/[0-9]*.md | wc -l | tr -d ' '
> ```
>
> Pick a **number** to jump into a module, or ask about a **section** (like "tell me about Core MCP Servers") to see descriptions and prerequisites before choosing. You can also type `/learn-` then Tab to see all modules, `/ccc-quick-install` to install MCP servers or plugins without a tutorial, or `/ccc-preflight` to check your prerequisites.
>
> **RHDP ops tools** (Flow, showroom QA, workshop intake) have moved to their own plugin.
> Install with: `claude plugin add github:rhpds/rhdp-ops-tools` then run `/ops-courseware`.
>
> Questions? Open an issue at [github.com/rhpds/claude-code-courseware/issues](https://github.com/rhpds/claude-code-courseware/issues).

## On Request: Expanded Section View

When the user asks for details about a specific section (by name, number range, or "full catalog" / "show all"), print the requested section(s) in this expanded format:

**Section 1 -- Setup & Foundation (01-02)**

**`01` Vertex AI Setup** -- ~10 min
Install Claude Code and configure Vertex AI as the backend provider.
*Prereq: Mac or Linux, Red Hat GCP account*

**`02` Writing CLAUDE.md** -- ~15 min
Write project instructions that shape Claude Code's behavior.
*Prereq: Module 01*

**Section 2 -- Core MCP Servers (03-08)**

**`03` Memory MCP** -- ~10 min
Persistent knowledge graph for cross-session memory.
*Prereq: Module 01*

**`04` Git MCP** -- ~10 min
Structured Git operations via MCP for status, history, and diffs.
*Prereq: Module 01*

**`05` Atlassian MCP (Jira)** -- ~5 min
Connect Claude Code to Jira via the Atlassian Rovo MCP server.
*Prereq: Module 01*

**`06` Playwright MCP** -- ~10 min
Browser automation and visual testing via the Playwright MCP server.
*Prereq: Module 01*

**`07` Notion MCP** -- ~15 min · **NEW**
Connect Claude Code to Notion for pages, databases, and search.
*Prereq: Module 01*

**`08` Container & Podman MCP** -- ~15 min · **NEW**
Build, run, inspect, and debug containers from Claude Code.
*Prereq: Module 01, container runtime (Podman or Docker)*

**Section 3 -- Skills & Customization (09-10, 21)**

**`09` Writing Custom Skills** -- ~15 min
Create skills for repeatable workflows. Covers unified skills model, plugin packaging, and skill budget.
*Prereq: Module 01*

**`10` Hooks** -- ~15 min
Pre/post command hooks for guardrails and automation.
*Prereq: Module 01*

**`21` Plugin Marketplace** -- ~15 min
Discover, install, and manage Claude Code plugins from marketplace registries.
*Prereq: Module 01, Module 09 recommended*

**Section 4 -- Security (24-25)**

**`24` Security-First Development** -- ~15 min
Install the security-guidance plugin, run /security-review, write OWASP-aware CLAUDE.md rules, and set up pre-commit security hooks.
*Prereq: Module 01*

**`25` Security Scanning & Vulnerability Research** -- ~20 min
Anthropic Mythos context, Claude Security scanning, triaging findings, Jira integration, SAST vs LLM audit comparison.
*Prereq: Module 01, Module 24 recommended*

**Section 5 -- Advanced Patterns (11-13, 26)**

**`11` Building MCP Servers** -- ~30 min
Build a custom MCP server in Python and register it with Claude Code. Covers streamable HTTP transport and MCP elicitation.
*Prereq: Module 01, Module 04 recommended*

**`12` Review Agents** -- ~15 min
Use Claude Code's agent system for specialized code reviews.
*Prereq: Module 01, Module 09 recommended*

**`13` Agent Teams vs Superpowers** -- ~15 min
Compare multi-agent coordination patterns for reviews and implementation.
*Prereq: Module 01, Module 12 recommended*

**`26` Claude Agent SDK** -- ~25 min
Build custom agents with the Agent SDK in Python or TypeScript. Covers tools, hooks, MCP, subagents, cost control, and production patterns.
*Prereq: Module 01, Module 11 recommended*

**Section 6 -- Parallel & Autonomous Workflows (22-23)**

**`22` Git Worktrees** -- ~15 min
Isolated workspaces for parallel development. Covers claude --worktree, .worktreeinclude, subagent isolation, and cleanup.
*Prereq: Module 01*

**`23` Background Agents & Goal Mode** -- ~15 min
Background sessions, agent view, /goal for outcome-based execution, /loop for recurring tasks, composing autonomous patterns.
*Prereq: Module 01*

**Section 7 -- Workflow & Operations (14-18, 27-29)**

**`14` Debugging & Troubleshooting** -- ~15 min
What to do when things go wrong -- MCP failures, tool errors, context issues.
*Prereq: Module 01*

**`15` Cost & Context Management** -- ~15 min
Session budgets, /usage, fast mode, auto-compaction settings, prompt caching, and June 2026 billing changes.
*Prereq: Module 01*

**`16` Multi-Repo Workspaces** -- ~15 min
Configure Claude Code across multiple repositories.
*Prereq: Module 01*

**`17` CI/CD Integration** -- ~15 min
GitHub Actions (claude-code-action), Cloud Routines, GitLab CI/CD, OpenShift Pipelines, and billing notes.
*Prereq: Module 01*

**`18` Profile Cleanup** -- ~15 min
Audit and clean ~/.claude/ for duplicate skills, orphaned plugins, and context bloat.
*Prereq: Module 01*

**`27` Checkpointing & Session Management** -- ~10 min
Esc+Esc rewind (conversation/code/both), session resume, auto mode, /branch, and permission customization.
*Prereq: Module 01*

**`28` Voice, Vim & Terminal Customization** -- ~10 min
Voice dictation, vim keybindings, custom themes, keybinding customization, fullscreen TUI, and output styles.
*Prereq: Module 01*

**`29` Effort & Reasoning Control** -- ~10 min · **NEW**
Control how hard Claude thinks per task with effort levels -- scoped to the team's Vertex models (Opus 4.6 / Sonnet 4.5, no xhigh). Covers /effort, the six ways to set it, per-skill effort frontmatter, ultrathink vs ultracode, and the Vertex capabilities gotcha.
*Prereq: Module 01, Module 15 recommended*

**Section 8 -- Team-Customizable (19-20)**

**`19` Red Hat Quick Deck** -- ~10 min
Generate branded HTML slide presentations with the Quick Deck skill.
*Prereq: Module 01, GitHub access to rhpds org*

**`20` Hivemind Knowledge Base** -- ~15 min
Contribute to and search the team's shared knowledge base.
*Prereq: Module 01, GitHub access to rhpds org*

## Module Routing

When the user picks a module, tell them to run the corresponding command:

| Module | Command |
|--------|---------|
| 01 | `/ccc-learn-01-vertex-setup` |
| 02 | `/ccc-learn-02-writing-claude-md` |
| 03 | `/ccc-learn-03-memory-mcp` |
| 04 | `/ccc-learn-04-git-mcp` |
| 05 | `/ccc-learn-05-atlassian-mcp` |
| 06 | `/ccc-learn-06-playwright-mcp` |
| 07 | `/ccc-learn-07-notion-mcp` |
| 08 | `/ccc-learn-08-container-podman-mcp` |
| 09 | `/ccc-learn-09-writing-custom-skills` |
| 10 | `/ccc-learn-10-hooks` |
| 11 | `/ccc-learn-11-building-mcp-servers` |
| 12 | `/ccc-learn-12-review-agents` |
| 13 | `/ccc-learn-13-agent-teams-vs-superpowers` |
| 14 | `/ccc-learn-14-debugging-troubleshooting` |
| 15 | `/ccc-learn-15-cost-context-management` |
| 16 | `/ccc-learn-16-multi-repo-workspaces` |
| 17 | `/ccc-learn-17-ci-cd-integration` |
| 18 | `/ccc-learn-18-profile-cleanup` |
| 19 | `/ccc-learn-19-red-hat-quick-deck` |
| 20 | `/ccc-learn-20-hivemind-knowledge-base` |
| 21 | `/ccc-learn-21-plugin-marketplace` |
| 22 | `/ccc-learn-22-git-worktrees` |
| 23 | `/ccc-learn-23-background-agents-goal-mode` |
| 24 | `/ccc-learn-24-security-first-development` |
| 25 | `/ccc-learn-25-security-scanning-vulnerability-research` |
| 26 | `/ccc-learn-26-claude-agent-sdk` |
| 27 | `/ccc-learn-27-checkpointing-session-management` |
| 28 | `/ccc-learn-28-voice-vim-terminal-customization` |
| 29 | `/ccc-learn-29-effort-reasoning-control` |
