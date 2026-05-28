# Module 23 -- Background Agents & Goal Mode
<!-- NEW -->

Estimated time: 15 minutes
Prerequisites: Module 01 (Claude Code installed and working)

Run Claude Code tasks in the background, monitor them from a dashboard, and set outcome-based goals that Claude works toward autonomously.

## Orientation

Print this once at the start:

```
You're learning background agents, agent view, goal mode, and loop mode.
This takes about 15 minutes.

Background sessions let you kick off work and keep using your terminal.
Agent view is a full-screen dashboard showing all your sessions.
Goal mode (/goal) tells Claude to keep working until a condition is met.
Loop mode (/loop) runs recurring tasks on an interval.

These compose: worktree + background + goal = fully autonomous feature work.

We'll cover:
  1. Starting and detaching background sessions
  2. Agent view -- the session dashboard
  3. Managing background sessions (resume, stop, respawn)
  4. Goal mode -- outcome-driven autonomy
  5. Loop mode -- recurring tasks
  6. Composing patterns for fully autonomous workflows

You'll need: Claude Code v2.1.139 or later (for agent view and goal mode).
```

## Progress Tracking

On module start, write a progress marker:

```bash
mkdir -p ~/.claude/courseware-progress && date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/23.started
```

## Preflight

Audit current state before doing anything. Each check prints EXISTS or MISSING.

```bash
# Check 1 -- Claude Code installed
command -v claude &>/dev/null && echo "EXISTS: Claude Code ($(claude --version 2>/dev/null | head -1))" || echo "MISSING: Claude Code -- run /learn-01-vertex-setup first"

# Check 2 -- Claude Code version supports background/goal features
if command -v claude &>/dev/null; then
  VERSION=$(claude --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
  if [ -n "$VERSION" ]; then
    MAJOR=$(echo "$VERSION" | cut -d. -f1)
    MINOR=$(echo "$VERSION" | cut -d. -f2)
    PATCH=$(echo "$VERSION" | cut -d. -f3)
    if [ "$MAJOR" -gt 2 ] 2>/dev/null || \
       ([ "$MAJOR" -eq 2 ] && [ "$MINOR" -gt 1 ] 2>/dev/null) || \
       ([ "$MAJOR" -eq 2 ] && [ "$MINOR" -eq 1 ] && [ "$PATCH" -ge 139 ] 2>/dev/null); then
      echo "EXISTS: Claude Code version $VERSION supports agent view and goal mode"
    else
      echo "MISSING: Claude Code version $VERSION is too old -- update to v2.1.139+ for agent view and goal mode"
    fi
  else
    echo "EXISTS: Claude Code installed (version could not be parsed -- assume current)"
  fi
fi

# Check 3 -- Check for any running background sessions
if command -v claude &>/dev/null; then
  BG_OUTPUT=$(claude sessions list 2>/dev/null)
  if [ $? -eq 0 ] && [ -n "$BG_OUTPUT" ]; then
    echo "EXISTS: Background session support available (found existing sessions)"
  else
    echo "EXISTS: Background session support available (no active sessions)"
  fi
fi
```

If Claude Code is MISSING, stop and tell the user:
```
Claude Code is not installed. Complete Module 01 first:
  /learn-01-vertex-setup
```

Print a summary of what was found. Skip steps where the item already exists.

## Step 1 -- Background sessions

This step is informational plus a hands-on exercise. Nothing to install.

Explain:
```
Background sessions let you start a Claude Code task and keep using
your terminal. The session runs via a supervisor process and survives
terminal closure.

Three ways to start a background session:

  1. From the command line:
       claude --bg "your prompt here"

     This starts a new session in the background with the given prompt.
     You get a session ID back immediately and can continue working.

  2. Send current session to background:
       /bg

     If you're in an interactive session and want to let Claude keep
     working while you do something else, type /bg. The session moves
     to the background. You can resume it later.

  3. Detach with left-arrow on empty prompt:
     When your input line is empty, press the left arrow key. This
     detaches the current session without stopping it.

Background sessions persist through terminal closure because they
run via a supervisor process. If you close your terminal, reconnect
via SSH, or open a new tab -- your sessions keep running.
```

Tell the user:
```
Try it now. Open a new terminal tab or window and run:

  ! claude --bg "List all files in this repository and count them by extension"

You'll see output like:
  Background session started: ses_abc123...
  Use 'claude sessions list' to check status.

The session is now running in the background.
```

