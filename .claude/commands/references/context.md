# Courseware Context Reference

Shared reference data for all learning modules.

---

## Team Environment

| Item | Value |
|------|-------|
| GCP project list | https://docs.google.com/spreadsheets/d/1qWoCx3i5jZ-t6BUD-2AIdutk9sMmkytoXqjBXh2oi4U/edit?gid=0#gid=0 |
| Vertex AI region | `global` |
| Atlassian instance | `redhat.atlassian.net` |
| Jira project (ops) | `RHDPOPS` |

---

## Atlassian Rovo MCP Server

| Item | Value |
|------|-------|
| Server name | `mcp-atlassian-prod` |
| Type | `http` |
| URL | `https://mcp.atlassian.com/v1/mcp` |
| Auth method | OAuth 2.1 (recommended) or API token |
| API token URL | `https://id.atlassian.com/manage-profile/security/api-tokens?autofillToken&expiryDays=max&appId=mcp&selectedScopes=all` |

---

## Claude Code Vertex AI Environment Variables

| Variable | Purpose |
|----------|---------|
| `CLAUDE_CODE_USE_VERTEX` | Set to `1` to route through Vertex AI |
| `ANTHROPIC_VERTEX_PROJECT_ID` | Your GCP project ID |
| `CLOUD_ML_REGION` | Vertex AI serving region (use `global`) |

---

## Git MCP Server

| Item | Value |
|------|-------|
| Server name | `git` |
| Package | `@modelcontextprotocol/server-git` |
| Command | `npx -y @modelcontextprotocol/server-git` |
| Key tools | `git_status`, `git_log`, `git_diff`, `git_show`, `git_branch` |
| Notes | All tools require `repo_path` parameter |

---

## Memory MCP Server

| Item | Value |
|------|-------|
| Server name | `memory` |
| Package | `@modelcontextprotocol/server-memory` |
| Command | `npx -y @modelcontextprotocol/server-memory` |
| Storage | Local JSON file (default: `~/.claude/memory.json`) |
| Env var | `MEMORY_FILE_PATH` — path to the knowledge graph JSON file |

---

## Red Hat Quick Deck Skill

| Item | Value |
|------|-------|
| Repository | `~/repos/red-hat-quick-deck` |
| Skill path | `~/.claude/skills/red-hat-quick-deck` |
| Installation | Symlink repo directory into `~/.claude/skills/` |
| Key file | `SKILL.md` — full skill definition |
| Reference files | `references/redhat-brand.md`, `references/story-arcs.md`, `references/rhds-icons.md` |
| Invocation | Ask Claude for a "quick deck" on any topic |
| Output | Self-contained `.html` file + `.md` companion |
| Color modes | Core Dark (default), Core Light, Expressive Dark |

---

## CLAUDE.md

| Item | Value |
|------|-------|
| File name | `CLAUDE.md` |
| Scope levels | Workspace (`~/repos/CLAUDE.md`), Project (repo root), Subdirectory |
| Key sections | Project overview, Conventions, MCP usage, Workflow rules, Preferences |
| Cost-saving patterns | Subagent delegation, Preferred tools, Session discipline |
| Reference bundle | `~/repos/claude-cost-saving/` (CLAUDE.md template + 10 skills) |

---

## Module Prerequisites

| Module | Requires |
|--------|----------|
| 01 — Vertex Setup | Mac or Linux, Red Hat GCP account |
| 02 — Atlassian MCP | Module 01 complete (Claude Code working) |
| 03 — Memory MCP | Module 01 complete (Claude Code working) |
| 04 — Git MCP | Module 01 complete (Claude Code working) |
| 05 — Writing CLAUDE.md | Module 01 complete (Claude Code working) |
| 13 — Red Hat Quick Deck | Module 01 complete (Claude Code working) |
