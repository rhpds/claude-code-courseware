---
name: courseware
description: "Claude Code Courseware — browse the module catalog and pick a learning module to start"
---

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

  13  Red Hat Quick Deck                     ~10 min
      Generate branded HTML slide presentations with the Quick Deck skill.
      Prerequisites: Module 01

  14  Agent Teams vs Superpowers             ~20 min
      Compare multi-agent coordination patterns for reviews and implementation.
      Prerequisites: Module 01, Module 12 recommended

  15  Profile Cleanup                        ~15 min
      Audit and clean ~/.claude/ for duplicate skills, orphaned plugins, and context bloat.
      Prerequisites: Module 01

  ---  Coming Soon  ---

  10  Workshop Intake                        ~15 min

To start a module, type: /learn-01-vertex-setup
Tab completion works after typing /learn-
```

After printing the catalog, ask:
> "Which module would you like to start? You can type the number or the full command."

If the user picks a module number, tell them to run the corresponding `/learn-NN-*` command.
If they pick a "Coming Soon" module (10), tell them it's not yet available and suggest other modules.
If they pick module 14, tell them to run `/learn-14-agent-teams-vs-superpowers`.
