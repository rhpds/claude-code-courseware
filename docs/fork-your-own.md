# Fork Your Own Courseware

This guide walks you through creating a customized version of Claude Code Courseware for your team.

## Quick Start

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone git@github.com:YOUR-ORG/claude-code-courseware.git
   cd claude-code-courseware
   ```
3. Edit `.claude/commands/references/context.md` with your organization's values
4. Start learning: `claude .` then `/courseware`

## What to Customize

### Reference Data (required)

Edit `.claude/commands/references/context.md` and replace the RHDP-specific values:

| Section | What to Change |
|---------|---------------|
| Team Environment | GCP project list URL, Vertex AI region |
| Atlassian Rovo MCP Server | Your Atlassian instance URL, Jira project key |
| Hivemind Knowledge Base | Your knowledge base repo (or remove this section) |

### Module Content (optional)

Modules in `modules/` reference your organization by name in some places.
Search for "Red Hat", "RHDP", and "rhpds" and replace with your org's names.
Modules that are specific to RHDP infrastructure (like Module 08 — Hivemind)
can be removed or replaced with your own team-specific modules.

### Adding or Removing Modules

Use the `/build-module` command to create new modules. It generates all
required files (module content, command dispatcher, skill dispatcher, catalog
entries) from a template.

To remove a module:
1. Delete `modules/NN-topic.md`
2. Delete `.claude/commands/learn-NN-topic.md`
3. Delete `skills/learn-NN-topic/SKILL.md`
4. Remove the entry from `.claude/commands/courseware.md`
5. Remove the entry from `skills/courseware/SKILL.md`
6. Remove the row from the table in `README.md`

## Distribution Options

### Clone Mode (simplest)

Share your fork URL. Users clone and run:
```bash
git clone git@github.com:YOUR-ORG/claude-code-courseware.git
cd claude-code-courseware
claude .
/courseware
```

### Plugin Mode (global install)

To distribute as a plugin, users add your fork as a marketplace source
in `~/.claude/marketplaces.json`:

```json
{
  "your-marketplace": {
    "org": "YOUR-ORG",
    "repo": "claude-code-courseware",
    "path": ".claude-plugin",
    "plugins": {
      "claude-code-courseware": {
        "name": "Claude Code Courseware",
        "description": "Your description here",
        "version": "1.0.0",
        "skills": ["courseware", "learn-01-vertex-setup", "..."]
      }
    }
  }
}
```

Then install:
```
claude plugin install claude-code-courseware --marketplace your-marketplace
```

The `/courseware` and `/learn-*` commands become available globally.
