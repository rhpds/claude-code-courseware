"""Deployment monitoring -- aggregate status, flag issues."""

from __future__ import annotations

from typing import Any


def monitor_deployments(deploy_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate deployment results by status and identify issues.

    Args:
        deploy_results: List of deployment result dicts from the Flow API.

    Returns:
        Dict with: total, by_status (counts), issues (list), summary (markdown).
    """
    by_status: dict[str, list[dict]] = {}
    issues: list[dict[str, str]] = []

    for result in deploy_results:
        phase = result.get("phase", "UNKNOWN")
        by_status.setdefault(phase, []).append(result)

        if phase == "<none>":
            issues.append({
                "workshop": result.get("name", "unknown"),
                "severity": "CRITICAL",
                "issue": "Ghost workshop -- no phase set",
                "fix": f"oc delete resourceclaim {result.get('name', '')} -n {result.get('namespace', '')}",
            })
        elif phase == "ERROR" or result.get("status", "").startswith("error"):
            issues.append({
                "workshop": result.get("name", "unknown"),
                "severity": "CRITICAL",
                "issue": f"Deployment error: {result.get('status', 'unknown')}",
                "fix": "Check logs and redeploy",
            })

    status_counts = {k: len(v) for k, v in by_status.items()}
    total = len(deploy_results)
    ready = status_counts.get("READY", 0)

    lines = [
        "Deployment Monitor",
        "==================",
        f"Total:         {total} workshops",
        f"READY:         {ready}/{total}",
    ]
    for status, count in sorted(status_counts.items()):
        if status != "READY":
            lines.append(f"{status:15s}{count}")

    if issues:
        lines.append(f"\nIssues ({len(issues)}):")
        for issue in issues:
            lines.append(f"  [{issue['severity']}] {issue['workshop']}: {issue['issue']}")

    return {
        "total": total,
        "by_status": status_counts,
        "issues": issues,
        "summary": "\n".join(lines),
    }
