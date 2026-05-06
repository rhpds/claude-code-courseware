# Plugin Repackaging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repackage claude-code-courseware as a Claude Code plugin installable from rhpds-marketplace while keeping the existing clone-and-use workflow unchanged.

**Architecture:** Overlay pattern -- add `.claude-plugin/plugin.json` for the plugin manifest and `skills/*/SKILL.md` for plugin-mode dispatchers alongside the existing `.claude/commands/` clone-mode dispatchers. Both modes share the same `modules/` content via relative paths. RHDP reference data stays in `references/context.md` with a fork-friendly comment added.

**Tech Stack:** Markdown (SKILL.md with YAML frontmatter), JSON (plugin.json), shell (build-module updates)

---

## File Structure

### New Files

| File | Responsibility |
|------|---------------|
| `.claude-plugin/plugin.json` | Plugin identity -- name, version, description, author, license |
| `skills/courseware/SKILL.md` | Plugin-mode catalog dispatcher (mirrors `.claude/commands/courseware.md`) |
| `skills/learn-01-vertex-setup/SKILL.md` | Plugin-mode dispatcher for Module 01 |
| `skills/learn-02-atlassian-mcp/SKILL.md` | Plugin-mode dispatcher for Module 02 |
| `skills/learn-03-memory-mcp/SKILL.md` | Plugin-mode dispatcher for Module 03 |
| `skills/learn-04-git-mcp/SKILL.md` | Plugin-mode dispatcher for Module 04 |
| `skills/learn-05-writing-claude-md/SKILL.md` | Plugin-mode dispatcher for Module 05 |
| `skills/learn-06-playwright-mcp/SKILL.md` | Plugin-mode dispatcher for Module 06 |
| `skills/learn-07-writing-custom-skills/SKILL.md` | Plugin-mode dispatcher for Module 07 |
| `skills/learn-08-hivemind-knowledge-base/SKILL.md` | Plugin-mode dispatcher for Module 08 |
| `skills/learn-11-building-mcp-servers/SKILL.md` | Plugin-mode dispatcher for Module 11 |
| `skills/learn-12-review-agents/SKILL.md` | Plugin-mode dispatcher for Module 12 |
| `skills/learn-13-red-hat-quick-deck/SKILL.md` | Plugin-mode dispatcher for Module 13 |
| `skills/build-module/SKILL.md` | Plugin-mode dispatcher for module authoring |
| `docs/fork-your-own.md` | Fork guide for external teams |

### Modified Files

| File | Change |
|------|--------|
| `.claude/commands/references/context.md` | Add fork-friendly comment block at top |
| `.claude/commands/build-module.md` | Add step to also generate `skills/*/SKILL.md` |
| `README.md` | Add plugin install path alongside existing clone instructions |

---

### Task 1: Create plugin manifest

**Files:**
- Create: `.claude-plugin/plugin.json`

- [ ] **Step 1: Create the `.claude-plugin/` directory and `plugin.json`**

```json
{
  "name": "claude-code-courseware",
  "description": "Interactive learning modules for Claude Code — MCP servers, skills, agents, and more",
  "version": "1.0.0",
  "author": { "name": "RHDP Team" },
  "repository": "https://github.com/rhpds/claude-code-courseware",
  "license": "Apache-2.0",
  "keywords": ["courseware", "training", "learning", "mcp", "skills"]
}
```

- [ ] **Step 2: Validate the JSON is parseable**

Run: `python3 -c "import json; json.load(open('.claude-plugin/plugin.json')); print('valid')"`
Expected: `valid`

- [ ] **Step 3: Commit**

```bash
git add .claude-plugin/plugin.json
git commit -m "add plugin manifest for marketplace distribution"
```

---

### Task 2: Create the courseware catalog skill

**Files:**
- Create: `skills/courseware/SKILL.md`
- Reference: `.claude/commands/courseware.md` (read for content to mirror)

- [ ] **Step 1: Create `skills/courseware/SKILL.md`**

The catalog skill must contain the same module listing as `.claude/commands/courseware.md` but wrapped in SKILL.md frontmatter. The content references modules via `/learn-*` commands which resolve to skills in plugin mode.

