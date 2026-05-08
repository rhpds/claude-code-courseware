"""RHDP-Flow CSV MCP Server -- 5 tools for CSV file operations."""

from __future__ import annotations

import json
import os
from typing import Optional

from mcp.server.fastmcp import FastMCP

from rhdp_flow_csv.bulk_update import bulk_parameter_update
from rhdp_flow_csv.diff import csv_diff
from rhdp_flow_csv.fix import fix_csv
from rhdp_flow_csv.multi_asset import expand_multi_asset
from rhdp_flow_csv.transform import transform_runbook

mcp = FastMCP(
    "rhdp-flow-csv",
    instructions="RHDP-Flow CSV pipeline -- transform, fix, expand, update, and diff workshop CSV files. No backend required.",
)


@mcp.tool()
async def flow_transform_runbook(
    source_path: str,
    output_path: str,
    event_config_json: str,
    user_mapping_json: str = "{}",
    exclude_users_json: str = "[]",
) -> str:
    """Convert a messy planning spreadsheet into a Flow-compliant CSV.

    Args:
        source_path: Path to the raw CSV/spreadsheet.
        output_path: Where to write the Flow-compliant CSV.
        event_config_json: JSON with: timezone, target_timezone, catalog_namespace, naming_template.
        user_mapping_json: JSON dict mapping emails to namespaces. Default "{}".
        exclude_users_json: JSON list of usernames to exclude. Default "[]".
    """
    event_config = json.loads(event_config_json)
    user_mapping = json.loads(user_mapping_json)
    exclude_users = json.loads(exclude_users_json)
    result = transform_runbook(
        source_path=source_path,
        output_path=output_path,
        event_config=event_config,
        user_mapping=user_mapping,
        exclude_users=exclude_users,
    )
    result.pop("csv_content", None)
    return json.dumps(result, indent=2)


@mcp.tool()
async def flow_fix_csv(csv_path: str, auto_fix: bool = True) -> str:
    """Validate and auto-fix common CSV issues.

    Args:
        csv_path: Path to the Flow CSV file.
        auto_fix: If True, apply fixes automatically. Default True.
    """
    result = fix_csv(csv_path, auto_fix=auto_fix)
    return json.dumps(result, indent=2)


@mcp.tool()
async def flow_expand_multi_asset(csv_path: str, auto_detect: bool = True) -> str:
    """Detect and correct multi-asset workshop formatting.

    Args:
        csv_path: Path to the CSV file.
        auto_detect: Scan for multi-asset patterns. Default True.
    """
    result = expand_multi_asset(csv_path, auto_detect=auto_detect)
    return json.dumps(result, indent=2)


@mcp.tool()
async def flow_bulk_parameter_update(
    csv_path: str,
    column: str,
    value: str,
    pattern: Optional[str] = None,
    filter_column: Optional[str] = None,
    filter_value: Optional[str] = None,
) -> str:
    """Apply parameter changes to matching rows in a CSV.

    Args:
        csv_path: Path to the CSV file.
        column: Target column name.
        value: New value (or replacement string in regex mode).
        pattern: Optional regex pattern. If set, uses re.sub(pattern, value, cell).
        filter_column: Only update rows where this column matches filter_value.
        filter_value: Value to match in filter_column.
    """
    result = bulk_parameter_update(
        csv_path, column=column, value=value,
        pattern=pattern, filter_column=filter_column, filter_value=filter_value,
    )
    return json.dumps(result, indent=2)


@mcp.tool()
async def flow_csv_diff(
    old_csv_path: str,
    new_csv_path: str,
    key_columns_json: str = '["CI Name", "CI", "Namespace"]',
) -> str:
    """Compare two CSV schedules and produce a structured diff.

    Args:
        old_csv_path: Path to the previous CSV.
        new_csv_path: Path to the new CSV.
        key_columns_json: JSON list of columns for row matching. Default: CI Name, CI, Namespace.
    """
    key_columns = json.loads(key_columns_json)
    result = csv_diff(old_csv_path, new_csv_path, key_columns=key_columns)
    return json.dumps(result, indent=2)
