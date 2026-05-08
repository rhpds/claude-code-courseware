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

### Advanced Patterns

| # | Title | Time | Description |
|---|-------|------|-------------|
| 11 | Building MCP Servers | ~30 min | Build a custom MCP server in Python and register it with Claude Code |
| 12 | Review Agents | ~15 min | Use Claude Code's agent system for specialized code reviews |
| 13 | Agent Teams vs Superpowers | ~15 min | Compare multi-agent coordination patterns for reviews and implementation |

### Workflow & Operations

| # | Title | Time | Description |
|---|-------|------|-------------|
| 14 | Debugging & Troubleshooting | ~15 min | What to do when things go wrong -- MCP failures, tool errors, context issues |
| 15 | Cost & Context Management | ~15 min | Session budgets, model routing, and context discipline |
| 16 | Multi-Repo Workspaces | ~15 min | Configure Claude Code across multiple repositories |
| 17 | CI/CD Integration | ~15 min | Use Claude Code in GitHub Actions and OpenShift Pipelines |
| 18 | Profile Cleanup | ~15 min | Audit and clean ~/.claude/ for duplicate skills, orphaned plugins, and context bloat |

### Team-Customizable

| # | Title | Time | Description |
|---|-------|------|-------------|
| 19 | Red Hat Quick Deck | ~10 min | Generate branded HTML slide presentations with the Quick Deck skill |
| 20 | Hivemind Knowledge Base | ~15 min | Contribute to and search the team's shared knowledge base |

### Team Tools

| # | Title | Time | Description |
|---|-------|------|-------------|
| 23 | RHDP-Flow MCP | ~20 min | Install and configure the RHDP-Flow MCP server for workshop deployment automation |
| 24 | RHDP-Flow Ops | ~15 min | Use Flow skills and agents for daily workshop operations |
| 25 | CSV Pipeline | ~20 min | Install the rhdp-flow-csv MCP server and process workshop CSVs through the full pipeline |

### Coming Soon

| # | Title | Time | Description |
|---|-------|------|-------------|
| 22 | Workshop Intake | ~15 min | Process white-glove requests end-to-end |

## Recommended Paths

Not sure where to start? Here are suggested paths by role:

- **Developer:** 01, 02, 03, 04, 06, 09 -- environment setup and daily tools.
- **Ops engineer:** 01, 02, 03, 05, 08, 10, 14 -- Jira, containers, hooks, debugging.
- **Team lead / manager:** 01, 02, 15 -- setup, project config, cost management.
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

## Authoring New Modules

1. Create `modules/NN-topic.md` following the module template (see any existing module)
2. Create `.claude/commands/learn-NN-topic.md` as a thin dispatcher
3. Add the module to the catalog in `.claude/commands/courseware.md`
4. Update the tables in this README
