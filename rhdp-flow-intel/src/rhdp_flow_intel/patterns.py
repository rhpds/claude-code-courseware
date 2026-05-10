"""Known failure patterns for RHDP-Flow workshop troubleshooting."""

from __future__ import annotations

FAILURE_PATTERNS = [
    {
        "id": "catalog_namespace_mismatch",
        "description": "CI suffix does not match the catalog namespace",
        "indicators": ["PHASE: <none>", "CatalogItem not found"],
        "confidence": "high",
        "fix_template": "Change CI suffix to match namespace: {ci} -> {suggested_ci}",
        "fix_explanation": (
            "The catalog item exists but in a different namespace. The CI suffix "
            "(.event, .prod, .dev) determines which catalog namespace Flow looks in."
        ),
    },
    {
        "id": "pool_exhaustion",
        "description": "Resource pool has 0 ready instances",
        "indicators": ["ready: 0", "provisioning timeout", "waiting for pool"],
        "confidence": "high",
        "fix_template": "Wait for pool provisioning or scale pool: oc scale --replicas={suggested_count}",
        "fix_explanation": (
            "All pool instances are claimed or provisioning. Either wait for current "
            "provisions to complete or increase the pool size."
        ),
    },
    {
        "id": "permission_error",
        "description": "Deployer lacks access to the target namespace",
        "indicators": ["forbidden", "cannot create", "unauthorized"],
        "confidence": "high",
        "fix_template": "Check RBAC: oc auth can-i create resourceclaims -n {namespace}",
        "fix_explanation": (
            "The service account or user does not have permission to create resources "
            "in the target namespace."
        ),
    },
    {
        "id": "multi_asset_format_error",
        "description": "Multi-asset workshop missing White_Glove or Asset_CIs",
        "indicators": ["MultiWorkshop creation failed", "White_Glove not set"],
        "confidence": "medium",
        "fix_template": "Set Multi_Asset=True, White_Glove=True, and populate Asset_CIs in the CSV",
        "fix_explanation": (
            "Multi-asset workshops require White_Glove=True and a comma-separated "
            "list of asset CIs in the Asset_CIs column."
        ),
    },
    {
        "id": "date_in_past",
        "description": "Provisioning date is in the past",
        "indicators": ["provision date", "past", "already passed"],
        "confidence": "high",
        "fix_template": "Update Provisioning Date (UTC) to a future date",
        "fix_explanation": "Flow will not provision workshops with a start date in the past.",
    },
    {
        "id": "seats_exceed_max",
        "description": "Requested users exceeds catalog item maximum",
        "indicators": ["exceeds maximum", "num_users", "validation failed"],
        "confidence": "high",
        "fix_template": "Split into {suggested_splits} rows of {max_users} users each",
        "fix_explanation": (
            "The catalog item has a hard maximum on num_users. Split into multiple "
            "deployments to stay within limits."
        ),
    },
    {
        "id": "ghost_workshop",
        "description": "Workshop stuck in PHASE: <none> with no progress",
        "indicators": ["PHASE: <none>", "no phase", "stuck"],
        "confidence": "medium",
        "fix_template": "Delete and redeploy: oc delete resourceclaim {name} -n {namespace}",
        "fix_explanation": (
            "Ghost workshops occur when the CatalogItem cannot be found or the "
            "provisioner fails silently. Delete and redeploy with correct parameters."
        ),
    },
]
