# Module 15 — Cost and Context Management

Estimated time: 15 minutes
Prerequisites: Module 01 (Claude Code installed and working)

Learn to manage session costs, context window usage, and model routing to get the most value from Claude Code.

## Orientation

Print this once at the start:

```
You're learning cost and context management.
This takes about 15 minutes.

We'll cover:
  1. Understanding session costs and the /cost command
  2. Context window — what fills it and how to manage it
  3. Model routing — when to use which model
  4. Session discipline patterns

You'll need:
  - Claude Code installed and working (Module 01)
```

## Preflight

```bash
# Check 1 — Claude Code installed?
command -v claude &>/dev/null && echo "EXISTS: Claude Code" || echo "MISSING: Claude Code — run /learn-01-vertex-setup first"

# Check 2 — Check current CLAUDE.md for cost-related instructions
if [ -f "CLAUDE.md" ]; then
  if grep -qi "cost\|budget\|context\|compact\|model" CLAUDE.md 2>/dev/null; then
    echo "EXISTS: CLAUDE.md mentions cost/context topics"
  else
    echo "INFO: CLAUDE.md exists but doesn't cover cost management"
  fi
else
  echo "INFO: No CLAUDE.md in current directory"
fi

# Check 3 — Check for subagent/model routing in settings
if [ -f "$HOME/.claude/settings.json" ]; then
  echo "EXISTS: Settings file present"
else
  echo "INFO: No global settings file"
fi
```

Print a summary.

## Step 1 — Understanding Session Costs

Tell the user:
```
Every message in Claude Code sends your full conversation context
to the model. The cost depends on:

  Input tokens  — everything Claude reads (your messages, tool results,
                  system prompt, CLAUDE.md, MCP server data)
  Output tokens — everything Claude writes back (responses, tool calls)

The /cost command shows your current session's token usage and cost.
Let's check it now.
```

Ask the user to type `/cost` or show them the current session metrics. Explain:
```
Key numbers to watch:
  - Total cost: cumulative for this session
  - Context size: how much of the window is used
  - Cache hit rate: higher is better (repeated content is cheaper)

Cost scales with context size. A session that starts at $0.01
per message can grow to $0.10+ per message as context fills up.
The most effective cost control is keeping sessions short and focused.
```

## Step 2 — Context Window Management

Tell the user:
```
The context window is finite. Everything loads into it:

  ALWAYS LOADED (every message):
    - System prompt
    - CLAUDE.md files (workspace + project)
    - Memory files loaded by auto-memory
    - Your conversation history (messages + tool results)
    - MCP server descriptions

  LOADED ON DEMAND:
    - File contents (Read tool results)
    - Command output (Bash tool results)
    - Search results
    - Subagent results

When the window fills up, Claude Code compresses older messages.
This is why Claude "forgets" things from early in a session.

Management tools:
  /compact     — manually compress context (keeps a summary)
  /clear       — wipe context and start fresh (same session)
  /cost        — check current usage
  New session  — exit and relaunch (cleanest reset)
```

Demonstrate the impact:
```bash
# Show what's in the always-loaded context
echo "=== Context contributors ==="

# CLAUDE.md files
WORKSPACE_CLAUDE=$(find ../.. -maxdepth 1 -name "CLAUDE.md" 2>/dev/null | head -1)
if [ -n "$WORKSPACE_CLAUDE" ]; then
  WC_SIZE=$(wc -c < "$WORKSPACE_CLAUDE" 2>/dev/null | tr -d ' ')
  echo "Workspace CLAUDE.md: ${WC_SIZE} bytes"
fi

if [ -f "CLAUDE.md" ]; then
  PC_SIZE=$(wc -c < "CLAUDE.md" | tr -d ' ')
  echo "Project CLAUDE.md: ${PC_SIZE} bytes"
fi

# Memory files
MEM_DIR="$HOME/.claude/projects/$(pwd | sed 's|/|-|g' | sed 's|^-||')/memory"
if [ -d "$MEM_DIR" ]; then
  MEM_SIZE=$(du -sh "$MEM_DIR" 2>/dev/null | cut -f1)
  MEM_COUNT=$(ls "$MEM_DIR"/*.md 2>/dev/null | wc -l | tr -d ' ')
  echo "Memory files: $MEM_COUNT files ($MEM_SIZE)"
fi

# Skills
SKILL_COUNT=$(find "$HOME/.claude/skills" -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')
echo "Global skills: $SKILL_COUNT"

echo ""
echo "All of these load into EVERY message. Keep them lean."
```

