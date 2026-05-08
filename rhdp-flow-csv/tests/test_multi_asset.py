"""Tests for flow_expand_multi_asset."""

import csv
from pathlib import Path

from rhdp_flow_csv.multi_asset import expand_multi_asset


def _write_csv(rows: list[dict], path: Path) -> Path:
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return path


def _read_csv(path: Path) -> list[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


class TestDetectCommaInCI:
    def test_detects_comma_separated_cis(self, tmp_path):
        rows = [{"CI Name": "Multi", "CI": "asset1.event,asset2.event",
                 "Namespace": "user-test", "Multi_Asset": "False",
                 "Asset_CIs": "", "White_Glove": "False"}]
        csv_path = _write_csv(rows, tmp_path / "test.csv")
        result = expand_multi_asset(str(csv_path))
        assert len(result["expansions"]) == 1
        updated = _read_csv(csv_path)
        assert updated[0]["Multi_Asset"] == "True"
        assert updated[0]["White_Glove"] == "True"
        assert "asset1.event" in updated[0]["Asset_CIs"]


class TestMissingAssetCIs:
    def test_detects_multi_asset_true_without_asset_cis(self, tmp_path):
        rows = [{"CI Name": "LB1577", "CI": "summit-2026.lb1577-rhel-troubleshooting-1.event",
                 "Namespace": "user-test", "Multi_Asset": "True",
                 "Asset_CIs": "", "White_Glove": "False"}]
        csv_path = _write_csv(rows, tmp_path / "test.csv")
        result = expand_multi_asset(str(csv_path))
        assert len(result["expansions"]) == 1
        updated = _read_csv(csv_path)
        assert updated[0]["White_Glove"] == "True"


class TestWhiteGloveEnforcement:
    def test_sets_white_glove_for_multi_asset(self, tmp_path):
        rows = [{"CI Name": "Multi", "CI": "main.event",
                 "Namespace": "user-test", "Multi_Asset": "True",
                 "Asset_CIs": "a1.event,a2.event", "White_Glove": "False"}]
        csv_path = _write_csv(rows, tmp_path / "test.csv")
        expand_multi_asset(str(csv_path))
        updated = _read_csv(csv_path)
        assert updated[0]["White_Glove"] == "True"


class TestNonMultiAssetUnchanged:
    def test_leaves_regular_rows_alone(self, tmp_path):
        rows = [{"CI Name": "Regular", "CI": "test.prod",
                 "Namespace": "user-test", "Multi_Asset": "False",
                 "Asset_CIs": "", "White_Glove": "False"}]
        csv_path = _write_csv(rows, tmp_path / "test.csv")
        result = expand_multi_asset(str(csv_path))
        assert len(result["expansions"]) == 0
