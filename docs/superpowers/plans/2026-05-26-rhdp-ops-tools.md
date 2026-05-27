# rhdp-ops-tools Extraction Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract all RHDP ops tooling (Flow skills, showroom QA, learning modules 23-27) from claude-code-courseware into a new standalone repo `rhpds/rhdp-ops-tools`, then clean-remove the extracted content from courseware.

**Architecture:** Two-phase extraction. Phase 1 builds the new repo with domain-organized structure (`flow/` domain containing skills, modules, scripts). Phase 2 removes the extracted content from courseware and updates all references. Each phase produces a working state.

**Tech Stack:** Git, GitHub CLI (`gh`), Bash, Python 3, Claude Code plugin manifest

---

## File Structure (new repo: rhdp-ops-tools)

```
rhdp-ops-tools/
  .claude-plugin/plugin.json
  .claude/
    commands/
      courseware.md
      preflight.md
      learn-flow-01-rhdp-flow-mcp.md
      learn-flow-02-rhdp-flow-ops.md
      learn-flow-03-csv-pipeline.md
      learn-flow-04-deployment-intel.md
      learn-flow-05-event-scale-ops.md
      references/context.md
    settings.json
  flow/
    skills/
      flow-bulk.md
      flow-csv-pipeline.md
      flow-deploy.md
      flow-event-prep.md
      flow-ops.md
      flow-qa.md
      flow-report.md
      flow-showroom-qa.md
      flow-status.md
      flow-summit-deploy.md
    modules/
      01-rhdp-flow-mcp.md
      02-rhdp-flow-ops.md
      03-csv-pipeline.md
      04-deployment-intel.md
      05-event-scale-ops.md
    scripts/
      showroom-qa/
        showroom-qa-antora.py
        README.md
      setup-all.sh
  intake/
    skills/.gitkeep
    modules/.gitkeep
  docs/
    CONTRIBUTING.md
    TODO.md
  CLAUDE.md
  README.md
```

---

### Task 1: Create GitHub repo and scaffold directory structure

**Files:**
- Create: all directories and placeholder files in the new repo

- [ ] **Step 1: Create the GitHub repo**

```bash
gh repo create rhpds/rhdp-ops-tools --public --description "RHDP operations toolkit -- Flow workshop automation, showroom QA, and ops training modules" --license Apache-2.0 --clone
```

- [ ] **Step 2: Create the directory scaffold**

```bash
cd rhdp-ops-tools
mkdir -p .claude-plugin
mkdir -p .claude/commands/references
mkdir -p flow/skills flow/modules flow/scripts/showroom-qa
mkdir -p intake/skills intake/modules
mkdir -p docs
touch intake/skills/.gitkeep intake/modules/.gitkeep
```

- [ ] **Step 3: Create plugin manifest**

Write `.claude-plugin/plugin.json`:

```json
{
  "name": "rhdp-ops-tools",
  "description": "RHDP operations toolkit -- Flow workshop automation, showroom QA, and ops training modules",
  "version": "1.0.0",
  "author": { "name": "RHDP Team" },
  "repository": "https://github.com/rhpds/rhdp-ops-tools",
  "license": "Apache-2.0",
  "keywords": ["rhdp", "ops", "flow", "workshops", "qa"]
}
```

- [ ] **Step 4: Create .claude/settings.json with MCP server declarations**

Write `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(git *)",
      "Bash(python3 *)",
      "Bash(python3 -c *)",
      "Bash(pip install *)",
      "Bash(bash *)",
      "Bash(ls *)",
      "Bash(grep *)",
      "Bash(mkdir -p *)"
    ]
  },
  "mcpServers": {
    "rhdp-flow": {
      "command": "python3",
      "args": ["-m", "rhdp_flow_mcp"],
      "env": { "FLOW_API_URL": "http://localhost:8000" }
    },
    "rhdp-flow-csv": {
      "command": "python3",
      "args": ["-m", "rhdp_flow_csv"]
    },
    "rhdp-flow-intel": {
      "command": "python3",
      "args": ["-m", "rhdp_flow_intel"],
      "env": { "FLOW_API_URL": "http://localhost:8000" }
    }
  }
}
```

- [ ] **Step 5: Commit scaffold**

```bash
git add -A
git commit -m "scaffold repo structure with plugin manifest and MCP server configs"
```

---

### Task 2: Copy flow skills into new repo

