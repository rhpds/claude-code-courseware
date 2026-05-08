"""RHDP-Flow MCP Server -- 15 tools wrapping the Flow API."""

from __future__ import annotations

import json
import os
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from rhdp_flow_mcp.api_client import FlowApiClient
from rhdp_flow_mcp.csv_generator import generate_csv
from rhdp_flow_mcp.models import CsvGenerateInput

FLOW_API_URL = os.environ.get("FLOW_API_URL", "http://localhost:8000")

mcp = FastMCP(
    "rhdp-flow",
    instructions="RHDP-Flow workshop automation -- deploy, manage, and audit OpenShift workshops",
)

_client = FlowApiClient(FLOW_API_URL)


@mcp.tool()
async def flow_health() -> str:
    """Check Flow backend and cluster connectivity. Returns status, cluster URL, and user info."""
    result = await _client.health()
    return json.dumps(result, indent=2)


@mcp.tool()
async def flow_catalog_items() -> str:
    """List all available catalog items with their parameters, limits, and descriptions."""
    items = await _client.catalog_items()
    return json.dumps(items, indent=2)


@mcp.tool()
async def flow_pools() -> str:
    """List all resource pools with availability counts (ready, claimed, provisioning)."""
    result = await _client.pools()
    return json.dumps(result, indent=2)


@mcp.tool()
async def flow_pool_lookup(catalog_item: str) -> str:
    """Check the resource pool for a specific catalog item.

    Args:
        catalog_item: Catalog item ID, e.g. openshift-cnv.ocp-virt-roadshow-multi-user.prod
    """
    result = await _client.pool_lookup(catalog_item)
    return json.dumps(result, indent=2)


@mcp.tool()
async def flow_generate_csv(input_json: str) -> str:
    """Generate a valid Flow CSV from structured input. No API call needed.

    Args:
        input_json: JSON object with fields: workshops (array of {ci, namespace, users, ...}),
                    start_time (ISO 8601), interval_minutes, auto_stop_hours, auto_destroy_days,
                    password, concurrency (optional). See CsvGenerateInput model for full schema.
    """
    data = json.loads(input_json)
    inp = CsvGenerateInput(**data)
    return generate_csv(inp)


@mcp.tool()
async def flow_upload_csv(csv_content: str) -> str:
    """Upload a CSV schedule to the Flow backend.

    Args:
        csv_content: Full CSV string content to upload.
    """
    result = await _client.upload_csv(csv_content)
    return json.dumps(result, indent=2)


@mcp.tool()
async def flow_validate(check: str = "all") -> str:
    """Validate uploaded schedules against catalog limits and namespace rules.

    Args:
        check: Which validation to run: 'num-users', 'catalog-namespaces', or 'all' (default).
    """
    results: dict[str, Any] = {}
    if check in ("num-users", "all"):
        results["num_users"] = await _client.validate_num_users()
    if check in ("catalog-namespaces", "all"):
        results["catalog_namespaces"] = await _client.validate_catalog_namespaces()
    return json.dumps(results, indent=2)


@mcp.tool()
async def flow_deploy(
    dry_run: bool = False,
    ci_filter: Optional[str] = None,
    resource_lock: bool = True,
    enable_resource_pools: bool = False,
) -> str:
    """Deploy workshops (dry-run or live).

    Args:
        dry_run: If True, generates manifests without applying them.
        ci_filter: Optional catalog item ID to deploy only that item.
        resource_lock: Apply lock-enabled label (default True).
        enable_resource_pools: Use Poolboy resource pools (default False).
    """
    kwargs: dict[str, Any] = {
        "resource_lock": resource_lock,
        "enable_resource_pools": enable_resource_pools,
    }
    if ci_filter:
        kwargs["ci_filter"] = ci_filter
    result = await _client.deploy(dry_run=dry_run, **kwargs)
    return json.dumps(result, indent=2)


@mcp.tool()
async def flow_deploy_status() -> str:
    """Get deployment results for the current session."""
    results = await _client.deploy_status()
    return json.dumps(results, indent=2)


@mcp.tool()
async def flow_qa_run(qa_type: str = "all", namespace: Optional[str] = None) -> str:
    """Run QA checks on deployed workshops.

    Args:
        qa_type: QA check type: '1' (setup), '2' (deployment), '3' (showroom), 'both' (1+2), 'all' (1+2+3).
        namespace: Optional namespace override (comma-separated for multiple).
    """
    result = await _client.qa_run(qa_type=qa_type, namespace=namespace)
    return json.dumps(result, indent=2)


@mcp.tool()
async def flow_qa_results() -> str:
    """Get QA check results for the current session."""
    results = await _client.qa_results()
    return json.dumps(results, indent=2)


@mcp.tool()
async def flow_operations(
    action: str,
    ci_filter: Optional[str] = None,
    days: int = 0,
    hours: int = 0,
    target_count: Optional[int] = None,
) -> str:
    """Perform operations on deployed workshops: lock, extend, scale.

    Args:
        action: Operation type: 'lock', 'unlock', 'extend-stop', 'extend-destroy', 'scale', 'disable-autostop'.
        ci_filter: Optional catalog item ID to filter affected workshops.
        days: Days to extend (for extend-stop, extend-destroy). Default 0.
        hours: Hours to extend (for extend-stop, extend-destroy). Default 0.
        target_count: Target instance count (for scale). Required when action='scale'.
    """
    kwargs: dict[str, Any] = {}
    if ci_filter:
        kwargs["ci_filter"] = ci_filter
    if action in ("extend-stop", "extend-destroy"):
        kwargs["days"] = days
        kwargs["hours"] = hours
    elif action == "scale" and target_count is not None:
        kwargs["target_count"] = target_count
    result = await _client.operation(action, **kwargs)
    return json.dumps(result, indent=2)


@mcp.tool()
async def flow_export_results(export_type: str = "results") -> str:
    """Export deployment, QA, or student results as CSV.

    Args:
        export_type: Type of export: 'results' or 'students'.
    """
    return await _client.export_results(export_type)


@mcp.tool()
async def flow_template() -> str:
    """Download a blank CSV schedule template with all columns."""
    return await _client.template()


@mcp.tool()
async def flow_diff(csv_content: str) -> str:
    """Compare a new CSV against currently loaded schedules.

    Args:
        csv_content: Full CSV string to compare against loaded schedules.
    """
    result = await _client.diff(csv_content)
    return json.dumps(result, indent=2)
