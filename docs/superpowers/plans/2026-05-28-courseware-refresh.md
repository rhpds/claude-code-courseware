# Courseware Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update 6 existing modules with current features and create 7 new modules covering security, worktrees, background agents, Agent SDK, session management, and terminal customization.

**Architecture:** Each module is a standalone markdown file in `modules/` following `TEMPLATE.md`. Each new module needs a dispatcher in `.claude/commands/` and a catalog entry in `.claude/commands/courseware.md`. Updates modify existing files in-place.

**Tech Stack:** Markdown, bash (preflight/verification scripts), Python (settings.json manipulation)

**Spec:** `docs/superpowers/specs/2026-05-28-courseware-refresh-design.md`

---

## File Map

### Modified files (updates)
- `modules/01-vertex-setup.md` -- replace npm install with native installer
- `modules/02-writing-claude-md.md` -- add /init, CLAUDE.local.md, auto memory, 200-line guideline
- `modules/09-writing-custom-skills.md` -- add unified skills model, plugin packaging, skill budget
- `modules/11-building-mcp-servers.md` -- add streamable HTTP, elicitation sections
- `modules/15-cost-context-management.md` -- add /usage, fast mode, billing changes, compaction settings
- `modules/17-ci-cd-integration.md` -- add Routines, claude-code-action, GitLab, billing note
- `.claude/commands/courseware.md` -- reorganize catalog with new sections and modules

### New files
- `modules/22-git-worktrees.md` -- Git Worktrees module
- `modules/23-background-agents-goal-mode.md` -- Background Agents & Goal Mode module
- `modules/24-security-first-development.md` -- Security-First Development module
- `modules/25-security-scanning-vulnerability-research.md` -- Security Scanning module
- `modules/26-claude-agent-sdk.md` -- Claude Agent SDK module
- `modules/27-checkpointing-session-management.md` -- Checkpointing & Session Management module
- `modules/28-voice-vim-terminal-customization.md` -- Voice, Vim & Terminal Customization module
- `.claude/commands/learn-22-git-worktrees.md` -- dispatcher
- `.claude/commands/learn-23-background-agents-goal-mode.md` -- dispatcher
- `.claude/commands/learn-24-security-first-development.md` -- dispatcher
- `.claude/commands/learn-25-security-scanning-vulnerability-research.md` -- dispatcher
- `.claude/commands/learn-26-claude-agent-sdk.md` -- dispatcher
- `.claude/commands/learn-27-checkpointing-session-management.md` -- dispatcher
- `.claude/commands/learn-28-voice-vim-terminal-customization.md` -- dispatcher

---

## Parallelization Strategy

All 13 module tasks are independent of each other -- they touch different files with no shared state. They can run in parallel batches:

**Batch 1 (7 agents):** All 7 new modules (22-28) -- these are greenfield, no conflicts possible
**Batch 2 (6 agents):** All 6 module updates (01, 02, 09, 11, 15, 17) -- each modifies a different file
**Batch 3 (1 agent):** Catalog reorganization -- depends on all modules existing

Max parallelism: Batch 1 + Batch 2 can run simultaneously (13 agents). Batch 3 runs after.

---

## Dispatcher Template

Every new module needs a dispatcher file in `.claude/commands/`. All dispatchers follow this exact pattern:

```markdown
---
description: "Learn MODULE_TITLE"
---

Read the file `modules/NN-slug.md` and follow it as a guided walkthrough.

Start with the Orientation section, then run the Preflight checks.
Walk through each step, skipping any where the preflight showed EXISTS.
End with the Challenge.
```

---

## Task 1: New Module 24 -- Security-First Development

**Files:**
- Create: `modules/24-security-first-development.md`
- Create: `.claude/commands/learn-24-security-first-development.md`

