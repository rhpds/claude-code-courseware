# Courseware Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the courseware repo multi-contributor ready by eliminating dead code, automating the add-a-module workflow, and adding CI + contributor docs.

**Architecture:** Three sequenced layers: (1) foundation cleanup — delete skills/, write validate.py, remove stale docs; (2) workflow automation — enhance /build-module, make dispatchers lazy-load, make discovery dynamic; (3) collaboration — GitHub Actions CI, CONTRIBUTING.md, templates. Each layer depends on the previous one.

**Tech Stack:** Python 3 (validation script), GitHub Actions (CI), Markdown (docs/templates), Bash (shell globs in courseware.md).

---

## File Map

**Create:**
- `scripts/validate.py` — integrity validation (6 checks)
- `CONTRIBUTING.md` — contributor guide
- `.github/workflows/courseware-ci.yml` — CI pipeline
- `.github/PULL_REQUEST_TEMPLATE.md` — PR checklist
- `.github/ISSUE_TEMPLATE/new-module.md` — new module proposal
- `.github/ISSUE_TEMPLATE/module-fix.md` — fix/improve a module
- `docs/developer-permissions.md` — reference doc for maintainer permissions

**Modify:**
- `.claude/commands/courseware.md` — dynamic progress scan, dynamic count, dynamic NEW tags
- `.claude/commands/build-module.md` — auto-generate dispatcher + catalog + README
- `.claude/commands/learn-*.md` (21 files) — lazy-load phased dispatchers
- `.claude/settings.local.json` — strip to end-user essentials
- `README.md` — remove skills/ references
- `CLAUDE.md` — update post-update protocol to call validate.py

**Delete:**
- `skills/` (18 directories, 18 SKILL.md files)
- `docs/superpowers/plans/2026-05-06-robust-mcp-install-pattern.md`
- `docs/superpowers/plans/2026-05-06-plugin-repackaging.md`

---

## Task 1: Delete skills/ directory

**Files:**
- Delete: `skills/` (entire directory tree — 18 subdirectories)
- Modify: `README.md`

- [ ] **Step 1: Verify skills/ contents match expectations**

```bash
find skills/ -name "SKILL.md" | wc -l
# Expected: 18
ls skills/
```

Confirm 18 SKILL.md files, all mirroring `.claude/commands/` dispatchers.

- [ ] **Step 2: Delete the skills/ directory**

```bash
rm -rf skills/
```

- [ ] **Step 3: Remove skills/ references from README.md**

In `README.md`, the "Authoring New Modules" section (around line 149-154) references skills. No other section references `skills/` directly. Update the authoring section to remove the skills/ dispatcher step.

Replace lines 149-154:

```markdown
## Authoring New Modules

1. Create `modules/NN-topic.md` following the module template (see any existing module)
2. Create `.claude/commands/learn-NN-topic.md` as a thin dispatcher
3. Add the module to the catalog in `.claude/commands/courseware.md`
4. Update the tables in this README
```

This removes the implicit reference to skills/ that was in the old workflow. The section already doesn't mention skills/ explicitly, but confirm with:

```bash
grep -n -i 'skills/' README.md
# Expected: no output
```

- [ ] **Step 4: Remove skills/ references from build-module.md**

The file `.claude/commands/build-module.md` generates a `skills/learn-NN-TOPIC/SKILL.md` file (lines 64-85) and updates `skills/courseware/SKILL.md` (line 87). Remove these references — the build-module command will be fully rewritten in Task 5, but for now remove the skills/ generation so the repo is consistent.

In `build-module.md`, delete the **Dispatcher skill** block (lines 64-85) that starts with `**Dispatcher skill** — \`skills/learn-NN-TOPIC/SKILL.md\`` and ends with the closing triple-backtick.

Also update line 87 to remove `skills/courseware/SKILL.md`:

Old:
```
   **Update catalogs** — Edit both `.claude/commands/courseware.md` AND `skills/courseware/SKILL.md`
```
New:
```
   **Update catalog** — Edit `.claude/commands/courseware.md`
```

Update step 7 commit commands to remove skills/ paths:

Old:
```
   - `git add .claude/commands/learn-NN-TOPIC.md skills/learn-NN-TOPIC/SKILL.md && git commit -m "add /learn-NN-TOPIC dispatchers"`
   - `git add .claude/commands/courseware.md skills/courseware/SKILL.md README.md && git commit -m "update catalog and README for Module NN"`
```
New:
```
   - `git add .claude/commands/learn-NN-TOPIC.md && git commit -m "add /learn-NN-TOPIC dispatcher"`
   - `git add .claude/commands/courseware.md README.md && git commit -m "update catalog and README for Module NN"`
```

- [ ] **Step 5: Verify no remaining skills/ references in commands**

```bash
grep -r 'skills/' .claude/commands/ --include="*.md"
# Expected: no output (or only references/context.md if it mentions skills as a concept)
```

- [ ] **Step 6: Commit**

```bash
git add -A skills/
git add README.md .claude/commands/build-module.md
git commit -m "$(cat <<'EOF'
delete skills/ directory — commands-only distribution

Plugin manifest exposes .claude/commands/ directly. The skills/
directory was a duplicate distribution path that is no longer needed.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Create scripts/validate.py

**Files:**
- Create: `scripts/validate.py`

- [ ] **Step 1: Create scripts/ directory if needed**

```bash
ls scripts/
# scripts/ already exists (has setup-claude-vertex.sh)
```

- [ ] **Step 2: Write validate.py**

Create `scripts/validate.py` with all 6 checks from the spec:

```python
#!/usr/bin/env python3
"""Courseware integrity validator.

Checks:
  1. Dispatcher coverage — every module has a dispatcher
  2. No orphan dispatchers — every dispatcher has a module
  3. Module structure — required sections present
  4. Catalog count — courseware.md count matches file count
  5. README sync — every module in README table
  6. No stale skills/ — skills/ directory must not exist

Exit 0 on all-pass, 1 on any failure.
"""

import glob
import os
import re
import sys


def get_module_files():
    files = glob.glob("modules/[0-9]*.md")
    return [f for f in files if "TEMPLATE" not in f]


def extract_module_info(path):
    basename = os.path.basename(path)
    match = re.match(r"^(\d+)-(.+)\.md$", basename)
    if match:
        return match.group(1), match.group(2)
    return None, None


def check_dispatcher_coverage(modules):
    errors = []
    for mod in modules:
        num, topic = extract_module_info(mod)
        if num is None:
            errors.append(f"  Cannot parse module filename: {mod}")
            continue
        dispatcher = f".claude/commands/learn-{num}-{topic}.md"
        if not os.path.exists(dispatcher):
            errors.append(f"  MISSING dispatcher: {dispatcher} (for {mod})")
    return errors


def check_orphan_dispatchers(modules):
    errors = []
    module_keys = set()
    for mod in modules:
        num, topic = extract_module_info(mod)
        if num and topic:
            module_keys.add(f"{num}-{topic}")

    dispatchers = glob.glob(".claude/commands/learn-[0-9]*.md")
    for disp in dispatchers:
        basename = os.path.basename(disp)
        match = re.match(r"^learn-(\d+)-(.+)\.md$", basename)
        if match:
            key = f"{match.group(1)}-{match.group(2)}"
            if key not in module_keys:
                errors.append(f"  ORPHAN dispatcher: {disp} (no matching module)")
    return errors


def check_module_structure(modules):
    errors = []
    required_sections = [
        (r"##\s+(Orientation|Quick Setup)", "Orientation or Quick Setup"),
        (r"##\s+Preflight", "Preflight"),
        (r"##\s+Step\s+\d", "at least one Step"),
        (r"##\s+Verification", "Verification"),
        (r"##\s+Challenge", "Challenge"),
    ]
    for mod in modules:
        with open(mod, "r") as f:
            content = f.read()
        missing = []
        for pattern, label in required_sections:
            if not re.search(pattern, content):
                missing.append(label)
        if missing:
            errors.append(f"  {mod}: missing sections: {', '.join(missing)}")
    return errors


