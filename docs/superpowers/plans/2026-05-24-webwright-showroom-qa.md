# Webwright Showroom QA Integration -- Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Install Microsoft Webwright as a Claude Code plugin, generate a reusable Playwright QA script for Antora-based RHDP showrooms, wrap it in a `flow-showroom-qa` skill, and wire it into the existing `flow-qa` pipeline as an enhanced QA3 check.

**Architecture:** Three layers -- (1) a `flow-showroom-qa` skill that orchestrates variant detection and result formatting, (2) standalone Python+Playwright QA scripts in `rhdp-flow-skills/scripts/showroom-qa/` (one per showroom variant, starting with Antora), (3) the Webwright plugin used only to generate new scripts for unknown variants. The skill calls the script via `python showroom-qa-antora.py --url X --user Y --pass Z`, parses the JSON output, and formats results.

**Tech Stack:** Python 3, Playwright, Webwright v0.1.0 (Microsoft), Claude Code plugin system, existing RHDP Flow MCP tools

**Spec:** `docs/superpowers/specs/2026-05-24-webwright-showroom-qa-design.md`

**Live test target:** `https://showroom-user-k9skk-showroom.apps.cluster-8vhnp.dyn.redhatworkshops.io/` (Agentic AIOps workshop, Antora variant, credentials on landing page)

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `rhdp-flow-skills/scripts/showroom-qa/showroom-qa-antora.py` | Standalone Playwright QA script for Antora showrooms |
| Create | `rhdp-flow-skills/scripts/showroom-qa/README.md` | Usage docs: args, output format, examples |
| Create | `rhdp-flow-skills/skills/flow-showroom-qa.md` | Skill file: orchestration, variant detection, result formatting |
| Modify | `rhdp-flow-skills/skills/flow-qa.md` | QA3 step delegates to flow-showroom-qa |
| Modify | `rhdp-flow-skills/README.md` | Add flow-showroom-qa to skill table |

---

### Task 1: Install Webwright Plugin and Runtime Dependencies

**Files:** None (environment setup)

This task installs the Webwright plugin into Claude Code and its Python runtime dependencies. The plugin must be installed before Task 2 because `/webwright:craft` is only available after a fresh session loads the plugin.

- [ ] **Step 1: Add the Webwright marketplace**

Run inside Claude Code:
```
/plugin marketplace add microsoft/Webwright
```

Expected: Marketplace registered successfully.

- [ ] **Step 2: Install the Webwright plugin from the marketplace**

Run inside Claude Code:
```
/plugin install webwright@webwright
```

Expected: Plugin installed. The output will show the install path (e.g., `~/.claude/plugins/cache/.../webwright/...`).

- [ ] **Step 3: Install Python runtime dependencies**

The Webwright plugin needs its Python package installed in editable mode. Find the plugin install path from Step 2 output, then run:

```bash
pip install -e <webwright-install-path>
playwright install chromium
```

If `playwright install chromium` reports it's already installed (from the existing Playwright MCP plugin), that's fine -- it's a no-op.

- [ ] **Step 4: Verify the install**

```bash
python -c "import webwright; print(webwright.__version__)"
```

Expected: `0.1.0` (or whatever version is current).

- [ ] **Step 5: Restart Claude Code session**

Plugins load at session start. Exit and restart Claude Code so the Webwright skill and `/webwright:craft` command become available.

After restart, verify:
```
/webwright:craft --help
```

Expected: Shows usage information for the craft command.

---

### Task 2: Generate the Antora QA Script with Webwright

**Files:**
- Create: `rhdp-flow-skills/scripts/showroom-qa/showroom-qa-antora.py`

This task uses Webwright's `/webwright:craft` to produce a parameterized Playwright script. The script is the core QA engine -- it navigates the showroom, runs checks, and outputs JSON. Webwright generates the initial version; we then review and tune it.

**Important:** This task MUST run in the new Claude Code session started at the end of Task 1 (so the Webwright plugin is loaded).

