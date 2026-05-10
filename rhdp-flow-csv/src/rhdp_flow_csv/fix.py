"""CSV validation and auto-fix for RHDP-Flow schedules."""

from __future__ import annotations

import csv
import re
from datetime import datetime
from pathlib import Path

from rhdp_flow_csv.constants import (
    CATALOG_SUFFIX_MAP,
    DATE_FMT,
    REQUIRED_COLUMNS,
)

_US_DATE_RE = re.compile(r"^(\d{2})/(\d{2})/(\d{4})\s+(\d{2}:\d{2})$")
_ISO_DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})\s+(\d{2}:\d{2})(?::(\d{2}))?$")
_FLOW_DATE_RE = re.compile(r"^(\d{2})/(\d{2})/(\d{4})\s+(\d{2}:\d{2})$")

DATE_COLUMNS = {"Provisioning Date (UTC)", "Auto-stop (UTC)", "Auto-destroy (UTC)"}


def _detect_date_format(value: str) -> str | None:
    value = value.strip()
    if _ISO_DATE_RE.match(value):
        return "iso"
    if _US_DATE_RE.match(value):
        m = _US_DATE_RE.match(value)
        month, day = int(m.group(1)), int(m.group(2))
        if month > 12:
            return "flow"
        if day > 12:
            return "us"
        return "ambiguous"
    return None


def _convert_date_to_flow(value: str, source_format: str) -> str:
    value = value.strip()
    if source_format == "iso":
        m = _ISO_DATE_RE.match(value)
        return f"{m.group(3)}/{m.group(2)}/{m.group(1)} {m.group(4)}"
    if source_format == "us":
        m = _US_DATE_RE.match(value)
        return f"{m.group(2)}/{m.group(1)}/{m.group(3)} {m.group(4)}"
    return value


def _detect_catalog_namespace(ci: str) -> str | None:
    for suffix, ns in CATALOG_SUFFIX_MAP.items():
        if ci.endswith(suffix):
            return ns
    return None


def fix_csv(csv_path: str, auto_fix: bool = True) -> dict:
    """Validate and optionally fix a Flow CSV file.

    Returns dict with keys: fixed_csv_path, issues, ready_to_deploy.
    """
    path = Path(csv_path)
    issues: list[dict] = []

    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        headers = set(reader.fieldnames or [])
        rows = list(reader)

    missing_required = REQUIRED_COLUMNS - headers
    optional_defaultable = {"Activity", "Purpose"}
    for col in missing_required:
        severity = "warning" if col in optional_defaultable else "error"
        issue = {
            "column": col,
            "issue": f"Missing required column: {col}",
            "severity": severity,
            "fix_applied": False,
        }
        if auto_fix and col in optional_defaultable:
            for row in rows:
                row.setdefault(col, "Admin" if col == "Activity" else "QA")
            issue["fix_applied"] = True
            if col not in headers:
                headers.add(col)
        issues.append(issue)

    for row_idx, row in enumerate(rows):
        for date_col in DATE_COLUMNS & headers:
            val = row.get(date_col, "").strip()
            if not val:
                continue
            fmt = _detect_date_format(val)
            if fmt in ("iso", "us"):
                issue = {
                    "column": date_col,
                    "issue": f"Row {row_idx + 1}: {'ISO' if fmt == 'iso' else 'US'} date format detected ({val}), expected DD/MM/YYYY HH:MM",
                    "severity": "error",
                    "fix_applied": False,
                }
                if auto_fix:
                    row[date_col] = _convert_date_to_flow(val, fmt)
                    issue["fix_applied"] = True
                issues.append(issue)

    date_cols_ordered = ["Provisioning Date (UTC)", "Auto-stop (UTC)", "Auto-destroy (UTC)"]
    for row_idx, row in enumerate(rows):
        dates = []
        for dc in date_cols_ordered:
            val = row.get(dc, "").strip()
            if not val:
                dates.append(None)
                continue
            try:
                dates.append(datetime.strptime(val, DATE_FMT))
            except ValueError:
                dates.append(None)

        provision, stop, destroy = dates
        if provision and stop and stop < provision:
            issues.append({
                "column": "Auto-stop (UTC)",
                "issue": f"Row {row_idx + 1}: Auto-stop is before Provisioning Date",
                "severity": "error",
                "fix_applied": False,
            })
        if provision and destroy and destroy < provision:
            issues.append({
                "column": "Auto-destroy (UTC)",
                "issue": f"Row {row_idx + 1}: Auto-destroy is before Provisioning Date",
                "severity": "error",
                "fix_applied": False,
            })
        if stop and destroy and destroy < stop:
            issues.append({
                "column": "Auto-destroy (UTC)",
                "issue": f"Row {row_idx + 1}: Auto-destroy is before Auto-stop",
                "severity": "warning",
                "fix_applied": False,
            })

    for row_idx, row in enumerate(rows):
        ci = row.get("CI", "").strip()
        explicit_ns = row.get("Catalog_Namespace", "").strip()
        if ci and explicit_ns:
            detected = _detect_catalog_namespace(ci)
            if detected and detected != explicit_ns:
                issues.append({
                    "column": "Catalog_Namespace",
                    "issue": f"Row {row_idx + 1}: CI suffix implies {detected} but Catalog_Namespace is {explicit_ns}",
                    "severity": "warning",
                    "fix_applied": False,
                })

    if auto_fix and rows:
        fieldnames = list(rows[0].keys())
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    errors = [i for i in issues if i["severity"] == "error" and not i.get("fix_applied")]
    return {
        "fixed_csv_path": str(path),
        "issues": issues,
        "ready_to_deploy": len(errors) == 0,
    }
