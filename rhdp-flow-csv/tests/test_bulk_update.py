"""Tests for flow_bulk_parameter_update."""

import csv
from pathlib import Path

from rhdp_flow_csv.bulk_update import bulk_parameter_update


def _write_csv(rows: list[dict], path: Path) -> Path:
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return path


def _read_csv(path: Path) -> list[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


BASE_ROW = {"CI Name": "WS1", "CI": "test1.prod", "Password": "old1"}


class TestSimpleUpdate:
    def test_set_all_passwords(self, tmp_path):
        rows = [
            {"CI Name": "WS1", "CI": "test1.prod", "Password": "old1"},
            {"CI Name": "WS2", "CI": "test2.prod", "Password": "old2"},
        ]
        csv_path = _write_csv(rows, tmp_path / "test.csv")
        result = bulk_parameter_update(str(csv_path), column="Password", value="newpass")
        assert result["rows_updated"] == 2
        updated = _read_csv(csv_path)
        assert all(r["Password"] == "newpass" for r in updated)

    def test_returns_changes(self, tmp_path):
        rows = [{"CI Name": "WS1", "CI": "test1.prod", "Password": "old"}]
        csv_path = _write_csv(rows, tmp_path / "test.csv")
        result = bulk_parameter_update(str(csv_path), column="Password", value="new")
        assert result["changes"][0]["old"] == "old"
        assert result["changes"][0]["new"] == "new"


class TestRegexUpdate:
    def test_add_event_suffix(self, tmp_path):
        rows = [
            {"CI Name": "WS1", "CI": "summit-2026.lb1208-image-mode"},
            {"CI Name": "WS2", "CI": "summit-2026.lb2655-net-automation.event"},
        ]
        csv_path = _write_csv(rows, tmp_path / "test.csv")
        result = bulk_parameter_update(
            str(csv_path), column="CI",
            pattern=r"(?<!\.event)$", value=".event",
        )
        assert result["rows_updated"] == 1
        updated = _read_csv(csv_path)
        assert updated[0]["CI"] == "summit-2026.lb1208-image-mode.event"
        assert updated[1]["CI"] == "summit-2026.lb2655-net-automation.event"


class TestFilteredUpdate:
    def test_update_with_filter(self, tmp_path):
        rows = [
            {"CI Name": "WS1", "CI": "test1.prod", "Namespace": "user-alice"},
            {"CI Name": "WS2", "CI": "test2.prod", "Namespace": "user-bob"},
        ]
        csv_path = _write_csv(rows, tmp_path / "test.csv")
        result = bulk_parameter_update(
            str(csv_path), column="Password", value="alicepass",
            filter_column="Namespace", filter_value="user-alice",
        )
        assert result["rows_updated"] == 1
        updated = _read_csv(csv_path)
        assert updated[0].get("Password") == "alicepass"
        assert updated[1].get("Password", "") != "alicepass"
