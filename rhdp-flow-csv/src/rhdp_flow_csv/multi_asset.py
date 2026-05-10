"""Multi-asset workshop detection and correction."""

from __future__ import annotations

import csv
from pathlib import Path


def expand_multi_asset(csv_path: str, auto_detect: bool = True) -> dict:
    """Detect and correct multi-asset workshop formatting.

    Returns dict with keys: csv_path, expansions.
    """
    path = Path(csv_path)
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    for col in ("Multi_Asset", "Asset_CIs", "White_Glove"):
        if col not in fieldnames:
            fieldnames.append(col)

    expansions: list[dict] = []

    for row_idx, row in enumerate(rows):
        ci = row.get("CI", "").strip()
        multi_asset = row.get("Multi_Asset", "").strip().lower() in ("true", "1", "yes")
        asset_cis = row.get("Asset_CIs", "").strip()
        white_glove = row.get("White_Glove", "").strip()
        before = {"Multi_Asset": row.get("Multi_Asset", ""), "Asset_CIs": asset_cis, "White_Glove": white_glove}
        changed = False

        if auto_detect and "," in ci and not multi_asset:
            parts = [p.strip() for p in ci.split(",")]
            row["CI"] = parts[0]
            row["Multi_Asset"] = "True"
            row["Asset_CIs"] = ",".join(parts)
            row["White_Glove"] = "True"
            changed = True

        if multi_asset and not asset_cis:
            row["White_Glove"] = "True"
            changed = True

        if multi_asset and white_glove.lower() not in ("true", "1", "yes"):
            row["White_Glove"] = "True"
            changed = True

        if changed:
            after = {"Multi_Asset": row.get("Multi_Asset", ""), "Asset_CIs": row.get("Asset_CIs", ""), "White_Glove": row.get("White_Glove", "")}
            expansions.append({"row": row_idx + 1, "ci_name": row.get("CI Name", ""), "before": before, "after": after})

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return {"csv_path": str(path), "expansions": expansions}
