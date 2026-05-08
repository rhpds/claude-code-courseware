"""Tests for column mappings, date formats, and catalog suffix rules."""

from rhdp_flow_csv.constants import (
    CATALOG_SUFFIX_MAP,
    COLUMN_ALIASES,
    DATE_FMT,
    REQUIRED_COLUMNS,
)


def test_date_format():
    assert DATE_FMT == "%d/%m/%Y %H:%M"


def test_required_columns_present():
    expected = {
        "CI Name", "CI", "Namespace", "Users",
        "Enable_workshop_interface", "Password", "Activity", "Purpose",
        "Provisioning Date (UTC)", "Auto-stop (UTC)", "Auto-destroy (UTC)",
    }
    assert REQUIRED_COLUMNS == expected


def test_catalog_suffix_map():
    assert CATALOG_SUFFIX_MAP[".event"] == "babylon-catalog-event"
    assert CATALOG_SUFFIX_MAP[".prod"] == "babylon-catalog-prod"
    assert CATALOG_SUFFIX_MAP[".dev"] == "babylon-catalog-dev"


def test_column_aliases_map_to_standard_names():
    assert COLUMN_ALIASES["Lab Code"] == "CI Name"
    assert COLUMN_ALIASES["Catalog Item"] == "CI"
    assert COLUMN_ALIASES["Attendees"] == "Users"
    assert COLUMN_ALIASES["Instances (Count)"] == "Instances"
