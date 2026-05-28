# Module 24 -- Security-First Development
<!-- NEW -->

Estimated time: 15 minutes
Prerequisites: Module 01 (Claude Code installed and working)

Learn to integrate security into your daily Claude Code workflow using the security-guidance plugin, /security-review, and secure coding patterns.

## Orientation

Print this once at the start:

```
You're learning security-first development with Claude Code.
This takes about 15 minutes.

We'll cover:
  1. The security-guidance plugin and its three scanning levels
  2. Installing the plugin if you don't have it
  3. Running /security-review for on-demand analysis
  4. Writing CLAUDE.md security instructions for OWASP Top 10
  5. Creating a security hook for pre-commit validation
  6. Claude's built-in security awareness vs. active plugin scanning

Context: Anthropic Mythos discovered 23,000+ vulnerabilities across
1,000+ open source projects, making security awareness in AI-assisted
development more important than ever. This module teaches you to
leverage Claude Code's security capabilities as part of your daily
workflow rather than treating security as an afterthought.

You'll need:
  - Claude Code installed and working (Module 01)
```

## Progress Tracking

On module start, write a progress marker:

```bash
mkdir -p ~/.claude/courseware-progress && date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/24.started
```

## Preflight

Audit current state before doing anything. Each check prints EXISTS or MISSING.

```bash
# Check 1 -- Claude Code installed?
command -v claude &>/dev/null && echo "EXISTS: Claude Code" || echo "MISSING: Claude Code -- run /learn-01-vertex-setup first"

# Check 2 -- security-guidance plugin installed?
claude plugin list 2>/dev/null | grep -qi security && echo "EXISTS: security-guidance plugin" || echo "MISSING: security-guidance plugin (will install)"

# Check 3 -- CLAUDE.md has security instructions?
grep -qi "security\|owasp\|vulnerability\|injection" CLAUDE.md 2>/dev/null && echo "EXISTS: CLAUDE.md has security instructions" || echo "INFO: CLAUDE.md has no security instructions yet"

# Check 4 -- Security hooks in project settings?
if [ -f ".claude/settings.local.json" ]; then
  python3 -c "
import json
d = json.load(open('.claude/settings.local.json'))
hooks = d.get('hooks', {}).get('PreToolUse', [])
sec = [h for h in hooks if 'security' in h.get('command', '').lower() or 'security' in str(h.get('matcher', '')).lower()]
if sec:
    print('EXISTS: Security hook configured in PreToolUse')
else:
    print('INFO: No security hooks configured yet')
" 2>/dev/null
else
  echo "INFO: No project-local settings file -- no hooks configured"
fi
```

Print a summary of what was found. Skip any step below where the item already exists and is valid.

If Claude Code is MISSING, stop:
```
Claude Code is not installed. Complete Module 01 first:
  /learn-01-vertex-setup
```

## Step 1 -- Understanding the Security-Guidance Plugin

This step is conceptual -- no commands to run, just essential context.

Tell the user:
```
The security-guidance plugin adds active security scanning to
Claude Code. It operates at three levels:

  Level 1 -- File Edits
    Scans every file Claude edits or creates in real time.
    Catches issues like hardcoded credentials, insecure file
    permissions, and dangerous function calls as they happen.

  Level 2 -- Diffs
    Analyzes staged changes (git diff) for security patterns.
    Catches injection vulnerabilities, authentication flaws,
    and data exposure before code leaves your machine.

  Level 3 -- Commits
    Reviews full commit context including cross-file impact.
    Catches architectural security issues like missing input
    validation across request handlers, or authentication
    bypasses introduced by multiple file changes together.

Each level builds on the previous one:
  - Level 1 catches line-level issues
  - Level 2 catches change-level issues
  - Level 3 catches system-level issues

The plugin works alongside /security-review, which you can
invoke any time for a comprehensive on-demand scan of your
current changes or entire project.
```

## Step 2 -- Install the Security-Guidance Plugin

Skip if preflight showed EXISTS for the security-guidance plugin.

Tell the user:
```
The security-guidance plugin is available from the Claude Code
plugin marketplace. Let's install it.
```

If missing, tell the user:
```
Install the security-guidance plugin:

  ! claude plugin add security-guidance

This adds the plugin to your Claude Code environment. It will
activate automatically on the next session start.
```

Verify:
```bash
claude plugin list 2>/dev/null | grep -qi security && echo "PASS: security-guidance plugin installed" || echo "FAIL: security-guidance plugin not found -- try running: claude plugin add security-guidance"
```