- [ ] **Step 1: Create the scripts directory**

```bash
mkdir -p rhdp-flow-skills/scripts/showroom-qa
```

- [ ] **Step 2: Run /webwright:craft to generate the QA script**

Run this command in Claude Code. Webwright will launch a browser, explore the showroom, and iteratively build a Playwright script:

```
/webwright:craft Navigate to the RHDP showroom at https://showroom-user-k9skk-showroom.apps.cluster-8vhnp.dyn.redhatworkshops.io/ and perform a full QA check. The showroom uses a split layout: left panel is an Antora docs site inside an iframe, right panel has service tabs (AAP2, Kira, Terminal, etc.) each in their own iframe. Perform these checks in order:

Phase 1 - Page Load: verify the page loads with HTTP 200, extract the workshop title from the H1 heading inside the content iframe, screenshot the landing page.

Phase 2 - Content Verification: verify the content iframe is not blank, extract the full module list from the sidebar nav links (they have class nav-link inside a nav-list), verify a credentials/IMPORTANT box exists containing username and password values.

Phase 3 - Module Walkthrough: click each module link in the sidebar nav, for each module verify the page loads with an H1 heading and non-empty article body, screenshot each module page.

Phase 4 - Service Tab Verification: click each tab in the outer tab bar (tablist element), for each tab verify the corresponding iframe loads and is not blank or showing an error page, screenshot each tab.

Accept these CLI arguments: --url (showroom URL), --user (username), --pass (password), --output-dir (where to save screenshots, default ./showroom-qa-results), --checks (comma-separated subset of: page_load,content,modules,tabs -- default all). Output a JSON report to stdout with this structure: {"url": "...", "variant": "antora", "timestamp": "ISO8601", "checks": [{"name": "check_name", "status": "pass|fail", "screenshot": "filename.png", ...}], "summary": {"total": N, "passed": N, "failed": N}}. Exit code 0 on all-pass, 1 on any failure. Use viewport size 1280x800. Run headless by default. Never log credentials.
```

Expected: Webwright generates a `final_script.py` in its workspace directory. It will iterate through plan/explore/author/verify phases, taking several minutes.

- [ ] **Step 3: Copy the generated script to the project**

```bash
cp <webwright-workspace>/final_script.py rhdp-flow-skills/scripts/showroom-qa/showroom-qa-antora.py
```

The exact workspace path is printed by Webwright during execution (look for `final_runs/run_<id>/final_script.py`).

- [ ] **Step 4: Review and tune the generated script**

Open `rhdp-flow-skills/scripts/showroom-qa/showroom-qa-antora.py` and verify:

1. **Argparse is correct:** `--url`, `--user`, `--pass`, `--output-dir`, `--checks` args are present with correct defaults
2. **Headless mode:** Browser launches with `headless=True` by default
3. **Viewport:** Set to `1280x800`
4. **JSON output:** Goes to stdout (not a file), matches the spec format
5. **Exit code:** `sys.exit(0)` on all-pass, `sys.exit(1)` on failure
6. **No credential leaks:** Username/password not in screenshot filenames or JSON output (except masked)
7. **Iframe handling:** The script correctly navigates into iframes for content and service tabs (this is the trickiest part -- Antora content is inside a nested iframe)

Fix any issues found. Common Webwright-generated script issues:
- May use `page.goto()` instead of handling iframe contexts with `page.frame()` or `frame_locator()`
- May hardcode selectors that should be parameterized
- May not handle slow-loading iframes with proper `wait_for` calls

- [ ] **Step 5: Test the script standalone against the live showroom**

```bash
cd rhdp-flow-skills/scripts/showroom-qa
python showroom-qa-antora.py \
  --url "https://showroom-user-k9skk-showroom.apps.cluster-8vhnp.dyn.redhatworkshops.io/" \
  --user "user-k9skk" \
  --pass "k7PdGKOSqYLU" \
  --output-dir ./test-run
```