```markdown
---
name: courseware
description: "Claude Code Courseware — browse the module catalog and pick a learning module to start"
---

# Claude Code Courseware

Display the module catalog below, then ask the user which module they'd like to start.

## Catalog

Print this catalog:

` ` `
Claude Code Courseware — Learning Modules
==========================================

  01  Claude Code + Vertex AI Setup          ~10 min
      Install Claude Code and configure Vertex AI as the backend provider.
      Prerequisites: Mac or Linux, Red Hat GCP account

  02  Atlassian MCP Server (Jira)            ~5 min
      Connect Claude Code to Jira via the Atlassian Rovo MCP server.
      Prerequisites: Module 01

  03  Memory MCP                             ~10 min
      Persistent knowledge graph for cross-session memory.
      Prerequisites: Module 01

  04  Git MCP                                ~10 min
      Structured Git operations via MCP for status, history, and diffs.
      Prerequisites: Module 01

  05  Writing CLAUDE.md                      ~15 min
      Write project instructions that shape Claude Code's behavior.
      Prerequisites: Module 01

  06  Playwright MCP                         ~10 min
      Browser automation and visual testing via the Playwright MCP server.
      Prerequisites: Module 01

  07  Writing Custom Skills                  ~20 min
      Create skills for repeatable workflows.
      Prerequisites: Module 01

  08  Hivemind Knowledge Base                ~15 min
      Contribute to and search the team's shared Hive Mind knowledge base.
      Prerequisites: Module 01, GitHub access to rhpds org (RHDP Team only)

  11  Building MCP Servers                   ~30 min
      Build a custom MCP server in Python and register it with Claude Code.
      Prerequisites: Module 01, Module 04 recommended

  12  Review Agents                          ~15 min
      Use Claude Code's agent system for specialized code reviews.
      Prerequisites: Module 01, Module 07 recommended

  ---  Coming Soon  ---

  10  Workshop Intake                        ~15 min

  13  Red Hat Quick Deck                     ~10 min
      Generate branded HTML slide presentations with the Quick Deck skill.
      Prerequisites: Module 01

To start a module, type: /learn-01-vertex-setup
Tab completion works after typing /learn-
` ` `

After printing the catalog, ask:
> "Which module would you like to start? You can type the number or the full command."

If the user picks a module number, tell them to run the corresponding `/learn-NN-*` command.
If they pick a "Coming Soon" module (10), tell them it's not yet available and suggest other modules.
```

Note: The triple backticks above are escaped with spaces for embedding. In the actual file, use normal triple backticks.

- [ ] **Step 2: Verify the SKILL.md frontmatter is valid YAML**

Run: `python3 -c "import yaml; data=open('skills/courseware/SKILL.md').read(); fm=data.split('---')[1]; yaml.safe_load(fm); print('valid')"`
Expected: `valid`

- [ ] **Step 3: Commit**

```bash
git add skills/courseware/SKILL.md
git commit -m "add courseware catalog skill for plugin mode"
```

---

### Task 3: Create all 11 learn-* dispatcher skills

**Files:**
- Create: `skills/learn-01-vertex-setup/SKILL.md`
- Create: `skills/learn-02-atlassian-mcp/SKILL.md`
- Create: `skills/learn-03-memory-mcp/SKILL.md`
- Create: `skills/learn-04-git-mcp/SKILL.md`
- Create: `skills/learn-05-writing-claude-md/SKILL.md`
- Create: `skills/learn-06-playwright-mcp/SKILL.md`
- Create: `skills/learn-07-writing-custom-skills/SKILL.md`
- Create: `skills/learn-08-hivemind-knowledge-base/SKILL.md`
- Create: `skills/learn-11-building-mcp-servers/SKILL.md`
- Create: `skills/learn-12-review-agents/SKILL.md`
- Create: `skills/learn-13-red-hat-quick-deck/SKILL.md`

Each SKILL.md follows the same pattern: YAML frontmatter (`name` and `description`) followed by the same body as the corresponding `.claude/commands/learn-*.md` dispatcher, but with paths adjusted to be relative from `skills/learn-*/SKILL.md` (two levels up to repo root).

- [ ] **Step 1: Create `skills/learn-01-vertex-setup/SKILL.md`**