**Files:**
- Create: `flow/skills/flow-bulk.md`, `flow/skills/flow-csv-pipeline.md`, `flow/skills/flow-deploy.md`, `flow/skills/flow-event-prep.md`, `flow/skills/flow-ops.md`, `flow/skills/flow-qa.md`, `flow/skills/flow-report.md`, `flow/skills/flow-showroom-qa.md`, `flow/skills/flow-status.md`, `flow/skills/flow-summit-deploy.md`
- Create: `flow/README.md`

- [ ] **Step 1: Copy all skill files from courseware**

Copy every file from `<courseware>/rhdp-flow-skills/skills/` to `flow/skills/` in the new repo. The skill files are self-contained markdown and require no path edits.

```bash
COURSEWARE="$HOME/repos/claude-code-courseware"
cp "$COURSEWARE"/rhdp-flow-skills/skills/*.md flow/skills/
```

- [ ] **Step 2: Copy flow README**

```bash
cp "$COURSEWARE/rhdp-flow-skills/README.md" flow/README.md
```

Then edit `flow/README.md` to update the install section -- replace references to `claude-code-courseware` with `rhdp-ops-tools`:

Old line: `Copy or symlink the skills/ directory into your Claude Code project, or install via the plugin manager.`

New line: `Install the rhdp-ops-tools plugin: claude plugin install rhpds/rhdp-ops-tools`

- [ ] **Step 3: Verify file count**

```bash
ls flow/skills/*.md | wc -l
# Expected: 10
```

- [ ] **Step 4: Commit**

```bash
git add flow/skills/ flow/README.md
git commit -m "add flow skills (10 skill files)"
```

---

### Task 3: Copy and transform flow modules

**Files:**
- Create: `flow/modules/01-rhdp-flow-mcp.md`, `flow/modules/02-rhdp-flow-ops.md`, `flow/modules/03-csv-pipeline.md`, `flow/modules/04-deployment-intel.md`, `flow/modules/05-event-scale-ops.md`

- [ ] **Step 1: Copy modules with renumbering**

```bash
COURSEWARE="$HOME/repos/claude-code-courseware"
cp "$COURSEWARE/modules/23-rhdp-flow-mcp.md"    flow/modules/01-rhdp-flow-mcp.md
cp "$COURSEWARE/modules/24-rhdp-flow-ops.md"    flow/modules/02-rhdp-flow-ops.md
cp "$COURSEWARE/modules/25-csv-pipeline.md"     flow/modules/03-csv-pipeline.md
cp "$COURSEWARE/modules/26-deployment-intel.md"  flow/modules/04-deployment-intel.md
cp "$COURSEWARE/modules/27-event-scale-ops.md"   flow/modules/05-event-scale-ops.md
```

- [ ] **Step 2: Update internal cross-references**

Search each module for references to old module numbers (23, 24, 25, 26, 27) and update them to new numbering (01, 02, 03, 04, 05). Also update any references to courseware module paths.

For each file in `flow/modules/`:
- Replace `Module 23` with `Module 01` (and similar for 24->02, 25->03, 26->04, 27->05)
- Replace `modules/23-` with `flow/modules/01-` (and similar)
- Replace `/learn-23-` with `/learn-flow-01-` (and similar)
- Remove any `<!-- NEW -->` HTML comments (these modules are the initial content in this repo)

Run:

```bash
cd flow/modules
for f in *.md; do
  sed -i '' \
    -e 's/Module 23/Module 01/g' \
    -e 's/Module 24/Module 02/g' \
    -e 's/Module 25/Module 03/g' \
    -e 's/Module 26/Module 04/g' \
    -e 's/Module 27/Module 05/g' \
    -e 's|modules/23-|flow/modules/01-|g' \
    -e 's|modules/24-|flow/modules/02-|g' \
    -e 's|modules/25-|flow/modules/03-|g' \
    -e 's|modules/26-|flow/modules/04-|g' \
    -e 's|modules/27-|flow/modules/05-|g' \
    -e 's|/learn-23-|/learn-flow-01-|g' \
    -e 's|/learn-24-|/learn-flow-02-|g' \
    -e 's|/learn-25-|/learn-flow-03-|g' \
    -e 's|/learn-26-|/learn-flow-04-|g' \
    -e 's|/learn-27-|/learn-flow-05-|g' \
    -e 's/<!-- NEW -->//g' \
    "$f"
done
cd ../..
```

- [ ] **Step 3: Verify modules have required sections**

