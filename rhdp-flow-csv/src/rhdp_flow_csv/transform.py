"""Runbook-to-Flow CSV transformation logic."""

from __future__ import annotations

import csv
import re
from datetime import datetime, timedelta
from pathlib import Path

from rhdp_flow_csv.constants import (
    ALL_FLOW_COLUMNS,
    CATALOG_SUFFIX_MAP,
    COLUMN_ALIASES,
    DATE_FMT,
)


def _normalize_header(header: str) -> str | None:
    h = header.strip()
    if h in ALL_FLOW_COLUMNS:
        return h
    if h in COLUMN_ALIASES:
        return COLUMN_ALIASES[h]
    h_lower = h.lower().replace(" ", "_")
    for alias, standard in COLUMN_ALIASES.items():
        if alias.lower().replace(" ", "_") == h_lower:
            return standard
    return None


def _ensure_catalog_suffix(ci: str, default_ns: str) -> tuple[str, str | None]:
    for suffix in CATALOG_SUFFIX_MAP:
        if ci.endswith(suffix):
            return ci, None
    if default_ns:
        for suffix, ns in CATALOG_SUFFIX_MAP.items():
            if ns == default_ns:
                return ci + suffix, f"Added {suffix} suffix to {ci}"
    return ci + ".event", f"Added .event suffix to {ci} (default)"


def _parse_date_flexible(date_str: str, time_str: str = "") -> datetime | None:
    combined = f"{date_str.strip()} {time_str.strip()}".strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d",
                "%d/%m/%Y %H:%M", "%m/%d/%Y %H:%M"):
        try:
            return datetime.strptime(combined, fmt)
        except ValueError:
            continue
    return None


def _build_ci_name(row: dict, title_col: str | None) -> str:
    lab_code = ""
    title = ""
    for orig_key, mapped in [("Lab Code", "CI Name"), ("Title", "CI Name")]:
        if orig_key in row and row[orig_key].strip():
            if orig_key == "Lab Code":
                lab_code = row[orig_key].strip()
            else:
                title = row[orig_key].strip()
    if lab_code and title:
        return f"{lab_code} {title}"
    return lab_code or title or row.get("CI", "")


def transform_runbook(
    source_path: str,
    output_path: str,
    event_config: dict,
    user_mapping: dict | None = None,
    exclude_users: list[str] | None = None,
) -> dict:
    """Transform a messy planning spreadsheet into a Flow-compliant CSV.

    Returns dict with: csv_content, output_path, rows_processed, rows_output,
    excluded, auto_fixes_applied, warnings.
    """
    user_mapping = user_mapping or {}
    exclude_users = exclude_users or []
    catalog_ns = event_config.get("catalog_namespace", "babylon-catalog-event")
    naming_template = event_config.get("naming_template", "{title}")
    auto_fixes: list[str] = []
    warnings: list[str] = []
    excluded: list[str] = []

    with open(source_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        raw_headers = list(reader.fieldnames or [])
        raw_rows = list(reader)

    header_map: dict[str, str] = {}
    for h in raw_headers:
        mapped = _normalize_header(h)
        if mapped:
            header_map[h] = mapped

    output_rows: list[dict] = []
    rows_processed = len(raw_rows)

    for raw_row in raw_rows:
        mapped_row: dict[str, str] = {}
        for orig_h, val in raw_row.items():
            target = header_map.get(orig_h)
            if target:
                mapped_row[target] = val.strip() if val else ""
            mapped_row[f"_orig_{orig_h}"] = val.strip() if val else ""

        ns = mapped_row.get("Namespace", "").strip()
        if any(eu.lower() in ns.lower() for eu in exclude_users):
            excluded.append(f"Row excluded: namespace {ns} matches exclude filter")
            continue

        ci_name = _build_ci_name(raw_row, None)
        mapped_row["CI Name"] = ci_name

        ci = mapped_row.get("CI", "")
        ci_fixed, fix_msg = _ensure_catalog_suffix(ci, catalog_ns)
        if fix_msg:
            auto_fixes.append(fix_msg)
        mapped_row["CI"] = ci_fixed

        date_str = mapped_row.get("Provisioning Date (UTC)", "")
        time_str = raw_row.get("Session Start", "")
        if not date_str and raw_row.get("Session Date"):
            date_str = raw_row["Session Date"].strip()
        parsed = _parse_date_flexible(date_str, time_str)
        if parsed:
            mapped_row["Provisioning Date (UTC)"] = parsed.strftime(DATE_FMT)
            if not mapped_row.get("Auto-stop (UTC)"):
                auto_stop = parsed + timedelta(days=365)
                mapped_row["Auto-stop (UTC)"] = auto_stop.strftime(DATE_FMT)
                auto_fixes.append(f"Set auto-stop to +1 year for {ci_name}")
            if not mapped_row.get("Auto-destroy (UTC)"):
                auto_destroy = parsed + timedelta(days=365)
                mapped_row["Auto-destroy (UTC)"] = auto_destroy.strftime(DATE_FMT)
                auto_fixes.append(f"Set auto-destroy to +1 year for {ci_name}")

        attendees = mapped_row.get("Users", "") or raw_row.get("Attendees", "")
        if attendees:
            mapped_row["Instances"] = attendees.strip()

        mapped_row.setdefault("Enable_workshop_interface", "True")
        mapped_row.setdefault("Activity", "Brand Event")
        mapped_row.setdefault("Purpose", "Summit 2026")
        mapped_row.setdefault("Redirect", "True")
        mapped_row.setdefault("Count", "1")
        mapped_row.setdefault("White_Glove", "False")

        mapped_row["Catalog_Namespace"] = catalog_ns

        workshop_name = naming_template.format(
            title=ci_name, day="3",
        )
        mapped_row["Workshop Name"] = workshop_name

        conc = mapped_row.get("Concurrency", "") or raw_row.get("Concurency", "")
        if conc:
            mapped_row["Concurrency"] = conc.strip()

        output = {}
        for col in ALL_FLOW_COLUMNS:
            output[col] = mapped_row.get(col, "")
        output_rows.append(output)

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ALL_FLOW_COLUMNS)
        writer.writeheader()
        writer.writerows(output_rows)

    csv_content = Path(output_path).read_text()

    return {
        "csv_content": csv_content,
        "output_path": output_path,
        "rows_processed": rows_processed,
        "rows_output": len(output_rows),
        "excluded": excluded,
        "auto_fixes_applied": auto_fixes,
        "warnings": warnings,
    }
