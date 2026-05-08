"""RHDP-Flow Intel MCP Server -- 5 tools for deployment intelligence."""

from __future__ import annotations

import json
import os
from typing import Optional

from mcp.server.fastmcp import FastMCP

from rhdp_flow_intel.api_client import FlowIntelClient
from rhdp_flow_intel.dashboard import event_dashboard
from rhdp_flow_intel.diff import deployment_diff
from rhdp_flow_intel.ghosts import detect_ghosts
from rhdp_flow_intel.monitor import monitor_deployments
from rhdp_flow_intel.troubleshoot import troubleshoot_workshop

FLOW_API_URL = os.environ.get("FLOW_API_URL", "http://localhost:8000")

mcp = FastMCP(
    "rhdp-flow-intel",
    instructions="RHDP-Flow deployment intelligence -- monitor, detect, diagnose workshop issues.",
)

_client = FlowIntelClient(FLOW_API_URL)


@mcp.tool()
async def flow_deployment_monitor() -> str:
    """Real-time deployment status with progress tracking and issue detection.

    Fetches current deployment results and aggregates by status (READY, PROVISIONING, ERROR, ghost).
    """
    results = await _client.deploy_results()
    report = monitor_deployments(results)
    return json.dumps(report, indent=2)


@mcp.tool()
async def flow_ghost_detector() -> str:
    """Find ghost workshops stuck in PHASE: <none> and generate cleanup commands.

    Scans all deployments for workshops with no phase, indicating failed provisioning.
    """
    results = await _client.deploy_results()
    report = detect_ghosts(results)
    return json.dumps(report, indent=2)


@mcp.tool()
async def flow_deployment_diff(old_results_json: str, new_results_json: Optional[str] = None) -> str:
    """Compare two deployment snapshots to track changes.

    Args:
        old_results_json: JSON string of previous deployment results.
        new_results_json: JSON string of new results. If omitted, fetches current state from API.
    """
    old = json.loads(old_results_json)
    if new_results_json:
        new = json.loads(new_results_json)
    else:
        new = await _client.deploy_results()
    report = deployment_diff(old, new)
    return json.dumps(report, indent=2)


@mcp.tool()
async def flow_event_dashboard() -> str:
    """Aggregate health report across deployments, QA results, and resource pools.

    Combines deployment status, QA check results, and pool availability into a single dashboard.
    """
    deploy = await _client.deploy_results()
    try:
        qa = await _client.qa_results()
    except Exception:
        qa = None
    try:
        pools = await _client.pools()
    except Exception:
        pools = None
    report = event_dashboard(deploy, qa_data=qa, pool_data=pools)
    return json.dumps(report, indent=2)


@mcp.tool()
async def flow_troubleshoot(workshop_json: str, logs: str = "") -> str:
    """Match a workshop's symptoms against known failure patterns and suggest fixes.

    Args:
        workshop_json: JSON string with workshop details (name, ci, namespace, phase, status).
        logs: Optional log text to scan for additional failure indicators.
    """
    workshop = json.loads(workshop_json)
    report = troubleshoot_workshop(workshop, logs=logs)
    return json.dumps(report, indent=2)
