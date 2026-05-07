# Courseware Review Design Spec

**Date:** 2026-05-07
**Scope:** Multi-contributor readiness — structural cleanup, automation, and collaboration infrastructure.
**Approach:** Full Automation (Option A) — contributors write one module file, everything else is generated, validated, or handled by scripts and CI.

---

## Layer 1 — Fix the Foundation

### 1.1 Eliminate Dual Distribution

Delete the entire `skills/` directory (18 directories, 18 SKILL.md files). The plugin manifest already exposes `.claude/commands/` for slash-command discovery.

**Migration:** No user-facing change. Plugin users get commands automatically. Anyone who manually symlinked a skill file switches to the plugin (`claude plugin add github:rhpds/claude-code-courseware`).

**Files deleted:** All 18 directories under `skills/`.
**Files updated:** README.md (remove any references to skills/ installation).

### 1.2 Integrity Validation Script

**File:** `scripts/validate.py`

**Checks:**

1. **Dispatcher coverage** — Every `modules/NN-*.md` (excluding TEMPLATE.md) has a matching `.claude/commands/learn-NN-*.md`.
2. **No orphan dispatchers** — Every `learn-NN-*.md` dispatcher points to an existing module.
3. **Module structure** — Every module contains required sections: Orientation or Quick Setup, Preflight, at least one Step, Verification, Challenge.
4. **Catalog count** — The module count in `courseware.md` matches the actual file count.
5. **README sync** — Every module appears in the README table.
6. **No stale skills/** — Fail if `skills/` directory exists.

**Output:** PASS/FAIL per check with clear error messages. Exit code 0 on all-pass, 1 on any failure.

**Usage:** Called by post-update protocol, GitHub Actions CI, and available for manual runs.

**Language:** Python 3 (available on all GitHub runners, no dependencies to install).

### 1.3 Clean Stale Content

**Delete:**

- `docs/superpowers/plans/2026-05-06-robust-mcp-install-pattern.md` (1452 lines)
- `docs/superpowers/plans/2026-05-06-plugin-repackaging.md` (1028 lines)

**Strip settings.local.json:** Audit the 94 permission entries. Keep only rules that end users need when running modules (git read ops, MCP tool calls for exercises). Move development-only rules (Confluence writes, Notion writes, broad bash patterns) to a separate `docs/developer-permissions.md` reference doc for maintainers.

---

## Layer 2 — Automate the Workflow

### 2.1 Enhanced /build-module Skill

**Current state:** `build-module.md` is 99 lines. It guides you through creating a module file and dispatcher manually. It does not auto-generate anything.

**New behavior:** After the user writes (or provides) the module file, /build-module automatically:

1. Detects the module number and topic from the filename (`modules/22-workshop-intake.md`).
2. Validates the module has all required sections (calls `scripts/validate.py` on just that file).
3. Generates the dispatcher at `.claude/commands/learn-22-workshop-intake.md` using the standard template.
4. Adds the module to the catalog in `courseware.md` under the correct section (asks the user which section).
5. Adds the module to the README table.
6. Runs full integrity validation to confirm everything is consistent.

**Contributor experience:** Write the module content, run `/build-module`, review the generated files, commit.

### 2.2 Dynamic Module Discovery

Replace all hardcoded module ranges with dynamic discovery:

- **courseware.md progress scan:** `for f in modules/[0-9]*.md` instead of `seq -w 1 21`. Extract number from filename.
- **Catalog count:** Compute from the glob, not a literal in the text.
- **NEW tag list:** Use a `<!-- NEW -->` marker in the module file. The maintainer adds it when creating the module and removes it later. Chosen over git-log-based detection because it's cheaper, simpler, and explicit.

### 2.3 Lazy-Load Dispatchers

Replace current 13-line dispatchers with phased dispatchers (~30 lines) that present modules in stages:

- **Phase 1:** Read only Quick Setup and Orientation sections. Present them. Ask: "Ready to check prerequisites?"
- **Phase 2:** Read only Preflight section. Run checks. Skip passing steps. Report results. Ask: "Ready to start the walkthrough?"
- **Phase 3:** Read and present one Step at a time. After each step's verification passes, proceed to the next. Do not read ahead.
- **Phase 4:** Read only Verification section. Run all checks. Report results.
- **Phase 5:** Read only Challenge and Challenge Verification sections. Present the challenge. After the user completes it, verify.

**Token savings estimate:** For a 700-line module, each phase loads ~50-150 lines. A typical session that completes preflight + 3 steps consumes roughly 40-60% fewer tokens than loading the full module.

### 2.4 Permissions Cleanup

**Current:** 94 permission entries in `settings.local.json`.

**Categorize each entry as:**

- **End-user essential** — needed to run modules (git read ops, npm/npx, python3 for checks, MCP tool calls used in exercises).
- **Maintainer-only** — Confluence writes, Notion writes, broad file writes, deployment commands.
- **Development artifact** — overly broad patterns from testing, duplicates.

**Result:** `settings.local.json` ships with end-user essentials only. Maintainer rules go in a documented `.claude/settings.maintainer.json` (not loaded by default — maintainers merge it manually or via a script).

---

## Layer 3 — Enable Contributors

### 3.1 GitHub Actions CI Pipeline

**File:** `.github/workflows/courseware-ci.yml`

**Triggers:** Push to main, pull requests targeting main.

**Jobs:**

1. **validate** — Run `python3 scripts/validate.py`. Checks dispatcher coverage, module structure, catalog count, README sync, no orphan files. This is the gate — if it fails, the PR can't merge.
2. **lint-markdown** (optional, lightweight) — Run `markdownlint` on modules/ to catch broken formatting. Warn-only, not blocking.

**Runtime:** Under 30 seconds. No dependencies to install beyond Python 3 (available on all GitHub runners).

**Contributor experience:** Open a PR with a new module. CI tells you within 30 seconds if you missed a dispatcher, forgot a section, or didn't update the catalog. Fix and push — no maintainer round-trip needed.

### 3.2 Contributor Documentation

**CONTRIBUTING.md** (new, ~80 lines):

- How to add a module: write the file, run `/build-module` (or manually create dispatcher + catalog entry), open PR.
- Module structure reference: required sections with one-line descriptions.
- What CI checks: link to validate.py, explanation of each check.
- Conventions: no conventional-commit prefixes, no emojis, preflight EXISTS/MISSING pattern.
- How to test locally: `python3 scripts/validate.py`.

**.github/PULL_REQUEST_TEMPLATE.md** (new, ~15 lines):

```
## What changed
(brief description)

## Module checklist
- [ ] Module file in modules/NN-topic.md
- [ ] Dispatcher in .claude/commands/learn-NN-topic.md
- [ ] Added to catalog in courseware.md
- [ ] Added to README table
- [ ] All required sections present (Orientation, Preflight, Steps, Verification, Challenge)
- [ ] Ran scripts/validate.py locally -- all checks pass
```

**.github/ISSUE_TEMPLATE/** (new, 2 templates):

- **new-module.md** — "Propose a new module": title, what it teaches, prerequisites, estimated time.
- **module-fix.md** — "Fix or improve a module": which module, what's wrong, suggested fix.

### 3.3 Dynamic Progress Tracking

**Problem:** Progress scan in courseware.md uses `seq -w 1 21`. Adding Module 22 requires updating this line.

**Fix:** Replace with a glob-based scan:

```bash
PROGRESS_DIR="$HOME/.claude/courseware-progress"
if [ -d "$PROGRESS_DIR" ]; then
  for f in modules/[0-9]*.md; do
    n=$(basename "$f" | grep -o '^[0-9]*')
    if [ -f "$PROGRESS_DIR/$n.done" ]; then
      echo "DONE:$n"
    elif [ -f "$PROGRESS_DIR/$n.started" ]; then
      echo "IN_PROGRESS:$n"
    fi
  done
fi
```

**Location:** Update in `courseware.md` (the catalog command). Same filesystem markers, just discovered dynamically. Works for any number of modules without code changes.

---

## Implementation Order

The three layers are sequenced by dependency:

1. **Layer 1** first — removes dead code, establishes validation infrastructure, cleans stale content.
2. **Layer 2** second — builds on the validation script (1.2) to automate the contributor workflow.
3. **Layer 3** third — builds on validation (1.2) and automation (2.1) to enable CI and collaboration.

Within each layer, items can be implemented in the order listed.
