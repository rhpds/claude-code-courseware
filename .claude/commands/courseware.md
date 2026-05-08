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
    echo "  Run /update-courseware to get the latest content."
    echo ""
  fi
fi
```

If the update check prints "UPDATE AVAILABLE", show that message to the user before the catalog. Also append:

> Run `/update-courseware` to pull the latest content before starting a module.

## Progress Scan

Run this silently to detect completion/in-progress state:

```bash
PROGRESS_DIR="$HOME/.claude/courseware-progress"
if [ -d "$PROGRESS_DIR" ]; then
  for f in modules/[0-9]*.md; do
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
`07`  Notion MCP · 15 min · **NEW**
`08`  Container & Podman MCP · 15 min · **NEW**

### Skills & Customization
`09`  Writing Custom Skills · 15 min
`10`  Hooks · 15 min · **NEW**
`21`  Plugin Marketplace · 15 min · **NEW**

### Advanced Patterns
`11`  Building MCP Servers · 30 min
`12`  Review Agents · 15 min
`13`  Agent Teams vs Superpowers · 15 min

### Workflow & Operations
`14`  Debugging & Troubleshooting · 15 min · **NEW**
`15`  Cost & Context Management · 15 min · **NEW**
`16`  Multi-Repo Workspaces · 15 min · **NEW**
`17`  CI/CD Integration · 15 min · **NEW**
`18`  Profile Cleanup · 15 min

### Team-Customizable
`19`  Red Hat Quick Deck · 10 min
`20`  Hivemind Knowledge Base · 15 min

### Team Tools
`23`  RHDP-Flow MCP · 20 min · **NEW**
`24`  RHDP-Flow Ops · 15 min · **NEW**
`25`  CSV Pipeline · 20 min · **NEW**

### Coming Soon
`22`  Workshop Intake · 15 min

## Recommended Paths

After the catalog, show the role-based recommendations:

> **Not sure where to start?** Here are suggested paths by role:
>
> **Developer:** 01, 02, 03, 04, 06, 09 -- get your environment set up and learn the tools you'll use daily.
>
> **Ops engineer:** 01, 02, 03, 05, 08, 10, 14 -- focus on Jira integration, containers, hooks, and debugging.
>
> **Team lead / manager:** 01, 02, 15 -- understand the setup, project configuration, and cost management.
>
> **Power user (all modules):** start at 01 and go in order. Each module builds on the previous ones.

## Footer

After the recommendations, print:

> **[COUNT] modules available.** Modules marked **NEW** were recently added.
>
> Where [COUNT] is computed by counting `modules/[0-9]*.md` files excluding TEMPLATE.md:
> ```bash
> ls modules/[0-9]*.md | wc -l | tr -d ' '
> ```
>
> Pick a **number** to jump into a module, or ask about a **section** (like "tell me about Core MCP Servers") to see descriptions and prerequisites before choosing. You can also type `/learn-` then Tab to see all modules, `/quick-install` to install MCP servers or plugins without a tutorial, or `/preflight` to check your prerequisites.
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
Create skills for repeatable workflows.
*Prereq: Module 01*

**`10` Hooks** -- ~15 min · **NEW**
Pre/post command hooks for guardrails and automation.
*Prereq: Module 01*

**`21` Plugin Marketplace** -- ~15 min · **NEW**
Discover, install, and manage Claude Code plugins from marketplace registries.
*Prereq: Module 01, Module 09 recommended*

**Section 4 -- Advanced Patterns (11-13)**

**`11` Building MCP Servers** -- ~30 min
Build a custom MCP server in Python and register it with Claude Code.
*Prereq: Module 01, Module 04 recommended*

**`12` Review Agents** -- ~15 min
Use Claude Code's agent system for specialized code reviews.
*Prereq: Module 01, Module 09 recommended*

**`13` Agent Teams vs Superpowers** -- ~15 min
Compare multi-agent coordination patterns for reviews and implementation.
*Prereq: Module 01, Module 12 recommended*

**Section 5 -- Workflow & Operations (14-18)**

**`14` Debugging & Troubleshooting** -- ~15 min · **NEW**
What to do when things go wrong -- MCP failures, tool errors, context issues.
*Prereq: Module 01*

**`15` Cost & Context Management** -- ~15 min · **NEW**
Session budgets, model routing, and context discipline.
*Prereq: Module 01*

**`16` Multi-Repo Workspaces** -- ~15 min · **NEW**
Configure Claude Code across multiple repositories.
*Prereq: Module 01*

**`17` CI/CD Integration** -- ~15 min · **NEW**
Use Claude Code in GitHub Actions and OpenShift Pipelines.
*Prereq: Module 01*

**`18` Profile Cleanup** -- ~15 min
Audit and clean ~/.claude/ for duplicate skills, orphaned plugins, and context bloat.
*Prereq: Module 01*

**Section 6 -- Team-Customizable (19-20)**

**`19` Red Hat Quick Deck** -- ~10 min
Generate branded HTML slide presentations with the Quick Deck skill.
*Prereq: Module 01, GitHub access to rhpds org*

**`20` Hivemind Knowledge Base** -- ~15 min
Contribute to and search the team's shared knowledge base.
*Prereq: Module 01, GitHub access to rhpds org*

**Section 7 -- Team Tools (23-27)**

**`23` RHDP-Flow MCP** -- ~20 min · **NEW**
Install and configure the RHDP-Flow MCP server for workshop deployment automation.
*Prereq: Module 01, Module 11 recommended*

**`24` RHDP-Flow Ops** -- ~15 min · **NEW**
Use Flow skills and agents for daily workshop operations -- status, QA, CSV validation, and pre-event readiness.
*Prereq: Module 23*

**`25` CSV Pipeline** -- ~20 min · **NEW**
Install the rhdp-flow-csv MCP server and process workshop CSVs through the full pipeline.
*Prereq: Module 01, Module 11 recommended*

**Section 8 -- Coming Soon (22)**

**`22` Workshop Intake** -- ~15 min
*Not yet available.*

## Module Routing

When the user picks a module, tell them to run the corresponding command:

| Module | Command |
|--------|---------|
| 01 | `/learn-01-vertex-setup` |
| 02 | `/learn-02-writing-claude-md` |
| 03 | `/learn-03-memory-mcp` |
| 04 | `/learn-04-git-mcp` |
| 05 | `/learn-05-atlassian-mcp` |
| 06 | `/learn-06-playwright-mcp` |
| 07 | `/learn-07-notion-mcp` |
| 08 | `/learn-08-container-podman-mcp` |
| 09 | `/learn-09-writing-custom-skills` |
| 10 | `/learn-10-hooks` |
| 11 | `/learn-11-building-mcp-servers` |
| 12 | `/learn-12-review-agents` |
| 13 | `/learn-13-agent-teams-vs-superpowers` |
| 14 | `/learn-14-debugging-troubleshooting` |
| 15 | `/learn-15-cost-context-management` |
| 16 | `/learn-16-multi-repo-workspaces` |
| 17 | `/learn-17-ci-cd-integration` |
| 18 | `/learn-18-profile-cleanup` |
| 19 | `/learn-19-red-hat-quick-deck` |
| 20 | `/learn-20-hivemind-knowledge-base` |
| 21 | `/learn-21-plugin-marketplace` |
| 23 | `/learn-23-rhdp-flow-mcp` |
| 24 | `/learn-24-rhdp-flow-ops` |
| 25 | `/learn-25-csv-pipeline` |

If they pick module 22 (Coming Soon), tell them it's not yet available and suggest other modules.
