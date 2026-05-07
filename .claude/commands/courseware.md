# Claude Code Courseware

Before displaying the catalog, check if the courseware plugin has updates available.

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

If the update check prints "UPDATE AVAILABLE", show that message to the user before the catalog. If the check prints nothing (plugin is current or not installed via plugin), proceed directly to the catalog.

## Catalog

Print this catalog:

```
Claude Code Courseware — Learning Modules
==========================================

  --- Setup & Foundation ---

  01  Claude Code + Vertex AI Setup          ~10 min
      Install Claude Code and configure Vertex AI as the backend provider.
      Prerequisites: Mac or Linux, Red Hat GCP account

  02  Writing CLAUDE.md                      ~15 min
      Write project instructions that shape Claude Code's behavior.
      Prerequisites: Module 01

  --- Core MCP Servers ---

  03  Memory MCP                             ~10 min
      Persistent knowledge graph for cross-session memory.
      Prerequisites: Module 01

  04  Git MCP                                ~10 min
      Structured Git operations via MCP for status, history, and diffs.
      Prerequisites: Module 01

  05  Atlassian MCP Server (Jira)            ~5 min
      Connect Claude Code to Jira via the Atlassian Rovo MCP server.
      Prerequisites: Module 01

  06  Playwright MCP                         ~10 min
      Browser automation and visual testing via the Playwright MCP server.
      Prerequisites: Module 01

  07  Notion MCP                             ~15 min
      Connect Claude Code to Notion for pages, databases, and search.
      Prerequisites: Module 01

  08  Container & Podman MCP                 ~15 min
      Build, run, inspect, and debug containers from Claude Code.
      Prerequisites: Module 01, container runtime (Podman or Docker)

  --- Skills & Customization ---

  09  Writing Custom Skills                  ~15 min
      Create skills for repeatable workflows.
      Prerequisites: Module 01

  10  Hooks                                  ~15 min
      Pre/post command hooks for guardrails and automation.
      Prerequisites: Module 01

  --- Advanced Patterns ---

  11  Building MCP Servers                   ~30 min
      Build a custom MCP server in Python and register it with Claude Code.
      Prerequisites: Module 01, Module 04 recommended

  12  Review Agents                          ~15 min
      Use Claude Code's agent system for specialized code reviews.
      Prerequisites: Module 01, Module 09 recommended

  13  Agent Teams vs Superpowers             ~15 min
      Compare multi-agent coordination patterns for reviews and implementation.
      Prerequisites: Module 01, Module 12 recommended

  --- Workflow & Operations ---

  14  Debugging & Troubleshooting            ~15 min
      What to do when things go wrong — MCP failures, tool errors, context issues.
      Prerequisites: Module 01

  15  Cost & Context Management              ~15 min
      Session budgets, model routing, and context discipline.
      Prerequisites: Module 01

  16  Multi-Repo Workspaces                  ~15 min
      Configure Claude Code across multiple repositories.
      Prerequisites: Module 01

  17  CI/CD Integration                      ~15 min
      Use Claude Code in GitHub Actions and OpenShift Pipelines.
      Prerequisites: Module 01

  18  Profile Cleanup                        ~15 min
      Audit and clean ~/.claude/ for duplicate skills, orphaned plugins, and context bloat.
      Prerequisites: Module 01

  --- Team-Customizable ---

  19  Red Hat Quick Deck                     ~10 min
      Generate branded HTML slide presentations with the Quick Deck skill.
      Prerequisites: Module 01, GitHub access to rhpds org

  20  Hivemind Knowledge Base                ~15 min
      Contribute to and search the team's shared knowledge base.
      Prerequisites: Module 01, GitHub access to rhpds org

  ---  Coming Soon  ---

  21  Workshop Intake                        ~15 min

To start a module, type: /learn-01-vertex-setup
Tab completion works after typing /learn-
```

After printing the catalog, ask:
> "Which module would you like to start? You can type the number or the full command."

If the user picks a module number, tell them to run the corresponding `/learn-NN-*` command.
If they pick a "Coming Soon" module (21), tell them it's not yet available and suggest other modules.
