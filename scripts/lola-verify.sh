#!/usr/bin/env bash
# lola-verify.sh — install the pinned lola-ai into an isolated venv,
# add the ccc module, install it for claude-code, and verify the output.
#
# Usage:
#   scripts/lola-verify.sh                   # verify against golden snapshot
#   scripts/lola-verify.sh --update-golden   # refresh the golden snapshot
#
# Requires: uv (for Python 3.13+ venv creation) or python3.13+
#
# The golden snapshot captures:
#   - installed.yml (the Lola installation manifest)
#   - module-tree.txt (sorted file listing of the installed module)
# These are deterministic outputs that drift when Lola changes behavior.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GOLDEN_DIR="$REPO_ROOT/tests/golden/ccc"
WORK_DIR="$(mktemp -d)"
VENV_DIR="$WORK_DIR/venv"
INSTALL_DIR="$WORK_DIR/ccc-verify"
LOLA_HOME="$WORK_DIR/lola-home"

cleanup() { rm -rf "$WORK_DIR"; }
trap cleanup EXIT

export LOLA_HOME

echo "==> Creating isolated Python 3.13 venv at $VENV_DIR"
if command -v uv &>/dev/null; then
  uv venv --python 3.13 "$VENV_DIR" --quiet
else
  python3.13 -m venv "$VENV_DIR"
fi
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "==> Installing pinned lola-ai from $REPO_ROOT/lola/requirements-lola.txt"
if command -v uv &>/dev/null; then
  uv pip install -q -r "$REPO_ROOT/lola/requirements-lola.txt"
else
  pip install -q -r "$REPO_ROOT/lola/requirements-lola.txt"
fi

echo "==> lola version: $(lola --version 2>/dev/null || echo 'unknown')"

echo "==> Adding module from $REPO_ROOT/lola/ccc/"
mkdir -p "$LOLA_HOME"
lola mod add "$REPO_ROOT/lola/ccc/"

echo "==> Installing ccc module for claude-code into $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
lola install ccc "$INSTALL_DIR" -a claude-code

echo ""
echo "==> Installed module tree:"
find "$LOLA_HOME/modules/ccc" -type f | sed "s|$LOLA_HOME/modules/ccc/||" | sort

echo ""
echo "==> Installation manifest:"
cat "$LOLA_HOME/installed.yml"

# Capture golden artifacts
ACTUAL_DIR="$WORK_DIR/actual"
mkdir -p "$ACTUAL_DIR"
cp "$LOLA_HOME/installed.yml" "$ACTUAL_DIR/installed.yml"
find "$LOLA_HOME/modules/ccc" -type f | sed "s|$LOLA_HOME/modules/ccc/||" | sort > "$ACTUAL_DIR/module-tree.txt"

# Normalize installed.yml: strip the project_path line (contains temp dir)
sed -i.bak '/project_path:/d' "$ACTUAL_DIR/installed.yml"
rm -f "$ACTUAL_DIR/installed.yml.bak"

if [ "${1:-}" = "--update-golden" ]; then
  echo ""
  echo "==> Updating golden snapshot at $GOLDEN_DIR"
  rm -rf "$GOLDEN_DIR"
  mkdir -p "$GOLDEN_DIR"
  cp "$ACTUAL_DIR/installed.yml" "$GOLDEN_DIR/installed.yml"
  cp "$ACTUAL_DIR/module-tree.txt" "$GOLDEN_DIR/module-tree.txt"
  echo "==> Golden snapshot updated (installed.yml + module-tree.txt)."
else
  echo ""
  echo "==> Comparing against golden snapshot at $GOLDEN_DIR"
  if [ ! -d "$GOLDEN_DIR" ]; then
    echo "WARN: No golden snapshot found. Run with --update-golden to create one."
    exit 1
  fi

  PASS=true
  for artifact in installed.yml module-tree.txt; do
    if [ ! -f "$GOLDEN_DIR/$artifact" ]; then
      echo "FAIL: Missing golden artifact: $artifact"
      PASS=false
      continue
    fi
    if diff "$ACTUAL_DIR/$artifact" "$GOLDEN_DIR/$artifact" > /dev/null 2>&1; then
      echo "PASS: $artifact matches golden snapshot."
    else
      echo "FAIL: $artifact differs from golden snapshot:"
      diff "$ACTUAL_DIR/$artifact" "$GOLDEN_DIR/$artifact" || true
      PASS=false
    fi
  done

  if [ "$PASS" = true ]; then
    echo ""
    echo "PASS: All golden artifacts match."
  else
    echo ""
    echo "FAIL: Golden snapshot mismatch. Review diffs above."
    echo "  To accept the new output: scripts/lola-verify.sh --update-golden"
    exit 1
  fi
fi

deactivate 2>/dev/null || true
