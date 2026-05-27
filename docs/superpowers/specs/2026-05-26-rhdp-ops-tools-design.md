# rhdp-ops-tools -- Design Spec

**Date:** 2026-05-26
**Status:** Draft
**Repo:** rhpds/rhdp-ops-tools (to be created)

## Summary

Extract all RHDP operations tooling from claude-code-courseware into a standalone repo (`rhdp-ops-tools`) that serves as both a Claude Code plugin and a standalone toolkit. The new repo owns Flow workshop automation skills, showroom QA scripts, ops-focused training modules, and future domains like workshop intake.

## Goals

1. Clean separation: courseware teaches general Claude Code; rhdp-ops-tools owns all ops-specific tooling and training
2. Independent versioning and release cycle for ops tools
3. Dual distribution: installable as a Claude Code plugin OR usable as a standalone repo
4. Domain-organized structure that scales as new ops tool domains are added

## Non-goals

- Rewriting existing skills or modules (content transfers as-is with path/numbering updates)
- Building the workshop intake domain now (placeholder directory only)
- Moving MCP server source code (the servers themselves live in their own repos; this repo declares them as dependencies)

## Repository Structure

```
rhdp-ops-tools/
  .claude-plugin/
    plugin.json                        # plugin manifest for marketplace
  .claude/
    commands/
      courseware.md                     # ops-tools module catalog
      preflight.md                     # ops-specific prerequisite checks
      learn-flow-01-rhdp-flow-mcp.md   # flow domain dispatchers
      learn-flow-02-rhdp-flow-ops.md
      learn-flow-03-csv-pipeline.md
      learn-flow-04-deployment-intel.md
      learn-flow-05-event-scale-ops.md
    settings.json                      # MCP server declarations (flow, flow-csv, flow-intel)
  flow/
    skills/                            # 11 flow skills (flow-deploy.md, flow-qa.md, etc.)
    modules/                           # 5 learning modules (renumbered 01-05)
    scripts/
      showroom-qa/                     # playwright-based QA scripts
      setup-all.sh                     # one-shot flow installer
  intake/                              # future: workshop intake domain
    skills/
    modules/
  docs/
    CONTRIBUTING.md                    # how to add new domains, skills, modules
    TODO.md                            # tracked roadmap items
  CLAUDE.md                            # project instructions for Claude Code
  README.md                            # overview, install, quick start
```

### Domain convention

Each domain (flow, intake, future) owns three directories:
- `skills/` -- Claude Code skill files (.md)
- `modules/` -- training modules (.md), numbered per-domain starting from 01
- `scripts/` -- standalone tools and automation scripts

Dispatchers in `.claude/commands/` are prefixed by domain: `learn-flow-01-*`, `learn-intake-01-*`.

## Plugin Manifest

```json
{
  "name": "rhdp-ops-tools",
  "description": "RHDP operations toolkit -- Flow workshop automation, showroom QA, and ops training modules",
  "version": "1.0.0",
  "author": { "name": "RHDP Team" },
  "repository": "https://github.com/rhpds/rhdp-ops-tools",
  "license": "Apache-2.0",
  "keywords": ["rhdp", "ops", "flow", "workshops", "qa"]
}
```

## Installation

### As a Claude Code plugin

```bash
claude plugin install rhpds/rhdp-ops-tools
```

This installs skills, modules, commands, and MCP server declarations into the user's Claude Code environment.

### As a standalone repo

```bash
git clone https://github.com/rhpds/rhdp-ops-tools.git
cd rhdp-ops-tools
bash flow/scripts/setup-all.sh
```

For ops engineers who want the scripts (showroom-qa, setup) without needing Claude Code.

## Migration Inventory

### Moves to rhdp-ops-tools

| Source (courseware) | Destination (rhdp-ops-tools) |
|---------------------|-------------------------------|
| `rhdp-flow-skills/skills/*.md` (11 files) | `flow/skills/*.md` |
| `rhdp-flow-skills/scripts/showroom-qa/` | `flow/scripts/showroom-qa/` |
| `rhdp-flow-skills/README.md` | `flow/README.md` |
| `modules/23-rhdp-flow-mcp.md` | `flow/modules/01-rhdp-flow-mcp.md` |
| `modules/24-rhdp-flow-ops.md` | `flow/modules/02-rhdp-flow-ops.md` |
| `modules/25-csv-pipeline.md` | `flow/modules/03-csv-pipeline.md` |
| `modules/26-deployment-intel.md` | `flow/modules/04-deployment-intel.md` |
| `modules/27-event-scale-ops.md` | `flow/modules/05-event-scale-ops.md` |
| `.claude/commands/learn-23-*.md` | `.claude/commands/learn-flow-01-rhdp-flow-mcp.md` |
| `.claude/commands/learn-24-*.md` | `.claude/commands/learn-flow-02-rhdp-flow-ops.md` |
| `.claude/commands/learn-25-*.md` | `.claude/commands/learn-flow-03-csv-pipeline.md` |
| `.claude/commands/learn-26-*.md` | `.claude/commands/learn-flow-04-deployment-intel.md` |
| `.claude/commands/learn-27-*.md` | `.claude/commands/learn-flow-05-event-scale-ops.md` |
| `scripts/setup-all.sh` | `flow/scripts/setup-all.sh` |
| Flow MCP server configs (settings) | `.claude/settings.json` |
| Flow-specific preflight checks | `.claude/commands/preflight.md` |