```bash
for f in flow/modules/*.md; do
  echo "--- $f ---"
  grep -c '## Orientation\|## Quick Setup\|## Preflight\|## Step\|## Verification\|## Challenge' "$f"
done
# Each module should have at least 5 matching section headers
```

- [ ] **Step 4: Commit**

```bash
git add flow/modules/
git commit -m "add flow learning modules (renumbered 01-05 from courseware 23-27)"
```

---

### Task 4: Copy showroom QA scripts and setup-all.sh

**Files:**
- Create: `flow/scripts/showroom-qa/showroom-qa-antora.py`, `flow/scripts/showroom-qa/README.md`
- Create: `flow/scripts/setup-all.sh`

- [ ] **Step 1: Copy showroom QA directory**

```bash
COURSEWARE="$HOME/repos/claude-code-courseware"
cp "$COURSEWARE"/rhdp-flow-skills/scripts/showroom-qa/* flow/scripts/showroom-qa/
```

- [ ] **Step 2: Copy and update setup-all.sh**

```bash
cp "$COURSEWARE/scripts/setup-all.sh" flow/scripts/setup-all.sh
```

Edit `flow/scripts/setup-all.sh` to update the plugin path reference:

Old line: `PLUGIN_REPO="$HOME/.claude/plugins/claude-code-courseware/repo"`
New line: `PLUGIN_REPO="$HOME/.claude/plugins/rhdp-ops-tools/repo"`

Also update all other references from `claude-code-courseware` to `rhdp-ops-tools`:

Old line: `PLUGIN_DIR="$HOME/.claude/plugins/claude-code-courseware"`
New line: `PLUGIN_DIR="$HOME/.claude/plugins/rhdp-ops-tools"`

Old paths referencing `rhdp-flow-skills/skills` should become `flow/skills`:

```bash
sed -i '' \
  -e 's|claude-code-courseware|rhdp-ops-tools|g' \
  -e 's|rhdp-flow-skills/skills|flow/skills|g' \
  -e 's|rhdp-flow-skills/scripts|flow/scripts|g' \
  -e 's|rhdp-flow-agents/agents|flow/agents|g' \
  flow/scripts/setup-all.sh
```

- [ ] **Step 3: Make setup script executable**

```bash
chmod +x flow/scripts/setup-all.sh
```

- [ ] **Step 4: Commit**

```bash
git add flow/scripts/
git commit -m "add showroom QA scripts and setup-all.sh"
```

---

### Task 5: Create dispatchers and catalog

**Files:**
- Create: `.claude/commands/learn-flow-01-rhdp-flow-mcp.md`
- Create: `.claude/commands/learn-flow-02-rhdp-flow-ops.md`
- Create: `.claude/commands/learn-flow-03-csv-pipeline.md`
- Create: `.claude/commands/learn-flow-04-deployment-intel.md`
- Create: `.claude/commands/learn-flow-05-event-scale-ops.md`
- Create: `.claude/commands/courseware.md`
- Create: `.claude/commands/references/context.md`

- [ ] **Step 1: Create dispatcher for module 01 (RHDP-Flow MCP)**

Write `.claude/commands/learn-flow-01-rhdp-flow-mcp.md`:

```markdown
# RHDP-Flow MCP

Install and use the RHDP-Flow MCP server for workshop deployment automation.
Estimated time: 20 minutes. Prerequisites: Claude Code installed, Module 11 (Building MCP Servers) recommended.

Read flow/modules/01-rhdp-flow-mcp.md but present it in phases:

Phase 1: Read only the Quick Setup and Orientation sections. Present them.
         Ask: "Ready to check prerequisites?"

Phase 2: Read only the Preflight section. Run the checks.
         Skip any step that passes. Report results.
         Ask: "Ready to start the walkthrough?"

Phase 3: Read and present one Step at a time.
         After each step's verification passes, proceed to the next.
         Do not read ahead -- load each step only when needed.

Phase 4: Read only the Verification section. Run all checks.
         Report results.

Phase 5: Read only the Challenge and Challenge Verification sections.
         Present the challenge. After the user completes it, verify.

Use .claude/commands/references/context.md for team-specific values.
Track progress in ~/.claude/courseware-progress/.
```

- [ ] **Step 2: Create dispatcher for module 02 (RHDP-Flow Ops)**

Write `.claude/commands/learn-flow-02-rhdp-flow-ops.md`:

