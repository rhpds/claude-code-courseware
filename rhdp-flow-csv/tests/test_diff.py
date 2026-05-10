"""Tests for flow_csv_diff."""

import csv
from pathlib import Path

from rhdp_flow_csv.diff import csv_diff


def _write_csv(rows: list[dict], path: Path) -> Path:
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return path


BASE_ROW = {"CI Name": "WS1", "CI": "test.prod", "Namespace": "user-alice", "Users": "20"}


class TestAdded:
    def test_detects_added_row(self, tmp_path):
        old = [BASE_ROW]
        new_row = {"CI Name": "WS2", "CI": "test2.prod", "Namespace": "user-bob", "Users": "30"}
        new = [BASE_ROW, new_row]
        old_path = _write_csv(old, tmp_path / "old.csv")
        new_path = _write_csv(new, tmp_path / "new.csv")
        result = csv_diff(str(old_path), str(new_path))
        assert len(result["added"]) == 1
        assert result["added"][0]["CI Name"] == "WS2"


class TestRemoved:
    def test_detects_removed_row(self, tmp_path):
        old = [BASE_ROW, {"CI Name": "WS2", "CI": "test2.prod", "Namespace": "user-bob", "Users": "30"}]
        new = [BASE_ROW]
        old_path = _write_csv(old, tmp_path / "old.csv")
        new_path = _write_csv(new, tmp_path / "new.csv")
        result = csv_diff(str(old_path), str(new_path))
        assert len(result["removed"]) == 1


class TestChanged:
    def test_detects_changed_field(self, tmp_path):
        old = [BASE_ROW.copy()]
        new = [dict(BASE_ROW, Users="40")]
        old_path = _write_csv(old, tmp_path / "old.csv")
        new_path = _write_csv(new, tmp_path / "new.csv")
        result = csv_diff(str(old_path), str(new_path))
        assert len(result["changed"]) == 1
        assert result["changed"][0]["differences"]["Users"]["old"] == "20"
        assert result["changed"][0]["differences"]["Users"]["new"] == "40"


class TestUnchanged:
    def test_counts_unchanged(self, tmp_path):
        rows = [BASE_ROW]
        old_path = _write_csv(rows, tmp_path / "old.csv")
        new_path = _write_csv(rows, tmp_path / "new.csv")
        result = csv_diff(str(old_path), str(new_path))
        assert result["unchanged"] == 1
        assert len(result["added"]) == 0
        assert len(result["removed"]) == 0
        assert len(result["changed"]) == 0


class TestSummary:
    def test_summary_is_nonempty_string(self, tmp_path):
        old = [BASE_ROW]
        new = [dict(BASE_ROW, Users="40")]
        old_path = _write_csv(old, tmp_path / "old.csv")
        new_path = _write_csv(new, tmp_path / "new.csv")
        result = csv_diff(str(old_path), str(new_path))
        assert isinstance(result["summary"], str)
        assert len(result["summary"]) > 0
