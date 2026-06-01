---
name: 29-effort-reasoning-control
description: "Learn to control how hard Claude thinks per task using effort levels — a direct cost, latency, and quality lever that is separate from which model you"
---

# Effort and Reasoning Control

Estimated time: 10 minutes
Prerequisites: Module 01 (Claude Code installed and working). Module 15 (Cost and Context) recommended.

Learn to control how hard Claude thinks per task using effort levels — a direct cost, latency, and quality lever that is separate from which model you run.

## Orientation

Print this once at the start:

```
You're learning effort and reasoning control.
This takes about 10 minutes.

We'll cover:
  1. What "effort" is — adaptive reasoning as a cost/latency lever
  2. What you actually have on Vertex AI (Opus 4.6 / Sonnet 4.5)
  3. The six ways to set effort
  4. ultrathink vs ultracode — what works on 4.6
  5. Using effort to control cost (ties into Module 15)
  6. The Vertex "effort options missing" gotcha

You'll need:
  - Claude Code installed and working (Module 01)
```

## Progress Tracking

On module start, write a progress marker:

```bash
mkdir -p ~/.claude/courseware-progress && date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/29.started
```

## Preflight

Audit current state before doing anything.

```bash
# Check 1 — Claude Code installed?
command -v claude &>/dev/null && echo "EXISTS: Claude Code $(claude --version 2>/dev/null)" || echo "MISSING: Claude Code — run /learn-01-vertex-setup first"

# Check 2 — Is a model pinned for Vertex? (affects which model and effort you get)
if [ -n "$ANTHROPIC_DEFAULT_OPUS_MODEL" ] || [ -n "$ANTHROPIC_DEFAULT_SONNET_MODEL" ]; then
  echo "EXISTS: model pinning — opus=${ANTHROPIC_DEFAULT_OPUS_MODEL:-<alias>} sonnet=${ANTHROPIC_DEFAULT_SONNET_MODEL:-<alias>}"
else
  echo "INFO: no ANTHROPIC_DEFAULT_*_MODEL pin — aliases resolve to provider defaults (Vertex: opus=Opus 4.6, sonnet=Sonnet 4.5)"
fi

# Check 3 — Is an effort level already configured?
EFFORT_ENV="${CLAUDE_CODE_EFFORT_LEVEL:-}"
EFFORT_SETTING=""
if [ -f "$HOME/.claude/settings.json" ]; then
  EFFORT_SETTING=$(python3 -c "import json,os; print(json.load(open(os.path.expanduser('~/.claude/settings.json'))).get('effortLevel',''))" 2>/dev/null)
fi
if [ -n "$EFFORT_ENV" ]; then
  echo "EXISTS: effort set via env CLAUDE_CODE_EFFORT_LEVEL=$EFFORT_ENV (highest precedence)"
elif [ -n "$EFFORT_SETTING" ]; then
  echo "EXISTS: effortLevel=\"$EFFORT_SETTING\" in settings.json"
else
  echo "INFO: no effort override — running at the model default (high on Opus 4.6 / Sonnet 4.6)"
fi
```

Print a summary of what was found.

## Step 1 — What "effort" actually is

Tell the user:
```
Effort controls ADAPTIVE REASONING: how much Claude thinks before and
between steps, decided per step based on task complexity. It is NOT the
same as choosing a model.

  Model choice  = WHICH brain answers (Opus vs Sonnet vs Haiku)
  Effort level  = HOW HARD that brain thinks on each step

Lower effort  -> faster, cheaper, less thinking. Good for routine work.
Higher effort -> deeper reasoning, more tokens, slower. Good for hard problems.

You are charged for thinking tokens even when the thinking is collapsed
and hidden. So effort is a real, direct cost lever — not just a quality knob.
```

## Step 2 — What you actually have on Vertex AI

