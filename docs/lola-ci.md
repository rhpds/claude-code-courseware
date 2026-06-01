# Lola CI: Pin, Bot, and Verification Gate

This document describes the automated pipeline that keeps the Lola packaging correct and the `lola-ai` dependency up to date.

## Overview

Three components work together:

1. **Pinned version** (`lola/requirements-lola.txt`) -- the exact `lola-ai` version the project uses
2. **Dependabot** (`.github/dependabot.yml`) -- opens PRs when a new `lola-ai` version is published
3. **GitHub Actions gate** (`.github/workflows/lola-verify.yml`) -- validates that the Lola output hasn't drifted

```
New lola-ai release
  -> Dependabot opens a version-bump PR
  -> lola-verify.yml runs automatically on the PR
  -> If golden snapshot matches: safe to merge
  -> If golden snapshot differs: human reviews the diff
```

## The pin file

`lola/requirements-lola.txt` contains a single pinned version:

```
lola-ai==0.4.4
```

This is a standard pip requirements file. Dependabot knows how to parse and bump it.

## Dependabot configuration

`.github/dependabot.yml` tracks the pin file:

- **Ecosystem**: `pip`
- **Directory**: `/lola` (where `requirements-lola.txt` lives)
- **Schedule**: weekly (Mondays)
- **Grouping**: all `lola-ai` updates in one PR

Dependabot only OPENS the bump PR. It does not auto-merge. The GitHub Actions gate decides whether the bump is safe.

## The verification gate

`.github/workflows/lola-verify.yml` runs on PRs that touch:

- `lola/**` (module content or pin file)
- `courseware-market.yml`
- `tests/golden/**` (golden snapshot)
- `scripts/lola-verify.sh`
- The workflow file itself

### What it does

1. Checks out the PR branch
2. Sets up Python 3.13 + uv
3. Installs the PINNED `lola-ai` from `lola/requirements-lola.txt`
4. Runs `scripts/lola-verify.sh`
5. The script creates the ccc module in a temp dir, installs it, and compares the output against `tests/golden/ccc/`

### Pass/fail

- **Pass**: The Lola output (installed.yml manifest + module file tree) matches the committed golden snapshot exactly
- **Fail**: The output differs -- this means either the content changed (update the golden snapshot) or a Lola version bump changed the output format (human review needed)

## The golden snapshot

`tests/golden/ccc/` contains two files:

- `installed.yml` -- the Lola installation manifest (skills, commands, agents listed)
- `module-tree.txt` -- sorted listing of all files in the installed module

These are committed to the repo and compared on every CI run.

## Refreshing the golden snapshot

When you intentionally change module content (add a skill, rename a command, etc.), the golden snapshot needs updating:

```bash
# 1. Make your content changes to lola/ccc/

# 2. Regenerate the golden snapshot
scripts/lola-verify.sh --update-golden

# 3. Verify it passes
scripts/lola-verify.sh

# 4. Commit the updated golden snapshot alongside your content changes
git add tests/golden/ccc/ lola/ccc/
git commit -m "update ccc module and golden snapshot"
```

## When a Lola version bump changes output

If Dependabot opens a version-bump PR and the CI gate fails, it means the new `lola-ai` version produces different output. This is the safety net:

1. Check out the Dependabot branch
2. Run `scripts/lola-verify.sh` to see the diff
3. If the diff is cosmetic (formatting, ordering): update the golden snapshot and push
4. If the diff is substantive (missing skills, changed structure): investigate before accepting
5. Push the updated golden snapshot to the Dependabot branch to make CI pass

## Requirements

- **Python 3.13+** (lola-ai requires it)
- **uv** (for fast venv creation in CI; falls back to `python3.13 -m venv` locally)
- The `LOLA_HOME` env var is set to a temp dir in CI so it doesn't pollute `~/.lola/`