- [ ] **Step 1: Write the module file** following `modules/TEMPLATE.md` structure. Content per spec:
  - Title: "Module 24 -- Security-First Development"
  - Duration: 15 min, Prereq: Module 01
  - Add `<!-- NEW -->` HTML comment after the title line
  - Orientation: security-guidance plugin, /security-review, OWASP Top 10 in Claude Code context
  - Preflight: check Claude Code installed, check if security-guidance plugin installed (`claude plugin list 2>/dev/null | grep -i security`), check for existing CLAUDE.md security sections
  - Step 1: Understand the security-guidance plugin (conceptual -- three levels: file edits, diffs, commits)
  - Step 2: Install and verify the security-guidance plugin
  - Step 3: Run `/security-review` on current changes
  - Step 4: Write CLAUDE.md security instructions (OWASP Top 10 patterns)
  - Step 5: Create a security hook (pre-commit validation)
  - Verification: plugin installed, /security-review available, CLAUDE.md has security section
  - Challenge: Intentionally introduce a SQL injection or hardcoded secret, run /security-review, verify caught, fix it
  - Challenge Verification: confirm the vulnerability was detected, fixed, and the review passes clean

- [ ] **Step 2: Write the dispatcher** using the dispatcher template above with title "Security-First Development" and file `modules/24-security-first-development.md`

- [ ] **Step 3: Verify** both files exist and module has all required sections (Orientation, Preflight, at least 3 Steps, Verification, Challenge, Challenge Verification)

---

## Task 2: New Module 25 -- Security Scanning & Vulnerability Research

**Files:**
- Create: `modules/25-security-scanning-vulnerability-research.md`
- Create: `.claude/commands/learn-25-security-scanning-vulnerability-research.md`

- [ ] **Step 1: Write the module file** following template. Content per spec:
  - Title: "Module 25 -- Security Scanning & Vulnerability Research"
  - Duration: 20 min, Prereq: Module 01, Module 24 recommended
  - Add `<!-- NEW -->` HTML comment
  - Orientation: Anthropic Mythos context (23,000+ issues, 1,000+ open source projects, 90% true positive), Claude Security, SAST vs LLM audit
  - Preflight: Claude Code installed, /security-review available, check for Jira MCP (for challenge)
  - Step 1: Context -- Anthropic Mythos and Project Glasswing (conceptual, cite stats)
  - Step 2: Claude Security scanning -- multi-stage verification, findings format (confidence, severity, impact, repro steps, patch)
  - Step 3: Scoping scans to directories/components
  - Step 4: Triaging findings -- severity assessment, false positive identification
  - Step 5: Integration with Jira/Slack workflows
  - Step 6: SAST vs LLM audit -- complementary relationship, limitations
  - Verification: understands scanning workflow, can triage findings
  - Challenge: Run /security-review on a project directory, triage by severity, create Jira ticket for actionable finding
  - Challenge Verification: verify Jira ticket created with proper severity and description

- [ ] **Step 2: Write the dispatcher**

- [ ] **Step 3: Verify** both files exist and have all sections

---

## Task 3: Update Module 01 -- Vertex AI Setup

**Files:**
- Modify: `modules/01-vertex-setup.md`

- [ ] **Step 1: Update Quick Setup section** -- replace `npm install -g @anthropic-ai/claude-code` with native installer. Add note about npm being deprecated.

- [ ] **Step 2: Update External Dependencies** -- change "npm registry" to note native installer is preferred, npm still works but is deprecated.

- [ ] **Step 3: Update Orientation** -- change item 3 from "Claude Code CLI" to mention native installer method.

- [ ] **Step 4: Update Preflight** -- add check for install method (native vs npm): `claude --version 2>/dev/null | grep -i "native\|npm" || echo "INFO: Install method unknown"`

- [ ] **Step 5: Update Step 3** -- replace `! npm install -g @anthropic-ai/claude-code` with native installer command. Add fallback note for npm.

- [ ] **Step 6: Verify** module still passes structure check (all sections present, bash blocks valid)

---

## Task 4: Update Module 15 -- Cost & Context Management

**Files:**
- Modify: `modules/15-cost-context-management.md`

