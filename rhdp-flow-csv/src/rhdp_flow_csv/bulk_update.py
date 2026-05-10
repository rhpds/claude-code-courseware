"""Bulk parameter update for Flow CSV files."""

from __future__ import annotations

import csv
import re
from pathlib import Path


def bulk_parameter_update(
    csv_path: str,
    column: str,
    value: str,
    pattern: str | None = None,
    filter_column: str | None = None,
    filter_value: str | None = None,
) -> dict:
    """Apply parameter changes to matching rows in a CSV.

    If pattern is set, uses re.sub(pattern, value, cell) instead of direct replacement.
    If filter_column/filter_value are set, only updates rows where filter matches.
    """
    path = Path(csv_path)
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    changes: list[dict] = []
    rows_updated = 0

    for row_idx, row in enumerate(rows):
        if filter_column and filter_value:
            if row.get(filter_column, "") != filter_value:
                continue

        old_val = row.get(column, "")

        if pattern:
            new_val = re.sub(pattern, value, old_val)
        else:
            new_val = value

        if new_val != old_val:
            row[column] = new_val
            if column not in fieldnames:
                fieldnames.append(column)
            rows_updated += 1
            changes.append({
                "row": row_idx + 1,
                "column": column,
                "old": old_val,
                "new": new_val,
            })

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return {
        "csv_path": str(path),
        "rows_updated": rows_updated,
        "changes": changes,
    }
