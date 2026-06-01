# Lola Packaging

This document describes how the courseware is packaged as a Lola module for distribution via `lola install`.

## What is a Lola module?

Lola is a CLI tool (`lola-ai`) that packages and distributes skills, commands, and agents across AI coding assistants. A Lola module is a directory containing skills, commands, and (optionally) agents in a standardized layout that Lola auto-discovers -- no manifest file needed.

## Module layout

The courseware lives under `lola/ccc/`:

```
lola/ccc/
  skills/
    01-vertex-setup/
      SKILL.md                  # the module content (from modules/01-vertex-setup.md)
      scripts/                  # supporting files (setup scripts, templates)
        setup-claude-vertex.sh
        setup-claude-vertex-portable.sh
    02-writing-claude-md/
      SKILL.md
    ...
    29-effort-reasoning-control/
      SKILL.md
    TEMPLATE/
      SKILL.md
    references/
      context.md                # shared team reference data
  commands/
    ccc-courseware.md            # catalog
    ccc-learn-01-vertex-setup.md
    ...
    ccc-preflight.md
    ccc-quick-install.md
    ccc-build-module.md
    ccc-update-courseware.md
```

Key points:
- Each course module is a skill directory: `skills/<name>/SKILL.md`
- Each dispatcher is a command: `commands/ccc-<name>.md`
- The `ccc-` prefix is the module name -- Lola prefixes all skills and commands with it on install
- Supporting files (scripts, templates) live inside their skill directory so relative paths work

## How to edit a skill

1. Edit the SKILL.md file directly under `lola/ccc/skills/<name>/SKILL.md`
2. The corresponding module source at `modules/<name>.md` is the canonical version on main -- Lola content is generated from it
3. To verify your changes work with Lola: `scripts/lola-verify.sh`
4. If the golden snapshot drifts (expected after content changes): `scripts/lola-verify.sh --update-golden`

## The edit-verify loop

```bash
# 1. Edit skill content
vim lola/ccc/skills/03-memory-mcp/SKILL.md

# 2. Verify Lola processes it correctly
scripts/lola-verify.sh

# 3. If content changed, update golden snapshot
scripts/lola-verify.sh --update-golden

# 4. Verify the new golden snapshot passes
scripts/lola-verify.sh
```

## Prefixing behavior

When Lola installs the `ccc` module, all skills and commands get the module name as a prefix:

| Source | Installed as |
|--------|-------------|
| `skills/01-vertex-setup/SKILL.md` | skill `ccc-01-vertex-setup` |
| `commands/ccc-learn-01-vertex-setup.md` | command `/ccc-learn-01-vertex-setup` |
| `commands/ccc-courseware.md` | command `/ccc-courseware` |

The `ccc-` prefix in command filenames is part of the command name, not doubled by Lola.

## Adding local-llm-courseware later

The layout is designed for a second module to sit beside `ccc`:

```
lola/
  ccc/                  # Claude Code courseware (this module)
  local-llm/            # future: local LLM courseware
  requirements-lola.txt # shared pin for both modules
```

To add it:
1. Create `lola/local-llm/` with the same `skills/` and `commands/` layout
2. Add a second entry to `courseware-market.yml`
3. Update `scripts/lola-verify.sh` to also verify the new module
4. Add a golden snapshot at `tests/golden/local-llm/`

## Relationship to .claude/

The existing `.claude/commands/` and `modules/` directories are the working setup on `main`. The Lola packaging under `lola/ccc/` is a parallel distribution format -- it does not replace or modify `.claude/`. Both can coexist.

On `main`, the courseware is consumed via the Claude Code plugin system (`.claude/commands/`).
Via Lola, the courseware is consumed via `lola install ccc -a claude-code`.