## Step 3 -- Run /security-review on Current Changes

This step demonstrates on-demand security analysis.

Tell the user:
```
The /security-review command scans your current project for
security issues. It checks:

  - Staged and unstaged changes (git diff)
  - New files that haven't been committed
  - Configuration files for insecure settings
  - Dependencies for known vulnerabilities (if lockfiles exist)

The output groups findings by severity:

  CRITICAL  -- Must fix before merging (e.g., hardcoded secrets,
               SQL injection, authentication bypass)
  HIGH      -- Should fix before merging (e.g., XSS, insecure
               deserialization, missing input validation)
  MEDIUM    -- Fix when practical (e.g., verbose error messages,
               weak cryptographic choices)
  LOW       -- Informational (e.g., missing security headers,
               commented-out authentication code)

Let's run it now. If there are no pending changes, it will scan
the project configuration and structure.
```

Run the review:
```
Run /security-review on this project and report the findings.
Summarize what was found at each severity level.
```

Tell the user:
```
Review the output above. Key things to note:

  1. Each finding includes a file path and line number
  2. Findings explain WHY something is a security issue
  3. Most findings include a suggested fix
  4. False positives are possible -- use your judgment

If there were no findings, that is normal for a well-maintained
project. The real value comes when you run this on active changes.
```

## Step 4 -- Write CLAUDE.md Security Instructions

Skip if preflight showed EXISTS for CLAUDE.md security instructions.

Tell the user:
```
Adding security instructions to your CLAUDE.md makes Claude Code
security-aware by default. Every time Claude generates or modifies
code in this project, it will check against these rules.

The instructions we'll add are based on the OWASP Top 10, adapted
for what Claude Code can realistically catch and prevent during
code generation.
```

Add a security section to CLAUDE.md. If the file already has security content, merge with existing. If not, append:

```markdown
## Security Requirements

All code in this project must follow these security practices. Claude Code
should check for and prevent these issues in every edit.

### Injection Prevention (OWASP A03)
- Never use string concatenation or f-strings to build SQL queries
- Use parameterized queries or ORM methods exclusively
- Validate and sanitize all user input before use in commands or queries
- Never pass user input directly to os.system(), subprocess with shell=True, or eval()

### Authentication and Session Management (OWASP A07)
- Never hardcode passwords, API keys, or tokens in source files
- Use environment variables or secret management for all credentials
- Enforce strong password policies in any authentication code
- Implement proper session timeout and invalidation

### Cross-Site Scripting Prevention (OWASP A03)
- Escape all user-supplied data before rendering in HTML
- Use framework-provided templating with auto-escaping enabled
- Validate and sanitize input on both client and server side
- Set Content-Security-Policy headers

### Sensitive Data Exposure (OWASP A02)
- Never log sensitive data (passwords, tokens, PII)
- Never commit .env files, credentials, or private keys
- Use HTTPS for all external API calls
- Encrypt sensitive data at rest

### Security Misconfiguration (OWASP A05)
- Never run with debug mode enabled in production
- Remove default credentials and example configurations
- Set restrictive file permissions (no world-readable secrets)
- Disable directory listing and verbose error pages in production
```

Verify:
```bash
grep -qi "injection\|owasp\|security requirements" CLAUDE.md 2>/dev/null && echo "PASS: CLAUDE.md security instructions added" || echo "FAIL: Security instructions not found in CLAUDE.md"
```

## Step 5 -- Create a Security Hook

This step creates a PreToolUse hook that scans code for common security issues before Claude commits.

Tell the user:
```
Now let's add a hook that runs a quick security check before
commits. This catches issues that might slip through during
iterative editing.

The hook fires on git commit commands and scans staged files
for common security red flags.
```

Create the hook script:

```bash
mkdir -p .claude/hooks

cat > .claude/hooks/security-precommit.sh << 'HOOKEOF'
#!/bin/bash
# PreToolUse hook: security scan before git commit
# Receives tool input as JSON on stdin

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_name',''))" 2>/dev/null)

# Only check Bash tool calls
if [ "$TOOL_NAME" != "Bash" ]; then
  exit 0
fi

COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null)

# Only check git commit commands
if ! echo "$COMMAND" | grep -qE 'git\s+commit'; then
  exit 0
fi

# Scan staged files for security issues
ISSUES=""

# Check for hardcoded secrets patterns in staged files
STAGED=$(git diff --cached --name-only 2>/dev/null)
if [ -z "$STAGED" ]; then
  exit 0
fi

for FILE in $STAGED; do
  [ -f "$FILE" ] || continue

  # Check for hardcoded passwords/keys
  if grep -nE "(password|secret|api_key|token)\s*=\s*['\"][^'\"]+['\"]" "$FILE" 2>/dev/null | grep -vE "(example|placeholder|test|TODO)" > /dev/null; then
    ISSUES="${ISSUES}WARNING: Possible hardcoded secret in $FILE\n"
  fi

  # Check for SQL injection patterns
  if grep -nE "(execute|query)\s*\(.*(%s|%d|\{.*\}|f['\"])" "$FILE" 2>/dev/null > /dev/null; then
    ISSUES="${ISSUES}WARNING: Possible SQL injection pattern in $FILE\n"
  fi

  # Check for shell injection patterns
  if grep -nE "os\.system\(|subprocess\.\w+\(.*shell\s*=\s*True" "$FILE" 2>/dev/null > /dev/null; then
    ISSUES="${ISSUES}WARNING: Possible shell injection pattern in $FILE\n"
  fi
done

if [ -n "$ISSUES" ]; then
  echo "Security pre-commit scan found potential issues:"
  echo ""
  echo -e "$ISSUES"
  echo "Review these before committing. The commit will proceed,"
  echo "but consider running /security-review for a full analysis."
  # Exit 0 to warn but not block -- change to exit 2 to block commits
  exit 0
fi

exit 0
HOOKEOF

chmod +x .claude/hooks/security-precommit.sh
echo "PASS: Security pre-commit hook created at .claude/hooks/security-precommit.sh"
```

Register it in project settings:

```bash
python3 << 'PYEOF'
import json, os

path = ".claude/settings.local.json"
try:
    with open(path) as f:
        settings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}

if "hooks" not in settings:
    settings["hooks"] = {}

if "PreToolUse" not in settings["hooks"]:
    settings["hooks"]["PreToolUse"] = []

# Check if hook already exists
existing = [h for h in settings["hooks"]["PreToolUse"]
            if "security-precommit" in h.get("command", "")]
if not existing:
    settings["hooks"]["PreToolUse"].append({
        "matcher": "Bash",
        "command": "bash .claude/hooks/security-precommit.sh",
        "timeout": 10000
    })

with open(path, "w") as f:
    json.dump(settings, f, indent=2)

print("PASS: Security pre-commit hook registered in .claude/settings.local.json")
PYEOF
```

Verify:
```bash
[ -x ".claude/hooks/security-precommit.sh" ] && echo "PASS: Security hook script exists and is executable" || echo "FAIL: Security hook script missing or not executable"

python3 -c "
import json
d = json.load(open('.claude/settings.local.json'))
hooks = d.get('hooks', {}).get('PreToolUse', [])
sec = [h for h in hooks if 'security-precommit' in h.get('command', '')]
assert sec
print('PASS: Security pre-commit hook registered')
" 2>/dev/null || echo "FAIL: Security pre-commit hook not registered"
```

## Step 6 -- Built-in Security vs. Plugin Scanning

This step is conceptual -- clarifying the two layers of security in Claude Code.

Tell the user:
```
Claude Code has two layers of security awareness, and
understanding the difference helps you use both effectively.

Layer 1: Claude's Built-in Security Awareness
  Claude is trained to recognize security patterns. Even without
  any plugin, it will:
  - Avoid generating code with obvious vulnerabilities
  - Warn about hardcoded credentials when it notices them
  - Suggest parameterized queries over string concatenation
  - Follow secure defaults when creating configuration files

  Limitations:
  - Passive -- only applies during code generation, not review
  - Not exhaustive -- may miss subtle or project-specific issues
  - No enforcement -- suggestions can be ignored
  - No scanning -- doesn't analyze existing code proactively

Layer 2: The Security-Guidance Plugin (Active Scanning)
  The plugin adds active, continuous scanning on top of Claude's
  baseline awareness:
  - Scans every file edit, diff, and commit automatically
  - Catches issues in existing code, not just generated code
  - Uses pattern matching for known vulnerability signatures
  - Enforces checks that Claude's built-in awareness may skip
  - Produces structured findings with severity levels

  Combined with CLAUDE.md instructions:
  - Your CLAUDE.md security rules guide Claude's generation
  - The plugin verifies Claude followed those rules
  - The /security-review command gives on-demand full scans
  - Pre-commit hooks add a final gate before code ships

Think of it as defense in depth:
  CLAUDE.md rules    -->  Shape what Claude writes
  Built-in awareness -->  Avoid obvious mistakes
  Plugin scanning    -->  Catch what slips through
  Hooks              -->  Gate what gets committed
  /security-review   -->  On-demand deep analysis
```

