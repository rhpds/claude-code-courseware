"""Event health dashboard -- aggregate deployment, QA, and pool data."""

from __future__ import annotations

from typing import Any

from rhdp_flow_intel.monitor import monitor_deployments


def event_dashboard(
    deploy_results: list[dict[str, Any]],
    qa_data: dict[str, Any] | None = None,
    pool_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Produce an aggregate health dashboard for an event.

    Args:
        deploy_results: Deployment results from the API.
        qa_data: Optional QA results.
        pool_data: Optional pool availability data.

    Returns:
        Dict with: deployment, qa, pools sections and overall health.
    """
    deployment = monitor_deployments(deploy_results)

    qa_summary = None
    if qa_data and "checks" in qa_data:
        checks = qa_data["checks"]
        passed = sum(1 for c in checks if all(
            v == "pass" for k, v in c.items() if k != "name"
        ))
        failed = sum(1 for c in checks if any(
            v == "fail" for k, v in c.items() if k != "name"
        ))
        qa_summary = {
            "total": len(checks),
            "passed": passed,
            "failed": failed,
            "not_run": len(checks) - passed - failed,
        }

    pool_summary = None
    if pool_data and "pools" in pool_data:
        pools = pool_data["pools"]
        pool_summary = {
            "total_pools": len(pools),
            "pools": [
                {
                    "name": p.get("pool_name", ""),
                    "ready": p.get("ready", 0),
                    "claimed": p.get("claimed", 0),
                    "provisioning": p.get("provisioning", 0),
                }
                for p in pools
            ],
            "any_exhausted": any(p.get("ready", 0) == 0 for p in pools),
        }

    has_deploy_issues = len(deployment.get("issues", [])) > 0
    has_qa_failures = qa_summary and qa_summary.get("failed", 0) > 0
    has_pool_issues = pool_summary and pool_summary.get("any_exhausted", False)

    overall = "HEALTHY"
    if has_deploy_issues or has_qa_failures:
        overall = "NEEDS ATTENTION"
    if has_pool_issues:
        overall = "NEEDS ATTENTION"

    lines = [
        "Event Health Dashboard",
        "======================",
        f"Overall: {overall}",
        "",
        f"Deployments: {deployment['total']} total, "
        f"{deployment['by_status'].get('READY', 0)} ready",
    ]

    if qa_summary:
        lines.append(
            f"QA: {qa_summary['passed']}/{qa_summary['total']} passed, "
            f"{qa_summary['failed']} failed"
        )

    if pool_summary:
        for p in pool_summary["pools"]:
            status = "OK" if p["ready"] > 0 else "EXHAUSTED"
            lines.append(f"Pool {p['name']}: {p['ready']} ready -- {status}")

    if deployment.get("issues"):
        lines.append(f"\nIssues ({len(deployment['issues'])}):")
        for issue in deployment["issues"]:
            lines.append(f"  [{issue['severity']}] {issue['workshop']}: {issue['issue']}")

    return {
        "overall": overall,
        "deployment": deployment,
        "qa": qa_summary,
        "pools": pool_summary,
        "summary": "\n".join(lines),
    }
