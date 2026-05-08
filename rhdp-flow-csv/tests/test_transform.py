"""Tests for flow_transform_runbook."""

import csv
from pathlib import Path

from rhdp_flow_csv.transform import transform_runbook


def _read_csv(path: Path) -> list[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


class TestBasicTransform:
    def test_transforms_messy_runbook(self, messy_runbook_path, tmp_path, default_event_config, default_user_mapping):
        result = transform_runbook(
            source_path=str(messy_runbook_path),
            output_path=str(tmp_path / "output.csv"),
            event_config=default_event_config,
            user_mapping=default_user_mapping,
        )
        assert result["rows_processed"] == 3
        assert result["rows_output"] == 3
        rows = _read_csv(tmp_path / "output.csv")
        assert len(rows) == 3

    def test_output_has_standard_columns(self, messy_runbook_path, tmp_path, default_event_config, default_user_mapping):
        transform_runbook(
            source_path=str(messy_runbook_path),
            output_path=str(tmp_path / "output.csv"),
            event_config=default_event_config,
            user_mapping=default_user_mapping,
        )
        rows = _read_csv(tmp_path / "output.csv")
        assert "CI Name" in rows[0]
        assert "CI" in rows[0]
        assert "Namespace" in rows[0]
        assert "Provisioning Date (UTC)" in rows[0]


class TestColumnAliases:
    def test_maps_lab_code_to_ci_name(self, messy_runbook_path, tmp_path, default_event_config, default_user_mapping):
        transform_runbook(
            source_path=str(messy_runbook_path),
            output_path=str(tmp_path / "output.csv"),
            event_config=default_event_config,
            user_mapping=default_user_mapping,
        )
        rows = _read_csv(tmp_path / "output.csv")
        assert rows[0]["CI Name"].startswith("LB1208")

    def test_maps_attendees_to_instances(self, messy_runbook_path, tmp_path, default_event_config, default_user_mapping):
        transform_runbook(
            source_path=str(messy_runbook_path),
            output_path=str(tmp_path / "output.csv"),
            event_config=default_event_config,
            user_mapping=default_user_mapping,
        )
        rows = _read_csv(tmp_path / "output.csv")
        assert rows[0].get("Instances") == "60"


class TestDateConversion:
    def test_converts_iso_dates_to_flow_format(self, messy_runbook_path, tmp_path, default_event_config, default_user_mapping):
        transform_runbook(
            source_path=str(messy_runbook_path),
            output_path=str(tmp_path / "output.csv"),
            event_config=default_event_config,
            user_mapping=default_user_mapping,
        )
        rows = _read_csv(tmp_path / "output.csv")
        prov_date = rows[0]["Provisioning Date (UTC)"]
        assert "/" in prov_date
        parts = prov_date.split("/")
        assert len(parts[2].split()[0]) == 4


class TestCatalogSuffix:
    def test_adds_event_suffix_when_missing(self, messy_runbook_path, tmp_path, default_event_config, default_user_mapping):
        transform_runbook(
            source_path=str(messy_runbook_path),
            output_path=str(tmp_path / "output.csv"),
            event_config=default_event_config,
            user_mapping=default_user_mapping,
        )
        rows = _read_csv(tmp_path / "output.csv")
        assert rows[0]["CI"].endswith(".event")
        assert rows[2]["CI"].endswith(".event")


class TestExcludeUsers:
    def test_excludes_specified_users(self, messy_runbook_path, tmp_path, default_event_config, default_user_mapping):
        result = transform_runbook(
            source_path=str(messy_runbook_path),
            output_path=str(tmp_path / "output.csv"),
            event_config=default_event_config,
            user_mapping=default_user_mapping,
            exclude_users=["klewis"],
        )
        rows = _read_csv(tmp_path / "output.csv")
        namespaces = [r["Namespace"] for r in rows]
        assert not any("klewis" in ns for ns in namespaces)
        assert result["rows_output"] < result["rows_processed"]


class TestReport:
    def test_report_has_auto_fixes(self, messy_runbook_path, tmp_path, default_event_config, default_user_mapping):
        result = transform_runbook(
            source_path=str(messy_runbook_path),
            output_path=str(tmp_path / "output.csv"),
            event_config=default_event_config,
            user_mapping=default_user_mapping,
        )
        assert "auto_fixes_applied" in result
        assert isinstance(result["auto_fixes_applied"], list)
