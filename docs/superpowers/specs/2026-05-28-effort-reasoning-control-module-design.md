# Module 29 — Effort & Reasoning Control (design)

Date: 2026-05-28
Status: approved for build (standalone module)

## Problem

The courseware (28 modules) is current overall, but a feature audit against the
live Claude Code docs found **zero coverage of effort levels / adaptive
reasoning** — now the primary reasoning control on current Claude models and a
direct cost/latency lever. The team runs Claude Code through Google Vertex AI,
where `opus` resolves to **Opus 4.6** and `sonnet` to **Sonnet 4.5**. Generic
docs would teach `xhigh`/`ultracode` the team cannot fully use, so the module is
scoped to the Vertex/4.6 reality.

## Vertex / 4.6 facts the module must get right

- On Vertex: `opus` → Opus 4.6, `sonnet` → Sonnet 4.5. The picker's *Default*
  option resolves to **Sonnet 4.5**, not Opus.
- Opus 4.6 effort levels: `low`, `medium`, `high` (default), `max`. **No `xhigh`.**
  Setting `xhigh` silently runs as `high` (fallback to highest supported ≤ requested).
- `ultracode` sends `xhigh` (→ `high` on 4.6) plus dynamic workflow orchestration;
  session-only. Partially useful — be honest about the degrade.
- `ultrathink` keyword works (prompt-level instruction, model-agnostic, one-off).
- Setting effort: `/effort` (slider / name / `auto`), `/model` arrow slider,
  `--effort` flag, `CLAUDE_CODE_EFFORT_LEVEL` env (precedence over all),
  `effortLevel` in settings (low/medium/high/xhigh only — not `max`/`ultracode`),
  skill/subagent `effort` frontmatter.
- Vertex gotcha: a pinned/custom model ID may not pattern-match, leaving effort
  disabled. Fix with `ANTHROPIC_DEFAULT_OPUS_MODEL_SUPPORTED_CAPABILITIES`
  (e.g. `effort,max_effort,thinking,adaptive_thinking,interleaved_thinking` —
  no `xhigh_effort` for 4.6).
- Opus 4.6/Sonnet 4.6 can revert to fixed thinking budget with
  `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` (+ `MAX_THINKING_TOKENS`).

## Module structure

Standard courseware structure (Orientation → Progress marker → Preflight →
Steps → Verification → Challenge → Challenge Verification).

1. What effort is — adaptive reasoning; cost/latency/quality lever distinct from model.
2. What you have on Vertex — 4.6 levels, no xhigh, default high, Default=Sonnet 4.5.
3. Setting effort — the six methods above; emphasize per-skill/subagent frontmatter.
4. ultrathink vs ultracode — works/partial, with honest caveats.
5. Effort as a cost lever — ties to Module 15 (low for mechanical, high default, max sparingly).
6. Vertex gotcha — `_SUPPORTED_CAPABILITIES` when `/effort` shows nothing.

Challenge: run `/effort`, confirm active model + effort from the "with X effort"
indicator, set a `low`-effort skill/subagent frontmatter for a mechanical
RHDPOPS task, report where they'd lower effort to cut cost.

## Metadata

- Number: 29. Files: `modules/29-effort-reasoning-control.md`,
  `.claude/commands/learn-29-effort-reasoning-control.md`.
- Catalog: Section 7 (Workflow & Operations), ~10 min, prereq 01 (15 recommended),
  tagged NEW via `<!-- NEW -->`.
- Wiring: catalog list + routing table + expanded-section entry in
  `courseware.md`; README count sync; `python3 scripts/validate.py` green.

## Out of scope

MCP tool-search and slash-command-fundamentals modules (other audit gaps) — not
built in this pass.