- [ ] **Step 1:** Read full current content, then add these new sections/updates:
  - Replace references to `/cost` and `/stats` with `/usage` (note the old commands still work as shortcuts)
  - Add fast mode section: what it is (Opus at higher speed, not smaller model), `/fast` toggle, when to use
  - Add auto-compaction settings: `autoCompactAt`, `sessionLimit`, `thinkingTokenLimit`
  - Add `/context` command for visualizing token usage
  - Add prompt caching explanation
  - Add June 2026 billing change section (Agent SDK credits, with note that Vertex AI billing through GCP is unaffected)

- [ ] **Step 2: Verify** module has all original sections plus new content

---

## Task 5: New Module 22 -- Git Worktrees

**Files:**
- Create: `modules/22-git-worktrees.md`
- Create: `.claude/commands/learn-22-git-worktrees.md`

- [ ] **Step 1: Write module** per spec and template:
  - Duration: 15 min, Prereq: Module 01
  - Add `<!-- NEW -->` HTML comment
  - Steps: what worktrees are, `claude --worktree`/`-w`, `.worktreeinclude`, worktree location config, subagent `isolation: worktree`, cleanup, when to use vs not
  - Challenge: create worktree, make isolated changes, verify main tree unaffected, merge or discard

- [ ] **Step 2: Write dispatcher**
- [ ] **Step 3: Verify**

---

## Task 6: New Module 23 -- Background Agents & Goal Mode

**Files:**
- Create: `modules/23-background-agents-goal-mode.md`
- Create: `.claude/commands/learn-23-background-agents-goal-mode.md`

- [ ] **Step 1: Write module** per spec and template:
  - Duration: 15 min, Prereq: Module 01
  - Add `<!-- NEW -->` HTML comment
  - Steps: `claude --bg`, `/bg`, agent view (`claude agents`), resume/manage, `/goal "condition"`, `/loop`, composing patterns, `claude respawn --all`
  - Challenge: start background agent for code review, monitor in agent view, retrieve results

- [ ] **Step 2: Write dispatcher**
- [ ] **Step 3: Verify**

---

## Task 7: Update Module 02 -- Writing CLAUDE.md

**Files:**
- Modify: `modules/02-writing-claude-md.md`

- [ ] **Step 1:** Read full current content, then add:
  - New Step after Step 1: "Use /init to bootstrap" -- `/init` command generates starter CLAUDE.md from codebase analysis
  - In Step 1 (Understand CLAUDE.md): add `.claude/CLAUDE.local.md` for personal project-specific notes (gitignored)
  - New content in Step 1 or new step: auto memory (`~/.claude/projects/<project>/memory/`) and how it complements CLAUDE.md
  - In Step 4 or Step 5: add 200-line guideline ("Stay under 200 lines. Claude attends ~150 instructions reliably.")
  - In Step 3 or new step: add note that CLAUDE.md is advisory (~70% followed) vs hooks being deterministic -- reference Module 10

- [ ] **Step 2: Verify** all original sections preserved plus new content added

---

## Task 8: New Module 27 -- Checkpointing & Session Management

**Files:**
- Create: `modules/27-checkpointing-session-management.md`
- Create: `.claude/commands/learn-27-checkpointing-session-management.md`

- [ ] **Step 1: Write module** per spec and template:
  - Duration: 10 min, Prereq: Module 01
  - Add `<!-- NEW -->` HTML comment
  - Steps: Esc+Esc rewind (3 options), --resume/--continue, /resume picker, --name, auto mode (Shift+Tab, 93% auto-approve), /branch
  - Challenge: start session, make changes, Esc+Esc rewind code only, try different approach, compare

- [ ] **Step 2: Write dispatcher**
- [ ] **Step 3: Verify**

---

## Task 9: New Module 26 -- Claude Agent SDK

**Files:**
- Create: `modules/26-claude-agent-sdk.md`
- Create: `.claude/commands/learn-26-claude-agent-sdk.md`

- [ ] **Step 1: Write module** per spec and template:
  - Duration: 25 min, Prereq: Module 01, Module 11 recommended
  - Add `<!-- NEW -->` HTML comment
  - Steps: what Agent SDK is, Agent SDK vs Client SDK, Python quickstart, TypeScript quickstart, key primitives (tools/hooks/MCP/subagents), cost control, production patterns, session management, billing note
  - Challenge: build Python agent that scans for TODOs and creates summary, run with `claude -p`

