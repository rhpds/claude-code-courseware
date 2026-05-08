# Contributing to Claude Code Courseware

## Adding a Module

1. Write your module file at `modules/NN-topic.md` following the structure in `modules/TEMPLATE.md`.
2. Run `/build-module` in Claude Code -- it auto-generates the dispatcher, updates the catalog, and updates the README.
3. Run `python3 scripts/validate.py` to confirm everything is consistent.
4. Open a pull request.

If you prefer to create files manually instead of using `/build-module`:

1. Create `modules/NN-topic.md` using `modules/TEMPLATE.md` as a guide.
2. Create `.claude/commands/learn-NN-topic.md` as a phased dispatcher (see any existing dispatcher for the template).
3. Add the module to `.claude/commands/courseware.md` in the correct section.
4. Add the module to the README table.
5. Run `python3 scripts/validate.py` to verify.

## Module Structure

Every module must contain these sections:

| Section | Purpose |
|---------|---------|
| **Orientation** or **Quick Setup** | What the module teaches, what the user will have when done |
| **Preflight** | Audit current state with EXISTS/MISSING checks |
| **Step N** | At least one guided step with verification |
| **Verification** | Final all-green check |
| **Challenge** | Hands-on task using real team data |

## What CI Checks

The `validate` job in `.github/workflows/courseware-ci.yml` runs `scripts/validate.py`, which checks:

1. Every module file has a matching dispatcher in `.claude/commands/`
2. No orphan dispatchers (dispatchers without a module file)
3. Every module contains all required sections
4. The module count in the catalog matches the actual file count
5. Every module appears in the README table
6. The `skills/` directory does not exist

## Conventions

- **No conventional-commit prefixes** in commit messages or PR titles. Write plain English.
- **No emojis** in any written output.
- **Preflight checks** use the EXISTS/MISSING pattern: audit first, skip what's green.
- **Read-only checks** run automatically; system-modifying actions use the `!` prefix in module instructions.
- **Challenges** use real team data (RHDPOPS Jira project, team MCP servers, etc.).

## Testing Locally

```bash
python3 scripts/validate.py
```

All 6 checks must pass before opening a PR.

## Marking a Module as NEW

Add `<!-- NEW -->` as the last line of the module file. Remove it when the module is no longer new. The catalog detects this marker automatically.
