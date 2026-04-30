# Claude Code Courseware

Hands-on learning modules for the RHDP operations team, delivered as Claude Code skills.

Each module is an interactive, guided walkthrough that runs inside Claude Code. Clone this repo, launch Claude Code, and start learning.

## Getting Started

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

## Modules

| # | Title | Time | Description |
|---|-------|------|-------------|
| 01 | Claude Code + Vertex AI Setup | ~10 min | Install Claude Code and configure Vertex AI as the backend provider |
| 02 | Atlassian MCP Server (Jira) | ~5 min | Connect Claude Code to Jira via the Atlassian Rovo MCP server |
| 03 | Memory MCP | ~10 min | Persistent knowledge graph for cross-session memory |
| 04 | Git MCP | ~10 min | Structured Git operations via MCP for status, history, and diffs |
| 05 | Writing CLAUDE.md | ~15 min | Write project instructions that shape Claude Code's behavior |
| 06 | Playwright MCP | ~10 min | Browser automation and visual testing via the Playwright MCP server |
| 07 | Writing Custom Skills | ~20 min | Create skills for repeatable workflows |
| 08 | Hivemind Knowledge Base | ~15 min | Contribute to and search the team's shared Hive Mind knowledge base |
| 09 | Jira Plugin | ~15 min | Install and configure the Jira Plugin for structured workflows |
| 13 | Red Hat Quick Deck | ~10 min | Generate branded HTML slide presentations with the Quick Deck skill |

### Coming Soon

| # | Title | Time | Description |
|---|-------|------|-------------|
| 10 | Workshop Intake | ~15 min | Process white-glove requests end-to-end |
| 11 | Building MCP Servers | ~30 min | Create your own MCP server |
| 12 | Review Agents | ~15 min | Use the team review agent system |

## How Modules Work

Every module follows the same pattern:

1. **Orientation** — what you'll learn
2. **Preflight** — checks what's already set up, skips what's done
3. **Steps** — guided walkthrough with verification at each step
4. **Verification** — all-green final check
5. **Challenge** — hands-on task using real team data

If you've already completed some prerequisites, the module automatically skips those steps.

## Alternative Setup (No Claude Code Yet)

If you don't have Claude Code installed yet, you can run the Vertex AI setup script directly:

```bash
bash scripts/setup-claude-vertex.sh
```

This walks you through the same steps as Module 01 but runs as a standalone shell script.

## Authoring New Modules

1. Create `modules/NN-topic.md` following the module template (see any existing module)
2. Create `.claude/commands/learn-NN-topic.md` as a thin dispatcher
3. Add the module to the catalog in `.claude/commands/courseware.md`
4. Update the tables in this README