```markdown
---
name: learn-01-vertex-setup
description: "Claude Code + Vertex AI Setup — install and configure Vertex AI (~10 min)"
---

# Claude Code + Vertex AI Setup

Install Claude Code and configure Vertex AI as the backend provider.
Estimated time: 10 minutes.

Read and follow the module at `../../modules/01-vertex-setup.md` step by step.

Start with the Orientation section, then run the Preflight checks.
Skip any step where the prerequisite already exists.
Guide the user through each remaining step, then run Verification.
Finish with the Challenge.

Use `../../.claude/commands/references/context.md` for team-specific values.
```

- [ ] **Step 2: Create `skills/learn-02-atlassian-mcp/SKILL.md`**

```markdown
---
name: learn-02-atlassian-mcp
description: "Atlassian MCP Server (Jira) — connect Claude Code to Jira (~5 min). Prerequisites: Module 01"
---

# Atlassian MCP Server (Jira)

Connect Claude Code to Jira via the Atlassian Rovo MCP server.
Estimated time: 5 minutes. Prerequisites: Module 01.

Read and follow the module at `../../modules/02-atlassian-mcp.md` step by step.

Start with the Orientation section, then run the Preflight checks.
Skip any step where the prerequisite already exists.
Guide the user through each remaining step, then run Verification.
Finish with the Challenge.

Use `../../.claude/commands/references/context.md` for team-specific values.
```

- [ ] **Step 3: Create `skills/learn-03-memory-mcp/SKILL.md`**

```markdown
---
name: learn-03-memory-mcp
description: "Memory MCP — persistent knowledge graph for cross-session memory (~10 min). Prerequisites: Module 01"
---

# Memory MCP

Persistent knowledge graph for Claude Code using the Memory MCP server.
Estimated time: 10 minutes. Prerequisites: Module 01.

Read and follow the module at `../../modules/03-memory-mcp.md` step by step.

Start with the Orientation section, then run the Preflight checks.
Skip any step where the prerequisite already exists.
Guide the user through each remaining step, then run Verification.
Finish with the Challenge.

Use `../../.claude/commands/references/context.md` for team-specific values.
```

- [ ] **Step 4: Create `skills/learn-04-git-mcp/SKILL.md`**

```markdown
---
name: learn-04-git-mcp
description: "Git MCP — structured Git operations via MCP (~10 min). Prerequisites: Module 01"
---

# Git MCP

Git operations via the Git MCP server for structured repository access.
Estimated time: 10 minutes. Prerequisites: Module 01.

Read and follow the module at `../../modules/04-git-mcp.md` step by step.

Start with the Orientation section, then run the Preflight checks.
Skip any step where the prerequisite already exists.
Guide the user through each remaining step, then run Verification.
Finish with the Challenge.

Use `../../.claude/commands/references/context.md` for team-specific values.
```

- [ ] **Step 5: Create `skills/learn-05-writing-claude-md/SKILL.md`**

```markdown
---
name: learn-05-writing-claude-md
description: "Writing CLAUDE.md — project instructions that shape Claude Code's behavior (~15 min). Prerequisites: Module 01"
---

# Writing CLAUDE.md

Write project instructions that shape Claude Code's behavior in every session.
Estimated time: 15 minutes. Prerequisites: Module 01.

Read and follow the module at `../../modules/05-writing-claude-md.md` step by step.

Start with the Orientation section, then run the Preflight checks.
Skip any step where the prerequisite already exists.
Guide the user through each remaining step, then run Verification.
Finish with the Challenge.

Use `../../.claude/commands/references/context.md` for team-specific values.
```

- [ ] **Step 6: Create `skills/learn-06-playwright-mcp/SKILL.md`**

```markdown
---
name: learn-06-playwright-mcp
description: "Playwright MCP — browser automation and visual testing (~10 min). Prerequisites: Module 01"
---

# Playwright MCP

Browser automation and visual testing via the Playwright MCP server.
Estimated time: 10 minutes. Prerequisites: Module 01.

Read and follow the module at `../../modules/06-playwright-mcp.md` step by step.

Start with the Orientation section, then run the Preflight checks.
Skip any step where the prerequisite already exists.
Guide the user through each remaining step, then run Verification.
Finish with the Challenge.

Use `../../.claude/commands/references/context.md` for team-specific values.
```

