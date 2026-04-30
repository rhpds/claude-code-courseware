# Claude Code Courseware

Display the module catalog below, then ask the user which module they'd like to start.

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
      Prerequisites: Module 01, GitHub access to rhpds org

  ---  Coming Soon  ---

  09  Workshop Ops (rhdp-ops)                ~10 min
  10  Workshop Intake                        ~15 min
  11  Building MCP Servers                   ~30 min
  12  Review Agents                          ~15 min


  13  Red Hat Quick Deck                     ~10 min
      Generate branded HTML slide presentations with the Quick Deck skill.
      Prerequisites: Module 01

To start a module, type: /learn-01-vertex-setup
Tab completion works after typing /learn-
```

After printing the catalog, ask:
> "Which module would you like to start? You can type the number or the full command."

If the user picks a module number, tell them to run the corresponding `/learn-NN-*` command.
If they pick a "Coming Soon" module (09-12), tell them it's not yet available and suggest modules 01-08 or 13.
