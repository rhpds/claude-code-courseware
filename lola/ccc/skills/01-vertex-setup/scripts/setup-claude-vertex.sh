#!/usr/bin/env bash
#
# Interactive setup script for Claude Code with Vertex AI on Google Cloud.
# Run: bash setup-claude-vertex.sh
#
# Project list: https://docs.google.com/spreadsheets/d/1qWoCx3i5jZ-t6BUD-2AIdutk9sMmkytoXqjBXh2oi4U/edit?gid=0#gid=0

set -euo pipefail

REGION="global"

# --- helpers ---

info()  { printf "\n\033[1;34m>>>\033[0m %s\n" "$*"; }
ok()    { printf "\033[1;32m  OK:\033[0m %s\n" "$*"; }
warn()  { printf "\033[1;33m  WARN:\033[0m %s\n" "$*"; }
fail()  { printf "\033[1;31m  FAIL:\033[0m %s\n" "$*"; }
ask()   { printf "\033[1;36m  ?\033[0m %s " "$*"; }

detect_shell_config() {
    if [ -n "${ZSH_VERSION:-}" ] || [ "$(basename "$SHELL")" = "zsh" ]; then
        echo "$HOME/.zshrc"
    else
        echo "$HOME/.bashrc"
    fi
}

# --- preflight checks ---

info "Checking prerequisites..."

MISSING=0

if command -v gcloud &>/dev/null; then
    ok "gcloud CLI found ($(gcloud version 2>/dev/null | head -1 | sed 's/Google Cloud SDK //'))"
else
    fail "gcloud CLI not found. Install: https://cloud.google.com/sdk/docs/install"
    MISSING=1
fi

if command -v node &>/dev/null; then
    NODE_VER=$(node --version)
    NODE_MAJOR=$(echo "$NODE_VER" | sed 's/v//' | cut -d. -f1)
    if [ "$NODE_MAJOR" -ge 18 ]; then
        ok "Node.js $NODE_VER"
    else
        fail "Node.js 18+ required (found $NODE_VER)"
        MISSING=1
    fi
else
    fail "Node.js not found. Install 18+ from https://nodejs.org"
    MISSING=1
fi

if command -v claude &>/dev/null; then
    ok "Claude Code found ($(claude --version 2>/dev/null || echo 'version unknown'))"
else
    warn "Claude Code not installed. Will install after authentication."
fi

if [ "$MISSING" -eq 1 ]; then
    fail "Fix the missing prerequisites above, then re-run this script."
    exit 1
fi

# --- GCP authentication ---

info "Google Cloud authentication"

CURRENT_ACCOUNT=$(gcloud config get-value account 2>/dev/null || true)
if [ -n "$CURRENT_ACCOUNT" ]; then
    ok "Currently logged in as: $CURRENT_ACCOUNT"
    ask "Use this account? [Y/n]"
    read -r USE_CURRENT
    if [[ "${USE_CURRENT,,}" == "n" ]]; then
        gcloud auth login
    fi
else
    echo "  You'll be taken to a browser to sign in with your @redhat.com account."
    ask "Press Enter to continue..."
    read -r
    gcloud auth login
fi

# --- Application Default Credentials ---

info "Setting up Application Default Credentials (ADC)"
echo "  ADC is what Claude Code uses to authenticate with Vertex AI."
echo "  This will open a browser for consent — approve it."

if gcloud auth application-default print-access-token &>/dev/null; then
    ok "ADC already configured and valid."
    ask "Re-authenticate anyway? [y/N]"
    read -r REAUTH
    if [[ "${REAUTH,,}" == "y" ]]; then
        gcloud auth application-default login
    fi
else
    ask "Press Enter to set up ADC..."
    read -r
    gcloud auth application-default login
fi

# --- GCP project selection ---

info "GCP project selection"
echo "  Find your assigned project ID in the project list:"
echo "  https://docs.google.com/spreadsheets/d/1qWoCx3i5jZ-t6BUD-2AIdutk9sMmkytoXqjBXh2oi4U/edit?gid=0#gid=0"
echo ""

CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || true)
if [ -n "$CURRENT_PROJECT" ]; then
    echo "  Current gcloud project: $CURRENT_PROJECT"
fi

