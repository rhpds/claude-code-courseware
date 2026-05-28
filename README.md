# Claude Code Courseware

Hands-on learning modules for the RHDP operations team, delivered as Claude Code skills.

Each module is an interactive, guided walkthrough that runs inside Claude Code. Install the plugin or clone the repo, launch Claude Code, and start learning.

## Getting Started

### Option A: Plugin Install (recommended)

Install the courseware plugin so `/courseware` and all `/learn-*` commands work from any directory:

```
claude plugin add github:rhpds/claude-code-courseware
```

Then from any project:
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

Tab completion works after typing `/learn-` -- it shows all available modules.

### Check Prerequisites

Run `/preflight` to verify your environment before starting modules.

### Quick Install (No Tutorial)

Run `/quick-install` to install MCP servers or plugins without going through a full module walkthrough.

## Modules

### Setup & Foundation

| # | Title | Time | Description |
|---|-------|------|-------------|
| 01 | Vertex AI Setup | ~10 min | Install Claude Code and configure Vertex AI as the backend provider |
| 02 | Writing CLAUDE.md | ~15 min | Write project instructions that shape Claude Code's behavior |

### Core MCP Servers

| # | Title | Time | Description |
|---|-------|------|-------------|
| 03 | Memory MCP | ~10 min | Persistent knowledge graph for cross-session memory |
| 04 | Git MCP | ~10 min | Structured Git operations via MCP for status, history, and diffs |
| 05 | Atlassian MCP (Jira) | ~5 min | Connect Claude Code to Jira via the Atlassian Rovo MCP server |
| 06 | Playwright MCP | ~10 min | Browser automation and visual testing via the Playwright MCP server |
| 07 | Notion MCP | ~15 min | Connect Claude Code to Notion for pages, databases, and search |
| 08 | Container & Podman MCP | ~15 min | Build, run, inspect, and debug containers from Claude Code |

### Skills & Customization

| # | Title | Time | Description |
|---|-------|------|-------------|
| 09 | Writing Custom Skills | ~15 min | Create skills for repeatable workflows |
| 10 | Hooks | ~15 min | Pre/post command hooks for guardrails and automation |
| 21 | Plugin Marketplace | ~15 min | Discover, install, and manage Claude Code plugins from marketplace registries |

### Security

| # | Title | Time | Description |
|---|-------|------|-------------|
| 24 | Security-First Development | ~15 min | Security-guidance plugin, /security-review, OWASP Top 10, security hooks |
| 25 | Security Scanning & Vulnerability Research | ~20 min | Anthropic Mythos context, Claude Security scanning, triage, Jira integration |

### Advanced Patterns

| # | Title | Time | Description |
|---|-------|------|-------------|
| 11 | Building MCP Servers | ~30 min | Build a custom MCP server in Python and register it with Claude Code |
| 12 | Review Agents | ~15 min | Use Claude Code's agent system for specialized code reviews |
| 13 | Agent Teams vs Superpowers | ~15 min | Compare multi-agent coordination patterns for reviews and implementation |
| 26 | Claude Agent SDK | ~25 min | Build custom agents with the Agent SDK in Python or TypeScript |

### Parallel & Autonomous Workflows

| # | Title | Time | Description |
|---|-------|------|-------------|
| 22 | Git Worktrees | ~15 min | Isolated workspaces for parallel development with claude --worktree |
| 23 | Background Agents & Goal Mode | ~15 min | Background sessions, agent view, /goal, /loop, autonomous patterns |

### Workflow & Operations

| # | Title | Time | Description |
|---|-------|------|-------------|
| 14 | Debugging & Troubleshooting | ~15 min | What to do when things go wrong -- MCP failures, tool errors, context issues |
| 15 | Cost & Context Management | ~15 min | Session budgets, /usage, fast mode, compaction, billing changes |
| 16 | Multi-Repo Workspaces | ~15 min | Configure Claude Code across multiple repositories |
| 17 | CI/CD Integration | ~15 min | GitHub Actions, Cloud Routines, GitLab CI/CD, OpenShift Pipelines |
| 18 | Profile Cleanup | ~15 min | Audit and clean ~/.claude/ for duplicate skills, orphaned plugins, and context bloat |
| 27 | Checkpointing & Session Management | ~10 min | Esc+Esc rewind, session resume, auto mode, /branch |
| 28 | Voice, Vim & Terminal Customization | ~10 min | Voice dictation, vim mode, keybindings, themes, fullscreen TUI |
| 29 | Effort & Reasoning Control | ~10 min | Effort levels as a cost lever on Vertex (Opus 4.6 / Sonnet 4.5), /effort, per-skill effort, ultrathink vs ultracode |

### Team-Customizable

| # | Title | Time | Description |
|---|-------|------|-------------|
| 19 | Red Hat Quick Deck | ~10 min | Generate branded HTML slide presentations with the Quick Deck skill |
| 20 | Hivemind Knowledge Base | ~15 min | Contribute to and search the team's shared knowledge base |

### RHDP Ops Tools

RHDP-specific ops tools (Flow, showroom QA, workshop intake) have moved to their own plugin:

```
claude plugin add github:rhpds/rhdp-ops-tools
```

See [rhpds/rhdp-ops-tools](https://github.com/rhpds/rhdp-ops-tools) for modules and documentation.

## Recommended Paths

Not sure where to start? Here are suggested paths by role:

- **Developer:** 01, 02, 03, 04, 06, 09, 24 -- environment setup, daily tools, and security-first habits.
- **Ops engineer:** 01, 02, 03, 05, 08, 10, 14, 24 -- Jira, containers, hooks, debugging, security.
- **Security-focused:** 01, 02, 24, 25, 10, 17 -- security modules, hooks for guardrails, CI/CD scanning.
- **Team lead / manager:** 01, 02, 15, 24 -- setup, project config, cost management, security awareness.
- **Power user:** start at 01 and go in order.

## How Modules Work

Every module follows the same pattern:

1. **Orientation** -- what you'll learn
2. **Preflight** -- checks what's already set up, skips what's done
3. **Steps** -- guided walkthrough with verification at each step
4. **Verification** -- all-green final check
5. **Challenge** -- hands-on task using real team data

If you've already completed some prerequisites, the module automatically skips those steps. Your progress is tracked in `~/.claude/courseware-progress/` so the catalog shows which modules you've completed.

## Alternative Setup (No Claude Code Yet)

If you don't have Claude Code installed yet, you can run the Vertex AI setup script directly:

```bash
bash scripts/setup-claude-vertex.sh
```

This walks you through the same steps as Module 01 but runs as a standalone shell script.

## Forking for Your Team

Want to run this courseware for your own organization? See [Fork Your Own Courseware](docs/fork-your-own.md).

## Branch Policy

The `main` branch is protected:

- **Pull requests required** -- all changes must go through a PR with at least 1 approval.
- **Stale reviews dismissed** -- pushing new commits to a PR resets existing approvals.
- **Force-push and deletion blocked** -- `main` history cannot be rewritten or removed.
- **Admin bypass** -- repo admins can merge without approval in emergencies.

This project uses **semver tags** on `main` (`vX.Y.Z`). New modules bump the minor version; fixes to existing content bump the patch version. Tags are created after merge by maintainers.

## Authoring New Modules

1. Create `modules/NN-topic.md` following the module template (see any existing module)
2. Create `.claude/commands/learn-NN-topic.md` as a thin dispatcher
3. Add the module to the catalog in `.claude/commands/courseware.md`
4. Update the tables in this README