```markdown
# RHDP-Flow Ops

Daily workshop operations with Flow skills and agents.
Estimated time: 15 minutes. Prerequisites: Module 01 (RHDP-Flow MCP).

Read flow/modules/02-rhdp-flow-ops.md but present it in phases:

Phase 1: Read only the Quick Setup and Orientation sections. Present them.
         Ask: "Ready to check prerequisites?"

Phase 2: Read only the Preflight section. Run the checks.
         Skip any step that passes. Report results.
         Ask: "Ready to start the walkthrough?"

Phase 3: Read and present one Step at a time.
         After each step's verification passes, proceed to the next.
         Do not read ahead -- load each step only when needed.

Phase 4: Read only the Verification section. Run all checks.
         Report results.

Phase 5: Read only the Challenge and Challenge Verification sections.
         Present the challenge. After the user completes it, verify.

Use .claude/commands/references/context.md for team-specific values.
Track progress in ~/.claude/courseware-progress/.
```

- [ ] **Step 3: Create dispatcher for module 03 (CSV Pipeline)**

Write `.claude/commands/learn-flow-03-csv-pipeline.md`:

```markdown
# CSV Pipeline

Process workshop CSVs through the rhdp-flow-csv pipeline.
Estimated time: 20 minutes. Prerequisites: Claude Code installed, Module 11 (Building MCP Servers) recommended.

Read flow/modules/03-csv-pipeline.md but present it in phases:

Phase 1: Read only the Quick Setup and Orientation sections. Present them.
         Ask: "Ready to check prerequisites?"

Phase 2: Read only the Preflight section. Run the checks.
         Skip any step that passes. Report results.
         Ask: "Ready to start the walkthrough?"

Phase 3: Read and present one Step at a time.
         After each step's verification passes, proceed to the next.
         Do not read ahead -- load each step only when needed.

Phase 4: Read only the Verification section. Run all checks.
         Report results.

Phase 5: Read only the Challenge and Challenge Verification sections.
         Present the challenge. After the user completes it, verify.

Use .claude/commands/references/context.md for team-specific values.
Track progress in ~/.claude/courseware-progress/.
```

- [ ] **Step 4: Create dispatcher for module 04 (Deployment Intelligence)**

Write `.claude/commands/learn-flow-04-deployment-intel.md`:

```markdown
# Deployment Intelligence

Monitor deployments, detect ghost workshops, and troubleshoot failures with rhdp-flow-intel.
Estimated time: 20 minutes. Prerequisites: Claude Code installed, Module 01 recommended, Module 03 recommended.

Read flow/modules/04-deployment-intel.md but present it in phases:

Phase 1: Read only the Quick Setup and Orientation sections. Present them.
         Ask: "Ready to check prerequisites?"

Phase 2: Read only the Preflight section. Run the checks.
         Skip any step that passes. Report results.
         Ask: "Ready to start the walkthrough?"

Phase 3: Read and present one Step at a time.
         After each step's verification passes, proceed to the next.
         Do not read ahead -- load each step only when needed.

Phase 4: Read only the Verification section. Run all checks.
         Report results.

Phase 5: Read only the Challenge and Challenge Verification sections.
         Present the challenge. After the user completes it, verify.

Use .claude/commands/references/context.md for team-specific values.
Track progress in ~/.claude/courseware-progress/.
```

- [ ] **Step 5: Create dispatcher for module 05 (Event-Scale Operations)**

Write `.claude/commands/learn-flow-05-event-scale-ops.md`:

```markdown
# Event-Scale Operations

Capstone: multi-day event simulation using all Flow skills, agents, and MCP tools.
Estimated time: 30 minutes. Prerequisites: Module 01, Module 03, Module 04.

Read flow/modules/05-event-scale-ops.md but present it in phases:

Phase 1: Read only the Quick Setup and Orientation sections. Present them.
         Ask: "Ready to check prerequisites?"

Phase 2: Read only the Preflight section. Run the checks.
         Skip any step that passes. Report results.
         Ask: "Ready to start the walkthrough?"

Phase 3: Read and present one Step at a time.
         After each step's verification passes, proceed to the next.
         Do not read ahead -- load each step only when needed.

Phase 4: Read only the Verification section. Run all checks.
         Report results.

Phase 5: Read only the Challenge and Challenge Verification sections.
         Present the challenge. After the user completes it, verify.

Use .claude/commands/references/context.md for team-specific values.
Track progress in ~/.claude/courseware-progress/.
```

- [ ] **Step 6: Copy references/context.md from courseware**

