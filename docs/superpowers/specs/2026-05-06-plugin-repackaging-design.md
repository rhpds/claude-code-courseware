# Plugin Repackaging Design

Repackage claude-code-courseware as a Claude Code plugin marketplace entry
while preserving the current clone-and-use workflow unchanged.

## Goals

1. Existing users running `git clone && claude .` see no behavior change
2. New users can install via rhpds-marketplace and get the same `/learn-*` commands globally
3. RHDP-specific reference data is clearly separated so forks can customize it
4. External teams can fork the repo, edit one file, and run their own courseware

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Marketplace | rhpds-marketplace | Existing RHDP team marketplace, already configured on team machines |
| Config externalization | Reference data only (context.md) | Module prose stays as-is; forks edit prose directly when needed |
| Dual-mode delivery | Overlay pattern | Additive-only; no files move; clone users unaffected |
| Content path resolution | Plugin-root-relative paths | Plugin cache preserves directory structure; `../../modules/` works |
| Config surface | `references/context.md` as-is | Adding a YAML layer is premature; one file is the right abstraction |

## Architecture

### Repo Structure (After)

```
claude-code-courseware/
├── .claude/
│   ├── commands/                ← UNCHANGED — clone mode entry point
│   │   ├── courseware.md
│   │   ├── learn-01-vertex-setup.md
│   │   ├── learn-02-atlassian-mcp.md
│   │   ├── ...
│   │   ├── build-module.md
│   │   └── references/
│   │       └── context.md       ← add "fork this" comment, otherwise unchanged
│   └── settings.json
│
├── .claude-plugin/              ← NEW — plugin manifest
│   └── plugin.json
│
├── skills/                      ← NEW — plugin mode entry point
│   ├── courseware/SKILL.md
│   ├── learn-01-vertex-setup/SKILL.md
│   ├── learn-02-atlassian-mcp/SKILL.md
│   ├── learn-03-memory-mcp/SKILL.md
│   ├── learn-04-git-mcp/SKILL.md
│   ├── learn-05-writing-claude-md/SKILL.md
│   ├── learn-06-playwright-mcp/SKILL.md
│   ├── learn-07-writing-custom-skills/SKILL.md
│   ├── learn-08-hivemind-knowledge-base/SKILL.md
│   ├── learn-11-building-mcp-servers/SKILL.md
│   ├── learn-12-review-agents/SKILL.md
│   ├── learn-13-red-hat-quick-deck/SKILL.md
│   └── build-module/SKILL.md
│
├── modules/                     ← UNCHANGED — shared content
│   ├── 01-vertex-setup.md
│   ├── 02-atlassian-mcp.md
│   ├── ...
│   └── TEMPLATE.md
│
├── docs/
│   ├── fork-your-own.md         ← NEW — fork guide for external teams
│   ├── current-output-and-capacity.html
│   ├── current-output-and-capacity.md
│   ├── meeting-agenda-claude-code-capacity.md
│   └── project-plan.md
│
├── scripts/                     ← UNCHANGED
├── CLAUDE.md                    ← UNCHANGED
└── README.md                    ← UPDATED — add install instructions
```

### Two Install Paths

**Clone mode** (unchanged):
```
git clone https://github.com/rhpds/claude-code-courseware
cd claude-code-courseware
claude .
/courseware
```

**Plugin mode** (new):
```
claude plugin install claude-code-courseware --marketplace rhpds-marketplace
/courseware     # works from any directory
```

Both paths reach the same module catalog and the same `/learn-*` commands.

## Components

### Plugin Manifest (.claude-plugin/)

**plugin.json**:
```json
{
  "name": "claude-code-courseware",
  "description": "Interactive learning modules for Claude Code — MCP servers, skills, agents, and more",
  "version": "1.0.0",
  "author": { "name": "RHDP Team" },
  "repository": "https://github.com/rhpds/claude-code-courseware",
  "license": "Apache-2.0",
  "keywords": ["courseware", "training", "learning", "mcp", "skills"]
}
```

**marketplace.json** is not needed in this repo. The marketplace entry lives in the
rhpds-utils repo (see Marketplace Registration below).

### Skills Directory (skills/)

Each skill is a thin dispatcher with SKILL.md frontmatter pointing at the
corresponding module file. Example for `skills/learn-01-vertex-setup/SKILL.md`:

```markdown
---
name: learn-01-vertex-setup
description: "Claude Code + Vertex AI Setup — install and configure Vertex AI as the backend provider (~10 min)"
---

# Claude Code + Vertex AI Setup

Install Claude Code and configure Vertex AI as the backend provider.
Estimated time: 10 minutes.

Read and follow the module at `../../modules/01-vertex-setup.md` step by step.

Start with the Orientation section, then run the Preflight checks.
Skip any step where the prerequisite already exists.
Guide the user through each remaining step, then run Verification.
Finish with the Challenge.

Use `../../.claude/commands/references/context.md` for team-specific values.
```

Path resolution: from `skills/learn-NN-topic/SKILL.md`, modules are at
`../../modules/NN-topic.md` and context is at
`../../.claude/commands/references/context.md`. The plugin cache preserves
the full directory tree, so these relative paths work in both clone and
plugin mode.

The `skills/courseware/SKILL.md` contains the same catalog display as
`.claude/commands/courseware.md`, directing users to type `/learn-*` commands.

### References / Config Surface

`references/context.md` remains the single file containing org-specific
reference data (Jira keys, MCP server URLs, GCP project list, etc.).
No YAML config layer. A comment at the top tells forks what to customize:

```markdown
# Courseware Context Reference

> Fork this repo? Edit the values below for your organization.
> See docs/fork-your-own.md for the full guide.

Shared reference data for all learning modules.
...
```

### Marketplace Registration (in rhpds-utils)

Add an entry to the rhpds-marketplace index in rhpds-utils. The courseware
repo is a separate GitHub repo (`rhpds/claude-code-courseware`), referenced
cross-repo like the `anthropic-agent-skills` marketplace references
`anthropics/skills`:

```json
"claude-code-courseware": {
  "name": "Claude Code Courseware",
  "description": "Interactive learning modules for Claude Code — MCP servers, skills, agents, and more",
  "version": "1.0.0",
  "skills": [
    "courseware",
    "learn-01-vertex-setup",
    "learn-02-atlassian-mcp",
    "learn-03-memory-mcp",
    "learn-04-git-mcp",
    "learn-05-writing-claude-md",
    "learn-06-playwright-mcp",
    "learn-07-writing-custom-skills",
    "learn-08-hivemind-knowledge-base",
    "learn-11-building-mcp-servers",
    "learn-12-review-agents",
    "learn-13-red-hat-quick-deck",
    "build-module"
  ]
}
```

The exact cross-repo reference format needs to be confirmed against how
rhpds-marketplace resolves external repos. This may require a `source`
field pointing to the GitHub repo.

### build-module Command Update

The existing `build-module` command generates `.claude/commands/learn-*.md`
dispatchers. Extend it to also generate `skills/learn-*/SKILL.md` files.
Both are derived from the same module file in `modules/`.

### Documentation

**docs/fork-your-own.md** — fork guide:
1. Fork the repo
2. Edit `.claude/commands/references/context.md` with your org's values
3. Customize module prose as needed (org names, identity providers, etc.)
4. Choose your install method:
   - Clone mode: `git clone <your-fork> && claude .`
   - Plugin mode: add your fork as a marketplace source, then install
5. Add or remove modules using the `build-module` command

**README.md** — updated with both install paths (plugin and clone) at the top.

## Change Summary

| Item | Action |
|------|--------|
| `.claude/commands/*.md` | Unchanged |
| `modules/*.md` | Unchanged |
| `references/context.md` | Add fork comment at top |
| `scripts/` | Unchanged |
| `CLAUDE.md` | Unchanged |
| `.claude-plugin/plugin.json` | New |
| `skills/*/SKILL.md` | New — 13 skill files |
| `docs/fork-your-own.md` | New |
| `README.md` | Updated — add install instructions |
| `build-module` command | Updated — generate both dispatcher formats |
| rhpds-marketplace index (rhpds-utils) | Updated — add courseware entry |

## Testing

1. **Clone mode**: fresh clone, run `/courseware`, verify catalog displays, run one module
2. **Plugin mode**: install from rhpds-marketplace, run `/courseware` from a different directory, verify catalog and one module work
3. **Path resolution**: verify module content and context.md load correctly from plugin cache paths
4. **Fork workflow**: fork repo, edit context.md, verify modules pick up new values
