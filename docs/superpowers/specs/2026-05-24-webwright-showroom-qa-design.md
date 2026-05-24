# Webwright Showroom QA Integration

**Date:** 2026-05-24
**Status:** Draft
**Author:** rhjcd + Claude

## Problem

RHDP workshop showrooms are the student-facing entry point for every event. The current QA pipeline (`flow-qa` skill, QA3 check) only validates that a showroom URL returns HTTP 200 -- it does not verify that content renders, modules are navigable, credentials are present, or service tabs load. A showroom can pass QA3 while being completely broken for students.

Multiple showroom implementations exist across the fleet (Antora-based, Bookbag-based, potentially others). Any QA solution must detect the variant and adapt.

## Solution

Integrate Microsoft's Webwright browser agent framework as a Claude Code plugin to generate reusable Playwright-based QA scripts, wrapped by a new `flow-showroom-qa` skill that handles orchestration, variant detection, and result formatting.

### Architecture

Three layers, each with a distinct responsibility:

```
┌─────────────────────────────────────────────────────┐
│  flow-showroom-qa skill (orchestration)             │
│  - Accepts showroom URL + credentials               │
│  - Detects showroom variant                          │
│  - Selects correct QA script                         │
│  - Runs script, parses output, formats results       │
│  - Integrates with flow-qa as enhanced QA3           │
├─────────────────────────────────────────────────────┤
│  QA Scripts (rhdp-flow-skills/scripts/showroom-qa/) │
│  - showroom-qa-antora.py  (Antora-based showrooms)  │
│  - showroom-qa-bookbag.py (future, if needed)        │
│  - Each is a standalone Playwright CLI tool          │
│  - Generated once via /webwright:craft               │
│  - Parameterized: --url, --user, --pass, --checks   │
├─────────────────────────────────────────────────────┤
│  Webwright Plugin (script generation only)           │
│  - /webwright:craft to create new variant scripts    │
│  - Only needed when a new showroom type appears      │
│  - Not a runtime dependency                          │
└─────────────────────────────────────────────────────┘
```

**Variant detection** happens in the skill layer. The skill hits the showroom URL, inspects the page structure (Antora nav markers, Bookbag sidebar patterns, DOM fingerprints), and picks the right script. If no script matches, it either falls back to Webwright to generate one on the fly (if installed) or reports "unknown variant."

### QA Check Phases

The generated scripts perform four phases of verification:

**Phase 1 -- Page Load**
- Navigate to showroom URL
- Verify HTTP 200 and page title contains workshop name
- Screenshot the landing page as evidence

**Phase 2 -- Content Verification**
- Verify the content iframe loads (not blank)
- Extract the module list from the sidebar navigation
- Confirm expected module count matches actual
- Verify credentials box is present and contains username/password values

**Phase 3 -- Module Walkthrough**
- Click through each module link in the sidebar
- For each module: verify the page loads, H1 heading exists, content body is non-empty
- Screenshot each module page
- Verify prev/next navigation links work

**Phase 4 -- Service Tab Verification**
- Click each tab in the tab bar (AAP2, Terminal, Kira, etc.)
- For each: verify the iframe loads (not blank/error)
- For tabs with login gates: submit credentials, verify login succeeds
- Screenshot each service tab state

### Output Format

Scripts produce a JSON report to stdout and screenshots to an output directory:

```json
{
  "url": "https://showroom-user-...",
  "variant": "antora",
  "timestamp": "2026-05-24T12:00:00Z",
  "checks": [
    {"name": "page_load", "status": "pass", "screenshot": "01-landing.png"},
    {"name": "module_list", "status": "pass", "module_count": 7},
    {"name": "module_1_content", "status": "pass", "title": "Module 1: The Problem Domain", "screenshot": "02-module-1.png"},
    {"name": "tab_aap2_load", "status": "pass", "screenshot": "08-tab-aap2.png"},
    {"name": "tab_aap2_login", "status": "fail", "error": "Login form submit returned 401", "screenshot": "09-tab-aap2-login-fail.png"}
  ],
  "summary": {"total": 15, "passed": 14, "failed": 1}
}
```

Exit code: 0 on all-pass, 1 on any failure.

### Skill Integration

**New skill: `flow-showroom-qa`**