```bash
COURSEWARE="$HOME/repos/claude-code-courseware"
cp "$COURSEWARE/.claude/commands/references/context.md" .claude/commands/references/context.md
```

- [ ] **Step 7: Create the catalog command**

Write `.claude/commands/courseware.md`:

```markdown
# RHDP Ops Tools

Before displaying the catalog, run the progress scan.

## Progress Scan

Run this silently to detect completion/in-progress state:

$BACKTICK$BACKTICKbash
PROGRESS_DIR="$HOME/.claude/courseware-progress"
if [ -d "$PROGRESS_DIR" ]; then
  for f in flow/modules/[0-9]*.md; do
    n=$(basename "$f" | grep -o '^[0-9]*')
    if [ -f "$PROGRESS_DIR/flow-$n.done" ]; then
      echo "DONE:$n"
    elif [ -f "$PROGRESS_DIR/flow-$n.started" ]; then
      echo "IN_PROGRESS:$n"
    fi
  done
fi
$BACKTICK$BACKTICK

Use the output to add status tags to the catalog.

## Catalog

Print the catalog using markdown (NOT inside a code block).

## RHDP Ops Tools

### Flow -- Workshop Automation
`01`  RHDP-Flow MCP -- 20 min
`02`  RHDP-Flow Ops -- 15 min
`03`  CSV Pipeline -- 20 min
`04`  Deployment Intelligence -- 20 min
`05`  Event-Scale Operations -- 30 min

### Intake -- Workshop Intake (coming soon)
`01`  Workshop Intake -- 15 min

---

> **5 modules available.**
>
> Pick a **number** to start a module, or run `/preflight` to check prerequisites.
> Run `bash flow/scripts/setup-all.sh` to install all Flow MCP servers, skills, and agents.

## Module Routing

| Module | Command |
|--------|---------|
| Flow 01 | `/learn-flow-01-rhdp-flow-mcp` |
| Flow 02 | `/learn-flow-02-rhdp-flow-ops` |
| Flow 03 | `/learn-flow-03-csv-pipeline` |
| Flow 04 | `/learn-flow-04-deployment-intel` |
| Flow 05 | `/learn-flow-05-event-scale-ops` |
```

Note: Replace `$BACKTICK$BACKTICK` with actual triple backticks when writing the file. The plan uses this placeholder to avoid breaking the fenced code block.

- [ ] **Step 8: Commit**

```bash
git add .claude/commands/
git commit -m "add dispatchers, catalog, and references for flow modules"
```

---

### Task 6: Create preflight command

**Files:**
- Create: `.claude/commands/preflight.md`

- [ ] **Step 1: Write preflight command**

Write `.claude/commands/preflight.md` with checks specific to the ops tools:

```markdown
# Preflight Check

Run prerequisite checks for RHDP Ops Tools.

## Run All Checks

Run these checks and print the results:

$BACKTICK$BACKTICKbash
echo "RHDP Ops Tools -- Preflight Check"
echo "=================================="
echo ""

PASS=0
TOTAL=6

# 1. Claude Code
if command -v claude &>/dev/null; then
  echo "PASS: Claude Code installed"
  PASS=$((PASS+1))
else
  echo "FAIL: Claude Code not found"
fi

# 2. Python 3.10+
if python3 -c "import sys; assert sys.version_info >= (3,10)" 2>/dev/null; then
  echo "PASS: Python $(python3 --version 2>&1 | awk '{print $2}')"
  PASS=$((PASS+1))
else
  echo "FAIL: Python 3.10+ required"
fi

# 3. RHDP-Flow MCP server
if python3 -c "import rhdp_flow_mcp" 2>/dev/null; then
  echo "PASS: rhdp-flow-mcp installed"
  PASS=$((PASS+1))
else
  echo "FAIL: rhdp-flow-mcp not installed -- run: pip install rhdp-flow-mcp"
fi

# 4. RHDP-Flow CSV server
if python3 -c "import rhdp_flow_csv" 2>/dev/null; then
  echo "PASS: rhdp-flow-csv installed"
  PASS=$((PASS+1))
else
  echo "FAIL: rhdp-flow-csv not installed -- run: pip install rhdp-flow-csv"
fi

# 5. RHDP-Flow Intel server
if python3 -c "import rhdp_flow_intel" 2>/dev/null; then
  echo "PASS: rhdp-flow-intel installed"
  PASS=$((PASS+1))
else
  echo "FAIL: rhdp-flow-intel not installed -- run: pip install rhdp-flow-intel"
fi

# 6. Playwright (for showroom QA)
if python3 -c "import playwright" 2>/dev/null; then
  echo "PASS: playwright installed"
  PASS=$((PASS+1))
else
  echo "INFO: playwright not installed -- needed for showroom QA scripts"
  echo "       Install: pip install playwright && playwright install chromium"
fi

echo ""
echo "$PASS/$TOTAL checks passed."
$BACKTICK$BACKTICK

## After the Checks

If all pass:
> You're ready to go. Run `/courseware` to see the module catalog and pick a module.

If MCP servers are missing:
> Run `bash flow/scripts/setup-all.sh` to install all Flow MCP servers and dependencies.
```

