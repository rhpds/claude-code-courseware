# Lola Marketplace

This document describes the self-hosted Lola marketplace for the courseware and how consumers install from it.

## What is a Lola marketplace?

A Lola marketplace is a YAML file hosted at a URL that lists available modules. Consumers add the marketplace to their Lola config, then install modules from it. The marketplace points at git repositories containing the module source.

## This repo's marketplace

The file `courseware-market.yml` at the repo root is the marketplace definition:

```yaml
name: RHDP Courseware
description: Learning modules for the RHDP operations team, delivered as Lola skills.
version: "1.0"
modules:
  - name: ccc
    description: Claude Code courseware -- 29 hands-on modules covering Vertex AI, MCP servers, skills, agents, security, and operations.
    version: "1.0.0"
    repository: https://github.com/rhpds/claude-code-courseware.git
    tags: [claude-code, courseware, rhdp, learning]
```

## Consumer setup

### 1. Add the marketplace

```bash
lola market add rhdp-courseware \
  https://raw.githubusercontent.com/rhpds/claude-code-courseware/feat/lola-packaging/courseware-market.yml
```

Once the branch merges to `main` or a release tag exists, update the URL:

```bash
lola market add rhdp-courseware \
  https://raw.githubusercontent.com/rhpds/claude-code-courseware/main/courseware-market.yml
```

### 2. Install the module

```bash
lola install ccc -a claude-code
```

This registers all 30 skills and 34 commands with Claude Code, prefixed with `ccc-`.

### 3. Update

```bash
lola update
```

## Access control: private now, public later

Access to the marketplace is controlled by repository visibility:

- **Private repo** (current): Only users with GitHub access to `rhpds/claude-code-courseware` can fetch the marketplace YAML and clone the module. This is the access gate -- no separate auth needed.
- **Public later**: When the repo goes public, anyone can add the marketplace and install the module. No changes to the marketplace file are needed.

There is no submission to an "official" Lola marketplace registry. This is a self-hosted marketplace pointed at by URL. The team controls it, the team distributes the URL.

## This is NOT rhdp-skills-marketplace

The `rhdp-skills-marketplace` is the Claude Code **plugin** marketplace -- a separate system that distributes Claude Code plugins via `claude plugin add`. Lola is a different, parallel distribution mechanism that works across multiple AI coding assistants (Claude Code, Copilot, Gemini, etc.).

| | rhdp-skills-marketplace | Lola marketplace |
|---|---|---|
| What it distributes | Claude Code plugins | Lola modules (skills + commands) |
| Install command | `claude plugin add github:rhpds/...` | `lola install ccc -a claude-code` |
| Scope | Claude Code only | Multi-assistant |
| Registry | `rhpds/rhdp-skills-marketplace` repo | `courseware-market.yml` in this repo |

Both can coexist. A team member who has the courseware installed as a Claude Code plugin does not need to also install it via Lola (and vice versa).
