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

## Memory MCP Server

| Item | Value |
|------|-------|
| Server name | `memory` |
| Package | `@modelcontextprotocol/server-memory` |
| Command | `npx -y @modelcontextprotocol/server-memory` |
| Storage | Local JSON file (default: `~/.claude/memory.json`) |
| Env var | `MEMORY_FILE_PATH` — path to the knowledge graph JSON file |

---

## Module Prerequisites

| Module | Requires |
|--------|----------|
| 01 — Vertex Setup | Mac or Linux, Red Hat GCP account |
| 02 — Atlassian MCP | Module 01 complete (Claude Code working) |
| 03 — Memory MCP | Module 01 complete (Claude Code working) |