- [ ] **Step 7: Create `skills/learn-07-writing-custom-skills/SKILL.md`**

```markdown
---
name: learn-07-writing-custom-skills
description: "Writing Custom Skills — create skills for repeatable workflows (~20 min). Prerequisites: Module 01"
---

# Writing Custom Skills

Create Claude Code skills for repeatable workflows.
Estimated time: 20 minutes. Prerequisites: Module 01.

Read and follow the module at `../../modules/07-writing-custom-skills.md` step by step.

Start with the Orientation section, then run the Preflight checks.
Skip any step where the prerequisite already exists.
Guide the user through each remaining step, then run Verification.
Finish with the Challenge.

Use `../../.claude/commands/references/context.md` for team-specific values.
```

- [ ] **Step 8: Create `skills/learn-08-hivemind-knowledge-base/SKILL.md`**

```markdown
---
name: learn-08-hivemind-knowledge-base
description: "Hivemind Knowledge Base — contribute to and search shared team knowledge (~15 min). Prerequisites: Module 01, rhpds org access"
---

# Hivemind Knowledge Base

Contribute to and search the team's shared Hive Mind knowledge base.
Estimated time: 15 minutes. Prerequisites: Module 01, GitHub access to rhpds org.

Read and follow the module at `../../modules/08-hivemind-knowledge-base.md` step by step.

Start with the Orientation section, then run the Preflight checks.
Skip any step where the prerequisite already exists.
Guide the user through each remaining step, then run Verification.
Finish with the Challenge.

Use `../../.claude/commands/references/context.md` for team-specific values.
```

- [ ] **Step 9: Create `skills/learn-11-building-mcp-servers/SKILL.md`**

```markdown
---
name: learn-11-building-mcp-servers
description: "Building MCP Servers — build a custom MCP server in Python (~30 min). Prerequisites: Module 01, Module 04 recommended"
---

# Building MCP Servers

Build a custom MCP server in Python and register it with Claude Code.
Estimated time: 30 minutes. Prerequisites: Module 01, Module 04 recommended.

Read and follow the module at `../../modules/11-building-mcp-servers.md` step by step.

Start with the Orientation section, then run the Preflight checks.
Skip any step where the prerequisite already exists.
Guide the user through each remaining step, then run Verification.
Finish with the Challenge.

Use `../../.claude/commands/references/context.md` for team-specific values.
```

- [ ] **Step 10: Create `skills/learn-12-review-agents/SKILL.md`**

```markdown
---
name: learn-12-review-agents
description: "Review Agents — use Claude Code's agent system for specialized code reviews (~15 min). Prerequisites: Module 01, Module 07 recommended"
---

# Review Agents

Use Claude Code's agent system for specialized code reviews and custom review agents.
Estimated time: 15 minutes. Prerequisites: Module 01, Module 07 recommended.

Read and follow the module at `../../modules/12-review-agents.md` step by step.

Start with the Orientation section, then run the Preflight checks.
Skip any step where the prerequisite already exists.
Guide the user through each remaining step, then run Verification.
Finish with the Challenge.

Use `../../.claude/commands/references/context.md` for team-specific values.
```

- [ ] **Step 11: Create `skills/learn-13-red-hat-quick-deck/SKILL.md`**

```markdown
---
name: learn-13-red-hat-quick-deck
description: "Red Hat Quick Deck — generate branded HTML slide presentations (~10 min). Prerequisites: Module 01"
---

# Red Hat Quick Deck

Generate branded HTML slide presentations with the Red Hat Quick Deck skill.
Estimated time: 10 minutes. Prerequisites: Module 01.

Read and follow the module at `../../modules/13-red-hat-quick-deck.md` step by step.

Start with the Orientation section, then run the Preflight checks.
Skip any step where the prerequisite already exists.
Guide the user through each remaining step, then run Verification.
Finish with the Challenge.

Use `../../.claude/commands/references/context.md` for team-specific values.
```

- [ ] **Step 12: Validate all SKILL.md frontmatter**

Run:
```bash
for f in skills/learn-*/SKILL.md; do
  python3 -c "import yaml; data=open('$f').read(); fm=data.split('---')[1]; yaml.safe_load(fm); print('OK: $f')" 2>&1
done
```
Expected: `OK` for all 11 files.