ask "Enter your GCP project ID:"
read -r PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    if [ -n "$CURRENT_PROJECT" ]; then
        PROJECT_ID="$CURRENT_PROJECT"
        ok "Using current project: $PROJECT_ID"
    else
        fail "No project ID provided. Exiting."
        exit 1
    fi
fi

gcloud config set project "$PROJECT_ID"
ok "GCP project set to: $PROJECT_ID"

# --- Install Claude Code if missing ---

if ! command -v claude &>/dev/null; then
    info "Installing Claude Code..."
    npm install -g @anthropic-ai/claude-code
    ok "Claude Code installed ($(claude --version 2>/dev/null || echo 'done'))"
fi

# --- Set environment variables ---

info "Configuring environment variables"

SHELL_CONFIG=$(detect_shell_config)
echo "  Shell config file: $SHELL_CONFIG"

ALREADY_SET=0
if grep -q "CLAUDE_CODE_USE_VERTEX" "$SHELL_CONFIG" 2>/dev/null; then
    warn "Vertex env vars already exist in $SHELL_CONFIG."
    ask "Overwrite them? [y/N]"
    read -r OVERWRITE
    if [[ "${OVERWRITE,,}" != "y" ]]; then
        ok "Keeping existing env vars."
        ALREADY_SET=1
    else
        # Remove old entries
        sed -i.bak '/# Claude Code.*Vertex/d; /CLAUDE_CODE_USE_VERTEX/d; /ANTHROPIC_VERTEX_PROJECT_ID/d; /CLOUD_ML_REGION/d' "$SHELL_CONFIG"
    fi
fi

if [ "$ALREADY_SET" -eq 0 ]; then
    {
        echo ""
        echo "# Claude Code — Vertex AI backend"
        echo "export CLAUDE_CODE_USE_VERTEX=1"
        echo "export ANTHROPIC_VERTEX_PROJECT_ID=$PROJECT_ID"
        echo "export CLOUD_ML_REGION=$REGION"
    } >> "$SHELL_CONFIG"
    ok "Environment variables written to $SHELL_CONFIG"
fi

# Export for current session
export CLAUDE_CODE_USE_VERTEX=1
export ANTHROPIC_VERTEX_PROJECT_ID="$PROJECT_ID"
export CLOUD_ML_REGION="$REGION"

# --- Verification ---

info "Verifying setup..."

PASS=0
TOTAL=0

TOTAL=$((TOTAL + 1))
if [ "$CLAUDE_CODE_USE_VERTEX" = "1" ]; then
    ok "CLAUDE_CODE_USE_VERTEX=1"
    PASS=$((PASS + 1))
else
    fail "CLAUDE_CODE_USE_VERTEX not set"
fi

TOTAL=$((TOTAL + 1))
if [ -n "$ANTHROPIC_VERTEX_PROJECT_ID" ]; then
    ok "ANTHROPIC_VERTEX_PROJECT_ID=$ANTHROPIC_VERTEX_PROJECT_ID"
    PASS=$((PASS + 1))
else
    fail "ANTHROPIC_VERTEX_PROJECT_ID not set"
fi

TOTAL=$((TOTAL + 1))
if [ -n "$CLOUD_ML_REGION" ]; then
    ok "CLOUD_ML_REGION=$CLOUD_ML_REGION"
    PASS=$((PASS + 1))
else
    fail "CLOUD_ML_REGION not set"
fi

TOTAL=$((TOTAL + 1))
if gcloud auth application-default print-access-token &>/dev/null; then
    ok "ADC token is valid"
    PASS=$((PASS + 1))
else
    fail "ADC token invalid — run: gcloud auth application-default login"
fi

TOTAL=$((TOTAL + 1))
if command -v claude &>/dev/null; then
    ok "Claude Code is installed"
    PASS=$((PASS + 1))
else
    fail "Claude Code not found in PATH"
fi

echo ""
if [ "$PASS" -eq "$TOTAL" ]; then
    info "All checks passed ($PASS/$TOTAL). You're ready to go."
    echo ""
    echo "  Open a new terminal (or run: source $SHELL_CONFIG)"
    echo "  Then launch Claude Code:"
    echo ""
    echo "    claude"
    echo ""
else
    warn "$PASS/$TOTAL checks passed. Fix the failures above and re-run."
fi
