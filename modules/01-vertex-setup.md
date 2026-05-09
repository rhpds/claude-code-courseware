# Module 01 — Claude Code + Vertex AI Setup

Estimated time: 10 minutes

Install Claude Code and configure Google Cloud Vertex AI as the backend provider. When complete, all Claude API calls route through your assigned GCP project — no Anthropic API key required.

## Orientation

Print this once at the start:

```
You're setting up Claude Code with Vertex AI as the backend.
This takes about 10 minutes the first time.

We'll set up:
  1. Google Cloud CLI (gcloud)
  2. Node.js 18+
  3. Claude Code CLI
  4. Google Cloud authentication
  5. Application Default Credentials (ADC)
  6. Your GCP project
  7. Vertex AI environment variables

You'll need your GCP project ID. Find yours in the project list:
https://docs.google.com/spreadsheets/d/1qWoCx3i5jZ-t6BUD-2AIdutk9sMmkytoXqjBXh2oi4U/edit?gid=0#gid=0
```

## Progress Tracking

On module start, write a progress marker:

```bash
mkdir -p ~/.claude/courseware-progress && date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/01.started
```

## Preflight

Audit current state before doing anything:

```bash
# gcloud CLI
command -v gcloud &>/dev/null && echo "EXISTS: gcloud CLI ($(gcloud version 2>/dev/null | head -1))" || echo "MISSING: gcloud CLI"

# Node.js
if command -v node &>/dev/null; then
  NODE_VER=$(node --version)
  NODE_MAJOR=$(echo "$NODE_VER" | sed 's/v//' | cut -d. -f1)
  if [ "$NODE_MAJOR" -ge 18 ]; then
    echo "EXISTS: Node.js $NODE_VER"
  else
    echo "OUTDATED: Node.js $NODE_VER (need 18+)"
  fi
else
  echo "MISSING: Node.js"
fi

# Claude Code
command -v claude &>/dev/null && echo "EXISTS: Claude Code ($(claude --version 2>/dev/null || echo 'installed'))" || echo "MISSING: Claude Code"

# gcloud auth
GCLOUD_ACCOUNT=$(gcloud config get-value account 2>/dev/null || true)
[ -n "$GCLOUD_ACCOUNT" ] && echo "EXISTS: gcloud authenticated as $GCLOUD_ACCOUNT" || echo "MISSING: gcloud authentication"

# ADC
gcloud auth application-default print-access-token &>/dev/null 2>&1 && echo "EXISTS: ADC token valid" || echo "MISSING: ADC not configured or expired"

# Vertex env vars — check shell AND ~/.claude/settings.json
SETTINGS_FILE="$HOME/.claude/settings.json"
if [ "$CLAUDE_CODE_USE_VERTEX" = "1" ]; then
  echo "EXISTS: CLAUDE_CODE_USE_VERTEX=1 (shell)"
elif [ -f "$SETTINGS_FILE" ] && python3 -c "import json; d=json.load(open('$SETTINGS_FILE')); assert d.get('env',{}).get('CLAUDE_CODE_USE_VERTEX')=='1'" 2>/dev/null; then
  echo "EXISTS: CLAUDE_CODE_USE_VERTEX=1 (settings.json)"
else
  echo "MISSING: CLAUDE_CODE_USE_VERTEX"
fi

if [ -n "$ANTHROPIC_VERTEX_PROJECT_ID" ]; then
  echo "EXISTS: ANTHROPIC_VERTEX_PROJECT_ID=$ANTHROPIC_VERTEX_PROJECT_ID (shell)"
elif [ -f "$SETTINGS_FILE" ] && python3 -c "import json; d=json.load(open('$SETTINGS_FILE')); v=d.get('env',{}).get('ANTHROPIC_VERTEX_PROJECT_ID',''); assert v; print(v)" 2>/dev/null; then
  echo "EXISTS: ANTHROPIC_VERTEX_PROJECT_ID=$(python3 -c "import json; print(json.load(open('$SETTINGS_FILE')).get('env',{}).get('ANTHROPIC_VERTEX_PROJECT_ID',''))")" " (settings.json)"
else
  echo "MISSING: ANTHROPIC_VERTEX_PROJECT_ID"
fi

if [ -n "$CLOUD_ML_REGION" ]; then
  echo "EXISTS: CLOUD_ML_REGION=$CLOUD_ML_REGION (shell)"
elif [ -f "$SETTINGS_FILE" ] && python3 -c "import json; d=json.load(open('$SETTINGS_FILE')); assert d.get('env',{}).get('CLOUD_ML_REGION')" 2>/dev/null; then
  echo "EXISTS: CLOUD_ML_REGION=$(python3 -c "import json; print(json.load(open('$SETTINGS_FILE')).get('env',{}).get('CLOUD_ML_REGION',''))")" " (settings.json)"
else
  echo "MISSING: CLOUD_ML_REGION"
fi

# GCP project
GCLOUD_PROJECT=$(gcloud config get-value project 2>/dev/null || true)
[ -n "$GCLOUD_PROJECT" ] && echo "EXISTS: gcloud project set to $GCLOUD_PROJECT" || echo "MISSING: gcloud project not set"
```