## Step 3 — Model Routing

Tell the user:
```
Claude Code can route to different models for different tasks.
This is a powerful cost lever:

  Opus    — most capable, most expensive
            Use for: planning, debugging, architecture, complex reasoning
            Cost: highest per token

  Sonnet  — balanced capability and cost
            Use for: code review, search, analysis, moderate tasks

  Haiku   — fastest, cheapest
            Use for: formatting, parsing, simple extraction, mechanical tasks

Routing strategies:

  1. MANUAL: Use /model to switch mid-session
     Good for: switching from planning (Opus) to execution (Sonnet)

  2. SKILLS: Set model: haiku in skill frontmatter
     Good for: repetitive skills that don't need full reasoning

  3. SUBAGENTS: Dispatch subagents with model selection
     Good for: isolating expensive work from cheap work

  4. FAST MODE: Toggle /fast for faster output on the same model
     Good for: when you need speed, not a model change
```

## Step 4 — Session Discipline Patterns

Tell the user:
```
Patterns that keep costs down and quality up:

  ONE TASK PER SESSION
    Start a session, do one thing, exit. Context stays small,
    costs stay low, Claude doesn't get confused.

  FRONT-LOAD CONTEXT
    Put critical info in CLAUDE.md, not in conversation.
    It loads every time without growing the context.

  USE SUBAGENTS FOR RESEARCH
    Research fills context fast. Dispatch an agent for research,
    get back a summary. The full search results stay in the
    subagent's context, not yours.

  COMPACT EARLY
    Don't wait for context to fill. /compact after completing
    a major step, before starting the next one.

  EXIT AND RESTART
    The cheapest message is the first one in a new session.
    Don't be afraid to start fresh.

  WRITE IT DOWN
    Plans, findings, decisions — write to files, not conversation.
    Files survive context compression and session restarts.
```

## Verification

Ask the user:
```
Let's verify understanding. Answer these:

1. What's the single most effective way to reduce session costs?

2. You're 30 minutes into a session and /cost shows $3.50.
   The next message will send all that context again.
   What should you do before continuing?

3. You have a skill that reformats JSON files.
   What model should it use and why?
```

Expected answers:
1. Keep sessions short and focused (one task per session, or restart between tasks).
2. Use /compact to compress context, or start a new session if the current task is done.
3. Haiku — it's a mechanical task (formatting) that doesn't need reasoning.

Accept reasonable variations.

If successful, print:
```
All checks passed. You understand cost and context management.
```

## Challenge

```
Audit your current session and make one improvement:

1. Check /cost for this session
2. Count how many CLAUDE.md files load into your context
   (workspace + project + any parent directories)
3. Identify the single largest context contributor
4. Make one change to reduce your per-message context size
   (trim a CLAUDE.md, remove an unused skill, compact, etc.)

Tell me:
  1. Your session cost so far
  2. Number of CLAUDE.md files loading
  3. Biggest context contributor
  4. What change you made
```

## Challenge Verification

Any reasonable answers pass. The key insight is that context size drives cost, and managing it is an active practice.

If successful, print:
```
Module 15 complete.

You now understand cost and context management.
Key takeaways:
  - Every message sends full context — cost grows with conversation
  - /cost, /compact, /clear are your management tools
  - Model routing (Opus/Sonnet/Haiku) is a direct cost lever
  - CLAUDE.md loads every message — keep it lean and relevant
  - Subagents isolate expensive research from your main context
  - One task per session is the simplest cost discipline

Cost reduction checklist:
  [ ] Session cost target: under $5 for most tasks
  [ ] /compact after major steps
  [ ] Subagents for research-heavy work
  [ ] Haiku for mechanical skills
  [ ] CLAUDE.md under 500 lines
  [ ] Exit and restart between unrelated tasks

Next module: /learn-16-multi-repo-workspaces
```
