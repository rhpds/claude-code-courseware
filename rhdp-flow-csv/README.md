# rhdp-flow-csv

MCP server for RHDP-Flow CSV file operations. Standalone -- no Flow backend required.

## Tools

| Tool | Purpose |
|------|---------|
| `flow_transform_runbook` | Convert messy planning spreadsheets to Flow CSV |
| `flow_fix_csv` | Auto-fix common CSV issues |
| `flow_expand_multi_asset` | Detect and correct multi-asset formatting |
| `flow_bulk_parameter_update` | Apply parameter changes to matching rows |
| `flow_csv_diff` | Compare two CSV schedules |

## Install

pip install -e .

## Register with Claude Code

claude mcp add rhdp-flow-csv -- python3 -m rhdp_flow_csv

## Run standalone

python3 -m rhdp_flow_csv