- [ ] **Step 13: Commit**

```bash
git add skills/learn-*/SKILL.md
git commit -m "add learn-* dispatcher skills for plugin mode"
```

---

### Task 4: Create the build-module dispatcher skill

**Files:**
- Create: `skills/build-module/SKILL.md`
- Reference: `.claude/commands/build-module.md` (read for content to mirror)

- [ ] **Step 1: Create `skills/build-module/SKILL.md`**

```markdown
---
name: build-module
description: "Build a new courseware module — generates module content, dispatchers, and catalog entries"
---

# Build a New Courseware Module

You are building a new learning module for the claude-code-courseware project.

## Instructions

1. Ask: "Which module number and topic?" (e.g., "03 — Memory MCP")
   If the user already specified it, skip this question.

2. Read `../../modules/TEMPLATE.md` for the exact structure to follow.

3. Read `../../.claude/commands/references/context.md` for team-specific values.

4. Ask: "Any specific source material I should read?" (e.g., a repo path, skill file, or MCP server docs)
   If the user provides a path, read it for content. If not, use your built-in knowledge of the tool.

5. Generate four files:

   **Module content** — `../../modules/NN-TOPIC.md`
   Follow TEMPLATE.md exactly. Fill in every placeholder. Every bash check must be
   a real, runnable command. Every step must have skip-if logic, user instructions
   (system-modifying via `!` prefix), and a verification command.

   **Dispatcher command** — `../../.claude/commands/learn-NN-TOPIC.md`
   Use this exact pattern (swap title, description, time, prerequisites, filename):
   ```
   # TITLE

   DESCRIPTION.
   Estimated time: X minutes. Prerequisites: LIST.

   Read and follow the module at `modules/NN-TOPIC.md` step by step.

   Start with the Orientation section, then run the Preflight checks.
   Skip any step where the prerequisite already exists.
   Guide the user through each remaining step, then run Verification.
   Finish with the Challenge.

   Use `.claude/commands/references/context.md` for team-specific values.
   ```

   **Dispatcher skill** — `../../skills/learn-NN-TOPIC/SKILL.md`
   Use this exact pattern (swap name, description, title, time, prerequisites, filename):
   ```
   ---
   name: learn-NN-TOPIC
   description: "TITLE — DESCRIPTION (~X min). Prerequisites: LIST"
   ---

   # TITLE

   DESCRIPTION.
   Estimated time: X minutes. Prerequisites: LIST.

   Read and follow the module at `../../modules/NN-TOPIC.md` step by step.

   Start with the Orientation section, then run the Preflight checks.
   Skip any step where the prerequisite already exists.
   Guide the user through each remaining step, then run Verification.
   Finish with the Challenge.

   Use `../../.claude/commands/references/context.md` for team-specific values.
   ```

   **Update catalog** — Edit `../../.claude/commands/courseware.md`
   AND edit `../../skills/courseware/SKILL.md`
   Move the module from "Coming Soon" to the active section above it.
   Add the full entry with description and prerequisites.

6. Update `../../README.md` — Move the module from the "Coming Soon" table to the
   "Modules" table.

7. Commit each file separately with plain English commit messages (no prefixes, no emojis):
   - `git add modules/NN-TOPIC.md && git commit -m "add Module NN — TITLE"`
   - `git add .claude/commands/learn-NN-TOPIC.md skills/learn-NN-TOPIC/SKILL.md && git commit -m "add /learn-NN-TOPIC dispatchers"`
   - `git add .claude/commands/courseware.md skills/courseware/SKILL.md README.md && git commit -m "update catalog and README for Module NN"`

8. Report what was created and suggest `git push origin main` for the user to approve.
```

- [ ] **Step 2: Validate frontmatter**

Run: `python3 -c "import yaml; data=open('skills/build-module/SKILL.md').read(); fm=data.split('---')[1]; yaml.safe_load(fm); print('valid')"`
Expected: `valid`

- [ ] **Step 3: Commit**

```bash
git add skills/build-module/SKILL.md
git commit -m "add build-module skill for plugin mode"
```

---

### Task 5: Update build-module command to generate both dispatcher formats