This is the part the generic docs get wrong for our team. Tell the user:
```
Red Hat runs Claude Code through Google Vertex AI. On Vertex, the model
aliases resolve differently than on the Anthropic API:

  Alias      Resolves to (on Vertex)
  opus    -> Opus 4.6
  sonnet  -> Sonnet 4.5
  Default -> Sonnet 4.5   (the "Default" picker option is NOT Opus here)

Effort levels are PER MODEL. What you get:

  Model                     Effort levels available
  Opus 4.6 / Sonnet 4.6     low, medium, high (default), max
  Opus 4.8 / Opus 4.7       low, medium, high, xhigh, max   (NOT on Vertex by default)

Key consequence for us: there is NO xhigh on Opus 4.6. If you set xhigh,
Claude Code silently falls back to the highest supported level at or below
it — so xhigh runs as high. No error, it just quietly clamps.

The default effort on Opus 4.6 and Sonnet 4.6 is "high".
```

Note for the user:
```
If you want Opus 4.7/4.8 (with xhigh) on Vertex, an admin must pin the
newer model with ANTHROPIC_DEFAULT_OPUS_MODEL=claude-opus-4-8 (and the
account must have access). That's a deployment decision, not a per-session
toggle. This module assumes the default Vertex resolution (Opus 4.6).
```

## Step 3 — The six ways to set effort

Tell the user:
```
You can set effort through any of these. Precedence runs top to bottom
(env var wins over everything, then your configured level, then the
model default):

  1. CLAUDE_CODE_EFFORT_LEVEL env var   — highest precedence; level name or "auto"
  2. --effort <level>                    — single launched session
  3. /effort                             — interactive slider; or /effort high;
                                           or /effort auto to reset to model default
  4. /model                              — left/right arrows move the effort slider
  5. effortLevel in settings.json        — low | medium | high | xhigh ONLY
                                           (max and ultracode are session-only,
                                            not accepted here)
  6. effort: in skill / subagent frontmatter
                                         — overrides the session level whenever
                                           that skill or subagent runs

The level persists for low/medium/high/xhigh. "max" is session-only (except
via the env var). The active level is shown next to the spinner, e.g.
"with low effort", so you can confirm it without opening /model.
```

Show the user the highest-leverage pattern — per-skill effort:
```
For a repetitive, mechanical skill (formatting, parsing, renaming), set
low effort in its frontmatter so it never burns deep-reasoning tokens:

  ---
  name: reformat-json
  description: Reformat and sort JSON files
  effort: low
  ---

This is the cleanest cost win: the skill runs cheap every time, while your
main session stays at high effort for the work that needs it.
```

Have the user run `/effort` (no arguments) to open the slider and observe the available levels for their current model. On Vertex/Opus 4.6 they should see low/medium/high/max and NOT xhigh.

## Step 4 — ultrathink vs ultracode

Tell the user:
```
Two extras often confused with effort levels:

  ultrathink  — a KEYWORD you put anywhere in a prompt. It asks for deeper
                reasoning on that one turn without changing your session
                effort. It's a prompt-level instruction, so it works on any
                model, including Opus 4.6. Use it for a single hard message.

                (Note: "think", "think hard", "think more" are NOT special —
                 only "ultrathink" is recognized.)

  ultracode   — a Claude Code SETTING (not a model effort level) offered in
                the /effort menu. It sends xhigh to the model AND has Claude
                plan a dynamic workflow for substantive tasks. Session-only.

                On Vertex/Opus 4.6 the xhigh part degrades to high (see Step 2),
                so you keep the workflow-orchestration behavior but NOT the
                deeper xhigh reasoning. Worth knowing before you reach for it.
```

## Step 5 — Effort as a cost lever (with Module 15)

Tell the user:
```
Module 15 covered model routing and session discipline. Effort is the third
cost lever, applied WITHIN a model:

  low      Short, scoped, latency-sensitive work that isn't intelligence-
           sensitive. Bulk/mechanical steps. Cheapest.
  medium   Cost-sensitive work that can trade a little intelligence.
  high     Default. Balances tokens and intelligence. Leave it here for
           most coding.
  max      Demanding problems only. Can overthink and show diminishing
           returns. Session-only. Test before adopting broadly.

Practical routing for our team on Vertex:
  - Keep the main session at high (the default).
  - Drop repetitive skills/subagents to low via frontmatter.
  - Use ultrathink on the occasional hard message instead of raising the
    whole session to max.
  - Reserve max for a genuinely stuck debugging or design problem, then
    drop back down.
```

## Step 6 — The Vertex "effort options missing" gotcha