### Content transformations during move

- **Module renumbering:** 23-27 become 01-05 within the flow domain
- **Internal cross-references:** Update any module-to-module links to use new numbering
- **Dispatcher paths:** Update `Read` paths to point to `flow/modules/` instead of `modules/`
- **setup-all.sh:** Update plugin repo path from `claude-code-courseware` to `rhdp-ops-tools`
- **Skill file paths:** No changes needed (skills are self-contained)

### Deleted from courseware (clean removal)

- `modules/23-rhdp-flow-mcp.md`
- `modules/24-rhdp-flow-ops.md`
- `modules/25-csv-pipeline.md`
- `modules/26-deployment-intel.md`
- `modules/27-event-scale-ops.md`
- `.claude/commands/learn-23-rhdp-flow-mcp.md`
- `.claude/commands/learn-24-rhdp-flow-ops.md`
- `.claude/commands/learn-25-csv-pipeline.md`
- `.claude/commands/learn-26-deployment-intel.md`
- `.claude/commands/learn-27-event-scale-ops.md`
- `rhdp-flow-skills/` (entire directory)
- `scripts/setup-all.sh`
- Flow MCP server declarations from `.claude/settings.json`

### Updated in courseware

| File | Change |
|------|--------|
| `.claude/commands/courseware.md` | Remove "Team Tools" (23-27) and "Coming Soon" (22) sections. Add footer note directing users to `rhdp-ops-tools` plugin. |
| `.claude/commands/preflight.md` | Remove Flow-specific prerequisite checks |
| `.claude/commands/quick-install.md` | Remove Flow MCP server install options |
| `scripts/validate.py` | Update expected module count, remove flow-related validations |
| `CLAUDE.md` | Remove Flow-specific references from post-update protocol and settings |
| `.claude/settings.json` | Remove rhdp-flow, rhdp-flow-csv, rhdp-flow-intel server declarations |

## Preflight (new repo)

The new repo includes its own preflight command that checks:

1. **Flow MCP servers:** rhdp-flow, rhdp-flow-csv, rhdp-flow-intel installed and responding
2. **Python dependencies:** playwright installed (for showroom-qa scripts)
3. **Plugin currency:** local plugin is up to date with remote
4. **Domain prerequisites:** per-module checks (e.g., cluster access for event-scale-ops)

Uses the same EXISTS/MISSING audit pattern as courseware's preflight.

## Versioning

Semver tags on `main`:
- **Major:** breaking changes (domain restructuring, incompatible skill or command renames)
- **Minor:** new domain added, new module, new skill
- **Patch:** fixes to existing content

Tag format: `vX.Y.Z` (annotated tags). Initial release: `v1.0.0`.

## Branch Protection (main)

- Require pull request reviews before merging
- Require status checks to pass (when CI is added)
- No force pushes to main
- No branch deletions on main

## Documentation

### README.md

- Project overview and purpose
- Quick start (plugin install + standalone clone)
- Domain listing with skill and module counts
- Link to CONTRIBUTING.md

### CONTRIBUTING.md

- How to add a new domain directory
- How to write a new skill (follows existing skill conventions)
- How to write a new module (follows courseware module structure: orientation, preflight, steps, verification, challenge)
- How to add a dispatcher and catalog entry
- PR and review process

### TODO.md

Initial items:
- Workshop intake domain (module 22 from courseware)
- CI pipeline for validation
- Automated plugin version bumping

## Catalog

The new repo gets its own `/courseware` command (same name as the courseware plugin, but scoped to the ops-tools plugin context) that lists ops-specific modules grouped by domain:

```
## RHDP Ops Tools

### Flow -- Workshop Automation
01  RHDP-Flow MCP -- 20 min
02  RHDP-Flow Ops -- 15 min
03  CSV Pipeline -- 20 min
04  Deployment Intelligence -- 20 min
05  Event-Scale Operations -- 30 min

### Intake -- Workshop Intake (coming soon)
01  Workshop Intake -- 15 min

Pick a number to start a module, or run /preflight to check prerequisites.
```

## Post-Update Protocol

Same convention as courseware:
1. Run validation (if a validator script exists)
2. Tag the release
3. Update Memory MCP entity (`rhdp-ops-tools`)
4. Update Notion Build Releases DB (Project = `rhdp-ops-tools`)
5. Create Jira task on RHDPOPS board

## Execution Order

1. Create `rhpds/rhdp-ops-tools` repo on GitHub
2. Set up repo structure (directories, plugin manifest, CLAUDE.md, README, docs)
3. Copy and transform flow content (skills, modules, scripts, dispatchers)
4. Create catalog and preflight commands
5. Write initial CONTRIBUTING.md and TODO.md
6. Set up branch protection on main
7. Tag v1.0.0
8. Clean remove flow content from courseware
9. Update courseware catalog, preflight, quick-install, validate.py
10. Bump courseware version (minor)
11. Update Confluence, Notion, Memory MCP for both repos