Note: Replace `$BACKTICK$BACKTICK` with actual triple backticks when writing the file.

- [ ] **Step 2: Commit**

```bash
git add .claude/commands/preflight.md
git commit -m "add preflight check command for ops tools prerequisites"
```

---

### Task 7: Create CLAUDE.md, README.md, and docs

**Files:**
- Create: `CLAUDE.md`
- Create: `README.md`
- Create: `docs/CONTRIBUTING.md`
- Create: `docs/TODO.md`

- [ ] **Step 1: Write CLAUDE.md**

Write `CLAUDE.md`:

```markdown
# CLAUDE.md

Project instructions for Claude Code when working with rhdp-ops-tools.

## What This Repo Does

RHDP operations toolkit delivered as a Claude Code plugin. Contains skills, learning modules, and scripts organized by domain (Flow workshop automation, future workshop intake). Installable as a plugin or usable standalone.

## Repository Structure

Domain-organized: each domain (flow, intake) owns its own skills, modules, and scripts.

- `flow/skills/` -- Claude Code skill files for Flow workshop automation
- `flow/modules/` -- learning modules for Flow tools
- `flow/scripts/` -- standalone scripts (showroom QA, setup)
- `intake/` -- future: workshop intake domain
- `.claude/commands/` -- dispatchers and catalog
- `.claude/settings.json` -- MCP server declarations

## Key Conventions

- Modules follow courseware structure: orientation, preflight, steps, verification, challenge
- Skills are self-contained markdown files
- Dispatchers are thin and load module files in phases
- No conventional-commit prefixes, no emojis in any output

## Versioning

Semver tags on `main` (`vX.Y.Z`). New domains or modules bump minor. Fixes bump patch.

## Adding a New Domain

1. Create `<domain>/skills/`, `<domain>/modules/`, `<domain>/scripts/`
2. Add dispatchers in `.claude/commands/learn-<domain>-NN-*.md`
3. Update the catalog in `.claude/commands/courseware.md`
4. Update README.md
```

- [ ] **Step 2: Write README.md**

Write `README.md`:

```markdown
# RHDP Ops Tools

Operations toolkit for the RHDP team -- Flow workshop automation, showroom QA, and ops training modules. Available as a Claude Code plugin or standalone repo.

## Getting Started

### Plugin Install (recommended)

```
claude plugin add github:rhpds/rhdp-ops-tools
```

Then run `/courseware` to see available modules.

### Standalone Clone

```bash
git clone git@github.com:rhpds/rhdp-ops-tools.git
cd rhdp-ops-tools
bash flow/scripts/setup-all.sh
```

### Check Prerequisites

Run `/preflight` to verify your environment.

## Domains

### Flow -- Workshop Automation

| # | Title | Time | Description |
|---|-------|------|-------------|
| 01 | RHDP-Flow MCP | ~20 min | Install and configure the RHDP-Flow MCP server |
| 02 | RHDP-Flow Ops | ~15 min | Daily workshop operations with Flow skills and agents |
| 03 | CSV Pipeline | ~20 min | Process workshop CSVs through the pipeline |
| 04 | Deployment Intelligence | ~20 min | Deployment monitoring, ghost detection, troubleshooting |
| 05 | Event-Scale Operations | ~30 min | Capstone: multi-day event simulation |

10 skills | 5 modules | showroom QA scripts | setup automation

### Intake -- Workshop Intake (coming soon)

Process white-glove workshop requests end-to-end.

## How Modules Work

1. **Orientation** -- what you'll learn
2. **Preflight** -- checks what's already set up, skips what's done
3. **Steps** -- guided walkthrough with verification at each step
4. **Verification** -- all-green final check
5. **Challenge** -- hands-on task using real team data

## Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).
```

- [ ] **Step 3: Write CONTRIBUTING.md**

Write `docs/CONTRIBUTING.md`:

