# rhdp-flow-mcp

MCP server that wraps the RHDP-Flow REST API into 15 tools for workshop deployment automation.

## Setup

```bash
pip install -e ".[dev]"
```

Set the Flow API URL (defaults to `http://localhost:8000`):

```bash
export FLOW_API_URL=https://flow.example.com
```

### Claude Code configuration

Add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "rhdp-flow": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "rhdp_flow_mcp"],
      "env": {
        "FLOW_API_URL": "https://flow.example.com"
      }
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `flow_health` | Check Flow backend and cluster connectivity |
| `flow_catalog_items` | List available catalog items with parameters and limits |
| `flow_pools` | List resource pools with availability counts |
| `flow_pool_lookup` | Check pool for a specific catalog item |
| `flow_generate_csv` | Generate a Flow CSV from structured JSON input |
| `flow_upload_csv` | Upload a CSV schedule to the Flow backend |
| `flow_validate` | Validate schedules against catalog limits and namespace rules |
| `flow_deploy` | Deploy workshops (dry-run or live) |
| `flow_deploy_status` | Get deployment results for the current session |
| `flow_qa_run` | Run QA checks on deployed workshops |
| `flow_qa_results` | Get QA check results |
| `flow_operations` | Lock, extend, scale, or disable autostop on workshops |
| `flow_export_results` | Export deployment, QA, or student results as CSV |
| `flow_template` | Download a blank CSV schedule template |
| `flow_diff` | Compare a new CSV against loaded schedules |

## CSV generation

The `flow_generate_csv` tool accepts a JSON string with the following structure:

```json
{
  "workshops": [
    {
      "ci": "openshift-cnv.ocp-virt-roadshow-multi-user.prod",
      "namespace": "user-alice",
      "users": 20
    }
  ],
  "start_time": "2026-05-07T11:45:00",
  "auto_stop_hours": 8,
  "auto_destroy_days": 23,
  "password": "workshop123"
}
```

Optional fields: `interval_minutes` (default 10), `concurrency`, `ci_name`, `multi_asset`, `asset_cis`, `multi_workshop_name`, `catalog_namespace`, `count`, `instances`.

## Tests

```bash
pytest tests/ -v
```

37 tests covering models, CSV generation, API client, and server tool registration.