Verify:
```bash
# List background sessions
claude sessions list 2>/dev/null || echo "No background sessions running (or sessions command not available in this version)"
```

## Step 2 -- Agent view

Explain:
```
Agent view is a full-screen terminal dashboard that shows all your
Claude Code sessions -- running, waiting for input, completed, or failed.

Launch it with:

  claude agents

What you'll see:

  The dashboard groups sessions by state:
    Working      -- actively processing
    Needs input  -- waiting for approval or a question answered
    Idle         -- ready but not doing anything
    Completed    -- finished successfully
    Failed       -- exited with an error
    Stopped      -- manually stopped

  Each session shows:
    - Session ID and working directory
    - Current status and what it's doing
    - Time elapsed
    - PR status indicators (if it created a PR):
        Draft, Open, Merged, or CI status

  Key bindings in agent view:
    Up/Down     -- navigate between sessions
    Enter       -- open/resume the selected session
    d           -- show session details
    s           -- stop a session
    r           -- respawn a stopped/failed session
    q           -- quit agent view (sessions keep running)

Agent view is read-only for most operations -- it monitors and
lets you jump into sessions. You can approve tool-use requests
directly from the dashboard when a session is in "Needs input" state.
```

Tell the user:
```
Try it now:

  ! claude agents

Look at the dashboard. You should see the background session you
started in Step 1. Note its state (Working, Completed, etc).

Press q to exit agent view when you're done looking.
```

After the user returns, explain:
```
Agent view is especially useful when running multiple background
sessions simultaneously. Instead of tracking session IDs in your
head, you get a live dashboard of everything.

When a session shows "Needs input", you can select it and approve
or reject the pending request right from the dashboard -- no need
to resume the full session.
```

## Step 3 -- Managing background sessions

Explain:
```
Background sessions need management -- resuming, stopping, and
recovering after system restarts.

Resume a session:
  claude resume                  -- resume picker UI (interactive list)
  claude resume SESSION_ID       -- resume a specific session
  /resume                        -- from inside Claude Code

  The resume picker shows all sessions and lets you select one.
  This is the easiest way when you have multiple sessions.

Stop a session:
  claude sessions stop SESSION_ID    -- stop a specific session
  claude sessions stop --all         -- stop all sessions

  Stopped sessions can be respawned (see below).

Respawn after sleep/shutdown:
  claude respawn --all

  When your machine sleeps or shuts down, background sessions stop.
  The respawn command restarts them from where they left off. This
  is useful when you start your workday -- respawn everything and
  check agent view.

Session lifecycle:
  Started  -->  Working  -->  Completed
                  |               |
                  v               v
            Needs input       (done)
                  |
                  v
              Stopped  -->  Respawned  -->  Working
                                              |
                                              v
                                          Completed
```

Tell the user:
```
If you still have the background session from Step 1 running,
try resuming it:

  ! claude resume

Select the session from the picker. You'll see its output and can
interact with it. Type /bg to send it back to the background, or
let it finish.
```

Verify:
```bash
# Show session status
claude sessions list 2>/dev/null && echo "" && echo "Session management commands working." || echo "Sessions command not available -- check Claude Code version"
```

## Step 4 -- Goal mode

Explain:
```
Goal mode tells Claude to keep working until a condition is met.
Instead of a single prompt-response turn, Claude evaluates after
each action whether the goal has been achieved.

Start goal mode:
  /goal "all tests pass"

  This sets a goal condition. After every tool call, an evaluator
  checks whether the condition is satisfied. The evaluator uses
  Haiku by default (fast and cheap) to assess the goal state.

How goal evaluation works:
  1. Claude performs an action (edit, run tests, etc.)
  2. The evaluator checks: "Is the goal met?"
  3. If no  --> Claude plans and takes the next action
  4. If yes --> Claude stops and reports success

Goal mode works in three contexts:
  Interactive:     /goal "condition" in a live session
  Headless:        claude -p "fix X" --goal "all tests pass"
  Background:      claude --bg --goal "condition" "prompt"

Safety limits:
  --max-turns N         -- stop after N turns (default: no limit)
  --max-time-minutes N  -- stop after N minutes
  /goal clear           -- cancel the current goal

The evaluator is conservative. It checks tool output and
conversation state, not just whether Claude says the goal is met.
This prevents false positives where Claude claims success but
the tests still fail.
```

