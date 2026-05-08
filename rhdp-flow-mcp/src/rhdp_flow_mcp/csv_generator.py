"""CSV generation logic for RHDP-Flow schedules.

Implements the CSV format specification from FLOW_CSV_SPEC_FOR_MCP.md.
Date format: DD/MM/YYYY HH:MM (24-hour). Uses UTC-style date headers.
"""

from __future__ import annotations

import csv
from datetime import datetime, timedelta
from io import StringIO
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rhdp_flow_mcp.models import CsvGenerateInput

DATE_FMT = "%d/%m/%Y %H:%M"

COLUMNS = [
    "CI Name",
    "CI",
    "Namespace",
    "Users",
    "Instances",
    "Enable_workshop_interface",
    "Password",
    "Activity",
    "Purpose",
    "Workshop Name",
    "Provisioning Date (UTC)",
    "Auto-stop (UTC)",
    "Auto-destroy (UTC)",
    "Concurrency",
    "Count",
    "Multi_Asset",
    "Asset_CIs",
    "Multi_Workshop_Name",
    "Redirect",
    "Catalog_Namespace",
]


def generate_csv(inp: CsvGenerateInput) -> str:
    """Generate a valid RHDP-Flow CSV string from structured input."""
    start = datetime.fromisoformat(inp.start_time)
    rows: list[dict[str, str]] = []

    for i, ws in enumerate(inp.workshops):
        prov_time = start + timedelta(minutes=i * inp.interval_minutes)
        auto_stop = prov_time + timedelta(hours=inp.auto_stop_hours)
        auto_destroy = prov_time + timedelta(days=inp.auto_destroy_days)

        row: dict[str, str] = {
            "CI Name": ws.ci_name or ws.ci,
            "CI": ws.ci,
            "Namespace": ws.namespace,
            "Users": str(ws.users) if ws.users is not None else "",
            "Instances": str(ws.instances) if ws.instances is not None else "",
            "Enable_workshop_interface": str(ws.enable_workshop_interface),
            "Password": inp.password,
            "Activity": inp.activity,
            "Purpose": inp.purpose,
            "Workshop Name": ws.workshop_name or ws.ci_name or ws.ci,
            "Provisioning Date (UTC)": prov_time.strftime(DATE_FMT),
            "Auto-stop (UTC)": auto_stop.strftime(DATE_FMT),
            "Auto-destroy (UTC)": auto_destroy.strftime(DATE_FMT),
            "Concurrency": str(inp.concurrency) if inp.concurrency else "",
            "Count": str(ws.count) if ws.count else "",
            "Multi_Asset": str(ws.multi_asset) if ws.multi_asset else "",
            "Asset_CIs": ",".join(ws.asset_cis) if ws.asset_cis else "",
            "Multi_Workshop_Name": ws.multi_workshop_name or "",
            "Redirect": str(ws.redirect),
            "Catalog_Namespace": ws.catalog_namespace or "",
        }
        rows.append(row)

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=COLUMNS)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()
