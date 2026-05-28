# Module 27 -- Checkpointing & Session Management
<!-- NEW -->

Estimated time: 10 minutes
Prerequisites: Module 01 (Claude Code installed and working)

Master session checkpoints, rewind, resume, and auto mode to work faster and recover from mistakes effortlessly.

## Orientation

Print this once at the start:

```
You're learning checkpointing and session management.
This takes about 10 minutes.

We'll cover:
  1. Checkpointing with Esc+Esc -- rewind conversation, code, or both
  2. Session resume -- pick up where you left off
  3. Session branching -- explore alternatives safely
  4. Auto mode -- automate most permission approvals
  5. Permission customization -- fine-grained tool control

You'll need:
  - Claude Code installed and working (Module 01)
```

## Progress Tracking

On module start, write a progress marker:

```bash
mkdir -p ~/.claude/courseware-progress && date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/27.started
```

## Preflight

Audit current state before doing anything. Each check prints EXISTS or MISSING.

```bash
# Check 1 -- Claude Code installed?
command -v claude &>/dev/null && echo "EXISTS: Claude Code installed" || echo "MISSING: Claude Code -- run /learn-01-vertex-setup first"

# Check 2 -- Claude Code version
if command -v claude &>/dev/null; then
  VERSION=$(claude --version 2>/dev/null | head -1)
  echo "EXISTS: Claude Code version $VERSION"
else
  echo "MISSING: Claude Code version -- install Claude Code first"
fi

# Check 3 -- Session history
if [ -d "$HOME/.claude/projects" ]; then
  SESSION_COUNT=$(find "$HOME/.claude/projects" -name "*.json" -type f 2>/dev/null | wc -l | tr -d ' ')
  echo "EXISTS: Session data directory (~/.claude/projects) with $SESSION_COUNT file(s)"
else
  echo "INFO: No session history directory yet -- this is normal for new installations"
fi

# Check 4 -- Settings file exists?
[ -f "$HOME/.claude/settings.json" ] && echo "EXISTS: ~/.claude/settings.json" || echo "MISSING: ~/.claude/settings.json -- will be created when needed"
```

Print a summary of what was found. The only hard requirement is Check 1 -- Claude Code must be installed.

## Step 1 -- Checkpointing with Esc+Esc

Claude Code automatically creates a checkpoint before every prompt you send. This means you can rewind to any prior state at any time.

Tell the user:
```
Press Esc twice (Esc+Esc) to open the checkpoint rewind menu.
You'll see a list of your recent prompts, each one a rewind point.

Select any checkpoint and you get three options:

  REWIND CONVERSATION ONLY
    Undoes what you said from that point forward. The conversation
    resets to just before that prompt. File changes are kept.

    Use when: you asked the wrong question or want to re-phrase
    a request without losing the code changes Claude already made.

  REWIND CODE ONLY
    Undoes all file changes made from that point forward. The
    conversation stays intact -- Claude still remembers what you
    discussed and what it tried.

    Use when: Claude made changes you don't like and you want to
    try a different approach. This is the most powerful option
    because Claude retains the context of what went wrong, so it
    can try something better on the next attempt.

  REWIND BOTH
    Undoes both the conversation and the code changes from that
    point forward. A full reset to that moment in time.

    Use when: you want to completely start over from a known-good
    state, as if the later prompts never happened.

Checkpoints are created automatically -- you never need to
manually save one. They persist for the duration of the session.
```

Key point to emphasize:
```
"Rewind code only" is especially valuable. It lets Claude learn
from a failed attempt. The conversation remembers what was tried
and why it didn't work, so the next attempt is usually better.

Think of it as: undo the changes, keep the lessons.
```

## Step 2 -- Session Resume

Tell the user:
```
Sessions persist when you exit Claude Code. You can pick up
exactly where you left off.

  claude --resume
    Resumes your most recent session in the current directory.
    All conversation history and context are restored.

  claude --continue
    Same as --resume. Both flags work identically.

  /resume
    Opens a picker UI showing all recent sessions, including
    background jobs. Select any session to jump back into it.
    This is useful when you have multiple sessions across
    different projects.

  claude --resume --name <label>
    Give sessions meaningful names when you start them so they
    are easy to identify later in the /resume picker.

    Example: claude --name "refactor-auth-module"
    Later:   claude --resume  (shows "refactor-auth-module" in the list)

Named sessions make it practical to juggle multiple workstreams.
Instead of guessing which session was which, you see descriptive
labels like "fix-login-bug" or "add-metrics-endpoint".
```

## Step 3 -- Session Branching

Tell the user:
```
Sometimes you want to explore an alternative approach without
losing your current progress. That's what session branching does.

  /branch
    Splits the current session into two independent conversations.
    The original session stays exactly as it is. The new branch
    starts with a copy of the full conversation history up to
    that point.

    (This command was formerly called /fork -- both names work.)

Each branch has its own:
  - Conversation history (diverges from the branch point)
  - Checkpoints (new checkpoints in each branch are independent)
  - Code changes (edits in one branch don't affect the other)

When to use branching:
  - You have a working approach but want to try a radically
    different one without risk
  - You want to compare two implementation strategies side by side
  - You're at a decision point and want to explore both paths

After branching, you can switch between sessions with /resume
to compare results.
```

## Step 4 -- Auto Mode

