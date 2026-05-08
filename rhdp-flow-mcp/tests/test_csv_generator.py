"""Tests for CSV generation logic."""

import csv
from io import StringIO

from rhdp_flow_mcp.csv_generator import generate_csv
from rhdp_flow_mcp.models import CsvGenerateInput, CsvWorkshopEntry


def parse_csv(csv_string: str) -> list[dict]:
    reader = csv.DictReader(StringIO(csv_string))
    return list(reader)


class TestSingleWorkshop:
    def test_basic_csv_generation(self):
        inp = CsvGenerateInput(
            workshops=[
                CsvWorkshopEntry(ci="test.workshop.prod", namespace="user-alice", users=20)
            ],
            start_time="2026-05-07T11:45:00",
            auto_stop_hours=8,
            auto_destroy_days=23,
            password="test123",
        )
        result = generate_csv(inp)
        rows = parse_csv(result)
        assert len(rows) == 1
        assert rows[0]["CI"] == "test.workshop.prod"
        assert rows[0]["Namespace"] == "user-alice"
        assert rows[0]["Users"] == "20"
        assert rows[0]["Password"] == "test123"

    def test_date_format_dd_mm_yyyy(self):
        inp = CsvGenerateInput(
            workshops=[CsvWorkshopEntry(ci="test.prod", namespace="user-bob", users=10)],
            start_time="2026-05-07T11:45:00",
            auto_stop_hours=8,
            auto_destroy_days=23,
            password="pass",
        )
        result = generate_csv(inp)
        rows = parse_csv(result)
        assert rows[0]["Provisioning Date (UTC)"] == "07/05/2026 11:45"

    def test_auto_stop_calculation(self):
        inp = CsvGenerateInput(
            workshops=[CsvWorkshopEntry(ci="test.prod", namespace="user-x", users=5)],
            start_time="2026-05-07T10:00:00",
            auto_stop_hours=8,
            auto_destroy_days=14,
            password="pass",
        )
        result = generate_csv(inp)
        rows = parse_csv(result)
        assert rows[0]["Auto-stop (UTC)"] == "07/05/2026 18:00"

    def test_auto_destroy_calculation(self):
        inp = CsvGenerateInput(
            workshops=[CsvWorkshopEntry(ci="test.prod", namespace="user-x", users=5)],
            start_time="2026-05-07T10:00:00",
            auto_stop_hours=8,
            auto_destroy_days=14,
            password="pass",
        )
        result = generate_csv(inp)
        rows = parse_csv(result)
        assert rows[0]["Auto-destroy (UTC)"] == "21/05/2026 10:00"

    def test_ci_name_defaults_to_ci(self):
        inp = CsvGenerateInput(
            workshops=[CsvWorkshopEntry(ci="test.workshop.prod", namespace="user-x", users=5)],
            start_time="2026-05-07T10:00:00",
            auto_stop_hours=8,
            auto_destroy_days=14,
            password="pass",
        )
        result = generate_csv(inp)
        rows = parse_csv(result)
        assert rows[0]["CI Name"] == "test.workshop.prod"

    def test_ci_name_override(self):
        inp = CsvGenerateInput(
            workshops=[
                CsvWorkshopEntry(ci="test.workshop.prod", namespace="user-x", users=5, ci_name="My Workshop")
            ],
            start_time="2026-05-07T10:00:00",
            auto_stop_hours=8,
            auto_destroy_days=14,
            password="pass",
        )
        result = generate_csv(inp)
        rows = parse_csv(result)
        assert rows[0]["CI Name"] == "My Workshop"