Expected: JSON report to stdout with checks for all four phases. Screenshots in `./test-run/`. Exit code 0 if all checks pass.

Inspect the JSON output:
```bash
python showroom-qa-antora.py \
  --url "https://showroom-user-k9skk-showroom.apps.cluster-8vhnp.dyn.redhatworkshops.io/" \
  --user "user-k9skk" \
  --pass "k7PdGKOSqYLU" \
  --output-dir ./test-run 2>/dev/null | python -m json.tool
```

Expected: Valid JSON with `checks` array and `summary` object. Each check has `name`, `status`, and most have `screenshot`.

- [ ] **Step 6: Test with --checks subset flag**

```bash
python showroom-qa-antora.py \
  --url "https://showroom-user-k9skk-showroom.apps.cluster-8vhnp.dyn.redhatworkshops.io/" \
  --user "user-k9skk" \
  --pass "k7PdGKOSqYLU" \
  --output-dir ./test-run-subset \
  --checks page_load,content 2>/dev/null | python -m json.tool
```

Expected: JSON output with only `page_load` and `content` phase checks. No `modules` or `tabs` checks.

- [ ] **Step 7: Clean up test artifacts and commit**

```bash
rm -rf ./test-run ./test-run-subset
git add rhdp-flow-skills/scripts/showroom-qa/showroom-qa-antora.py
git commit -m "add Antora showroom QA script generated via Webwright

Standalone Playwright script that performs four-phase QA checks on
Antora-based RHDP showrooms: page load, content verification, module
walkthrough, and service tab verification. Parameterized via argparse
for URL, credentials, output directory, and check selection.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 3: Create the Scripts README

**Files:**
- Create: `rhdp-flow-skills/scripts/showroom-qa/README.md`

- [ ] **Step 1: Write the README**

Create `rhdp-flow-skills/scripts/showroom-qa/README.md`:

```markdown
# Showroom QA Scripts

Standalone Playwright scripts that perform end-to-end QA checks on RHDP workshop showrooms. Each script targets a specific showroom variant.

## Available Scripts

| Script | Variant | Description |
|--------|---------|-------------|
| `showroom-qa-antora.py` | Antora | Split-panel showroom with Antora docs + service tabs |

## Requirements

- Python 3.10+
- Playwright (`pip install playwright && playwright install chromium`)

No Claude Code, Webwright, or API keys required to run these scripts.

## Usage

```bash
python showroom-qa-antora.py \
  --url "https://showroom-user-...-showroom.apps.cluster-....dyn.redhatworkshops.io/" \
  --user "user-xxxxx" \
  --pass "password" \
  --output-dir ./results
```

### Arguments

| Arg | Required | Default | Description |
|-----|----------|---------|-------------|
| `--url` | Yes | -- | Showroom URL |
| `--user` | Yes | -- | Login username |
| `--pass` | Yes | -- | Login password |
| `--output-dir` | No | `./showroom-qa-results` | Screenshot output directory |
| `--checks` | No | all | Comma-separated: `page_load,content,modules,tabs` |

### Output

JSON report to stdout:

```json
{
  "url": "https://showroom-...",
  "variant": "antora",
  "timestamp": "2026-05-24T12:00:00Z",
  "checks": [
    {"name": "page_load", "status": "pass", "screenshot": "01-landing.png"},
    {"name": "module_list", "status": "pass", "module_count": 7}
  ],
  "summary": {"total": 15, "passed": 14, "failed": 1}
}
```

Exit code: 0 = all pass, 1 = any failure.

Screenshots saved to `--output-dir` with numbered filenames.

## Adding New Variants

Use Webwright's `/webwright:craft` command to generate a script for a new showroom type. See the design spec at `docs/superpowers/specs/2026-05-24-webwright-showroom-qa-design.md` for the variant detection approach.
```

- [ ] **Step 2: Commit**

```bash
git add rhdp-flow-skills/scripts/showroom-qa/README.md
git commit -m "add showroom QA scripts README with usage and argument docs

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 4: Create the flow-showroom-qa Skill