Tell the user:
```
By default, Claude Code asks for permission before running
commands, writing files, or calling MCP tools. You can change
this behavior.

Press Shift+Tab to cycle through permission modes:

  NORMAL (default)
    Claude asks permission for every tool call. You approve
    or deny each one individually.

  AUTO-ACCEPT
    All tool calls are automatically approved. Fast but gives
    Claude unrestricted access. Use with caution.

  PLAN
    Claude explains what it wants to do but doesn't execute.
    Useful for reviewing a proposed approach before committing.

  DON'T ASK
    Auto-approves everything for just this session, including
    commands. Equivalent to "yes to all" for the session duration.

  AUTO
    Uses model-based classifiers to decide whether each tool
    call is safe. Approves safe calls automatically and blocks
    risky ones. Automates roughly 93% of manual permission
    approvals while maintaining safety.

    Safety feature: when entering Auto mode, Claude strips any
    blanket shell access rules to prevent over-permissive configs
    from carrying over.

Best practices:
  - Use Normal mode when doing sensitive work (production configs,
    credentials, destructive operations)
  - Use Auto mode for routine development (writing code, running
    tests, reading files)
  - Use Plan mode when you want Claude to think through a complex
    task before acting
  - Avoid Don't Ask on shared or production systems
```

## Step 5 -- Permission Customization

Tell the user:
```
For fine-grained control over what Claude can do without asking,
use allowedTools and deniedTools in your settings files.

Location:
  ~/.claude/settings.json           -- global (all projects)
  .claude/settings.json             -- project-wide (checked in)
  .claude/settings.local.json       -- project-local (gitignored)

Format (in any of the above files):
  {
    "permissions": {
      "allowedTools": [
        "Bash(git *)",
        "Bash(npm test)",
        "mcp__github__*",
        "Read",
        "Glob",
        "Grep"
      ],
      "deniedTools": [
        "Bash(rm -rf *)",
        "Bash(git push --force *)"
      ]
    }
  }

Rules:
  - Glob patterns work: "Bash(git *)" matches any git command
  - "mcp__github__*" matches all tools from the GitHub MCP server
  - Deny rules always win over allow rules -- if a tool matches
    both an allow and a deny pattern, it is denied
  - Use settings.local.json for project-scoped permissions that
    you don't want committed to the repository

Common patterns:
  "Bash(git *)"           -- all git commands
  "Bash(npm *)"           -- all npm commands
  "Bash(python3 *)"       -- all python3 commands
  "mcp__git__*"           -- all Git MCP tools
  "mcp__memory__*"        -- all Memory MCP tools
  "Read"                  -- read any file (no arguments needed)
  "Edit"                  -- edit any file
  "Write"                 -- write any file
  "Bash(cat *)"           -- cat any file

Prefer settings.local.json for project-specific permissions.
This keeps your global settings clean and avoids committing
overly broad permissions into shared repos.
```

## Verification

Run all preflight checks again as PASS/FAIL:

```bash
PASS=0
TOTAL=3

command -v claude &>/dev/null && { echo "PASS: Claude Code installed"; PASS=$((PASS+1)); } || echo "FAIL: Claude Code not installed"

claude --version &>/dev/null && { echo "PASS: Claude Code version accessible"; PASS=$((PASS+1)); } || echo "FAIL: Claude Code version not accessible"

# Check that the user has been through the module content
[ -f "$HOME/.claude/courseware-progress/27.started" ] && { echo "PASS: Module 27 progress tracked"; PASS=$((PASS+1)); } || echo "FAIL: Module 27 progress not tracked"

echo ""
echo "$PASS/$TOTAL checks passed."
```

If all pass, print:
```
All checks passed. You understand checkpointing, session management,
auto mode, and permission customization in Claude Code.
```

If any fail, tell the user which step to re-run.

## Challenge

```
Try the checkpointing workflow hands-on:

1. Pick any file in this repository and make a small edit --
   add a comment line somewhere. Confirm the edit was made.

2. Press Esc+Esc to open the checkpoint rewind menu.

3. Select the checkpoint from before your edit and choose
   "rewind code only."

4. Verify that:
   - The file change was undone (the comment is gone)
   - Your conversation context is preserved (Claude remembers
     what you edited and that you rewound)

5. Ask Claude to make a different edit to the same file --
   something better than the first attempt. Claude should
   reference the first attempt in its reasoning.

Tell me:
  1. What file you edited and what the first change was
  2. What "rewind code only" did (was the change undone?)
  3. Whether conversation context was preserved after rewind
  4. What the second (improved) edit was
```

## Challenge Verification

Review the user's answers. The key things to confirm:

1. They made a file edit and confirmed it was applied
2. "Rewind code only" undid the file change
3. Conversation context survived the rewind -- Claude still knew what happened
4. The second edit attempt benefited from the retained context

Accept any reasonable demonstration that shows understanding of the rewind workflow. The specific file and edits don't matter -- the process is what counts.

If successful, write the completion marker:

```bash
date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/27.done
```

Then print:
```
Module 27 complete.

You now know how to use checkpointing and session management.
Key capabilities:
  Esc+Esc:       Rewind conversation, code, or both to any checkpoint
  --resume:      Pick up where you left off
  /branch:       Explore alternatives without losing progress
  Shift+Tab:     Cycle through permission modes (Normal/Auto/Plan)
  allowedTools:  Fine-grained permission control in settings.json

Rules of thumb:
  - "Rewind code only" is the most useful option -- it keeps
    lessons learned while undoing changes
  - Name your sessions when juggling multiple workstreams
  - Use Auto mode for routine work, Normal for sensitive operations
  - Deny rules always beat allow rules in permission settings
  - Prefer settings.local.json for project-scoped permissions

Next module: /learn-28-voice-vim-terminal-customization

Questions or feedback? https://github.com/rhpds/claude-code-courseware/issues
```
