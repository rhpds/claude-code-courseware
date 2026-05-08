"""Tests for MCP tool input/output models."""

from rhdp_flow_mcp.models import (
    CsvGenerateInput,
    CsvWorkshopEntry,
    DeployInput,
    ExtendInput,
    OperationsInput,
    ScaleInput,
)


class TestCsvGenerateInput:
    def test_single_workshop(self):
        inp = CsvGenerateInput(
            workshops=[
                CsvWorkshopEntry(
                    ci="test.workshop.prod",
                    namespace="user-alice",
                    users=20,
                )
            ],
            start_time="2026-05-07T11:45:00",
            auto_stop_hours=8,
            auto_destroy_days=23,
            password="test123",
        )
        assert len(inp.workshops) == 1
        assert inp.workshops[0].ci == "test.workshop.prod"
        assert inp.interval_minutes == 10

    def test_staggered_bulk(self):
        inp = CsvGenerateInput(
            workshops=[
                CsvWorkshopEntry(ci="test.prod", namespace="user-bob", users=10)
                for _ in range(5)
            ],
            start_time="2026-05-07T10:00:00",
            interval_minutes=5,
            auto_stop_hours=8,
            auto_destroy_days=14,
            password="bulk123",
            concurrency=12,
        )
        assert len(inp.workshops) == 5
        assert inp.concurrency == 12

    def test_multi_asset_entry(self):
        entry = CsvWorkshopEntry(
            ci="main.prod",
            namespace="user-charlie",
            users=25,
            multi_asset=True,
            asset_cis=["asset1.prod", "asset2.prod"],
        )
        assert entry.multi_asset is True
        assert len(entry.asset_cis) == 2

    def test_users_optional(self):
        entry = CsvWorkshopEntry(
            ci="test.prod",
            namespace="user-dave",
            instances=30,
        )
        assert entry.users is None
        assert entry.instances == 30


class TestOperationsInput:
    def test_extend_stop(self):
        inp = OperationsInput(
            action="extend-stop",
            extend=ExtendInput(days=3, hours=0),
        )
        assert inp.action == "extend-stop"
        assert inp.extend.days == 3

    def test_scale(self):
        inp = OperationsInput(
            action="scale",
            scale=ScaleInput(target_count=50),
        )
        assert inp.action == "scale"
        assert inp.scale.target_count == 50

    def test_lock(self):
        inp = OperationsInput(action="lock")
        assert inp.action == "lock"


class TestDeployInput:
    def test_dry_run(self):
        inp = DeployInput(dry_run=True)
        assert inp.dry_run is True
        assert inp.resource_lock is True

    def test_with_ci_filter(self):
        inp = DeployInput(ci_filter="test.workshop.prod")
        assert inp.ci_filter == "test.workshop.prod"