- [ ] **Step 2: Write dispatcher**
- [ ] **Step 3: Verify**

---

## Task 10: Update Module 09 -- Writing Custom Skills

**Files:**
- Modify: `modules/09-writing-custom-skills.md`

- [ ] **Step 1:** Read full content, then add:
  - In Step 1 (skill anatomy): update to mention unified skills model (v2.1.101) -- skills can be auto-invoked by description match OR manually via `/skillname`
  - In Step 1: add `disable-model-invocation: true` frontmatter option (prevents auto-invoke, manual only)
  - New step or in Step 5: cover skill budget (1% of context window, overflow managed by frequency-based trimming)
  - New step or in Step 5: add section on packaging skills into plugins (bridge to Module 21)
  - In verification or troubleshooting: mention `/doctor` reports skill budget overflow

- [ ] **Step 2: Verify** all original content preserved

---

## Task 11: Update Module 11 -- Building MCP Servers

**Files:**
- Modify: `modules/11-building-mcp-servers.md`

- [ ] **Step 1:** Read full content, then add after existing steps:
  - New Step: "Going Remote: Streamable HTTP Transport" -- what it is, why it replaced SSE, `type: "streamable-http"` config in `.mcp.json` or settings.json
  - New Step: "MCP Elicitation" -- servers requesting input mid-task, form mode vs URL mode, when to use
  - Brief mention of OAuth for authenticated remote servers (advanced topic, link to docs)
  - Update External Dependencies to note evolving MCP spec (2025-11-25 stable)

- [ ] **Step 2: Verify** all original content preserved, new sections added

---

## Task 12: Update Module 17 -- CI/CD Integration

**Files:**
- Modify: `modules/17-ci-cd-integration.md`

- [ ] **Step 1:** Read full content, then:
  - Update GitHub Actions section to reference `anthropic/claude-code-action` (official action), interactive mode (@claude mentions) vs automation mode
  - Add new section: "Cloud Routines" -- research preview, three trigger types (schedule, API, GitHub), complement to Actions, requires claude.ai/code
  - Add mention of GitLab CI/CD support
  - Add note about June 2026 Agent SDK credit changes for `claude -p` and GitHub Actions
  - Keep OpenShift Pipelines section as-is

- [ ] **Step 2: Verify** all original content preserved

---

## Task 13: New Module 28 -- Voice, Vim & Terminal Customization

**Files:**
- Create: `modules/28-voice-vim-terminal-customization.md`
- Create: `.claude/commands/learn-28-voice-vim-terminal-customization.md`

- [ ] **Step 1: Write module** per spec and template:
  - Duration: 10 min, Prereq: Module 01
  - Add `<!-- NEW -->` HTML comment
  - Steps: /voice (push-to-talk, auto-submit), /vim (mode switching, navigation, operators), keybinding customization (~/.claude/keybindings.json), custom themes, fullscreen TUI, status line, output styles
  - Challenge: enable vim mode, customize keybinding, try voice dictation

- [ ] **Step 2: Write dispatcher**
- [ ] **Step 3: Verify**

---

## Task 14: Catalog Reorganization

**Files:**
- Modify: `.claude/commands/courseware.md`

**Depends on:** Tasks 1-13 (all modules must exist)

- [ ] **Step 1:** Update the catalog structure per the spec's Part 3. Add new sections "Security" and "Parallel & Autonomous Workflows". Insert all 7 new modules in their correct sections. Mark new modules with **NEW** tag reference.

- [ ] **Step 2:** Update the "Recommended Paths" section with the new paths from the spec (Developer, Ops engineer, Security-focused, Team lead, Power user).

- [ ] **Step 3:** Update the "Module Routing" table with all 7 new module commands (22-28).

- [ ] **Step 4:** Update the "Expanded Section View" with descriptions and prerequisites for all new modules.

- [ ] **Step 5:** Update the Footer module count logic (should now find 28 modules).

- [ ] **Step 6: Verify** by counting modules in catalog vs files in `modules/` directory -- they must match.
