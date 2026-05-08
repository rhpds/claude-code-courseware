"""Ghost workshop detector -- find stuck workshops with no phase."""

from __future__ import annotations

from typing import Any


def detect_ghosts(deploy_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Scan deploy results for ghost workshops (PHASE: <none>).

    Args:
        deploy_results: List of deployment result dicts.

    Returns:
        Dict with: ghosts (list), cleanup_commands (list), summary (str).
    """
    ghosts: list[dict[str, Any]] = []
    cleanup_commands: list[str] = []

    for result in deploy_results:
        phase = result.get("phase", "")
        if phase in ("<none>", "none", "") or "no phase" in str(phase).lower():
            name = result.get("name", "unknown")
            namespace = result.get("namespace", "unknown")
            ghosts.append({
                "name": name,
                "ci": result.get("ci", ""),
                "namespace": namespace,
                "phase": phase,
                "status": result.get("status", ""),
            })
            cleanup_commands.append(f"oc delete resourceclaim {name} -n {namespace}")

    summary_lines = [f"Ghost Detector: {len(ghosts)} ghost(s) found"]
    if ghosts:
        for g in ghosts:
            summary_lines.append(f"  - {g['name']} in {g['namespace']} (CI: {g['ci']})")
        summary_lines.append("\nCleanup commands:")
        for cmd in cleanup_commands:
            summary_lines.append(f"  {cmd}")

    return {
        "ghosts": ghosts,
        "cleanup_commands": cleanup_commands,
        "count": len(ghosts),
        "summary": "\n".join(summary_lines),
    }