Tell the user:
```
Try goal mode in your current session:

  /goal "I have listed three benefits of background sessions"

Now ask Claude about background sessions. The goal evaluator will
check after each response whether you've received three clear
benefits. Once it determines the goal is met, it will notify you.

After trying it, clear the goal:

  /goal clear
```

Explain after the exercise:
```
Goal mode is most powerful in headless and background contexts.
Example use cases:

  Fix failing tests:
    claude -p "fix the failing tests" --goal "all tests pass"

  Refactor until clean:
    claude -p "refactor auth module" --goal "no lint warnings"

  Complete a feature:
    claude -p "implement user search" --goal "search works and has tests"

The key insight: goal mode shifts Claude from "answer this question"
to "achieve this outcome." It will try multiple approaches, debug
failures, and iterate until the condition is met or limits are reached.
```

## Step 5 -- Loop mode

Explain:
```
Loop mode repeats a task on a fixed interval. It is useful for
monitoring and polling workflows.

Start a loop:
  /loop 5m "check deploy status and report any errors"
  /loop 10m "run the test suite and summarize results"
  /loop 1h "check for new Jira issues assigned to me"

Format: /loop INTERVAL "prompt"
  Interval: Nm (minutes) or Nh (hours)
  Default interval: 10 minutes (if you omit the time)

Loop characteristics:
  - Session-scoped: dies when the session closes
  - Maximum 50 active loop tasks per session
  - 7-day expiry: loops automatically stop after 7 days
  - Each iteration runs the prompt as a fresh task
  - Results accumulate in the session history

Good use cases for loops:
  Deploy monitoring:     /loop 5m "check pod status in staging"
  Test watching:         /loop 10m "run tests and flag new failures"
  Service health:        /loop 15m "curl health endpoints and report"
  PR status:             /loop 30m "check CI status on open PRs"

Stop a loop:
  /loop stop             -- stop all loops in this session
  /loop stop LOOP_ID     -- stop a specific loop
  /loop list             -- show active loops

Loops are intentionally simple -- they repeat a prompt on a timer.
For more complex automation, combine goal mode with background
sessions instead.
```

Tell the user:
```
Loop mode is best experienced with a real monitoring scenario.
Here's a safe example you can try:

  /loop 1m "list the 3 most recently modified files in this repo"

Watch it run once, then stop it:

  /loop stop

In practice, you'd use longer intervals (5-30 minutes) and more
meaningful prompts. The 1-minute interval is just for demonstration.
```

## Step 6 -- Composing patterns

Explain:
```
The real power comes from composing these features together.
Each feature solves one problem; combined, they enable fully
autonomous workflows.

Pattern 1: Background + Goal
  Run a task in the background that keeps working until done.

    claude --bg --goal "all tests pass" "fix the failing integration tests"

  This starts a background session with a goal. Claude will edit code,
  run tests, see failures, fix them, and repeat until all tests pass.
  Meanwhile, you keep working in your terminal.

Pattern 2: Worktree + Background
  Isolate work in a separate branch while keeping your main workspace clean.

    claude --worktree --bg "refactor the auth module to use JWT"

  This creates a git worktree (isolated branch + working directory),
  then runs the task in the background. Your current branch is untouched.

Pattern 3: Worktree + Background + Goal (full autonomy)
  The complete pattern for autonomous feature work.

    claude --worktree --bg --goal "all tests pass" \
      "fix the failing integration tests"

  This:
    1. Creates a worktree with a new branch
    2. Starts a background session in that worktree
    3. Works autonomously until all tests pass
    4. You monitor progress in agent view

  When it completes, you review the changes in the worktree,
  merge if satisfied, or give further instructions.

Pattern 4: Multiple autonomous agents
  Start several background+goal sessions for independent tasks.

    claude --worktree --bg --goal "lint passes" "fix lint warnings in src/"
    claude --worktree --bg --goal "tests pass" "add missing test coverage"
    claude --worktree --bg --goal "no TODOs remain" "resolve all TODO comments"

  Each runs in its own worktree on its own branch. Monitor all of
  them in agent view. Merge the results independently.

When to use which pattern:
  Quick task, stay in terminal    -->  claude --bg "prompt"
  Long task, need outcome         -->  claude --bg --goal "X" "prompt"
  Risky changes, want isolation   -->  claude --worktree --bg "prompt"
  Full autonomy                   -->  claude --worktree --bg --goal "X" "prompt"
  Recurring check                 -->  /loop Nm "prompt"
```