## Verification

Run all checks as PASS/FAIL:

```bash
PASS=0
TOTAL=5

# 1. Claude Code installed
command -v claude &>/dev/null && { echo "PASS: Claude Code installed"; PASS=$((PASS+1)); } || echo "FAIL: Claude Code not installed"

# 2. Security-guidance plugin
claude plugin list 2>/dev/null | grep -qi security && { echo "PASS: security-guidance plugin installed"; PASS=$((PASS+1)); } || echo "FAIL: security-guidance plugin not installed"

# 3. CLAUDE.md security instructions
grep -qi "injection\|owasp\|security requirements" CLAUDE.md 2>/dev/null && { echo "PASS: CLAUDE.md has security instructions"; PASS=$((PASS+1)); } || echo "FAIL: CLAUDE.md missing security instructions"

# 4. Security hook script
[ -x ".claude/hooks/security-precommit.sh" ] && { echo "PASS: Security hook script exists"; PASS=$((PASS+1)); } || echo "FAIL: Security hook script missing"

# 5. Security hook registered
python3 -c "
import json
d = json.load(open('.claude/settings.local.json'))
hooks = d.get('hooks', {}).get('PreToolUse', [])
sec = [h for h in hooks if 'security-precommit' in h.get('command', '')]
assert sec
print('PASS: Security hook registered in settings')
" 2>/dev/null && PASS=$((PASS+1)) || echo "FAIL: Security hook not registered"

echo ""
echo "$PASS/$TOTAL checks passed."
```

If all pass, print:
```
All checks passed. Security-first development is configured.
```

If any fail, tell the user which step to re-run.

## Challenge

```
Test the full security pipeline by introducing and catching a vulnerability.

1. Create a file called security-test.py with this intentionally
   vulnerable code:

   import sqlite3
   import os

   def get_user(username):
       conn = sqlite3.connect("app.db")
       cursor = conn.cursor()
       query = "SELECT * FROM users WHERE name = '" + username + "'"
       cursor.execute(query)
       return cursor.fetchone()

   def run_command(user_input):
       os.system("echo " + user_input)

   API_KEY = "sk-proj-abc123def456"

2. Run /security-review on the project

3. Note what vulnerabilities were found

4. Fix all the vulnerabilities in security-test.py

5. Run /security-review again to confirm a clean result

6. Delete security-test.py when done (it was just for testing)

Tell me:
  1. What vulnerabilities /security-review found (list each one)
  2. How you fixed each vulnerability
  3. Whether the second /security-review came back clean
```

## Challenge Verification

Verify the user's answers cover at least these issues:

1. SQL injection -- the string-concatenated query in get_user() should be
   replaced with a parameterized query: `cursor.execute("SELECT * FROM users WHERE name = ?", (username,))`

2. Shell injection -- os.system() with user input should be replaced with
   subprocess.run() with a list argument and shell=False:
   `subprocess.run(["echo", user_input], shell=False)`

3. Hardcoded secret -- the API_KEY should be moved to an environment variable:
   `API_KEY = os.environ.get("API_KEY")`

If the user identified and fixed all three, and confirmed the cleanup scan was clean, the challenge is complete.

Write the completion marker:

```bash
date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/24.done
```

If successful, print:
```
Module 24 complete.

You can now integrate security into your Claude Code workflow.
Key concepts:
  - security-guidance plugin scans at three levels: edits, diffs, commits
  - /security-review provides on-demand security analysis
  - CLAUDE.md security instructions guide code generation
  - Pre-commit hooks add a final security gate
  - Defense in depth: rules, awareness, scanning, hooks, reviews
  - OWASP Top 10 patterns: injection, XSS, auth flaws, secrets, data exposure

Common security patterns to watch for:
  - String-concatenated SQL queries (use parameterized queries)
  - os.system() or shell=True with user input (use subprocess with lists)
  - Hardcoded credentials (use environment variables or secret managers)
  - Debug mode in production configs (disable before deploy)
  - Sensitive data in log output (redact PII, tokens, passwords)

Next module: /learn-25-security-scanning-vulnerability-research

Questions or feedback? https://github.com/rhpds/claude-code-courseware/issues
```