Print a summary of what was found. Skip any step below where the item already exists and is valid.

## Step 1 — Install gcloud CLI

Skip if gcloud CLI is already installed.

If missing, tell the user:

```
gcloud CLI is not installed. Install it using one of these methods:

  Mac (Homebrew):   brew install google-cloud-sdk
  Linux:            curl https://sdk.cloud.google.com | bash && exec -l $SHELL

Then re-run /learn-01-vertex-setup to continue.
```

After install, verify:
```bash
gcloud version | head -1
```

## Step 2 — Install Node.js

Skip if Node.js 18+ is already installed.

If missing or outdated, tell the user:

```
Node.js 18+ is required by Claude Code.

  Mac (Homebrew):   brew install node
  Linux:            See https://nodejs.org/en/download/

Then re-run /learn-01-vertex-setup to continue.
```

After install, verify:
```bash
node --version
```

## Step 3 — Install Claude Code

Skip if Claude Code is already installed.

If missing, tell the user to run:

```
Install Claude Code by running this command:

  ! npm install -g @anthropic-ai/claude-code
```

After install, verify:
```bash
claude --version 2>/dev/null || echo "NOT FOUND"
```

## Step 4 — Authenticate with Google Cloud

Skip if `gcloud config get-value account` returns a non-empty value.

Tell the user:

```
Sign in with your Red Hat Google identity. This opens a browser.

  ! gcloud auth login

Sign in with your @redhat.com account.
```

After auth, verify:
```bash
GCLOUD_ACCOUNT=$(gcloud config get-value account 2>/dev/null || true)
[ -n "$GCLOUD_ACCOUNT" ] && echo "Authenticated as: $GCLOUD_ACCOUNT" || echo "FAILED — not authenticated"
```

## Step 5 — Set up Application Default Credentials (ADC)

Skip if `gcloud auth application-default print-access-token` succeeds.

Tell the user:

```
ADC is what Claude Code uses to get authentication tokens from Google Cloud.
This opens a browser — approve the consent screen.

  ! gcloud auth application-default login
```

After setup, verify:
```bash
gcloud auth application-default print-access-token &>/dev/null 2>&1 && echo "ADC: valid" || echo "ADC: FAILED"
```

## Step 6 — Set GCP project

Skip if `gcloud config get-value project` returns a non-empty value AND the Vertex env vars are already set.

Ask:
> "What is your GCP project ID? Find it in the project list: https://docs.google.com/spreadsheets/d/1qWoCx3i5jZ-t6BUD-2AIdutk9sMmkytoXqjBXh2oi4U/edit?gid=0#gid=0"

After the user provides their project ID, tell them to run:

```
  ! gcloud config set project YOUR_PROJECT_ID
```

Verify:
```bash
gcloud config get-value project 2>/dev/null
```

## Step 7 — Write Vertex AI environment variables

Skip if all three env vars (`CLAUDE_CODE_USE_VERTEX`, `ANTHROPIC_VERTEX_PROJECT_ID`, `CLOUD_ML_REGION`) are already set in the current shell AND present in `~/.claude/settings.json`.

This step writes the Vertex AI configuration to two places:

1. **`~/.claude/settings.json`** — where Claude Code reads them (reliable, works in CLI and VS Code)
2. **Shell config** (`~/.zshrc` or `~/.bashrc`) — so other tools and new terminals also have them

### Write to ~/.claude/settings.json

Ask the user for their GCP project ID if not already known from Step 6. Then run:

```bash
python3 << 'PYEOF'
import json, os

project_id = os.popen("gcloud config get-value project 2>/dev/null").read().strip()
if not project_id:
    print("FAIL: No GCP project set. Run Step 6 first.")
    exit(1)

path = os.path.expanduser("~/.claude/settings.json")
settings = json.load(open(path)) if os.path.exists(path) else {}
settings.setdefault("env", {})

settings["env"]["CLAUDE_CODE_USE_VERTEX"] = "1"
settings["env"]["ANTHROPIC_VERTEX_PROJECT_ID"] = project_id
settings["env"]["CLOUD_ML_REGION"] = "global"

with open(path, "w") as f:
    json.dump(settings, f, indent=2)

print(f"PASS: Vertex AI env vars written to {path}")
print(f"  CLAUDE_CODE_USE_VERTEX=1")
print(f"  ANTHROPIC_VERTEX_PROJECT_ID={project_id}")
print(f"  CLOUD_ML_REGION=global")
PYEOF
```

### Write to shell config

Also add them to the shell config so new terminals pick them up:

```bash
SHELL_CONFIG="$HOME/.zshrc"
[ "$(basename "$SHELL")" != "zsh" ] && SHELL_CONFIG="$HOME/.bashrc"

if grep -q "CLAUDE_CODE_USE_VERTEX" "$SHELL_CONFIG" 2>/dev/null; then
  echo "SKIP: Vertex vars already in $SHELL_CONFIG"
else
  PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
  cat >> "$SHELL_CONFIG" << SHEOF

# Claude Code — Vertex AI backend
export CLAUDE_CODE_USE_VERTEX=1
export ANTHROPIC_VERTEX_PROJECT_ID=$PROJECT_ID
export CLOUD_ML_REGION=global
SHEOF
  echo "PASS: Vertex vars added to $SHELL_CONFIG"
fi
```

Then reload:

```bash
SHELL_CONFIG="$HOME/.zshrc"
[ "$(basename "$SHELL")" != "zsh" ] && SHELL_CONFIG="$HOME/.bashrc"
source "$SHELL_CONFIG"
```

### Why both?

`~/.claude/settings.json` is what Claude Code reads directly -- it works in the CLI, VS Code extension, and any other integration without depending on shell startup. The shell config is a backup so other tools and fresh terminal sessions also have the vars.

## Verification

Run the full preflight check again:

```bash
PASS=0
TOTAL=7

command -v gcloud &>/dev/null && { echo "PASS: gcloud CLI"; PASS=$((PASS+1)); } || echo "FAIL: gcloud CLI"

NODE_MAJOR=$(node --version 2>/dev/null | sed 's/v//' | cut -d. -f1)
[ "${NODE_MAJOR:-0}" -ge 18 ] && { echo "PASS: Node.js $(node --version)"; PASS=$((PASS+1)); } || echo "FAIL: Node.js 18+"

command -v claude &>/dev/null && { echo "PASS: Claude Code"; PASS=$((PASS+1)); } || echo "FAIL: Claude Code"

GCLOUD_ACCOUNT=$(gcloud config get-value account 2>/dev/null || true)
[ -n "$GCLOUD_ACCOUNT" ] && { echo "PASS: gcloud auth ($GCLOUD_ACCOUNT)"; PASS=$((PASS+1)); } || echo "FAIL: gcloud auth"

gcloud auth application-default print-access-token &>/dev/null 2>&1 && { echo "PASS: ADC valid"; PASS=$((PASS+1)); } || echo "FAIL: ADC"

VERTEX_OK=false
if [ "$CLAUDE_CODE_USE_VERTEX" = "1" ] && [ -n "$ANTHROPIC_VERTEX_PROJECT_ID" ] && [ -n "$CLOUD_ML_REGION" ]; then
  VERTEX_OK=true
elif python3 -c "
import json, os
d=json.load(open(os.path.expanduser('~/.claude/settings.json')))
e=d.get('env',{})
assert e.get('CLAUDE_CODE_USE_VERTEX')=='1'
assert e.get('ANTHROPIC_VERTEX_PROJECT_ID')
assert e.get('CLOUD_ML_REGION')
" 2>/dev/null; then
  VERTEX_OK=true
fi
if [ "$VERTEX_OK" = true ]; then
  echo "PASS: Vertex env vars set"; PASS=$((PASS+1))
else
  echo "FAIL: Vertex env vars"
fi

GCLOUD_PROJECT=$(gcloud config get-value project 2>/dev/null || true)
[ -n "$GCLOUD_PROJECT" ] && { echo "PASS: GCP project ($GCLOUD_PROJECT)"; PASS=$((PASS+1)); } || echo "FAIL: GCP project"

echo ""
echo "$PASS/$TOTAL checks passed."
```

If all 7 pass, print:
```
All prerequisites are in place. Claude Code is configured to use Vertex AI.
```

If any fail, tell the user which step to re-run.

## Challenge

```
Now let's verify it works end-to-end.

1. Open a NEW terminal window (so your env vars are loaded fresh)
2. Run: claude
3. Ask Claude a question — anything you like
4. Look at the output — it should show the model name (e.g. claude-sonnet-4-6)

Come back here and tell me:
  - Did Claude Code launch successfully?
  - What model name did it show?
```

## Challenge Verification

The user should report that:
1. Claude Code launched without authentication errors
2. A Claude model responded (any model name confirms Vertex AI is working)

If they got an auth error, check:
- ADC may have expired: `! gcloud auth application-default login`
- Wrong project: `echo $ANTHROPIC_VERTEX_PROJECT_ID`
- Region issue: `echo $CLOUD_ML_REGION` (should be `global`)

Write the completion marker:

```bash
date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/01.done
```

If successful, print:
```
Module 01 complete.

Claude Code is installed and using Vertex AI as the backend.
Your setup:
  GCP Project: $ANTHROPIC_VERTEX_PROJECT_ID
  Region: $CLOUD_ML_REGION
  Auth: Application Default Credentials

Next module: /learn-02-writing-claude-md

Questions or feedback? https://github.com/rhpds/claude-code-courseware/issues
```