**Files:**
- Create: `rhdp-flow-skills/skills/flow-showroom-qa.md`

This is the orchestration skill that Claude Code users invoke. It detects the showroom variant, runs the correct script, parses JSON output, and formats results.

- [ ] **Step 1: Create the skill file**

Create `rhdp-flow-skills/skills/flow-showroom-qa.md`:

```markdown
---
name: flow-showroom-qa
description: Run deep browser-based QA checks on RHDP workshop showrooms -- verifies content renders, modules navigate, service tabs load
user-invocable: true
argument-hint: "<url> | --from-deploy | --craft <url>"
---

# Flow Showroom QA

Run end-to-end browser-based QA checks on RHDP workshop showrooms. Goes beyond HTTP accessibility -- verifies content renders, modules are navigable, credentials are visible, and service tabs load.

## Prerequisite Check

1. Verify `rhdp-flow-skills/scripts/showroom-qa/` directory exists. If not, stop and report: "Showroom QA scripts not found. Install the rhdp-flow-skills plugin or check your working directory."
2. Verify `playwright` is installed: run `python3 -c "import playwright"`. If it fails, stop and report: "Playwright is not installed. Run: pip install playwright && playwright install chromium"

## Workflow

### Step 1: Determine target showrooms

Parse the user's arguments:

- **Single URL** (e.g., `/flow-showroom-qa https://showroom-...`): Use that URL directly. Ask the user for credentials (username and password).
- **`--from-deploy`**: Call `flow_deploy_status` to get current deployment results. Extract showroom URLs by finding service URLs matching the pattern `*-showroom.*` in each namespace. Ask the user for the common password (username is derived from the namespace, typically `user-<id>`).
- **`--craft <url>`**: This mode generates a new QA script for an unknown showroom variant. Requires the Webwright plugin. Delegate to `/webwright:craft` with the standard QA prompt template (see the Craft Mode section below). Save the output to `rhdp-flow-skills/scripts/showroom-qa/`. Stop after generation -- do not run QA.

If no argument is provided, ask: "Provide a showroom URL, or use --from-deploy to check all deployed showrooms."

### Step 2: Detect showroom variant

For each target URL, detect the variant by navigating to the URL with Playwright MCP and inspecting the DOM:

1. Navigate to the URL using `browser_navigate`
2. Take a snapshot using `browser_snapshot`
3. Check for Antora fingerprints:
   - Content is inside an iframe
   - The iframe contains a `nav-toggle` button or `.nav-list` element
   - An `article` element with Asciidoc-generated structure exists
   - Footer contains "Powered by" with a link to demo.redhat.com
4. If Antora fingerprints match, variant = `antora`
5. If no known variant matches, report: "Unknown showroom variant at <url>. Use --craft <url> to generate a QA script for this variant."

### Step 3: Run QA script

Execute the matching script. For the `antora` variant:

```bash
python3 rhdp-flow-skills/scripts/showroom-qa/showroom-qa-antora.py \
  --url "<showroom_url>" \
  --user "<username>" \
  --pass "<password>" \
  --output-dir "showroom-qa-results/<namespace_or_timestamp>"
```

Capture both stdout (JSON report) and the exit code.

### Step 4: Parse and format results

Parse the JSON report from stdout. Format results in the standard flow-qa table:

```
Showroom QA Results
-------------------
URL:      <url>
Variant:  <variant>
Total:    <N> checks
Passed:   <N>
Failed:   <N>

Passed Checks:
  [PASS] page_load -- Page loaded with title "<title>"
  [PASS] module_list -- Found <N> modules
  [PASS] module_1_content -- "Module 1: The Problem Domain" rendered
  ...

Failed Checks:
  [FAIL] <check_name> -- <error message>
         Fix: <suggested action based on check type>

Screenshots saved to: showroom-qa-results/<dir>/
```

