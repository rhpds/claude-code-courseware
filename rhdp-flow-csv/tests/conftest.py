"""Shared test fixtures for rhdp-flow-csv tests."""

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir():
    return FIXTURES_DIR


@pytest.fixture
def messy_runbook_path():
    return FIXTURES_DIR / "messy_runbook.csv"


@pytest.fixture
def valid_flow_path():
    return FIXTURES_DIR / "valid_flow.csv"


@pytest.fixture
def broken_dates_path():
    return FIXTURES_DIR / "broken_dates.csv"


@pytest.fixture
def multi_asset_wrong_path():
    return FIXTURES_DIR / "multi_asset_wrong.csv"


@pytest.fixture
def default_event_config():
    return {
        "timezone": "UTC",
        "target_timezone": "UTC",
        "catalog_namespace": "babylon-catalog-event",
        "naming_template": "Day {day}-Test-{title}",
    }


@pytest.fixture
def default_user_mapping():
    return {
        "klewis@redhat.com": "user-klewis-redhat-com",
        "jappleii@redhat.com": "user-jappleii-redhat-com",
        "bbethell@redhat.com": "user-bbethell-redhat-com",
    }