def check_catalog_count(modules):
    errors = []
    catalog_path = ".claude/commands/courseware.md"
    if not os.path.exists(catalog_path):
        errors.append(f"  Catalog not found: {catalog_path}")
        return errors

    with open(catalog_path, "r") as f:
        content = f.read()

    match = re.search(r"\*\*(\d+)\s+modules?\s+available", content)
    if not match:
        errors.append("  No module count found in catalog (expected '**N modules available')")
        return errors

    catalog_count = int(match.group(1))
    actual_count = len(modules)
    if catalog_count != actual_count:
        errors.append(
            f"  Catalog says {catalog_count} modules, but found {actual_count} module files"
        )
    return errors


def check_readme_sync(modules):
    errors = []
    if not os.path.exists("README.md"):
        errors.append("  README.md not found")
        return errors

    with open("README.md", "r") as f:
        readme = f.read()

    for mod in modules:
        num, topic = extract_module_info(mod)
        if num is None:
            continue
        num_stripped = num.lstrip("0") or "0"
        if f"| {num_stripped} " not in readme and f"| {num} " not in readme:
            errors.append(f"  Module {num} ({topic}) not found in README table")
    return errors


def check_no_stale_skills():
    errors = []
    if os.path.isdir("skills"):
        count = len(glob.glob("skills/*/SKILL.md"))
        errors.append(f"  skills/ directory still exists ({count} SKILL.md files)")
    return errors


def main():
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    modules = get_module_files()
    if not modules:
        print("FAIL: No module files found in modules/")
        sys.exit(1)

    checks = [
        ("Dispatcher coverage", check_dispatcher_coverage(modules)),
        ("No orphan dispatchers", check_orphan_dispatchers(modules)),
        ("Module structure", check_module_structure(modules)),
        ("Catalog count", check_catalog_count(modules)),
        ("README sync", check_readme_sync(modules)),
        ("No stale skills/", check_no_stale_skills()),
    ]

    failed = False
    for name, errors in checks:
        if errors:
            print(f"FAIL: {name}")
            for e in errors:
                print(e)
            failed = True
        else:
            print(f"PASS: {name}")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Make it executable**

```bash
chmod +x scripts/validate.py
```

- [ ] **Step 4: Run validate.py to verify it works**

```bash
python3 scripts/validate.py
```

Expected: all 6 checks PASS (assuming Task 1 already deleted skills/).

If any check fails, fix the issue in the codebase (not in validate.py — the script is the source of truth).

- [ ] **Step 5: Commit**

```bash
git add scripts/validate.py
git commit -m "$(cat <<'EOF'
add courseware integrity validator

Six checks: dispatcher coverage, orphan dispatchers, module
structure, catalog count, README sync, no stale skills/.
Runs in CI and locally via python3 scripts/validate.py.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Delete stale planning docs

**Files:**
- Delete: `docs/superpowers/plans/2026-05-06-robust-mcp-install-pattern.md`
- Delete: `docs/superpowers/plans/2026-05-06-plugin-repackaging.md`

- [ ] **Step 1: Delete the files**

```bash
rm docs/superpowers/plans/2026-05-06-robust-mcp-install-pattern.md
rm docs/superpowers/plans/2026-05-06-plugin-repackaging.md
```

- [ ] **Step 2: Verify no other code references them**

```bash
grep -r "robust-mcp-install-pattern\|plugin-repackaging" . --include="*.md" --include="*.py" --include="*.yml" | grep -v ".git/"
# Expected: no output
```

- [ ] **Step 3: Commit**

```bash
git add -A docs/superpowers/plans/2026-05-06-robust-mcp-install-pattern.md docs/superpowers/plans/2026-05-06-plugin-repackaging.md
git commit -m "$(cat <<'EOF'
delete stale planning docs

These specs were implemented and are no longer needed.
Removes 2480 lines of obsolete planning content.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Strip settings.local.json to end-user essentials

**Files:**
- Modify: `.claude/settings.local.json`
- Create: `docs/developer-permissions.md`

- [ ] **Step 1: Categorize current permissions**

Read `.claude/settings.local.json` (94 entries). Categorize each into:

**End-user essential** (keep — needed to run modules):
```json
{
  "permissions": {
    "allow": [
      "Bash(git *)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(git diff *)",
      "Bash(git pull *)",
      "Bash(git push *)",
      "Bash(command -v claude)",
      "Bash(python3 *)",
      "Bash(python3 -c ' *)",
      "Bash(npx --version)",
      "Bash(npm --version)",
      "Bash(npm list *)",
      "Bash(npx --yes @playwright/mcp@latest --help)",
      "Bash(grep *)",
      "Bash(chmod +x *)",
      "Bash(bash *)",
      "Bash(claude plugin *)",
      "Bash(claude mcp *)",
      "Bash(claude skill *)",
      "Bash(mkdir -p ~/.claude/courseware-progress)",
      "Bash(date -u +%Y-%m-%dT%H:%M:%SZ)",
      "Bash(open *)",
      "mcp__memory__create_entities",
      "mcp__memory__search_nodes",
      "mcp__memory__add_observations",
      "mcp__git__git_log",
      "mcp__git__git_status",
      "mcp__git__git_diff_unstaged",
      "mcp__plugin_playwright_playwright__browser_navigate",
      "mcp__plugin_playwright_playwright__browser_snapshot",
      "mcp__plugin_playwright_playwright__browser_click",
      "mcp__plugin_playwright_playwright__browser_evaluate",
      "mcp__plugin_playwright_playwright__browser_take_screenshot",
      "mcp__plugin_playwright_playwright__browser_press_key",
      "mcp__plugin_playwright_playwright__browser_close",
      "mcp__plugin_playwright_playwright__browser_wait_for",
      "mcp__plugin_atlassian_atlassian__getAccessibleAtlassianResources",
      "mcp__plugin_atlassian_atlassian__searchJiraIssuesUsingJql",
      "mcp__plugin_atlassian_atlassian__getJiraIssue",
      "mcp__plugin_atlassian_atlassian__getTransitionsForJiraIssue",
      "mcp__plugin_atlassian_atlassian__addCommentToJiraIssue",
      "mcp__plugin_atlassian_atlassian__transitionJiraIssue",
      "mcp__plugin_atlassian_atlassian__createJiraIssue",
      "mcp__sequential-thinking__sequentialthinking",
      "WebSearch"
    ]
  }
}
```

**Maintainer-only** (document in developer-permissions.md):
- `Bash(gh api *)`, `Bash(gh pr *)`
- `mcp__plugin_atlassian_atlassian__search`
- `mcp__plugin_atlassian_atlassian__getConfluencePage`
- `mcp__plugin_atlassian_atlassian__updateConfluencePage`
- `mcp__claude_ai_Notion__notion-fetch`
- `mcp__claude_ai_Notion__notion-create-pages`
- `mcp__claude_ai_Notion__notion-update-data-source`
- `mcp__jira__*` (legacy Jira MCP entries)
- `Bash(lsof *)`, `Bash(xargs kill *)`
- Various one-off `Bash(curl *)`, `Bash(ln -sf *)` patterns

- [ ] **Step 2: Write the stripped settings.local.json**

Overwrite `.claude/settings.local.json` with the end-user essential list from Step 1.

- [ ] **Step 3: Create docs/developer-permissions.md**

```markdown
# Developer / Maintainer Permissions

These permission rules are used by courseware maintainers but are NOT needed by end users running modules. To use them, merge into your `.claude/settings.local.json`:

## GitHub CLI

```json
"Bash(gh api *)",
"Bash(gh pr *)"
```

## Confluence (post-update protocol)

```json
"mcp__plugin_atlassian_atlassian__search",
"mcp__plugin_atlassian_atlassian__getConfluencePage",
"mcp__plugin_atlassian_atlassian__updateConfluencePage"
```

## Notion (build log)

```json
"mcp__claude_ai_Notion__notion-fetch",
"mcp__claude_ai_Notion__notion-create-pages",
"mcp__claude_ai_Notion__notion-update-data-source"
```

## Process Management

```json
"Bash(lsof *)",
"Bash(xargs kill *)"
```

## Symlink Management

```json
"Bash(ln -sf *)"
```
```

- [ ] **Step 4: Run validate.py to confirm nothing broke**

