---
name: update-courseware
description: "Update the courseware plugin to the latest version — pulls new modules and improvements"
---

# Update Courseware

Update the courseware plugin to get the latest modules and improvements.

## Find the plugin repo

```bash
PLUGIN_REPO="$HOME/.claude/plugins/claude-code-courseware/repo"
if [ ! -d "$PLUGIN_REPO/.git" ]; then
  echo "NOT FOUND: Courseware plugin repo not at expected location."
  echo "  Expected: $PLUGIN_REPO"
  echo "  The courseware plugin may not be installed via the marketplace."
  echo ""
  echo "  To install: run /install in Claude Code, search for"
  echo "  'claude-code-courseware' in the rhpds marketplace."
fi
```

If the plugin repo is NOT FOUND, stop and show the install instructions above.

## Check for updates

```bash
PLUGIN_REPO="$HOME/.claude/plugins/claude-code-courseware/repo"
echo "Checking for updates..."
git -C "$PLUGIN_REPO" fetch origin main --quiet 2>/dev/null

LOCAL=$(git -C "$PLUGIN_REPO" rev-parse HEAD 2>/dev/null)
REMOTE=$(git -C "$PLUGIN_REPO" rev-parse origin/main 2>/dev/null)

if [ "$LOCAL" = "$REMOTE" ]; then
  echo "Already up to date. No new modules or changes available."
else
  BEHIND=$(git -C "$PLUGIN_REPO" rev-list HEAD..origin/main --count 2>/dev/null)
  echo "Updates available: $BEHIND new commit(s)."
  echo ""
  echo "Changes since your last update:"
  git -C "$PLUGIN_REPO" log HEAD..origin/main --oneline --no-decorate 2>/dev/null
  echo ""

  # Check for new module files
  NEW_MODULES=$(git -C "$PLUGIN_REPO" diff HEAD..origin/main --name-only --diff-filter=A -- 'modules/*.md' 2>/dev/null)
  if [ -n "$NEW_MODULES" ]; then
    echo "New modules added:"
    echo "$NEW_MODULES" | while read f; do echo "  + $f"; done
    echo ""
  fi

  # Check for updated module files
  UPDATED_MODULES=$(git -C "$PLUGIN_REPO" diff HEAD..origin/main --name-only --diff-filter=M -- 'modules/*.md' 2>/dev/null)
  if [ -n "$UPDATED_MODULES" ]; then
    echo "Updated modules:"
    echo "$UPDATED_MODULES" | while read f; do echo "  ~ $f"; done
    echo ""
  fi

  # Check for new skills
  NEW_SKILLS=$(git -C "$PLUGIN_REPO" diff HEAD..origin/main --name-only --diff-filter=A -- 'skills/*/SKILL.md' '.claude/commands/*.md' 2>/dev/null)
  if [ -n "$NEW_SKILLS" ]; then
    echo "New skills/commands:"
    echo "$NEW_SKILLS" | while read f; do echo "  + $f"; done
    echo ""
  fi
fi
```

If already up to date, print the message and stop.

If updates are available, show the summary above and then tell the user:

```
Ready to update. This will pull the latest changes into the plugin:

  ! git -C ~/.claude/plugins/claude-code-courseware/repo pull origin main

After the pull completes, restart Claude Code to load the updated
modules and skills.
```

## After the pull

```bash
PLUGIN_REPO="$HOME/.claude/plugins/claude-code-courseware/repo"
LOCAL=$(git -C "$PLUGIN_REPO" rev-parse HEAD 2>/dev/null)
REMOTE=$(git -C "$PLUGIN_REPO" rev-parse origin/main 2>/dev/null)
if [ "$LOCAL" = "$REMOTE" ]; then
  echo "PASS: Plugin is now up to date."
  MODULE_COUNT=$(ls "$PLUGIN_REPO/modules/"*.md 2>/dev/null | grep -v TEMPLATE | wc -l | tr -d ' ')
  echo "  Modules available: $MODULE_COUNT"
  echo ""
  echo "Restart Claude Code to load the updated content, then run"
  echo "/courseware to see the full catalog."
else
  echo "FAIL: Pull may not have completed. Try running manually:"
  echo "  git -C ~/.claude/plugins/claude-code-courseware/repo pull origin main"
fi
```