class TestStaggeredBulk:
    def test_staggered_provisioning_times(self):
        inp = CsvGenerateInput(
            workshops=[
                CsvWorkshopEntry(ci="test.prod", namespace="user-bulk", users=10)
                for _ in range(3)
            ],
            start_time="2026-05-07T10:00:00",
            interval_minutes=10,
            auto_stop_hours=8,
            auto_destroy_days=14,
            password="bulk",
        )
        result = generate_csv(inp)
        rows = parse_csv(result)
        assert len(rows) == 3
        assert rows[0]["Provisioning Date (UTC)"] == "07/05/2026 10:00"
        assert rows[1]["Provisioning Date (UTC)"] == "07/05/2026 10:10"
        assert rows[2]["Provisioning Date (UTC)"] == "07/05/2026 10:20"

    def test_zero_interval_same_time(self):
        inp = CsvGenerateInput(
            workshops=[
                CsvWorkshopEntry(ci="test.prod", namespace="user-x", users=10)
                for _ in range(2)
            ],
            start_time="2026-05-07T10:00:00",
            interval_minutes=0,
            auto_stop_hours=8,
            auto_destroy_days=14,
            password="pass",
        )
        result = generate_csv(inp)
        rows = parse_csv(result)
        assert rows[0]["Provisioning Date (UTC)"] == rows[1]["Provisioning Date (UTC)"]

    def test_concurrency_applied(self):
        inp = CsvGenerateInput(
            workshops=[CsvWorkshopEntry(ci="test.prod", namespace="user-x", users=10)],
            start_time="2026-05-07T10:00:00",
            auto_stop_hours=8,
            auto_destroy_days=14,
            password="pass",
            concurrency=12,
        )
        result = generate_csv(inp)
        rows = parse_csv(result)
        assert rows[0]["Concurrency"] == "12"


class TestMultiAsset:
    def test_legacy_multi_asset(self):
        inp = CsvGenerateInput(
            workshops=[
                CsvWorkshopEntry(
                    ci="main.prod", namespace="user-x", users=25,
                    multi_asset=True, asset_cis=["asset1.prod", "asset2.prod"],
                )
            ],
            start_time="2026-05-07T10:00:00",
            auto_stop_hours=8,
            auto_destroy_days=14,
            password="pass",
        )
        result = generate_csv(inp)
        rows = parse_csv(result)
        assert rows[0]["Multi_Asset"] == "True"
        assert rows[0]["Asset_CIs"] == "asset1.prod,asset2.prod"

    def test_new_style_multi_asset(self):
        inp = CsvGenerateInput(
            workshops=[
                CsvWorkshopEntry(
                    ci=f"asset{i}.prod", namespace="user-x", users=10,
                    multi_workshop_name="Summit Workshop",
                )
                for i in range(1, 4)
            ],
            start_time="2026-05-07T10:00:00",
            interval_minutes=0,
            auto_stop_hours=8,
            auto_destroy_days=14,
            password="pass",
        )
        result = generate_csv(inp)
        rows = parse_csv(result)
        assert len(rows) == 3
        for row in rows:
            assert row["Multi_Workshop_Name"] == "Summit Workshop"


class TestEdgeCases:
    def test_empty_users_when_none(self):
        inp = CsvGenerateInput(
            workshops=[CsvWorkshopEntry(ci="test.prod", namespace="user-x", instances=30)],
            start_time="2026-05-07T10:00:00",
            auto_stop_hours=8,
            auto_destroy_days=14,
            password="pass",
        )
        result = generate_csv(inp)
        rows = parse_csv(result)
        assert rows[0]["Users"] == ""

    def test_catalog_namespace_override(self):
        inp = CsvGenerateInput(
            workshops=[
                CsvWorkshopEntry(
                    ci="test.prod", namespace="user-x", users=10,
                    catalog_namespace="babylon-catalog-event",
                )
            ],
            start_time="2026-05-07T10:00:00",
            auto_stop_hours=8,
            auto_destroy_days=14,
            password="pass",
        )
        result = generate_csv(inp)
        rows = parse_csv(result)
        assert rows[0]["Catalog_Namespace"] == "babylon-catalog-event"

    def test_count_field(self):
        inp = CsvGenerateInput(
            workshops=[CsvWorkshopEntry(ci="test.prod", namespace="user-x", users=20, count=2)],
            start_time="2026-05-07T10:00:00",
            auto_stop_hours=8,
            auto_destroy_days=14,
            password="pass",
        )
        result = generate_csv(inp)
        rows = parse_csv(result)
        assert rows[0]["Count"] == "2"

    def test_csv_has_required_columns(self):
        inp = CsvGenerateInput(
            workshops=[CsvWorkshopEntry(ci="test.prod", namespace="user-x", users=10)],
            start_time="2026-05-07T10:00:00",
            auto_stop_hours=8,
            auto_destroy_days=14,
            password="pass",
        )
        result = generate_csv(inp)
        reader = csv.DictReader(StringIO(result))
        list(reader)
        required = [
            "CI Name", "CI", "Namespace", "Users", "Enable_workshop_interface",
            "Password", "Activity", "Purpose", "Provisioning Date (UTC)",
            "Auto-stop (UTC)", "Auto-destroy (UTC)",
        ]
        for col in required:
            assert col in reader.fieldnames