```bash
python3 scripts/validate.py
```

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add .claude/settings.local.json docs/developer-permissions.md
git commit -m "$(cat <<'EOF'
strip settings.local.json to end-user essentials

Maintainer-only permissions (Confluence, Notion, GitHub CLI,
process management) moved to docs/developer-permissions.md.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Rewrite /build-module for auto-generation

**Files:**
- Modify: `.claude/commands/build-module.md`

- [ ] **Step 1: Write the new build-module.md**

Replace the entire contents of `.claude/commands/build-module.md` with:

```markdown
# Build a New Courseware Module

You are building a new learning module for the claude-code-courseware project.

## Instructions

1. Ask: "Which module number and topic?" (e.g., "22 -- Workshop Intake")
   If the user already specified it, skip this question.

2. Read `modules/TEMPLATE.md` for the exact structure to follow.

3. Read `.claude/commands/references/context.md` for team-specific values.

4. Ask: "Any specific source material I should read?" (e.g., a repo path, skill file, or MCP server docs)
   If the user provides a path, read it for content. If not, use your built-in knowledge of the tool.

4b. **Detect MCP module**: If the topic contains "MCP" or the user mentions
    an MCP server, ask: "This looks like an MCP module. What's the npm package name?"
    Then gather:
    - **npm package**: e.g., `@playwright/mcp`
    - **server name**: key in mcpServers (e.g., `playwright`)
    - **npx args**: args array (e.g., `["@playwright/mcp@latest", "--browser", "chrome"]`)
    - **tool prefix**: expected MCP tool prefix (e.g., `mcp__playwright__`)
    - **extra deps**: any server-specific dependencies (e.g., Chrome)

    When generating the module content in step 5, use the **MCP Module Variant**
    section from `modules/TEMPLATE.md` instead of the generic Preflight and Step 1.
    Fill in all `<PLACEHOLDER>` values with the gathered information.

    The generated module MUST include:
    - Phase 1 dependency checks (node, npm, npx, PATH consistency, extra deps)
    - Phase 2 global npm install + smoke test (Step 1a + 1b)
    - Phase 3 full-path config write using `shutil.which("npx")` (Step 1c)
    - Phase 4 post-restart verification with diagnostic ladder
    - The restart instruction with the verification contract wording

5. Generate the module file at `modules/NN-TOPIC.md`.
   Follow TEMPLATE.md exactly. Fill in every placeholder.

6. **Validate the module** before generating other files:

   ```bash
   python3 scripts/validate.py
   ```

   If the module is missing required sections, fix it before proceeding.

7. **Auto-generate the dispatcher** at `.claude/commands/learn-NN-TOPIC.md`:

   ```
   # TITLE

   DESCRIPTION.
   Estimated time: X minutes. Prerequisites: LIST.

   Read modules/NN-TOPIC.md but present it in phases:

   Phase 1: Read only the Quick Setup and Orientation sections. Present them.
            Ask: "Ready to check prerequisites?"

   Phase 2: Read only the Preflight section. Run the checks.
            Skip any step that passes. Report results.
            Ask: "Ready to start the walkthrough?"

   Phase 3: Read and present one Step at a time.
            After each step's verification passes, proceed to the next.
            Do not read ahead -- load each step only when needed.

   Phase 4: Read only the Verification section. Run all checks.
            Report results.

   Phase 5: Read only the Challenge and Challenge Verification sections.
            Present the challenge. After the user completes it, verify.

   Use .claude/commands/references/context.md for team-specific values.
   Track progress in ~/.claude/courseware-progress/.
   ```

8. **Add to catalog** — Ask the user: "Which section should this go in?"
   Show the section list from `courseware.md`. Insert the module entry
   in the correct section. Update the module count in the Footer.

9. **Add to README** — Insert a row in the correct section table in `README.md`.

10. **Run full validation:**

    ```bash
    python3 scripts/validate.py
    ```

    All 6 checks must pass before proceeding.

11. Commit all generated files:

    ```bash
    git add modules/NN-TOPIC.md .claude/commands/learn-NN-TOPIC.md .claude/commands/courseware.md README.md
    git commit -m "add Module NN -- TITLE"
    ```

12. Report what was created and suggest `git push origin main` for the user to approve.
```