**Files:**
- Modify: `.claude/commands/build-module.md`

- [ ] **Step 1: Read the current build-module.md**

Run: `cat .claude/commands/build-module.md`

Confirm it currently generates only `.claude/commands/learn-NN-TOPIC.md`.

- [ ] **Step 2: Update `.claude/commands/build-module.md`**

Replace step 5 (which currently says "Generate three files") to say "Generate four files" and add the SKILL.md generation instruction. Replace step 7 commit instructions to group command and skill dispatchers together. Full updated content:

```markdown
# Build a New Courseware Module

You are building a new learning module for the claude-code-courseware project.

## Instructions

1. Ask: "Which module number and topic?" (e.g., "03 — Memory MCP")
   If the user already specified it, skip this question.

2. Read `modules/TEMPLATE.md` for the exact structure to follow.

3. Read `.claude/commands/references/context.md` for team-specific values.

4. Ask: "Any specific source material I should read?" (e.g., a repo path, skill file, or MCP server docs)
   If the user provides a path, read it for content. If not, use your built-in knowledge of the tool.

5. Generate four files:

   **Module content** — `modules/NN-TOPIC.md`
   Follow TEMPLATE.md exactly. Fill in every placeholder. Every bash check must be
   a real, runnable command. Every step must have skip-if logic, user instructions
   (system-modifying via `!` prefix), and a verification command.

   **Dispatcher command** — `.claude/commands/learn-NN-TOPIC.md`
   Use this exact pattern (swap title, description, time, prerequisites, filename):
   ```
   # TITLE

   DESCRIPTION.
   Estimated time: X minutes. Prerequisites: LIST.

   Read and follow the module at `modules/NN-TOPIC.md` step by step.

   Start with the Orientation section, then run the Preflight checks.
   Skip any step where the prerequisite already exists.
   Guide the user through each remaining step, then run Verification.
   Finish with the Challenge.

   Use `.claude/commands/references/context.md` for team-specific values.
   ```

   **Dispatcher skill** — `skills/learn-NN-TOPIC/SKILL.md`
   Use this exact pattern (swap name, description, title, time, prerequisites, filename):
   ```
   ---
   name: learn-NN-TOPIC
   description: "TITLE — DESCRIPTION (~X min). Prerequisites: LIST"
   ---

   # TITLE

   DESCRIPTION.
   Estimated time: X minutes. Prerequisites: LIST.

   Read and follow the module at `../../modules/NN-TOPIC.md` step by step.

   Start with the Orientation section, then run the Preflight checks.
   Skip any step where the prerequisite already exists.
   Guide the user through each remaining step, then run Verification.
   Finish with the Challenge.

   Use `../../.claude/commands/references/context.md` for team-specific values.
   ```

   **Update catalogs** — Edit both `.claude/commands/courseware.md` AND `skills/courseware/SKILL.md`
   Move the module from "Coming Soon" to the active section above it.
   Add the full entry with description and prerequisites.

6. Update `README.md` — Move the module from the "Coming Soon" table to the
   "Modules" table.

7. Commit each file separately with plain English commit messages (no prefixes, no emojis):
   - `git add modules/NN-TOPIC.md && git commit -m "add Module NN — TITLE"`
   - `git add .claude/commands/learn-NN-TOPIC.md skills/learn-NN-TOPIC/SKILL.md && git commit -m "add /learn-NN-TOPIC dispatchers"`
   - `git add .claude/commands/courseware.md skills/courseware/SKILL.md README.md && git commit -m "update catalog and README for Module NN"`

8. Report what was created and suggest `git push origin main` for the user to approve.
```

- [ ] **Step 3: Verify the updated file is valid markdown**

Run: `head -5 .claude/commands/build-module.md`
Expected: starts with `# Build a New Courseware Module`

- [ ] **Step 4: Commit**

```bash
git add .claude/commands/build-module.md
git commit -m "update build-module to generate both command and skill dispatchers"
```

---

### Task 6: Add fork-friendly comment to references/context.md

**Files:**
- Modify: `.claude/commands/references/context.md`

- [ ] **Step 1: Add the fork comment block**

Insert the following blockquote after the `# Courseware Context Reference` heading and before the `Shared reference data` line:

```markdown
> **Forking this repo?** Edit the values below for your organization.
> See `docs/fork-your-own.md` for the full customization guide.
```

The file should then start:

```markdown
# Courseware Context Reference

> **Forking this repo?** Edit the values below for your organization.
> See `docs/fork-your-own.md` for the full customization guide.

Shared reference data for all learning modules.
```

- [ ] **Step 2: Verify the edit**

Run: `head -6 .claude/commands/references/context.md`
Expected: heading, blank line, blockquote (2 lines), blank line, "Shared reference data"

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/references/context.md
git commit -m "add fork-friendly comment to context reference"
```

---

### Task 7: Write the fork guide

**Files:**
- Create: `docs/fork-your-own.md`

- [ ] **Step 1: Create `docs/fork-your-own.md`**

```markdown
# Fork Your Own Courseware

This guide walks you through creating a customized version of Claude Code Courseware for your team.

## Quick Start

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone git@github.com:YOUR-ORG/claude-code-courseware.git
   cd claude-code-courseware
   ```
3. Edit `.claude/commands/references/context.md` with your organization's values
4. Start learning: `claude .` then `/courseware`

## What to Customize

### Reference Data (required)

Edit `.claude/commands/references/context.md` and replace the RHDP-specific values:

| Section | What to Change |
|---------|---------------|
| Team Environment | GCP project list URL, Vertex AI region |
| Atlassian Rovo MCP Server | Your Atlassian instance URL, Jira project key |
| Hivemind Knowledge Base | Your knowledge base repo (or remove this section) |

### Module Content (optional)

Modules in `modules/` reference your organization by name in some places.
Search for "Red Hat", "RHDP", and "rhpds" and replace with your org's names.
Modules that are specific to RHDP infrastructure (like Module 08 — Hivemind)
can be removed or replaced with your own team-specific modules.

### Adding or Removing Modules

Use the `/build-module` command to create new modules. It generates all
required files (module content, command dispatcher, skill dispatcher, catalog
entries) from a template.

To remove a module:
1. Delete `modules/NN-topic.md`
2. Delete `.claude/commands/learn-NN-topic.md`
3. Delete `skills/learn-NN-topic/SKILL.md`
4. Remove the entry from `.claude/commands/courseware.md`
5. Remove the entry from `skills/courseware/SKILL.md`
6. Remove the row from the table in `README.md`

## Distribution Options

### Clone Mode (simplest)

Share your fork URL. Users clone and run:
```bash
git clone git@github.com:YOUR-ORG/claude-code-courseware.git
cd claude-code-courseware
claude .
/courseware
```

### Plugin Mode (global install)

To distribute as a plugin, users add your fork as a marketplace source
in `~/.claude/marketplaces.json`:

```json
{
  "your-marketplace": {
    "org": "YOUR-ORG",
    "repo": "claude-code-courseware",
    "path": ".claude-plugin",
    "plugins": {
      "claude-code-courseware": {
        "name": "Claude Code Courseware",
        "description": "Your description here",
        "version": "1.0.0",
        "skills": ["courseware", "learn-01-vertex-setup", "..."]
      }
    }
  }
}
```

Then install:
```
claude plugin install claude-code-courseware --marketplace your-marketplace
```

The `/courseware` and `/learn-*` commands become available globally.
```

- [ ] **Step 2: Commit**

```bash
git add docs/fork-your-own.md
git commit -m "add fork-your-own guide for external teams"
```

---

### Task 8: Update README.md with plugin install path

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update the Getting Started section**

Replace the current "Getting Started" section with two install paths. The new section:

```markdown
## Getting Started

### Option A: Plugin Install (global)

If your team uses the rhpds-marketplace:

```
claude plugin install claude-code-courseware --marketplace rhpds-marketplace
```

Then from any directory:
```
/courseware
```

### Option B: Clone (project-scoped)

1. Clone this repo:
   ```bash
   git clone git@github.com:rhpds/claude-code-courseware.git
   cd claude-code-courseware
   ```

2. Launch Claude Code:
   ```bash
   claude .
   ```

3. See what's available:
   ```
   /courseware
   ```

4. Start a module:
   ```
   /learn-01-vertex-setup
   ```

Tab completion works after typing `/learn-` — it shows all available modules.
```

