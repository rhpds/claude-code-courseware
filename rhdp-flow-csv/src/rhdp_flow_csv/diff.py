"""CSV schedule comparison for RHDP-Flow."""

from __future__ import annotations

import csv
from pathlib import Path


def _row_key(row: dict, key_columns: list[str]) -> tuple:
    return tuple(row.get(k, "") for k in key_columns)


def csv_diff(
    old_csv_path: str,
    new_csv_path: str,
    key_columns: list[str] | None = None,
) -> dict:
    """Compare two CSV schedules and produce a structured diff.

    Returns dict with keys: added, removed, changed, unchanged, summary.
    """
    if key_columns is None:
        key_columns = ["CI Name", "CI", "Namespace"]

    with open(old_csv_path, newline="") as f:
        old_rows = list(csv.DictReader(f))

    with open(new_csv_path, newline="") as f:
        new_rows = list(csv.DictReader(f))

    old_by_key = {}
    for row in old_rows:
        key = _row_key(row, key_columns)
        old_by_key[key] = row

    new_by_key = {}
    for row in new_rows:
        key = _row_key(row, key_columns)
        new_by_key[key] = row

    added = []
    removed = []
    changed = []
    unchanged = 0

    for key, row in new_by_key.items():
        if key not in old_by_key:
            added.append(dict(row))
        else:
            old_row = old_by_key[key]
            diffs = {}
            all_cols = set(row.keys()) | set(old_row.keys())
            for col in all_cols:
                if col in key_columns:
                    continue
                old_val = old_row.get(col, "")
                new_val = row.get(col, "")
                if old_val != new_val:
                    diffs[col] = {"old": old_val, "new": new_val}
            if diffs:
                changed.append({
                    "key": {k: row.get(k, "") for k in key_columns},
                    "differences": diffs,
                })
            else:
                unchanged += 1

    for key in old_by_key:
        if key not in new_by_key:
            removed.append(dict(old_by_key[key]))

    parts = []
    if added:
        parts.append(f"{len(added)} added")
    if removed:
        parts.append(f"{len(removed)} removed")
    if changed:
        parts.append(f"{len(changed)} changed")
    parts.append(f"{unchanged} unchanged")
    summary = "Schedule diff: " + ", ".join(parts) + "."

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged,
        "summary": summary,
    }