```markdown
# Contributing to RHDP Ops Tools

## Adding a New Domain

1. Create the directory structure:
   ```
   <domain>/
     skills/
     modules/
     scripts/
   ```

2. Add skill files to `<domain>/skills/`. Each skill is a self-contained `.md` file.

3. Add learning modules to `<domain>/modules/`, numbered starting from `01`:
   - Each module must include: Orientation (or Quick Setup), Preflight, Steps, Verification, Challenge
   - Follow existing modules as examples

4. Create dispatchers in `.claude/commands/learn-<domain>-NN-<topic>.md`

5. Update the catalog in `.claude/commands/courseware.md`

6. Update `README.md` with the new domain table

## Adding a Skill

1. Create `<domain>/skills/<skill-name>.md`
2. Update the domain's README with the new skill
3. Commit with a clear description

## Adding a Module

1. Create `<domain>/modules/NN-<topic>.md` following the module structure
2. Create `.claude/commands/learn-<domain>-NN-<topic>.md` as a dispatcher
3. Update the catalog in `.claude/commands/courseware.md`
4. Update `README.md`

## Commit Messages

Write plain English commit subjects. No conventional-commit prefixes (`feat:`, `fix:`, etc.). No emojis.

## Pull Requests

All changes go through PRs on the `main` branch. Include a clear description of what changed and why.
```

- [ ] **Step 4: Write TODO.md**

Write `docs/TODO.md`:

```markdown
# TODO

## Planned

- [ ] Workshop intake domain (skills and modules)
- [ ] CI pipeline for validation (dispatcher coverage, module structure checks)
- [ ] Automated plugin version bumping on release

## Ideas

- [ ] Additional showroom QA variants (non-Antora showrooms)
- [ ] Flow agent definitions (`flow/agents/`)
```

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md README.md docs/
git commit -m "add CLAUDE.md, README, contributing guide, and TODO"
```

---

### Task 8: Tag v1.0.0 and set up branch protection

- [ ] **Step 1: Push all commits to GitHub**

```bash
git push -u origin main
```

- [ ] **Step 2: Tag v1.0.0**

```bash
git tag -a v1.0.0 -m "initial release: Flow domain with 10 skills, 5 modules, showroom QA"
git push origin v1.0.0
```

- [ ] **Step 3: Set up branch protection**

```bash
gh api repos/rhpds/rhdp-ops-tools/branches/main/protection \
  --method PUT \
  --input - <<'EOF'
{
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true
  },
  "enforce_admins": false,
  "required_status_checks": null,
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
```

- [ ] **Step 4: Commit (no changes -- just verify)**

Verify the tag and protection are set:

```bash
git tag -l 'v*'
# Expected: v1.0.0

gh api repos/rhpds/rhdp-ops-tools/branches/main/protection --jq '.required_pull_request_reviews.required_approving_review_count'
# Expected: 1
```

---

### Task 9: Clean-remove flow content from courseware

**Files (in courseware repo):**
- Delete: `modules/23-rhdp-flow-mcp.md`, `modules/24-rhdp-flow-ops.md`, `modules/25-csv-pipeline.md`, `modules/26-deployment-intel.md`, `modules/27-event-scale-ops.md`
- Delete: `.claude/commands/learn-23-rhdp-flow-mcp.md`, `.claude/commands/learn-24-rhdp-flow-ops.md`, `.claude/commands/learn-25-csv-pipeline.md`, `.claude/commands/learn-26-deployment-intel.md`, `.claude/commands/learn-27-event-scale-ops.md`
- Delete: `rhdp-flow-skills/` (entire directory)
- Delete: `scripts/setup-all.sh`

- [ ] **Step 1: Switch to courseware repo**

```bash
cd "$HOME/repos/claude-code-courseware"
```

- [ ] **Step 2: Delete modules 23-27**

```bash
git rm modules/23-rhdp-flow-mcp.md modules/24-rhdp-flow-ops.md modules/25-csv-pipeline.md modules/26-deployment-intel.md modules/27-event-scale-ops.md
```

- [ ] **Step 3: Delete dispatchers for 23-27**

```bash
git rm .claude/commands/learn-23-rhdp-flow-mcp.md .claude/commands/learn-24-rhdp-flow-ops.md .claude/commands/learn-25-csv-pipeline.md .claude/commands/learn-26-deployment-intel.md .claude/commands/learn-27-event-scale-ops.md
```

- [ ] **Step 4: Delete rhdp-flow-skills directory**

```bash
git rm -r rhdp-flow-skills/
```

- [ ] **Step 5: Delete setup-all.sh**

```bash
git rm scripts/setup-all.sh
```

- [ ] **Step 6: Commit deletions**

```bash
git commit -m "remove flow content (moved to rhpds/rhdp-ops-tools)"
```

---

### Task 10: Update courseware references

**Files (in courseware repo):**
- Modify: `.claude/commands/courseware.md`
- Modify: `.claude/commands/preflight.md`
- Modify: `.claude/commands/quick-install.md`
- Modify: `README.md`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update courseware.md catalog**

Remove the "Team Tools" section (lines containing modules 23-27) and the "Coming Soon" section (module 22). Remove the corresponding entries from the expanded section view, module routing table, and recommended paths.

Add to the footer, before the closing line:

```
> **RHDP ops tools** (Flow, showroom QA, workshop intake) have moved to their own plugin.
> Install with: `claude plugin add github:rhpds/rhdp-ops-tools`
```

Also remove the line: `> **RHDP-Flow users:** Run \`bash scripts/setup-all.sh\` ...`

