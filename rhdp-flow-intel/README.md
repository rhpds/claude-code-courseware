# rhdp-flow-intel

MCP server for RHDP-Flow deployment intelligence -- monitor, detect, diagnose.

## Tools

| Tool | Description |
|------|-------------|
| `flow_deployment_monitor` | Real-time deployment status with progress tracking |
| `flow_ghost_detector` | Find stuck/ghost workshops and generate cleanup commands |
| `flow_deployment_diff` | Compare deployment snapshots to track changes |
| `flow_event_dashboard` | Aggregate health report across deployments, QA, and pools |
| `flow_troubleshoot` | Match workshop symptoms to known failure patterns |

## Install

```bash
pip install -e rhdp-flow-intel
```

## Configure

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "rhdp-flow-intel": {
      "type": "stdio",
      "command": "python3",
      "args": ["-m", "rhdp_flow_intel"],
      "env": {
        "FLOW_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

## Run

```bash
python3 -m rhdp_flow_intel
```
