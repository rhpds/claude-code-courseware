"""Workshop troubleshooter -- match symptoms to known failure patterns."""

from __future__ import annotations

from typing import Any

from rhdp_flow_intel.patterns import FAILURE_PATTERNS


def troubleshoot_workshop(
    workshop: dict[str, Any],
    logs: str = "",
) -> dict[str, Any]:
    """Match a workshop's symptoms against known failure patterns.

    Args:
        workshop: Workshop deployment result dict with name, ci, namespace, phase, status, etc.
        logs: Optional log text to scan for additional indicators.

    Returns:
        Dict with: matches (list of matching patterns), top_match, fix_commands.
    """
    symptom_text = " ".join([
        str(workshop.get("phase", "")),
        str(workshop.get("status", "")),
        logs,
    ]).lower()

    matches = []
    for pattern in FAILURE_PATTERNS:
        matched_indicators = []
        for indicator in pattern["indicators"]:
            if indicator.lower() in symptom_text:
                matched_indicators.append(indicator)

        if matched_indicators:
            fix = pattern["fix_template"].format(
                ci=workshop.get("ci", ""),
                suggested_ci=workshop.get("ci", "") + ".event",
                namespace=workshop.get("namespace", ""),
                name=workshop.get("name", ""),
                suggested_count="5",
                suggested_splits="2",
                max_users="30",
            )
            matches.append({
                "pattern_id": pattern["id"],
                "description": pattern["description"],
                "confidence": pattern["confidence"],
                "matched_indicators": matched_indicators,
                "fix": fix,
                "explanation": pattern["fix_explanation"],
            })

    matches.sort(key=lambda m: (
        0 if m["confidence"] == "high" else 1,
        -len(m["matched_indicators"]),
    ))

    top_match = matches[0] if matches else None

    summary_lines = [f"Troubleshoot: {workshop.get('name', 'unknown')}"]
    if top_match:
        summary_lines.append(f"Diagnosis: {top_match['description']} (confidence: {top_match['confidence']})")
        summary_lines.append(f"Fix: {top_match['fix']}")
        summary_lines.append(f"Explanation: {top_match['explanation']}")
    else:
        summary_lines.append("No known pattern matched. Manual investigation needed.")

    if len(matches) > 1:
        summary_lines.append(f"\n{len(matches) - 1} additional possible match(es):")
        for m in matches[1:]:
            summary_lines.append(f"  - {m['description']} ({m['confidence']})")

    return {
        "workshop": workshop.get("name", ""),
        "matches": matches,
        "top_match": top_match,
        "summary": "\n".join(summary_lines),
    }
