# Preflight Check

Run a prerequisite check for Claude Code Courseware. This verifies the tools and access needed before starting modules.

## Run All Checks

Run these checks and print the results:

```bash
echo "Claude Code Courseware — Preflight Check"
echo "========================================="
echo ""

PASS=0
TOTAL=8

# 1. Operating system
OS=$(uname -s)
if [ "$OS" = "Darwin" ] || [ "$OS" = "Linux" ]; then
  echo "PASS: Operating system ($OS)"
  PASS=$((PASS+1))
else
  echo "FAIL: Unsupported OS ($OS) — requires macOS or Linux"
fi

# 2. Claude Code
if command -v claude &>/dev/null; then
  echo "PASS: Claude Code ($(claude --version 2>/dev/null || echo 'installed'))"
  PASS=$((PASS+1))
else
  echo "FAIL: Claude Code not found — Module 01 will install it"
fi

# 3. Node.js 18+
if command -v node &>/dev/null; then
  NODE_VER=$(node --version)
  NODE_MAJOR=$(echo "$NODE_VER" | sed 's/v//' | cut -d. -f1)
  if [ "$NODE_MAJOR" -ge 18 ]; then
    echo "PASS: Node.js $NODE_VER"
    PASS=$((PASS+1))
  else
    echo "FAIL: Node.js $NODE_VER (need 18+) — brew install node"
  fi
else
  echo "FAIL: Node.js not found — brew install node"
fi

# 4. npm / npx
if command -v npm &>/dev/null && command -v npx &>/dev/null; then
  echo "PASS: npm $(npm --version) + npx"
  PASS=$((PASS+1))
else
  echo "FAIL: npm/npx not found — comes with Node.js"
fi

# 5. gcloud CLI
if command -v gcloud &>/dev/null; then
  echo "PASS: gcloud CLI"
  PASS=$((PASS+1))
else
  echo "FAIL: gcloud CLI not found — Module 01 will install it"
fi

# 6. GCP auth
if gcloud auth list --filter="status:ACTIVE" --format="value(account)" 2>/dev/null | grep -q "@"; then
  ACCT=$(gcloud auth list --filter="status:ACTIVE" --format="value(account)" 2>/dev/null | head -1)
  echo "PASS: GCP authenticated ($ACCT)"
  PASS=$((PASS+1))
else
  echo "FAIL: No active GCP auth — Module 01 will set this up"
fi

# 7. Git
if command -v git &>/dev/null; then
  echo "PASS: git $(git --version | awk '{print $3}')"
  PASS=$((PASS+1))
else
  echo "FAIL: git not found — xcode-select --install"
fi

# 8. GitHub SSH access
if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
  echo "PASS: GitHub SSH access"
  PASS=$((PASS+1))
else
  echo "WARN: GitHub SSH not verified (may still work with HTTPS)"
  PASS=$((PASS+1))
fi

echo ""
echo "$PASS/$TOTAL checks passed."
```

## After the Checks

Print a summary based on results:

If all pass:
> You're ready to go. Run `/courseware` to see the module catalog and pick a module to start.

If Claude Code or gcloud are missing:
> Some tools are missing, but that's expected if you're just getting started. Module 01 (`/learn-01-vertex-setup`) will walk you through installing everything you need.

If Node.js is missing:
> Node.js is required for most MCP servers. Install it first: `brew install node` (macOS) or see https://nodejs.org.
