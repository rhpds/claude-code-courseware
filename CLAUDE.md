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