Suggested fixes per check type:
- `page_load` fail: "Verify the showroom URL is correct and the route exists"
- `module_list` fail: "Check the Antora navigation configuration in the showroom repo"
- `module_*_content` fail: "Verify the module page exists and Antora build completed"
- `tab_*_load` fail: "Check that the service is running in the namespace"
- `tab_*_login` fail: "Verify credentials are correct and the service accepts login"

### Step 5: Offer follow-up

If there are failures:
> "Would you like to re-run QA after fixing issues, or view the screenshots for failed checks?"

If all pass:
> "All showroom QA checks passed. Screenshots saved to <dir> for evidence."

If multiple showrooms were checked (--from-deploy mode), present a summary table:

```
Showroom QA Summary (--from-deploy)
------------------------------------
  [PASS] namespace-1  https://showroom-...  15/15 checks passed
  [FAIL] namespace-2  https://showroom-...  13/15 checks passed
  [PASS] namespace-3  https://showroom-...  15/15 checks passed

Overall: 2/3 showrooms fully passing
```

## Craft Mode

When invoked with `--craft <url>`, generate a new variant script using Webwright:

1. Check that the Webwright plugin is available (try invoking `/webwright:craft --help`). If not available, stop and report: "Webwright plugin is required for --craft mode. Install with: /plugin marketplace add microsoft/Webwright && /plugin install webwright@webwright"
2. Navigate to the URL to understand the showroom structure
3. Invoke `/webwright:craft` with the standard QA prompt (adapted for the specific showroom's DOM structure)
4. Save the generated script to `rhdp-flow-skills/scripts/showroom-qa/showroom-qa-<variant>.py`
5. Report: "Generated QA script for <variant> variant. Review the script, test it, and commit."
```

- [ ] **Step 2: Verify the skill frontmatter matches existing patterns**

Compare the frontmatter format with `flow-qa.md`:
- `name:` field present
- `description:` is a single line
- `user-invocable: true` is set
- `argument-hint:` provides usage hints

- [ ] **Step 3: Commit**

```bash
git add rhdp-flow-skills/skills/flow-showroom-qa.md
git commit -m "add flow-showroom-qa skill for deep browser-based showroom QA

Orchestrates variant detection, script execution, and result formatting.
Supports single URL, --from-deploy batch mode, and --craft for generating
new variant scripts via Webwright.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 5: Update flow-qa to Delegate QA3 to flow-showroom-qa

**Files:**
- Modify: `rhdp-flow-skills/skills/flow-qa.md`

- [ ] **Step 1: Read current flow-qa.md**

Read `rhdp-flow-skills/skills/flow-qa.md` to understand the exact current QA3 description and step structure.

Current QA3 description (from the argument-hint): `qa3 (showroom)`
Current QA3 behavior: "validates landing page accessibility"

- [ ] **Step 2: Update the QA3 description in the argument-hint**

In the frontmatter, change the argument-hint to reflect the enhanced QA3:

Old:
```
argument-hint: "qa1 (setup) | qa2 (health) | qa3 (showroom) | both (qa1+qa2) | all (qa1+qa2+qa3) [namespace]"
```

New:
```
argument-hint: "qa1 (setup) | qa2 (health) | qa3 (showroom, deep browser check) | both (qa1+qa2) | all (qa1+qa2+qa3) [namespace]"
```

- [ ] **Step 3: Update Step 1 QA scope descriptions**

In the "Step 1: Determine QA scope" section, update the QA3 bullet:

Old:
```
- **QA3** (showroom): validates landing page accessibility
```

New:
```
- **QA3** (showroom): deep browser-based check -- verifies content renders, modules navigate, service tabs load (uses flow-showroom-qa)
```

- [ ] **Step 4: Add QA3 delegation logic after Step 2**

After "Step 2: Run QA" (which calls `flow_qa_run`), add a new step for QA3 delegation. Insert before "Step 3: Get results":

```markdown
### Step 2b: Run showroom QA (QA3 only)

If the user selected QA3 (or "all" which includes QA3):

1. Check if `rhdp-flow-skills/scripts/showroom-qa/` exists. If not, skip this step and fall back to the standard QA3 HTTP check from `flow_qa_run`.
2. Invoke `/flow-showroom-qa --from-deploy` to run deep browser checks on all deployed showrooms.
3. Merge the showroom QA results into the overall QA results presented in Step 4.

If the showroom QA scripts are not available, report a note:
> "Note: Deep showroom QA (browser checks) skipped -- showroom QA scripts not installed. Running HTTP-level check only."
```

- [ ] **Step 5: Update the failure suggestions in Step 4**

In "Step 4: Present results", add showroom-specific failure suggestions after the existing list:

```markdown
- Showroom content not rendering: "Run `/flow-showroom-qa <url>` for detailed browser-level diagnostics"
- Showroom module missing: "Check the Antora nav configuration in the showroom Git repo"
- Showroom service tab failing: "Verify the service pod is running in the namespace"
```

- [ ] **Step 6: Commit**

```bash
git add rhdp-flow-skills/skills/flow-qa.md
git commit -m "update flow-qa QA3 to delegate to flow-showroom-qa for deep browser checks

QA3 now runs end-to-end browser verification (content, modules, tabs)
via the flow-showroom-qa skill when available, with fallback to the
existing HTTP-level check if showroom QA scripts are not installed.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 6: Update rhdp-flow-skills README

**Files:**
- Modify: `rhdp-flow-skills/README.md`

- [ ] **Step 1: Add flow-showroom-qa to the skill table**

In `rhdp-flow-skills/README.md`, add a row to the Skills table:

Old table:
```markdown
| Skill | Trigger | Description |
|-------|---------|-------------|
| `flow-deploy` | "deploy workshops" | Guided CSV generation, validation, dry-run, and deploy |
| `flow-qa` | "run QA", "check workshops" | Run QA checks with pass/fail summary and fix suggestions |
| `flow-ops` | "extend workshop", "lock", "scale" | Lock, extend, scale, or disable autostop on workshops |
| `flow-status` | "workshop status" | Deployment, QA, and pool availability dashboard |
| `flow-bulk` | "deploy N workshops" | Bulk staggered deployments for events and load tests |
| `flow-report` | "generate report" | Formatted reports for Slack, email, or stakeholders |
```

New table (add after `flow-qa` row):
```markdown
| Skill | Trigger | Description |
|-------|---------|-------------|
| `flow-deploy` | "deploy workshops" | Guided CSV generation, validation, dry-run, and deploy |
| `flow-qa` | "run QA", "check workshops" | Run QA checks with pass/fail summary and fix suggestions |
| `flow-showroom-qa` | "check showroom", "showroom QA" | Deep browser-based showroom QA: content, modules, tabs, login |
| `flow-ops` | "extend workshop", "lock", "scale" | Lock, extend, scale, or disable autostop on workshops |
| `flow-status` | "workshop status" | Deployment, QA, and pool availability dashboard |
| `flow-bulk` | "deploy N workshops" | Bulk staggered deployments for events and load tests |
| `flow-report` | "generate report" | Formatted reports for Slack, email, or stakeholders |
```

- [ ] **Step 2: Add a note about the scripts directory**

Below the Install section, add:

```markdown
## Scripts

The `scripts/` directory contains standalone tools that skills depend on:

| Directory | Description |
|-----------|-------------|
| `scripts/showroom-qa/` | Playwright-based showroom QA scripts (one per variant) |

Scripts run independently -- no Claude Code or Webwright required. See each directory's README for usage.
```

- [ ] **Step 3: Commit**

```bash
git add rhdp-flow-skills/README.md
git commit -m "add flow-showroom-qa to skills table and document scripts directory

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 7: End-to-End Integration Test

**Files:** None (testing)

This task verifies the full pipeline works: skill invocation, variant detection, script execution, result formatting.

- [ ] **Step 1: Test the standalone script directly**

```bash
cd rhdp-flow-skills/scripts/showroom-qa
python3 showroom-qa-antora.py \
  --url "https://showroom-user-k9skk-showroom.apps.cluster-8vhnp.dyn.redhatworkshops.io/" \
  --user "user-k9skk" \
  --pass "k7PdGKOSqYLU" \
  --output-dir /tmp/showroom-qa-test
```

Expected: JSON to stdout with all four phases. Exit code 0. Screenshots in `/tmp/showroom-qa-test/`.

Verify the JSON is valid:
```bash
python3 showroom-qa-antora.py \
  --url "https://showroom-user-k9skk-showroom.apps.cluster-8vhnp.dyn.redhatworkshops.io/" \
  --user "user-k9skk" \
  --pass "k7PdGKOSqYLU" \
  --output-dir /tmp/showroom-qa-test2 2>/dev/null | python3 -m json.tool
```

Expected: Pretty-printed JSON with `url`, `variant`, `timestamp`, `checks`, `summary` fields.

- [ ] **Step 2: Test the skill invocation (single URL mode)**

In Claude Code, invoke:
```
/flow-showroom-qa https://showroom-user-k9skk-showroom.apps.cluster-8vhnp.dyn.redhatworkshops.io/
```

When prompted for credentials, provide: user `user-k9skk`, password `k7PdGKOSqYLU`.

Expected: The skill detects Antora variant, runs the script, and presents formatted pass/fail results matching the spec format.

- [ ] **Step 3: Test with --checks subset**

```bash
python3 rhdp-flow-skills/scripts/showroom-qa/showroom-qa-antora.py \
  --url "https://showroom-user-k9skk-showroom.apps.cluster-8vhnp.dyn.redhatworkshops.io/" \
  --user "user-k9skk" \
  --pass "k7PdGKOSqYLU" \
  --output-dir /tmp/showroom-qa-subset \
  --checks page_load,content 2>/dev/null | python3 -m json.tool
```

Expected: JSON with only page_load and content checks. No module or tab checks.

- [ ] **Step 4: Verify screenshots were saved**

```bash
ls -la /tmp/showroom-qa-test/
```

Expected: Numbered PNG files (01-landing.png, 02-module-1.png, etc.) at consistent dimensions.

- [ ] **Step 5: Test failure detection (invalid URL)**

```bash
python3 rhdp-flow-skills/scripts/showroom-qa/showroom-qa-antora.py \
  --url "https://nonexistent-showroom.example.com/" \
  --user "test" \
  --pass "test" \
  --output-dir /tmp/showroom-qa-fail 2>/dev/null; echo "Exit code: $?"
```

Expected: JSON with `page_load` check status `fail`. Exit code 1.

- [ ] **Step 6: Clean up test artifacts**

```bash
rm -rf /tmp/showroom-qa-test /tmp/showroom-qa-test2 /tmp/showroom-qa-subset /tmp/showroom-qa-fail
```

---

### Task 8: Final Commit and Tag

**Files:** None (git operations)

- [ ] **Step 1: Review all changes**

```bash
git status
git log --oneline -5
```

Expected: 4 commits from Tasks 2-6 (script, README, skill, flow-qa update, skills README update).

- [ ] **Step 2: Verify no test artifacts were committed**

```bash
git diff --cached --name-only
```

Expected: No files staged. All test artifacts cleaned up.

- [ ] **Step 3: Check the latest version tag**

```bash
git tag -l 'v*' --sort=-v:refname | head -1
```

This is a new skill + new script = minor version bump.

- [ ] **Step 4: Create the version tag**

```bash
git tag -a v<next-minor> -m "add Webwright showroom QA integration

New flow-showroom-qa skill with Antora QA script for deep browser-based
showroom verification. Extends flow-qa QA3 with content, module, and
service tab checks."
```

Do not push the tag unless the user explicitly asks.