Invocation modes:
- `/flow-showroom-qa <url>` -- run against a single showroom with prompted credentials
- `/flow-showroom-qa --from-deploy` -- pull showroom URLs from current deployment results via `flow_deploy_status` (extracts URLs matching the `*-showroom.*` route pattern from each namespace's services) and check all of them
- `/flow-showroom-qa --craft <url>` -- generate a new QA script for an unknown showroom variant (requires Webwright plugin)

Result formatting follows the existing `flow-qa` pass/fail table pattern:
```
Showroom QA Results
-------------------
URL:      https://showroom-user-...
Variant:  antora
Total:    15 checks
Passed:   14
Failed:   1

Failed Checks:
  [FAIL] tab_aap2_login -- Login form submit returned 401
         Fix: Verify credentials are correct and AAP2 service is running

Screenshots saved to: showroom-qa-results/screenshots/
```

**flow-qa integration:** The existing `flow-qa.md` skill's QA3 step is updated to invoke `flow-showroom-qa --from-deploy` instead of the current URL accessibility check. When `flow-showroom-qa` is not available or showroom URLs cannot be determined, QA3 falls back to the current HTTP-level check.

### Showroom Anatomy (Antora Variant)

Based on live exploration of an Agentic AIOps workshop showroom:

**Outer frame:**
- View mode switcher toolbar: Instructions / Split / Tabs
- Left panel: content iframe (Antora docs site)
- Right panel: service tab bar + service iframes

**Content iframe (Antora):**
- Header: Red Hat Summit / AnsibleFest branding, workshop title, link to GitHub repo
- Navigation: hamburger menu button, home icon, breadcrumb
- Article: H1 title, table of contents (anchor links), body sections, credential callout box
- Footer: prev/next module navigation, "Powered by Demo Platform"

**Service tabs:**
- Tab bar across top of right panel
- Each tab loads a separate iframe (AAP2, Kira, Terminal, Rocket.Chat, Gitea, OpenShift Console, etc.)
- Some tabs present login gates (username/password form)
- Tab set varies by workshop

**Variant fingerprint (Antora):** Content iframe contains `nav-toggle` button class, Antora-style breadcrumb navigation, `article` element with Asciidoc-generated structure, footer linking to demo.redhat.com.

## File Layout

**New files:**
```
rhdp-flow-skills/
  skills/
    flow-showroom-qa.md              # skill file (orchestration + formatting)
  scripts/
    showroom-qa/
      showroom-qa-antora.py          # Playwright QA script for Antora showrooms
      README.md                      # usage: args, output format, examples
```

**Modified files:**
```
rhdp-flow-skills/
  skills/
    flow-qa.md                       # QA3 step updated to call flow-showroom-qa
  README.md                          # add flow-showroom-qa to skill table
```

**Runtime artifacts (per-run, not committed):**
```
showroom-qa-results/
  report.json
  screenshots/
    01-landing.png
    02-module-1.png
    ...
```

## Distribution and Shareability

**Two-tier distribution:**

1. **QA scripts + skill** ship with the `rhdp-flow-skills` directory (currently in `claude-code-courseware`, future candidate for its own repo/plugin). Team members get them automatically on plugin update. Running the scripts requires only Python + Playwright -- no Claude Code or Webwright dependency.

2. **Webwright plugin** is an optional install for script authors who need to generate QA scripts for new showroom variants. One-time setup:
   ```
   /plugin marketplace add microsoft/Webwright
   /plugin install webwright@webwright
   pip install -e <webwright-path>
   playwright install chromium
   ```

**Decoupling note:** The `rhdp-flow-skills` directory has no dependencies on the courseware modules. It can be extracted to its own repo and plugin at any time without changes to the skill files or scripts.

## POC Workflow

1. Install Webwright plugin (marketplace add + install + pip deps)
2. Use `/webwright:craft` to generate `showroom-qa-antora.py` against the live Agentic AIOps showroom
3. Review, tune, and commit the generated script
4. Create `flow-showroom-qa.md` skill with variant detection and result formatting
5. Update `flow-qa.md` QA3 step to delegate to the new skill
6. Test end-to-end against the live showroom
7. Verify the standalone script runs independently (outside Claude Code)

## Constraints

- Scripts must run headless (no GUI) for CI/unattended use
- Screenshots must be taken at a consistent viewport size (1280x800) for comparability
- Login credentials must never be logged or included in screenshot filenames
- JSON output must be machine-parseable for integration with monitoring/alerting
- Webwright is v0.1.0 -- generated scripts may need manual tuning; treat them as a starting point, not a final product
