"""Tests for flow_fix_csv -- CSV validation and auto-fix."""

import csv
import tempfile
from pathlib import Path

from rhdp_flow_csv.fix import fix_csv


def _write_csv(rows: list[dict], path: Path) -> Path:
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return path


class TestMissingColumns:
    def test_detects_missing_activity(self, tmp_path):
        rows = [{"CI Name": "Test", "CI": "test.prod", "Namespace": "user-test",
                 "Users": "20", "Enable_workshop_interface": "True",
                 "Password": "pass", "Purpose": "QA",
                 "Provisioning Date (UTC)": "14/05/2026 08:00",
                 "Auto-stop (UTC)": "30/05/2026 18:00",
                 "Auto-destroy (UTC)": "30/05/2026 18:00"}]
        csv_path = _write_csv(rows, tmp_path / "test.csv")
        result = fix_csv(str(csv_path), auto_fix=False)
        issues = [i for i in result["issues"] if i["column"] == "Activity"]
        assert len(issues) == 1
        assert issues[0]["severity"] == "warning"

    def test_auto_fixes_missing_activity(self, tmp_path):
        rows = [{"CI Name": "Test", "CI": "test.prod", "Namespace": "user-test",
                 "Users": "20", "Enable_workshop_interface": "True",
                 "Password": "pass", "Purpose": "QA",
                 "Provisioning Date (UTC)": "14/05/2026 08:00",
                 "Auto-stop (UTC)": "30/05/2026 18:00",
                 "Auto-destroy (UTC)": "30/05/2026 18:00"}]
        csv_path = _write_csv(rows, tmp_path / "test.csv")
        result = fix_csv(str(csv_path), auto_fix=True)
        assert result["ready_to_deploy"]


class TestDateFormat:
    def test_detects_us_date_format(self, broken_dates_path):
        result = fix_csv(str(broken_dates_path), auto_fix=False)
        date_issues = [i for i in result["issues"] if "date" in i["issue"].lower()]
        assert len(date_issues) > 0

    def test_detects_iso_date_format(self, broken_dates_path):
        result = fix_csv(str(broken_dates_path), auto_fix=False)
        iso_issues = [i for i in result["issues"] if "ISO" in i["issue"] or "iso" in i["issue"].lower()]
        assert len(iso_issues) > 0

    def test_auto_fixes_date_format(self, broken_dates_path, tmp_path):
        import shutil
        test_csv = tmp_path / "broken.csv"
        shutil.copy(broken_dates_path, test_csv)
        result = fix_csv(str(test_csv), auto_fix=True)
        fixed_issues = [i for i in result["issues"] if i.get("fix_applied")]
        assert len(fixed_issues) > 0


class TestDateSanity:
    def test_detects_stop_before_provision(self, tmp_path):
        rows = [{"CI Name": "Test", "CI": "test.prod", "Namespace": "user-test",
                 "Users": "20", "Enable_workshop_interface": "True",
                 "Password": "pass", "Activity": "Admin", "Purpose": "QA",
                 "Provisioning Date (UTC)": "30/05/2026 18:00",
                 "Auto-stop (UTC)": "14/05/2026 08:00",
                 "Auto-destroy (UTC)": "30/06/2026 18:00"}]
        csv_path = _write_csv(rows, tmp_path / "test.csv")
        result = fix_csv(str(csv_path), auto_fix=False)
        sanity_issues = [i for i in result["issues"] if "before" in i["issue"].lower() or "after" in i["issue"].lower()]
        assert len(sanity_issues) > 0


class TestCatalogNamespaceConsistency:
    def test_detects_suffix_mismatch(self, tmp_path):
        rows = [{"CI Name": "Test", "CI": "test.workshop.event", "Namespace": "user-test",
                 "Users": "20", "Enable_workshop_interface": "True",
                 "Password": "pass", "Activity": "Admin", "Purpose": "QA",
                 "Provisioning Date (UTC)": "14/05/2026 08:00",
                 "Auto-stop (UTC)": "30/05/2026 18:00",
                 "Auto-destroy (UTC)": "30/05/2026 18:00",
                 "Catalog_Namespace": "babylon-catalog-prod"}]
        csv_path = _write_csv(rows, tmp_path / "test.csv")
        result = fix_csv(str(csv_path), auto_fix=False)
        ns_issues = [i for i in result["issues"] if "catalog" in i["issue"].lower() or "namespace" in i["issue"].lower()]
        assert len(ns_issues) > 0


class TestValidCsv:
    def test_valid_csv_has_no_errors(self, valid_flow_path):
        result = fix_csv(str(valid_flow_path), auto_fix=False)
        errors = [i for i in result["issues"] if i["severity"] == "error"]
        assert len(errors) == 0
        assert result["ready_to_deploy"]
