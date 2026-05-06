# Getting Started with Claude Code Courseware

Two ways to install. Same 12 learning modules.

**RHDP Team** - May 2026
_RHDP Team - Red Hat_

---

## Slide 1 -- Title

Getting Started with **Claude Code Courseware**

Two ways to install. Same 12 learning modules. Clone for development, install as a plugin for instant access.

Tags: Plugin, Clone, 12 Modules, MCP Servers, Skills

---

## Slide 2 -- What Is Courseware?

Interactive, hands-on learning modules for Claude Code. Each module teaches a specific tool or integration through guided walkthroughs with built-in verification.

- **11 modules** covering MCP servers, CLAUDE.md, custom skills, review agents, and more
- **Self-paced** with preflight checks that skip what you already have
- **Real team data** in every challenge (RHDPOPS Jira, team MCP servers)
- **Two install modes** from the same repo: clone or plugin

> Contextual notes: The courseware repo lives at github.com/rhpds/claude-code-courseware. Each module is a guided walkthrough with preflight checks, step-by-step instructions, verification, and a hands-on challenge against real team data.

---

## Slide 3 -- Two Ways to Install

### Option A: Clone

Full repo access. Best for contributors and developers who want to modify modules or fork for their team.

```
git clone git@github.com:rhpds/claude-code-courseware.git
cd claude-code-courseware
claude .
```

### Option B: Plugin (Recommended)

Global install. Commands available from any directory. Best for learners who just want to start.

```
/plugin marketplace add rhpds/rhpds-utils/marketplace
/plugin install claude-code-courseware
```

> Contextual notes: Clone mode gives you the full repo with all files. Plugin mode installs just the skills globally so you can access /learn-* commands from any directory. Both read the same module content and reference data.

---

## Slide 4 -- Plugin Install Step by Step

1. **Register Marketplace** -- `/plugin marketplace add rhpds/rhpds-utils/marketplace`
2. **Install Plugin** -- `/plugin install claude-code-courseware`
3. **Browse Catalog** -- `/courseware`
4. **Start Learning** -- `/learn-01-vertex-setup`

Step 1 is one-time setup. After that, just `/plugin install` and go.

> Contextual notes: The plugin install workflow: register the marketplace (one-time), install the plugin, then use /courseware to browse and /learn-* to start any module.

---

## Slide 5 -- 12 Modules Available

**Foundations:**
01 Vertex AI Setup, 02 Atlassian MCP (Jira), 03 Memory MCP, 04 Git MCP, 05 Writing CLAUDE.md, 06 Playwright MCP

**Advanced:**
07 Writing Custom Skills, 08 Hivemind Knowledge Base, 11 Building MCP Servers, 12 Review Agents, 13 Red Hat Quick Deck, 14 Agent Teams vs Superpowers

---

## Slide 6 -- QA Results

- PASS: All 12 skill symlinks resolve to valid SKILL.md files
- PASS: All 12 module files reachable via relative paths
- PASS: Clone-mode dispatchers unchanged (zero diff)
- PASS: Module content files unchanged (zero diff)
- PASS: /courseware catalog displays correctly from global skill
- PASS: /learn-02-atlassian-mcp loads module and runs preflight
- PASS: Preflight checks execute for all modules

---

## Slide 7 -- Fork Your Own Courseware

All RHDP-specific data lives in a single file. Fork the repo, edit one file, and you have courseware for your own team.

File: `.claude/commands/references/context.md`

**Source:** Full guide at docs/fork-your-own.md

---

## Slide 8 -- Thank You

Start learning: `/courseware`

RHDP Team - Red Hat
