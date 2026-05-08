"""Deployment diff -- compare two deployment snapshots."""

from __future__ import annotations

from typing import Any


def deployment_diff(
    old_results: list[dict[str, Any]],
    new_results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compare two deployment snapshots and produce a structured diff.

    Args:
        old_results: Previous deployment results.
        new_results: Current deployment results.

    Returns:
        Dict with: added, removed, changed, unchanged counts and details.
    """
    old_by_name = {r.get("name", ""): r for r in old_results}
    new_by_name = {r.get("name", ""): r for r in new_results}

    old_names = set(old_by_name.keys())
    new_names = set(new_by_name.keys())

    added = [new_by_name[n] for n in sorted(new_names - old_names)]
    removed = [old_by_name[n] for n in sorted(old_names - new_names)]

    changed = []
    unchanged = []
    for name in sorted(old_names & new_names):
        old_r = old_by_name[name]
        new_r = new_by_name[name]
        diffs = {}
        for key in set(list(old_r.keys()) + list(new_r.keys())):
            if old_r.get(key) != new_r.get(key):
                diffs[key] = {"old": old_r.get(key), "new": new_r.get(key)}
        if diffs:
            changed.append({"name": name, "changes": diffs})
        else:
            unchanged.append(name)

    summary_lines = [
        "Deployment Diff",
        "===============",
        f"Added:     {len(added)}",
        f"Removed:   {len(removed)}",
        f"Changed:   {len(changed)}",
        f"Unchanged: {len(unchanged)}",
    ]

    if added:
        summary_lines.append("\nAdded:")
        for a in added:
            summary_lines.append(f"  + {a.get('name', '')} ({a.get('ci', '')})")
    if removed:
        summary_lines.append("\nRemoved:")
        for r in removed:
            summary_lines.append(f"  - {r.get('name', '')} ({r.get('ci', '')})")
    if changed:
        summary_lines.append("\nChanged:")
        for c in changed:
            summary_lines.append(f"  ~ {c['name']}:")
            for field, vals in c["changes"].items():
                summary_lines.append(f"      {field}: {vals['old']} -> {vals['new']}")

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged_count": len(unchanged),
        "summary": "\n".join(summary_lines),
    }