- [ ] **Step 2: Add a "Forking" section before the "Authoring New Modules" section**

Insert:

```markdown
## Forking for Your Team

Want to run this courseware for your own organization? See [Fork Your Own Courseware](docs/fork-your-own.md).
```

- [ ] **Step 3: Verify the README structure**

Run: `grep "^## " README.md`
Expected sections: Getting Started, Modules, Coming Soon (as a subsection), How Modules Work, Alternative Setup, Forking for Your Team, Authoring New Modules

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "update README with plugin install path and fork guide link"
```

---

### Task 9: Verify clone mode is unchanged

- [ ] **Step 1: Verify all existing dispatchers are untouched**

Run:
```bash
git diff HEAD -- .claude/commands/learn-*.md .claude/commands/courseware.md
```
Expected: no output (no changes to these files)

- [ ] **Step 2: Verify modules are untouched**

Run:
```bash
git diff HEAD -- modules/
```
Expected: no output (no changes to module content)

- [ ] **Step 3: Verify skill files exist for every dispatcher**

Run:
```bash
for cmd in .claude/commands/learn-*.md; do
  name=$(basename "$cmd" .md)
  if [ -f "skills/$name/SKILL.md" ]; then
    echo "OK: $name"
  else
    echo "MISSING: skills/$name/SKILL.md"
  fi
done
```
Expected: `OK` for all 11 learn-* names.

- [ ] **Step 4: Verify relative paths in skills resolve**

Run:
```bash
for f in skills/learn-*/SKILL.md; do
  dir=$(dirname "$f")
  module_path=$(grep -o '../../modules/[^ ]*' "$f" | head -1)
  resolved="$dir/$module_path"
  if [ -f "$resolved" ]; then
    echo "OK: $f -> $resolved"
  else
    echo "BROKEN: $f -> $resolved"
  fi
done
```
Expected: `OK` for all 11 files — each skill's relative path resolves to an existing module.

---

### Task 10: Marketplace registration (rhpds-utils — separate repo)

This task is in a different repository (`rhpds-utils`). It should be done after the courseware repo changes are pushed.

**Files:**
- Modify: `~/repos/rhpds-utils/marketplace/` (exact file TBD — depends on how the marketplace index is structured)

- [ ] **Step 1: Investigate the rhpds-marketplace index format**

Run:
```bash
ls ~/repos/rhpds-utils/marketplace/
cat ~/repos/rhpds-utils/marketplace/*.json 2>/dev/null || echo "check directory structure"
```

Determine how existing plugins (claude-pulse, rhdp-scheduler, rhdp-ops) are registered. The `marketplaces.json` on user machines references `path: "marketplace"` inside rhpds-utils, so the index file lives there.

- [ ] **Step 2: Add courseware entry**

The entry needs to reference the courseware repo cross-repo. Based on what's found in Step 1, either:
- Add a `source` field pointing to `github.com/rhpds/claude-code-courseware`
- Or add a git submodule/subtree at `plugins/claude-code-courseware`

The entry content:
```json
"claude-code-courseware": {
  "name": "Claude Code Courseware",
  "description": "Interactive learning modules for Claude Code — MCP servers, skills, agents, and more",
  "version": "1.0.0",
  "skills": [
    "courseware",
    "learn-01-vertex-setup",
    "learn-02-atlassian-mcp",
    "learn-03-memory-mcp",
    "learn-04-git-mcp",
    "learn-05-writing-claude-md",
    "learn-06-playwright-mcp",
    "learn-07-writing-custom-skills",
    "learn-08-hivemind-knowledge-base",
    "learn-11-building-mcp-servers",
    "learn-12-review-agents",
    "learn-13-red-hat-quick-deck",
    "build-module"
  ]
}
```

- [ ] **Step 3: Test plugin install**

Run:
```bash
claude plugin install claude-code-courseware --marketplace rhpds-marketplace
```

Then from a different directory:
```
/courseware
```

Verify the catalog displays and at least one `/learn-*` command loads its module.

- [ ] **Step 4: Commit in rhpds-utils**

```bash
cd ~/repos/rhpds-utils
git add marketplace/
git commit -m "add claude-code-courseware to rhpds-marketplace"
```
