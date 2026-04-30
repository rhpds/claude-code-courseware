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

# Vertex env vars
[ "$CLAUDE_CODE_USE_VERTEX" = "1" ] && echo "EXISTS: CLAUDE_CODE_USE_VERTEX=1" || echo "MISSING: CLAUDE_CODE_USE_VERTEX"
[ -n "$ANTHROPIC_VERTEX_PROJECT_ID" ] && echo "EXISTS: ANTHROPIC_VERTEX_PROJECT_ID=$ANTHROPIC_VERTEX_PROJECT_ID" || echo "MISSING: ANTHROPIC_VERTEX_PROJECT_ID"
[ -n "$CLOUD_ML_REGION" ] && echo "EXISTS: CLOUD_ML_REGION=$CLOUD_ML_REGION" || echo "MISSING: CLOUD_ML_REGION"

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

Skip if all three env vars (`CLAUDE_CODE_USE_VERTEX`, `ANTHROPIC_VERTEX_PROJECT_ID`, `CLOUD_ML_REGION`) are already set in the current shell.

Detect the user's shell config file:

```bash
if [ "$(basename "$SHELL")" = "zsh" ]; then
  echo "Shell config: ~/.zshrc"
else
  echo "Shell config: ~/.bashrc"
fi
```

Check if the vars already exist in the shell config:

```bash
SHELL_CONFIG="$HOME/.zshrc"
[ "$(basename "$SHELL")" != "zsh" ] && SHELL_CONFIG="$HOME/.bashrc"
grep -q "CLAUDE_CODE_USE_VERTEX" "$SHELL_CONFIG" 2>/dev/null && echo "ALREADY IN $SHELL_CONFIG" || echo "NOT YET IN $SHELL_CONFIG"
```

If not already in the shell config, tell the user to run these commands (substitute their project ID):

```
Add these lines to your shell config:

  ! echo '' >> ~/.zshrc
  ! echo '# Claude Code — Vertex AI backend' >> ~/.zshrc
  ! echo 'export CLAUDE_CODE_USE_VERTEX=1' >> ~/.zshrc
  ! echo 'export ANTHROPIC_VERTEX_PROJECT_ID=YOUR_PROJECT_ID' >> ~/.zshrc
  ! echo 'export CLOUD_ML_REGION=global' >> ~/.zshrc

IMPORTANT: Replace YOUR_PROJECT_ID with your actual GCP project ID.

Then reload:

  ! source ~/.zshrc
```

For bash users, substitute `~/.bashrc` in all commands above.

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

[ "$CLAUDE_CODE_USE_VERTEX" = "1" ] && [ -n "$ANTHROPIC_VERTEX_PROJECT_ID" ] && [ -n "$CLOUD_ML_REGION" ] && { echo "PASS: Vertex env vars set"; PASS=$((PASS+1)); } || echo "FAIL: Vertex env vars"

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

If successful, print:
```
Module 01 complete.

Claude Code is installed and using Vertex AI as the backend.
Your setup:
  GCP Project: $ANTHROPIC_VERTEX_PROJECT_ID
  Region: $CLOUD_ML_REGION
  Auth: Application Default Credentials

Next module: /learn-02-atlassian-mcp
```
