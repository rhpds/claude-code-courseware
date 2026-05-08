"""Column mappings, date formats, and catalog suffix rules for Flow CSV."""

DATE_FMT = "%d/%m/%Y %H:%M"

REQUIRED_COLUMNS = {
    "CI Name", "CI", "Namespace", "Users",
    "Enable_workshop_interface", "Password", "Activity", "Purpose",
    "Provisioning Date (UTC)", "Auto-stop (UTC)", "Auto-destroy (UTC)",
}

OPTIONAL_COLUMNS = {
    "Instances", "Workshop Name", "Concurrency", "Count",
    "Multi_Asset", "Asset_CIs", "Multi_Workshop_Name",
    "Redirect", "Catalog_Namespace", "AWS_Region",
    "Salesforce IDs", "Salesforce_Type", "White_Glove",
    "Showroom_Repo", "Showroom_Ref", "Showroom_NoVNC", "Showroom_Zerotouch",
}

ALL_FLOW_COLUMNS = [
    "CI Name", "CI", "Namespace", "Users", "Instances",
    "Enable_workshop_interface", "Password", "Activity", "Purpose",
    "Workshop Name", "Provisioning Date (UTC)", "Auto-stop (UTC)",
    "Auto-destroy (UTC)", "Concurrency", "Count", "AWS_Region",
    "White_Glove", "Redirect", "Multi_Asset", "Asset_CIs",
    "Multi_Workshop_Name", "Catalog_Namespace",
]

CATALOG_SUFFIX_MAP = {
    ".event": "babylon-catalog-event",
    ".prod": "babylon-catalog-prod",
    ".dev": "babylon-catalog-dev",
}

DEFAULT_CATALOG_NAMESPACE = "babylon-catalog-prod"

COLUMN_ALIASES: dict[str, str] = {
    "Lab Code": "CI Name",
    "Lab Name": "CI Name",
    "Workshop": "CI Name",
    "Title": "CI Name",
    "Catalog Item": "CI",
    "CI (AgV Path)": "CI",
    "Catalog_Item": "CI",
    "Attendees": "Users",
    "Num Users": "Users",
    "num_users": "Users",
    "Instances (Count)": "Instances",
    "Instance Count": "Instances",
    "Workshop_instance_count": "Instances",
    "Session Date": "Provisioning Date (UTC)",
    "Provision Date": "Provisioning Date (UTC)",
    "MUST-START Provisioning Date (UTC)": "Provisioning Date (UTC)",
    "Stop Date": "Auto-stop (UTC)",
    "Destroy Date": "Auto-destroy (UTC)",
    "CI Pool Name": "Catalog_Namespace",
}