- [ ] **Step 2: Verify the new build-module.md has no skills/ references**

```bash
grep -i 'skills/' .claude/commands/build-module.md
# Expected: no output
```

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/build-module.md
git commit -m "$(cat <<'EOF'
rewrite /build-module for auto-generation

After the user writes the module file, /build-module now auto-generates
the lazy-load dispatcher, adds to catalog, adds to README, and runs
full integrity validation. No more manual dispatcher creation.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Make courseware.md discovery dynamic

**Files:**
- Modify: `.claude/commands/courseware.md`

- [ ] **Step 1: Replace the hardcoded progress scan**

In `.claude/commands/courseware.md`, replace the progress scan section (lines 33-44):

Old:
```bash
PROGRESS_DIR="$HOME/.claude/courseware-progress"
if [ -d "$PROGRESS_DIR" ]; then
  for n in $(seq -w 1 21); do
    if [ -f "$PROGRESS_DIR/$n.done" ]; then
      echo "DONE:$n"
    elif [ -f "$PROGRESS_DIR/$n.started" ]; then
      echo "IN_PROGRESS:$n"
    fi
  done
fi
```

New:
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

- [ ] **Step 2: Replace hardcoded NEW list with marker-based detection**

In `.claude/commands/courseware.md`, replace line 58:

Old:
```
**NEW modules:** 07, 08, 10, 14, 15, 16, 17, 21
```

New:
```
**NEW modules:** Scan each module file for a `<!-- NEW -->` HTML comment. If present, that module gets the **NEW** tag. This replaces the hardcoded list.
```

- [ ] **Step 3: Make the footer count dynamic**

In `.claude/commands/courseware.md`, replace the hardcoded count in the footer (line 116):

Old:
```
> **21 modules available.** Modules marked **NEW** were recently added.
```

New:
```
> **[COUNT] modules available.** Modules marked **NEW** were recently added.

Where [COUNT] is computed by counting `modules/[0-9]*.md` files excluding TEMPLATE.md:
```bash
ls modules/[0-9]*.md | wc -l | tr -d ' '
```
```

- [ ] **Step 4: Add `<!-- NEW -->` markers to the 8 currently-new module files**

Add `<!-- NEW -->` as the last line of each of these module files:

```bash
for mod in modules/07-notion-mcp.md modules/08-container-podman-mcp.md modules/10-hooks.md modules/14-debugging-troubleshooting.md modules/15-cost-context-management.md modules/16-multi-repo-workspaces.md modules/17-ci-cd-integration.md modules/21-plugin-marketplace.md; do
  echo "" >> "$mod"
  echo "<!-- NEW -->" >> "$mod"
done
```

- [ ] **Step 5: Run validate.py**

```bash
python3 scripts/validate.py
```

Expected: all PASS. The catalog count check will need the footer to use the dynamic count — if it fails because of the `[COUNT]` placeholder text, update the instruction wording so the catalog renders the actual number dynamically.

- [ ] **Step 6: Commit**

```bash
git add .claude/commands/courseware.md modules/07-notion-mcp.md modules/08-container-podman-mcp.md modules/10-hooks.md modules/14-debugging-troubleshooting.md modules/15-cost-context-management.md modules/16-multi-repo-workspaces.md modules/17-ci-cd-integration.md modules/21-plugin-marketplace.md
git commit -m "$(cat <<'EOF'
make module discovery and progress tracking dynamic

Replace hardcoded seq range and NEW list with glob-based scan
and per-file markers. Adding a module no longer requires updating
the progress scan or NEW list.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Convert all dispatchers to lazy-load format

**Files:**
- Modify: `.claude/commands/learn-01-vertex-setup.md` through `learn-21-plugin-marketplace.md` (21 files)

- [ ] **Step 1: Read one existing dispatcher to confirm the current template**

```bash
cat .claude/commands/learn-01-vertex-setup.md
```

Confirm it matches the 13-line pattern:
```
# TITLE

DESCRIPTION.
Estimated time: X minutes.

Read and follow the module at `modules/NN-TOPIC.md` step by step.