Tell the user:
```
The composed patterns are best understood by trying one. Here's a
safe example that demonstrates worktree + background + goal:

  ! claude --worktree --bg --goal "report is complete" \
      "analyze the modules/ directory and write a summary of what each module covers"

Then check on it:

  ! claude agents

When it completes, you'll have a summary in a worktree branch.
You can review it, keep it, or discard it.
```

## Verification

Run all checks and report:

```bash
PASS=0
TOTAL=3

# 1. Claude Code installed
command -v claude &>/dev/null && { echo "PASS: Claude Code installed"; PASS=$((PASS+1)); } || echo "FAIL: Claude Code not installed"

# 2. Version supports background/goal features
if command -v claude &>/dev/null; then
  VERSION=$(claude --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
  if [ -n "$VERSION" ]; then
    MAJOR=$(echo "$VERSION" | cut -d. -f1)
    MINOR=$(echo "$VERSION" | cut -d. -f2)
    PATCH=$(echo "$VERSION" | cut -d. -f3)
    if [ "$MAJOR" -gt 2 ] 2>/dev/null || \
       ([ "$MAJOR" -eq 2 ] && [ "$MINOR" -gt 1 ] 2>/dev/null) || \
       ([ "$MAJOR" -eq 2 ] && [ "$MINOR" -eq 1 ] && [ "$PATCH" -ge 139 ] 2>/dev/null); then
      echo "PASS: Version $VERSION supports agent view and goal mode"
      PASS=$((PASS+1))
    else
      echo "FAIL: Version $VERSION too old -- need v2.1.139+"
    fi
  else
    echo "PASS: Claude Code installed (version assumed current)"
    PASS=$((PASS+1))
  fi
fi

# 3. Background session support working
if command -v claude &>/dev/null; then
  claude sessions list &>/dev/null && { echo "PASS: Background session support confirmed"; PASS=$((PASS+1)); } || echo "FAIL: Background session support not available"
fi

echo ""
echo "$PASS/$TOTAL checks passed."
```

If all pass:
```
All checks passed. Background agents, agent view, goal mode, and loop mode
are available and working.
```

If any fail, tell the user which step to revisit or to update Claude Code.

## Challenge

```
Start a background agent that reviews the current repository for code
quality issues. Ask it to find:
  - Functions or code blocks over 50 lines
  - Unused imports or variables
  - Missing error handling

Monitor it in agent view. When it completes, retrieve and summarize
the results.

Tell me:
  1. How you started the background session (the exact command)
  2. What agent view showed (session state, time elapsed)
  3. The key findings from the review
```

## Challenge Verification

The user should report:
1. A command like `claude --bg "review..."` or similar
2. What they observed in `claude agents` (state transitions, session info)
3. A summary of code quality findings from the review

Verify the user understood the concepts by checking their report covers:
- They used `claude --bg` or `/bg` to start a background session
- They used `claude agents` to monitor progress
- They retrieved results (via resume or agent view)

If the user's report demonstrates understanding of background sessions,
agent view, and retrieving results, the challenge passes.

Write the completion marker:

```bash
date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/23.done
```

Then print:
```
Module 23 complete.

You can now run Claude Code tasks in the background and monitor them.
Key concepts:
  - Background sessions: claude --bg "prompt" to start, /bg to detach
  - Agent view: claude agents for a full-screen session dashboard
  - Session management: resume, stop, respawn --all after restarts
  - Goal mode: /goal "condition" for outcome-driven autonomy
  - Loop mode: /loop Nm "prompt" for recurring tasks
  - Composing: worktree + background + goal for fully autonomous work

When to use each:
  Quick async task           -->  claude --bg "prompt"
  Monitor multiple sessions  -->  claude agents
  Outcome-driven work        -->  --goal "condition"
  Recurring monitoring       -->  /loop 5m "prompt"
  Full autonomy              -->  --worktree --bg --goal "X" "prompt"

Next module: /learn-24-security-first-development

Questions or feedback? https://github.com/rhpds/claude-code-courseware/issues
```
