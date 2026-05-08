# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## What This Repo Does

Interactive learning modules for the RHDP operations team, delivered as Claude Code skills.
Each module teaches a specific tool or integration (Vertex AI, MCP servers, skills authoring)
through a guided, hands-on walkthrough with verification and a challenge.

## Repository Structure

```
claude-code-courseware/
  .claude/commands/          # skill dispatchers and menu
    courseware.md             # /courseware — module catalog
    learn-NN-topic.md        # dispatchers that load modules/NN-topic.md
    references/context.md    # shared team data
  modules/                   # full module content (the courseware)
    NN-topic.md              # one file per module
  scripts/                   # setup scripts
```

## How Modules Work

Each module in `modules/` follows a fixed structure:
1. **Orientation** — what you'll learn
2. **Preflight** — audit current state, skip what's already done
3. **Steps** — guided walkthrough with verification at each step
4. **Verification** — all-green final check
5. **Challenge** — hands-on task against real team data
6. **Challenge Verification** — confirm the result

Dispatchers in `.claude/commands/` are thin (10 lines) and load the corresponding module file.

## Authoring New Modules

1. Create `modules/NN-topic.md` following the structure above
2. Create `.claude/commands/learn-NN-topic.md` as a dispatcher
3. Add the module to the catalog in `.claude/commands/courseware.md`

## Key Conventions

- Preflight checks use EXISTS/MISSING pattern (audit first, skip what's green)
- Read-only checks run automatically; system-modifying actions use `!` prefix
- Challenges use real team data (RHDPOPS Jira project, team MCP servers, etc.)
- No conventional-commit prefixes, no emojis in any output

## Versioning

This project uses semver tags on the `main` branch.

| Bump  | When |
|-------|------|
| Major | Breaking changes: module restructuring, incompatible skill/command renames |
| Minor | New module added, new skill/command added |
| Patch | Fixes or edits to existing modules, catalog, commands, or docs |

Tag format: `vX.Y.Z` (e.g. `v1.0.0`). Create annotated tags:
```
git tag -a vX.Y.Z -m "description of release"
```

## Post-Update Protocol

After ANY commit in this project, complete ALL of the following steps automatically before reporting to the user. No confirmation needed -- run unattended.

### Step 1 -- Module Integrity Check

Run the integrity validator:

```bash
python3 scripts/validate.py
```

If any check fails, fix the issue before proceeding. The validator checks dispatcher coverage, module structure, catalog count, README sync, and no stale files.

### Step 2 -- Git Tagging

If the commit adds a new module or command, bump the minor version. If it fixes existing content, bump the patch version. Check the latest tag:

```bash
git tag -l 'v*' --sort=-v:refname | head -1
```

Create the new tag after the commit. Do not push the tag unless the user asks.

### Step 3 -- Confluence Update

Update the courseware Confluence page with the current module list. This is the single source of truth for the team.

- Cloud ID: `2b9e35e3-6bd3-4cec-b838-f4249ee02432`
- Page ID: `400032764`
- Space: RHPDS

Use `mcp__plugin_atlassian_atlassian__getConfluencePage` to fetch current content, then `mcp__plugin_atlassian_atlassian__updateConfluencePage` to update the module tables and count. Only update if the content actually changed.

### Step 4 -- Notion Build Log

Add a row to the Build Releases database:

- Data source ID: `8092bf78-4a79-415e-a4c3-48c7f9ad3d4d`
- Properties: `Build` (title), `date:Date:start` (ISO date), `Commit` (short SHA), `Summary` (1-2 sentences), `Project` = `courseware`

Use `mcp__claude_ai_Notion__notion-create-pages` with `parent.data_source_id`.

### Step 5 -- Memory MCP

- New module or feature: `mcp__memory__create_entities` with date and details
- Update to existing content: `mcp__memory__add_observations` on the `claude-code-courseware` entity
- Include: date (YYYY-MM-DD), what changed, version tag if created

### Protocol References

| Resource | ID |
|----------|----|
| Confluence page | `400032764` (cloud `2b9e35e3-6bd3-4cec-b838-f4249ee02432`) |
| Notion Dev Log page | `359b44c5-54f5-81d9-bb69-e509a01772a7` |
| Notion Build Releases DB | `8092bf78-4a79-415e-a4c3-48c7f9ad3d4d` (Project select = `courseware`) |
| GitHub repo | `rhpds/claude-code-courseware` |