Tell the user:
```
Claude Code decides whether a model supports effort by pattern-matching the
model ID. Standard Vertex version names like "claude-opus-4-6" match fine.
But if an admin pins a CUSTOM or non-standard model ID, the pattern may not
match — and then /effort shows nothing and the slider disappears.

Fix (set by whoever pins the model), declaring capabilities explicitly:

  export ANTHROPIC_DEFAULT_OPUS_MODEL_SUPPORTED_CAPABILITIES=\
    'effort,max_effort,thinking,adaptive_thinking,interleaved_thinking'

Note: do NOT include xhigh_effort for Opus 4.6 — it doesn't support xhigh.

Separately, on Opus 4.6 / Sonnet 4.6 you can revert to the OLD fixed
thinking budget (pre-adaptive-reasoning) if you ever need it:

  export CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1
  export MAX_THINKING_TOKENS=10000   # then control thinking by token budget

Most people should leave adaptive reasoning on and just use effort levels.
```

## Verification

Ask the user these questions:
```
Let's verify understanding:

1. On Vertex, you type /model and pick "opus". Which model and which
   effort levels do you get?

2. You set effortLevel "xhigh" in settings.json while on Opus 4.6.
   What actually happens?

3. You have a skill that renames files in bulk. How do you make it cheap
   without changing your whole session?

4. You hit one genuinely hard bug mid-session and want deeper reasoning
   for just that message. What's the lightest-weight way to get it?
```

Expected answers:
1. Opus 4.6, with effort levels low / medium / high (default) / max — no xhigh.
2. It silently runs as high (xhigh clamps to the highest supported level <= xhigh on 4.6). No error.
3. Add `effort: low` to the skill's frontmatter — it overrides the session level only when that skill runs.
4. Put the keyword `ultrathink` in that one prompt (no session/effort change needed).

Accept reasonable variations.

If successful, print:
```
All checks passed. You understand effort and reasoning control.
```

## Challenge

```
Apply effort control to real work:

1. Run /effort with no arguments. Read the slider — confirm which model
   you're on and which levels are offered. Note the effort indicator next
   to the spinner (e.g. "with high effort").

2. Pick a mechanical, repetitive task you actually do (reformatting,
   parsing logs, renaming, generating a boilerplate RHDPOPS Jira summary)
   and write a tiny skill or subagent with `effort: low` in its frontmatter.

3. Identify one place in your normal workflow where you've been running
   high effort but low would do — somewhere you could cut cost.

Tell me:
  1. Active model + effort levels offered (confirms Vertex resolution)
  2. The skill/subagent you set to low effort (paste the frontmatter)
  3. The one place you'd lower effort to save cost, and why
```

## Challenge Verification

Confirm the user reports:
- The active model resolves correctly on Vertex (Opus 4.6 if they picked opus, with low/medium/high/max and no xhigh; or Sonnet 4.5 on Default).
- A valid `effort: low` frontmatter block on a genuinely mechanical task.
- A sensible cost-reduction call (mechanical/latency-sensitive work moved to low, main session left at high).

Accept reasonable answers. The key insight: effort is a per-task cost lever applied within a model, and the team's Vertex models cap at `max` (no `xhigh`).

If successful, write the completion marker:

```bash
date -u +%Y-%m-%dT%H:%M:%SZ > ~/.claude/courseware-progress/29.done
```

Then print:
```
Module 29 complete.

You now understand effort and reasoning control.
Key takeaways:
  - Effort = how hard the model thinks per step; separate from model choice
  - On Vertex: opus -> Opus 4.6, sonnet -> Sonnet 4.5, Default -> Sonnet 4.5
  - Opus 4.6 effort: low / medium / high (default) / max — NO xhigh
  - xhigh silently clamps to high on 4.6; ultracode's xhigh degrades too
  - Set effort: env var > --effort > /effort > /model slider > settings > frontmatter
  - Per-skill `effort: low` frontmatter is the cleanest repeatable cost win
  - ultrathink keyword = one-off deep reasoning, works on any model
  - If /effort shows nothing on a pinned model, set _SUPPORTED_CAPABILITIES

Next module: back to /courseware for the catalog

Questions or feedback? https://github.com/rhpds/claude-code-courseware/issues
```

<!-- NEW -->
