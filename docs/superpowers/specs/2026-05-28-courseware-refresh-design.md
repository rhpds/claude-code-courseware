# Courseware Refresh Design -- May 2026

## Problem

The claude-code-courseware has 21 modules written between early and mid-May 2026. Claude Code has shipped significant features since then (and the courseware missed some features that were already GA at the time of writing). The result: 6 modules have stale content and 15+ GA features have zero coverage. Security is now the team's north star after Anthropic Mythos revealed the scale of open-source vulnerabilities.

## Audience

RHDP ops team at Red Hat. All users access Claude Code through Vertex AI (required by Red Hat approval). The courseware is delivered as a Claude Code plugin with skill-based modules.

## Scope

Approach B: comprehensive refresh. Update 6 stale modules, add 7 new modules, reorganize catalog sections. No full rewrite, no audience expansion.

## Changes Summary

| Action | Count | Details |
|--------|-------|---------|
| Update existing modules | 6 | Modules 01, 02, 09, 11, 15, 17 |
| Add new modules | 7 | Modules 22-28 |
| Remove modules | 0 | All existing modules stay |
| Reorganize catalog | Yes | New sections for Security and Parallel Workflows |

Total after refresh: **28 modules** (up from 21).

---

## Part 1: Updates to Existing Modules

### Module 01 -- Vertex AI Setup

**What's stale:** npm installation method is deprecated; native installer is now recommended. Module doesn't mention auto-updates via native install.

**Changes:**
- Replace `npm install -g @anthropic-ai/claude-code` with the native installer command
- Add note that npm installation still works but is deprecated and won't auto-update
- Keep the module tightly scoped to CLI + Vertex AI (per Red Hat approval: code assistant use cases only, Vertex is required)
- Update the `claude --version` verification to also check install method
- Add a preflight check for existing native install vs npm install and guide migration

### Module 02 -- Writing CLAUDE.md

**What's stale:** Missing `/init` command, `.claude/CLAUDE.local.md` for personal notes, auto memory, and the 200-line guidance from Anthropic best practices.

**Changes:**
- Add `/init` as the recommended starting point (analyzes codebase, generates starter CLAUDE.md)
- Cover `.claude/CLAUDE.local.md` for personal project-specific notes (gitignored)
- Mention auto memory (`~/.claude/projects/<project>/memory/`) and how it complements CLAUDE.md
- Add the 200-line guideline: "Stay under 200 lines. Claude attends ~150 instructions reliably."
- Add guidance on CLAUDE.md being advisory (~70% followed) vs hooks being deterministic

### Module 09 -- Writing Custom Skills

**What's stale:** Doesn't cover the unified skills model (v2.1.101), plugin packaging, or `disable-model-invocation` frontmatter.

**Changes:**
- Update skill anatomy to reflect unified model: skills can be auto-invoked by description match or manually via `/skillname`
- Add `disable-model-invocation: true` frontmatter option
- Cover the skill budget (1% of context window, overflow managed by frequency-based trimming)
- Add section on packaging skills into plugins (bridge to Module 21)
- Mention `/doctor` reports skill budget overflow

### Module 11 -- Building MCP Servers

**What's stale:** Only covers stdio transport. Missing streamable HTTP (the new recommended remote transport), OAuth, and elicitation.