Start with the Orientation section, then run the Preflight checks.
Skip any step where the prerequisite already exists.
Guide the user through each remaining step, then run Verification.
Finish with the Challenge.

Use `.claude/commands/references/context.md` for team-specific values.
```

- [ ] **Step 2: Write a script to batch-convert all dispatchers**

Create a temporary Python script to convert each dispatcher to the lazy-load format. For each `learn-NN-TOPIC.md` file:

1. Extract the title (first `#` line) and description (second line)
2. Extract the estimated time and prerequisites
3. Replace the body with the phased template

The new template for each dispatcher:

```
# TITLE

DESCRIPTION.
Estimated time: X minutes. Prerequisites: LIST.

Read modules/NN-TOPIC.md but present it in phases:

Phase 1: Read only the Quick Setup and Orientation sections. Present them.
         Ask: "Ready to check prerequisites?"

Phase 2: Read only the Preflight section. Run the checks.
         Skip any step that passes. Report results.
         Ask: "Ready to start the walkthrough?"

Phase 3: Read and present one Step at a time.
         After each step's verification passes, proceed to the next.
         Do not read ahead -- load each step only when needed.

Phase 4: Read only the Verification section. Run all checks.
         Report results.

Phase 5: Read only the Challenge and Challenge Verification sections.
         Present the challenge. After the user completes it, verify.

Use .claude/commands/references/context.md for team-specific values.
Track progress in ~/.claude/courseware-progress/.
```

Process all 21 dispatchers. For each one:
- Preserve the existing title and description lines
- Extract module path from the old `Read and follow the module at` line
- Replace everything after the description/time/prereqs with the phased template

- [ ] **Step 3: Verify all 21 dispatchers were updated**

```bash
for f in .claude/commands/learn-[0-9]*.md; do
  if grep -q "Phase 1:" "$f"; then
    echo "OK: $f"
  else
    echo "MISSING PHASES: $f"
  fi
done
```

Expected: 21 "OK" lines.

- [ ] **Step 4: Run validate.py**

```bash
python3 scripts/validate.py
```

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add .claude/commands/learn-*.md
git commit -m "$(cat <<'EOF'
convert all dispatchers to lazy-load phased format

Each dispatcher now presents modules in 5 phases instead of
loading the full file upfront. Reduces token consumption by
40-60% for typical sessions.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: Create GitHub Actions CI pipeline

**Files:**
- Create: `.github/workflows/courseware-ci.yml`

- [ ] **Step 1: Create .github/workflows/ directory**

```bash
mkdir -p .github/workflows
```

- [ ] **Step 2: Write courseware-ci.yml**

```yaml
name: Courseware CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Run courseware validation
        run: python3 scripts/validate.py

  lint-markdown:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    continue-on-error: true
    steps:
      - uses: actions/checkout@v4
      - uses: DavidAnson/markdownlint-cli2-action@v19
        with:
          globs: "modules/*.md"
```

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/courseware-ci.yml
git commit -m "$(cat <<'EOF'
add GitHub Actions CI for courseware validation

Runs scripts/validate.py on push to main and on PRs.
Optional markdownlint on PRs (warn-only, not blocking).
Under 30 seconds runtime.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: Create contributor documentation

**Files:**
- Create: `CONTRIBUTING.md`
- Create: `.github/PULL_REQUEST_TEMPLATE.md`
- Create: `.github/ISSUE_TEMPLATE/new-module.md`
- Create: `.github/ISSUE_TEMPLATE/module-fix.md`

- [ ] **Step 1: Write CONTRIBUTING.md**

```markdown
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
```

- [ ] **Step 2: Write .github/PULL_REQUEST_TEMPLATE.md**

```bash
mkdir -p .github
```

```markdown
## What changed

(brief description)

## Module checklist

- [ ] Module file in `modules/NN-topic.md`
- [ ] Dispatcher in `.claude/commands/learn-NN-topic.md`
- [ ] Added to catalog in `courseware.md`
- [ ] Added to README table
- [ ] All required sections present (Orientation, Preflight, Steps, Verification, Challenge)
- [ ] Ran `python3 scripts/validate.py` locally -- all checks pass
```