- [ ] **Step 2: Update preflight.md**

Remove checks #10 (RHDP-Flow MCP servers) and update TOTAL from 11 to 9. Remove the `for server in rhdp-flow...` block and the corresponding counter logic. Also remove the `# 9. Python 3.10+` check that references "RHDP-Flow modules (23-27)" -- change it to just check Python without the flow reference.

- [ ] **Step 3: Update quick-install.md**

Remove items 7, 8, 9 (RHDP-Flow MCP, RHDP-Flow CSV, RHDP-Flow Intel) from the menu, status detection, and install procedures. Remove the `"all flow"` group. Remove the `### python-mcp` install procedure section for the three flow servers.

- [ ] **Step 4: Update README.md**

Remove the "Team Tools" section (lines 108-116) and the "Coming Soon" section (lines 118-122). Add a note after the last module table:

```markdown
### RHDP Ops Tools (separate plugin)

For Flow workshop automation, showroom QA, and workshop intake modules, install the [rhdp-ops-tools](https://github.com/rhpds/rhdp-ops-tools) plugin:

```
claude plugin add github:rhpds/rhdp-ops-tools
```
```

- [ ] **Step 5: Update CLAUDE.md**

Remove Flow-specific references from the post-update protocol. The courseware CLAUDE.md should no longer mention `rhdp-flow-skills/`, `scripts/setup-all.sh`, or Flow MCP servers.

- [ ] **Step 6: Remove Flow MCP servers from settings (if declared)**

Check `.claude/settings.json` and `.claude/settings.local.json` for rhdp-flow, rhdp-flow-csv, rhdp-flow-intel declarations and remove them. (The project `.claude/settings.json` currently only has permissions, so this may be a no-op.)

- [ ] **Step 7: Run validate.py and fix any failures**

```bash
python3 scripts/validate.py
```

The validator will now expect fewer modules (21 instead of 26). If catalog count or README sync checks fail, fix the specific references. The dispatcher coverage and orphan dispatcher checks should pass since we deleted both sides.

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "update courseware references after flow content extraction to rhdp-ops-tools"
```

---

### Task 11: Version bump courseware and update tracking systems

- [ ] **Step 1: Tag courseware with minor bump**

```bash
cd "$HOME/repos/claude-code-courseware"
git tag -a v2.4.0 -m "remove Team Tools section (moved to rhpds/rhdp-ops-tools)"
```

- [ ] **Step 2: Update Memory MCP**

Create a new entity for `rhdp-ops-tools` and update the `claude-code-courseware` entity:

- `mcp__memory__create_entities`: entity `rhdp-ops-tools` with observations about initial release, what it contains, repo URL
- `mcp__memory__add_observations`: entity `claude-code-courseware` noting the extraction of modules 23-27 and flow skills to rhdp-ops-tools, version v2.4.0

- [ ] **Step 3: Update the existing decouple memory**

Update or delete the `rhdp-flow-decouple` memory file since the decoupling is now complete.

- [ ] **Step 4: Update Notion Build Releases DB**

Add a row for `rhdp-ops-tools` v1.0.0 and a row for `courseware` v2.4.0.

- [ ] **Step 5: Update Confluence courseware page**

Fetch page 400032764, update the module tables to remove Team Tools (23-27) and Coming Soon (22), add a note about the rhdp-ops-tools plugin.