**Changes:**
- Keep stdio as the primary teaching path (it's simpler and most common for local servers)
- Add a new section: "Going Remote: Streamable HTTP Transport"
  - What streamable HTTP is and why it replaced SSE
  - How to configure a remote MCP server in `.mcp.json` or settings.json
  - `type: "streamable-http"` configuration
- Add a section on MCP elicitation (servers requesting input from users mid-task)
  - Form mode vs URL mode
  - When to use elicitation in server design
- Mention OAuth as an advanced topic for authenticated remote servers
- Update the external dependencies section to note the evolving MCP spec

### Module 15 -- Cost & Context Management

**What's stale:** Missing `/usage` command, fast mode, auto-compaction settings, June 2026 billing changes.

**Changes:**
- Update `/cost` and `/stats` references to `/usage` (the merged command; `/cost` and `/stats` still work as shortcuts)
- Add fast mode coverage: what it is (Opus at higher speed, not a smaller model), how to toggle (`/fast`), when to use it
- Cover auto-compaction settings: `autoCompactAt`, `sessionLimit`, `thinkingTokenLimit`
- Add the June 2026 billing change: Agent SDK and `claude -p` usage moves to separate monthly credit on June 15
  - $20 Pro / $100 Max 5x / $200 Max 20x
  - Metered at full API rates, no rollover
  - Note: this doesn't affect Vertex AI billing for Red Hat (Vertex is billed through GCP)
- Add `/context` command for visualizing token usage breakdown
- Mention prompt caching and how it reduces repeated content costs

### Module 17 -- CI/CD Integration

**What's stale:** Doesn't cover Routines, the official `claude-code-action` GitHub Action, GitLab CI/CD, or Agent SDK billing separation.

**Changes:**
- Update the GitHub Actions section to reference `anthropic/claude-code-action` (the official action)
  - Interactive mode (@claude mentions in PRs) vs automation mode (headless on events)
  - PR review, code implementation, issue triage, CI failure analysis
- Add Routines section (research preview): saved automations on Anthropic cloud
  - Three trigger types: schedule, API, GitHub event
  - Complement to GitHub Actions (interpretive tasks vs deterministic CI/CD)
  - Note: requires claude.ai/code access, daily run caps by plan tier
- Mention GitLab CI/CD support
- Add note about June 2026 Agent SDK credit changes for `claude -p` and GitHub Actions usage
- Keep OpenShift Pipelines section as-is (still relevant for the team)

---

## Part 2: New Modules

### Module 22 -- Git Worktrees

**Section:** Parallel & Autonomous Workflows
**Duration:** 15 min
**Prerequisites:** Module 01

**What it teaches:**
- What git worktrees are and why Claude Code uses them for isolation
- `claude --worktree` / `-w` flag for CLI sessions
- `.worktreeinclude` file for copying gitignored files (e.g., `.env`) into worktrees
- Worktree location: `.claude/worktrees/` by default, configurable
- Subagent isolation: `isolation: worktree` in agent YAML definitions
- Cleaning up worktrees
- When to use worktrees vs when to work in the main tree

**Challenge:** Create a worktree, make changes in isolation, verify they don't affect the main tree, then merge or discard.

### Module 23 -- Background Agents & Goal Mode

**Section:** Parallel & Autonomous Workflows
**Duration:** 15 min
**Prerequisites:** Module 01

**What it teaches:**
- Background sessions: `claude --bg "prompt"`, `/bg` to background active session, left-arrow detach
- Agent view: `claude agents` dashboard showing all sessions grouped by state
- Resuming and managing background sessions
- `/goal "condition"` -- outcome-based autonomous execution (Claude keeps working until condition is met)
- `/loop` for recurring tasks (polling deploy status, watching test results)
- Composing these patterns: worktree + background + goal for fully autonomous feature work
- `claude respawn --all` after sleep/shutdown

**Challenge:** Start a background agent to perform a code review, monitor it in agent view, and retrieve results.

### Module 24 -- Security-First Development

**Section:** Security
**Duration:** 15 min
**Prerequisites:** Module 01

**What it teaches:**
- The security-guidance plugin: what it is, how it works (three levels: file edits, diffs, commits)
- Installing and verifying the security-guidance plugin
- `/security-review` command for on-demand security analysis of current changes
- OWASP Top 10 in the context of Claude Code: what Claude watches for (injection, XSS, auth flaws, data exposure)
- Writing CLAUDE.md security instructions that reinforce secure patterns
- Integrating security hooks: pre-commit security validation
- The difference between Claude's built-in security awareness and the plugin's active scanning

**Challenge:** Intentionally introduce a security vulnerability (SQL injection or hardcoded secret), run `/security-review`, verify it's caught, then fix it.

### Module 25 -- Security Scanning & Vulnerability Research

**Section:** Security
**Duration:** 20 min
**Prerequisites:** Module 01, Module 24 recommended

**What it teaches:**
- Context: Anthropic Mythos and Project Glasswing -- what they found (23,000+ issues across 1,000+ open source projects, 90% true positive rate)
- Claude Security on the web (claude.ai/code): scanning codebases for vulnerabilities
  - Multi-stage verification: how Claude challenges its own conclusions
  - Findings format: confidence score, severity, impact, reproduction steps, suggested patch
- Scoping scans to specific directories or components
- Triaging findings: severity assessment, false positive identification
- Integration with team workflows: sending findings to Jira, Slack
- The complementary relationship: SAST (rule-driven) vs LLM audit (semantic-driven)
- Responsible disclosure and the CVE process (context from Mythos findings)
- Limitations: what Claude Security can and can't detect vs traditional scanners

**Challenge:** Use `/security-review` to scan a project directory for vulnerabilities, triage the findings by severity, and create a Jira ticket for any actionable vulnerability. If Claude Security web access is available, compare the CLI findings with a full web-based scan.

### Module 26 -- Claude Agent SDK

**Section:** Advanced Patterns
**Duration:** 25 min
**Prerequisites:** Module 01, Module 11 recommended (Building MCP Servers)

**What it teaches:**
- What the Agent SDK is: programmatic access to the same tools, agent loop, and context management that power Claude Code
- Agent SDK vs Client SDK: SDK handles the tool loop vs you implement it yourself
- Python quickstart: install `claude-agent-sdk`, create a simple agent that reads a file and reports findings
- TypeScript quickstart: same pattern with `@anthropic-ai/claude-agent-sdk`
- Key primitives: tools, hooks, MCP integration, subagents
- Cost control: `max_budget_usd`, per-session limits
- Production patterns: `allowedTools` for scoped safety, hook-based validation
- Session management: continue, resume, fork
- Billing note: Agent SDK usage on subscription plans moves to separate credit June 15, 2026 (Vertex billing through GCP is separate)

**Challenge:** Build a simple agent in Python that scans a directory for TODO comments and creates a summary report. Run it with `claude -p` to verify headless execution.

### Module 27 -- Checkpointing & Session Management

**Section:** Workflow & Operations
**Duration:** 10 min
**Prerequisites:** Module 01

**What it teaches:**
- Checkpointing: Esc+Esc opens rewind menu
  - Three rewind options: conversation only, code only, both
  - "Rewind code only" keeps conversation context (powerful for trying alternatives)
- Session resume: `--resume` and `--continue` flags
- `/resume` picker UI for selecting from recent sessions (including background ones)
- Session naming: `--name <label>` for easy identification
- Auto mode: classifier-based permission automation (Shift+Tab to cycle permission modes)
  - How it works: model-based classifiers auto-approve/deny tool calls
  - 93% of manual approvals automated
  - Safety: strips blanket shell access rules on entry
- `/branch` (formerly `/fork`) to split a session into two

**Challenge:** Start a session, make some changes, use Esc+Esc to rewind code only, try a different approach, then compare results.

### Module 28 -- Voice, Vim & Terminal Customization

**Section:** Workflow & Operations
**Duration:** 10 min
**Prerequisites:** Module 01

**What it teaches:**
- Voice dictation: `/voice`, push-to-talk (hold spacebar), auto-submit option
  - Transcription via Anthropic servers, does not consume tokens
- Vim mode: `/vim` for vim keybindings in the prompt input
  - Mode switching, navigation (hjkl, w/b/e), editing operators, text objects
  - Vim mode vs keybindings: different layers (text input vs application actions)
- Keybinding customization: `~/.claude/keybindings.json`
  - Chord sequences, modifier combinations, unbinding defaults
- Custom themes: `~/.claude/themes/`, `/theme` command
- Fullscreen TUI: `/tui fullscreen` for flicker-free rendering
  - Mouse support, Ctrl+O transcript mode with search
- Status line customization
- Output styles: custom markdown files in `~/.claude/output-styles/`

**Challenge:** Enable vim mode, customize at least one keybinding, and (if on macOS) try voice dictation for a prompt.

---

## Part 3: Catalog Reorganization

### New catalog structure

```
### Setup & Foundation
01  Vertex AI Setup . 10 min
02  Writing CLAUDE.md . 15 min

### Core MCP Servers
03  Memory MCP . 10 min
04  Git MCP . 10 min
05  Atlassian MCP (Jira) . 5 min
06  Playwright MCP . 10 min
07  Notion MCP . 15 min
08  Container & Podman MCP . 15 min

### Skills & Customization
09  Writing Custom Skills . 15 min
10  Hooks . 15 min
21  Plugin Marketplace . 15 min

### Security
24  Security-First Development . 15 min        <-- NEW
25  Security Scanning & Vulnerability Research . 20 min  <-- NEW

### Advanced Patterns
11  Building MCP Servers . 30 min
12  Review Agents . 15 min
13  Agent Teams vs Superpowers . 15 min
26  Claude Agent SDK . 25 min                   <-- NEW

### Parallel & Autonomous Workflows               <-- NEW SECTION
22  Git Worktrees . 15 min                      <-- NEW
23  Background Agents & Goal Mode . 15 min      <-- NEW

### Workflow & Operations
14  Debugging & Troubleshooting . 15 min
15  Cost & Context Management . 15 min
16  Multi-Repo Workspaces . 15 min
17  CI/CD Integration . 15 min
18  Profile Cleanup . 15 min
27  Checkpointing & Session Management . 10 min  <-- NEW
28  Voice, Vim & Terminal Customization . 10 min  <-- NEW

### Team-Customizable
19  Red Hat Quick Deck . 10 min
20  Hivemind Knowledge Base . 15 min
```

### Updated recommended paths

- **Developer:** 01, 02, 03, 04, 06, 09, 24 -- environment setup, daily tools, and security-first habits
- **Ops engineer:** 01, 02, 03, 05, 08, 10, 14, 24 -- Jira integration, containers, hooks, debugging, security
- **Security-focused:** 01, 02, 24, 25, 10, 17 -- security modules, hooks for guardrails, CI/CD scanning
- **Team lead / manager:** 01, 02, 15, 24 -- setup, project config, cost management, security awareness
- **Power user (all modules):** start at 01 and go in order

---

## Part 4: Implementation Order

Priority 1 (highest impact, do first):
1. Module 24 -- Security-First Development (new north star)
2. Module 25 -- Security Scanning & Vulnerability Research
3. Module 01 update -- fix deprecated npm install
4. Module 15 update -- billing changes before June 15

Priority 2 (major gaps):
5. Module 22 -- Git Worktrees
6. Module 23 -- Background Agents & Goal Mode
7. Module 02 update -- /init, auto memory
8. Module 27 -- Checkpointing & Session Management

Priority 3 (remaining):
9. Module 26 -- Claude Agent SDK
10. Module 09 update -- unified skills model
11. Module 11 update -- streamable HTTP, elicitation
12. Module 17 update -- Routines, official GitHub Action
13. Module 28 -- Voice, Vim & Terminal Customization

---

## Out of Scope (explicitly deferred)

These features exist but are not included in this refresh:

| Feature | Reason |
|---------|--------|
| Desktop App module | Red Hat approval is for code assistant use cases via Vertex AI; Desktop requires Anthropic direct plan |
| Web (claude.ai/code) module | Same approval constraint |
| Remote Control | Research preview; too early for courseware |
| Channels (Telegram/Discord) | Research preview; niche use case |
| Connectors | Requires claude.ai access, not Vertex |
| Ultraplan / Ultrareview | Research preview; cloud-only |
| Chrome Extension | Beta; niche use case |
| Managed Agents (API) | API product, not Claude Code CLI |
| Dreaming (Managed Agents) | Research preview; API product |
| Computer Use | Niche; limited practical application |
| Agent Teams (experimental) | Experimental flag required; not GA |

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| June 2026 billing changes may affect Agent SDK module accuracy | Module 15 and 26 note the billing change with dates; can be updated post-June 15 |
| Claude Security is in research preview | Module 25 clearly labels it as preview; focuses on concepts and workflow, not specific UI steps |
| MCP spec may evolve (streamable HTTP, elicitation) | Module 11 teaches the pattern, not the exact API; references official docs |
| Some features may change before modules are written | Each module has an External Dependencies section that documents what could change |