- [ ] **Step 3: Write issue templates**

```bash
mkdir -p .github/ISSUE_TEMPLATE
```

`.github/ISSUE_TEMPLATE/new-module.md`:

```markdown
---
name: Propose a new module
about: Suggest a new learning module for the courseware
title: "Module: "
labels: new-module
---

**Module title:**

**What it teaches:**

**Prerequisites:**

**Estimated time:**

**Additional context:**
```

`.github/ISSUE_TEMPLATE/module-fix.md`:

```markdown
---
name: Fix or improve a module
about: Report an issue or suggest an improvement to an existing module
title: "Fix: "
labels: module-fix
---

**Which module:**

**What's wrong or could be improved:**

**Suggested fix:**
```

- [ ] **Step 4: Run validate.py**

```bash
python3 scripts/validate.py
```

Expected: all PASS (these new files don't affect any checks).

- [ ] **Step 5: Commit**

```bash
git add CONTRIBUTING.md .github/PULL_REQUEST_TEMPLATE.md .github/ISSUE_TEMPLATE/new-module.md .github/ISSUE_TEMPLATE/module-fix.md
git commit -m "$(cat <<'EOF'
add contributor documentation and templates

CONTRIBUTING.md with module authoring guide, CI explanation,
and conventions. PR template with module checklist. Issue
templates for new modules and module fixes.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 10: Update CLAUDE.md post-update protocol

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update post-update Step 1 to use validate.py**

In `CLAUDE.md`, replace the current Step 1 module integrity check bash block with:

Old (the inline bash script starting with `# Count module files`):
```bash
# Count module files (excluding TEMPLATE.md)
MODULE_COUNT=$(ls modules/*.md 2>/dev/null | grep -v TEMPLATE | wc -l | tr -d ' ')
...
```

New:
```bash
python3 scripts/validate.py
```

Update the surrounding text to say:

```markdown
### Step 1 -- Module Integrity Check

Run the integrity validator:

\`\`\`bash
python3 scripts/validate.py
\`\`\`

If any check fails, fix the issue before proceeding. The validator checks dispatcher coverage, module structure, catalog count, README sync, and no stale files.
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "$(cat <<'EOF'
update post-update protocol to use validate.py

Replace inline bash integrity checks with the centralized
validation script for consistency with CI.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 11: Final validation and tag

**Files:** None (validation only)

- [ ] **Step 1: Run full validation**

```bash
python3 scripts/validate.py
```

All 6 checks must pass.

- [ ] **Step 2: Check for any remaining skills/ references**

```bash
grep -r 'skills/' . --include="*.md" --include="*.py" --include="*.yml" --include="*.json" | grep -v ".git/" | grep -v "node_modules/" | grep -v ".superpowers/"
```

Review any hits. References to "skills" as a concept (e.g., "Writing Custom Skills") are fine. References to the `skills/` directory path are not.

- [ ] **Step 3: Verify dispatchers are all phased**

```bash
for f in .claude/commands/learn-[0-9]*.md; do
  if grep -q "Phase 1:" "$f"; then
    echo "OK: $(basename $f)"
  else
    echo "NEEDS UPDATE: $(basename $f)"
  fi
done
```

Expected: 21 "OK" lines.

- [ ] **Step 4: Tag the release**

```bash
git tag -l 'v*' --sort=-v:refname | head -1
# Check current version (should be v1.0.0)

git tag -a v2.0.0 -m "multi-contributor readiness: delete skills/, add validate.py, lazy-load dispatchers, CI pipeline, contributor docs"
```

This is a major version bump because:
- Removing `skills/` is a breaking change for anyone who symlinked skill files
- Dispatcher format changed from 13-line to phased 30-line
- `settings.local.json` stripped to essentials

- [ ] **Step 5: Report completion**

Print summary of all changes:
- Files deleted: skills/ (18 dirs), 2 planning docs
- Files created: validate.py, CI workflow, CONTRIBUTING.md, PR template, 2 issue templates, developer-permissions.md
- Files modified: 21 dispatchers, courseware.md, build-module.md, settings.local.json, README.md, CLAUDE.md
- Version: v2.0.0
