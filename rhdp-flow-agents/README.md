# rhdp-flow-agents

Claude Code agents plugin for RHDP-Flow workshop review and auditing. Provides analytical agents that examine and report on workshop deployments.

## Requirements

- `rhdp-flow-mcp` must be installed and configured

## Agents

| Agent | Trigger | Description |
|-------|---------|-------------|
| `flow-csv-validator` | "validate this CSV" | Reviews CSV files against the Flow spec before upload |
| `flow-deployment-auditor` | "audit deployments" | Analyzes deployment health, resource issues, and anomalies |
| `flow-pre-event-checklist` | "pre-event check" | Go/no-go readiness audit before workshop events |

## Agent vs Skill distinction

Agents are analytical -- they examine data and report findings. Skills are procedural -- they guide you through workflows. The `flow-csv-validator` agent can be called by the `flow-deploy` skill as a pre-flight step, or invoked standalone.

## Install

Copy or symlink the `agents/` directory into your Claude Code project, or install via the plugin manager.
