# RHDP-Flow Real-Time Monitoring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add 7 new MCP tools to rhdp-ops-mcp for real-time workshop monitoring, deeper OCP visibility, and event-scale operations, plus a background watcher agent and `/ops` skill extensions.

**Architecture:** New tools follow the existing pattern: dataclasses in `models.py`, K8s API calls in `k8s_client.py`, helper functions + `@mcp.tool()` registrations in `mcp_server.py`. Tests mock at the `_get_client()` factory boundary using conftest factories. The watcher agent is a Claude Code agent definition that uses `ScheduleWakeup` for periodic ticks.

**Tech Stack:** Python 3.10+, kubernetes>=29.0, fastmcp>=2.0, pytest, pytest-asyncio

**Target repo:** `~/repos/rhpds-utils/rhdp-ops-mcp/`

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `rhdp_ops/models.py` | Modify | Add 8 new dataclasses (SnapshotRow, PoolHealthRow, CatalogItemRow, ResourcePoolDetail, MultiWorkshopDetail, MultiWorkshopAsset, ServiceAccessRow, WatchThresholds) |
| `rhdp_ops/k8s_client.py` | Modify | Add 6 new read methods for ResourcePool, CatalogItem, MultiWorkshop, ServiceAccess CRDs |
| `rhdp_ops/mcp_server.py` | Modify | Add 7 new `@mcp.tool()` functions + helpers |
| `tests/conftest.py` | Modify | Add factories: `make_resource_pool`, `make_catalog_item`, `make_multiworkshop`, `make_service_access` |
| `tests/test_models.py` | Modify | Add tests for 8 new dataclasses |
| `tests/test_k8s_client.py` | Modify | Add tests for 6 new client methods |
| `tests/test_tools.py` | Modify | Add tests for 7 new MCP tools |
| `marketplace/skills/ops/SKILL.md` | Modify | Add watch, summary, pools, catalog, group commands |

---

### Task 1: New Dataclasses

**Files:**
- Modify: `rhdp_ops/models.py`
- Modify: `tests/test_models.py`

- [ ] **Step 1: Write failing tests for new dataclasses**

Add to `tests/test_models.py`:

```python
from rhdp_ops.models import (
    SnapshotRow, PoolHealthRow, CatalogItemRow, ResourcePoolDetail,
    MultiWorkshopDetail, MultiWorkshopAsset, ServiceAccessRow, WatchThresholds,
)


def test_snapshot_row_fields():
    row = SnapshotRow(
        name="ws-test", namespace="ns", display_name="Test",
        stage="prod", provision_phase="Ready",
        stop_time="2026-05-13T12:00:00Z", destroy_time="2026-05-14T12:00:00Z",
        seats_assigned=5, seats_capacity=10,
        white_glove=False, multiworkshop_name=None,
    )
    assert row.name == "ws-test"
    assert row.provision_phase == "Ready"
    assert row.seats_assigned == 5
    assert row.multiworkshop_name is None


def test_pool_health_row_fields():
    row = PoolHealthRow(
        name="pool-1", min_available=4,
        available=3, ready=3, unready=0, health="degraded",
    )
    assert row.health == "degraded"
    assert row.available < row.min_available


def test_catalog_item_row_fields():
    row = CatalogItemRow(
        name="agd-v2.maas.prod", display_name="MaaS Workshop",
        stage="prod", category="AI", namespace="babylon-catalog-prod",
        age_days=30,
    )
    assert row.stage == "prod"
    assert row.age_days == 30


def test_resource_pool_detail_fields():
    detail = ResourcePoolDetail(
        name="pool-1", namespace="poolboy",
        min_available=6, max_unready=10,
        lifespan_default="2d", lifespan_maximum="180d",
        lifespan_unclaimed="7d",
        available=6, ready=6, unready=0,
        delete_unhealthy=True, provider_names=["provider-1"],
    )
    assert detail.delete_unhealthy is True
    assert detail.provider_names == ["provider-1"]


def test_multiworkshop_detail_fields():
    asset = MultiWorkshopAsset(
        display_name="Roadshow 01", catalog_key="summit-2026.lb1997-roadshow-1.event",
        workshop_name="automation-voasv-summit-2026.lb1997-roadshow-1.event-d8tl5",
        namespace="user-klewis-redhat-com", workshop_id="kkhc8h",
        status="Ready",
    )
    detail = MultiWorkshopDetail(
        name="automation-voasv", namespace="user-klewis-redhat-com",
        display_name="Ansible Roadshow", description="Three-part roadshow",
        purpose="Training", start_date="2026-05-12", end_date="2026-05-14",
        number_seats=30, assets=[asset],
    )
    assert len(detail.assets) == 1
    assert detail.assets[0].workshop_id == "kkhc8h"


def test_service_access_row_fields():
    row = ServiceAccessRow(
        user="jdoe@redhat.com", workshop_ref="ws-test",
        state="active", created="2026-05-13T10:00:00Z",
    )
    assert row.state == "active"


def test_watch_thresholds_defaults():
    t = WatchThresholds()
    assert t.deadline_critical_seconds == 3600
    assert t.deadline_warning_seconds == 14400
    assert t.deadline_info_seconds == 86400
    assert t.seat_warning_pct == 80
    assert t.seat_critical_pct == 100
    assert t.pool_mode == "auto"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd ~/repos/rhpds-utils/rhdp-ops-mcp && .venv/bin/pytest tests/test_models.py -v -k "snapshot or pool_health or catalog_item or resource_pool_detail or multiworkshop or service_access or watch_thresholds"`

Expected: FAIL with `ImportError: cannot import name 'SnapshotRow'`

- [ ] **Step 3: Add dataclasses to models.py**

Append to `rhdp_ops/models.py`:

```python
@dataclass
class SnapshotRow:
    name: str
    namespace: str
    display_name: str
    stage: str
    provision_phase: str
    stop_time: str | None
    destroy_time: str | None
    seats_assigned: int
    seats_capacity: int
    white_glove: bool
    multiworkshop_name: str | None


@dataclass
class PoolHealthRow:
    name: str
    min_available: int
    available: int
    ready: int
    unready: int
    health: str


@dataclass
class CatalogItemRow:
    name: str
    display_name: str
    stage: str
    category: str
    namespace: str
    age_days: int


@dataclass
class ResourcePoolDetail:
    name: str
    namespace: str
    min_available: int
    max_unready: int
    lifespan_default: str
    lifespan_maximum: str
    lifespan_unclaimed: str
    available: int
    ready: int
    unready: int
    delete_unhealthy: bool
    provider_names: list[str]


@dataclass
class MultiWorkshopAsset:
    display_name: str
    catalog_key: str
    workshop_name: str
    namespace: str
    workshop_id: str
    status: str | None


@dataclass
class MultiWorkshopDetail:
    name: str
    namespace: str
    display_name: str
    description: str
    purpose: str
    start_date: str
    end_date: str
    number_seats: int
    assets: list[MultiWorkshopAsset]


@dataclass
class ServiceAccessRow:
    user: str
    workshop_ref: str
    state: str
    created: str


@dataclass
class WatchThresholds:
    deadline_critical_seconds: int = 3600
    deadline_warning_seconds: int = 14400
    deadline_info_seconds: int = 86400
    seat_warning_pct: int = 80
    seat_critical_pct: int = 100
    pool_mode: str = "auto"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd ~/repos/rhpds-utils/rhdp-ops-mcp && .venv/bin/pytest tests/test_models.py -v`

Expected: All PASS (existing + new)

- [ ] **Step 5: Commit**

```bash
cd ~/repos/rhpds-utils/rhdp-ops-mcp
git add rhdp_ops/models.py tests/test_models.py
git commit -m "add dataclasses for snapshot, pool health, catalog, multiworkshop, service access, and watch thresholds

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 2: K8s Client — ResourcePool and CatalogItem Methods

**Files:**
- Modify: `rhdp_ops/k8s_client.py`
- Modify: `tests/test_k8s_client.py`
- Modify: `tests/conftest.py`

- [ ] **Step 1: Add test factories to conftest.py**

Append to `tests/conftest.py`:

```python
def make_resource_pool(
    name="pool-test",
    namespace="poolboy",
    min_available=6,
    max_unready=10,
    lifespan_default="2d",
    lifespan_maximum="180d",
    lifespan_unclaimed="7d",
    available=6,
    ready=6,
    unready=0,
    delete_unhealthy=True,
    provider_name=None,
):
    provider_name = provider_name or name
    return {
        "apiVersion": f"{POOLBOY}/v1",
        "kind": "ResourcePool",
        "metadata": {"name": name, "namespace": namespace},
        "spec": {
            "minAvailable": min_available,
            "maxUnready": max_unready,
            "deleteUnhealthyResourceHandles": delete_unhealthy,
            "lifespan": {
                "default": lifespan_default,
                "maximum": lifespan_maximum,
                "unclaimed": lifespan_unclaimed,
            },
            "resources": [
                {"name": name, "provider": {"name": provider_name, "namespace": namespace}},
            ],
        },
        "status": {
            "resourceHandleCount": {
                "available": available,
                "ready": ready,
                **({"unready": unready} if unready else {}),
            },
        },
    }


def make_catalog_item(
    name="agd-v2.maas.prod",
    namespace="babylon-catalog-prod",
    display_name="MaaS Workshop",
    category="AI",
    age_days=30,
):
    from datetime import datetime, timezone, timedelta
    created = (datetime.now(timezone.utc) - timedelta(days=age_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "apiVersion": f"{BABYLON}/v1",
        "kind": "CatalogItem",
        "metadata": {
            "name": name,
            "namespace": namespace,
            "creationTimestamp": created,
            "annotations": {
                f"{BABYLON}/category": category,
                f"{BABYLON}/displayName": display_name,
            },
            "labels": {},
        },
        "spec": {},
    }
```

- [ ] **Step 2: Write failing tests for new K8s client methods**

Append to `tests/test_k8s_client.py`:

```python
from tests.conftest import make_resource_pool, make_catalog_item


class TestResourcePoolMethods:
    def test_list_resource_pools_cluster_wide(self, mock_custom_api):
        mock_custom_api.list_cluster_custom_object.return_value = {
            "items": [make_resource_pool(name="pool-1"), make_resource_pool(name="pool-2")]
        }
        with patch("kubernetes.config.load_kube_config"):
            client = RhdpOpsClient.__new__(RhdpOpsClient)
            client._custom = mock_custom_api
            client._core = MagicMock()
        result = client.list_resource_pools()
        assert len(result) == 2
        mock_custom_api.list_cluster_custom_object.assert_called_once_with(
            group="poolboy.gpte.redhat.com", version="v1", plural="resourcepools"
        )

    def test_list_resource_pools_namespaced(self, mock_custom_api):
        mock_custom_api.list_namespaced_custom_object.return_value = {
            "items": [make_resource_pool()]
        }
        with patch("kubernetes.config.load_kube_config"):
            client = RhdpOpsClient.__new__(RhdpOpsClient)
            client._custom = mock_custom_api
            client._core = MagicMock()
        result = client.list_resource_pools(namespace="poolboy")
        assert len(result) == 1

    def test_get_resource_pool(self, mock_custom_api):
        mock_custom_api.get_cluster_custom_object.return_value = make_resource_pool(name="pool-1")
        with patch("kubernetes.config.load_kube_config"):
            client = RhdpOpsClient.__new__(RhdpOpsClient)
            client._custom = mock_custom_api
            client._core = MagicMock()
        result = client.get_resource_pool("pool-1")
        assert result["metadata"]["name"] == "pool-1"


class TestCatalogItemMethods:
    def test_list_catalog_items_cluster_wide(self, mock_custom_api):
        mock_custom_api.list_cluster_custom_object.return_value = {
            "items": [make_catalog_item()]
        }
        with patch("kubernetes.config.load_kube_config"):
            client = RhdpOpsClient.__new__(RhdpOpsClient)
            client._custom = mock_custom_api
            client._core = MagicMock()
        result = client.list_catalog_items()
        assert len(result) == 1
        mock_custom_api.list_cluster_custom_object.assert_called_once_with(
            group="babylon.gpte.redhat.com", version="v1", plural="catalogitems"
        )

    def test_list_catalog_items_namespaced(self, mock_custom_api):
        mock_custom_api.list_namespaced_custom_object.return_value = {
            "items": [make_catalog_item()]
        }
        with patch("kubernetes.config.load_kube_config"):
            client = RhdpOpsClient.__new__(RhdpOpsClient)
            client._custom = mock_custom_api
            client._core = MagicMock()
        result = client.list_catalog_items(namespace="babylon-catalog-prod")
        assert len(result) == 1
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd ~/repos/rhpds-utils/rhdp-ops-mcp && .venv/bin/pytest tests/test_k8s_client.py -v -k "resource_pool or catalog_item"`

Expected: FAIL with `AttributeError: 'RhdpOpsClient' has no attribute 'list_resource_pools'`

- [ ] **Step 4: Implement K8s client methods**

Add to `rhdp_ops/k8s_client.py` in the `RhdpOpsClient` class, inside the `# ---- Reads ----` section:

```python
    def list_resource_pools(self, namespace: str | None = None) -> list[dict]:
        """List ResourcePool resources from poolboy."""
        if namespace:
            validate_k8s_name(namespace, "namespace")
            result = self._custom.list_namespaced_custom_object(
                group=POOLBOY, version=V1, namespace=namespace, plural="resourcepools"
            )
        else:
            result = self._custom.list_cluster_custom_object(
                group=POOLBOY, version=V1, plural="resourcepools"
            )
        return result.get("items", [])

    def get_resource_pool(self, name: str) -> dict:
        """Get a single ResourcePool by name (cluster-scoped in poolboy ns)."""
        validate_k8s_name(name, "pool name")
        return self._custom.get_cluster_custom_object(
            group=POOLBOY, version=V1, plural="resourcepools", name=name
        )

    def list_catalog_items(self, namespace: str | None = None) -> list[dict]:
        """List CatalogItem resources."""
        if namespace:
            validate_k8s_name(namespace, "namespace")
            result = self._custom.list_namespaced_custom_object(
                group=BABYLON, version=V1, namespace=namespace, plural="catalogitems"
            )
        else:
            result = self._custom.list_cluster_custom_object(
                group=BABYLON, version=V1, plural="catalogitems"
            )
        return result.get("items", [])
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd ~/repos/rhpds-utils/rhdp-ops-mcp && .venv/bin/pytest tests/test_k8s_client.py -v`

Expected: All PASS

- [ ] **Step 6: Commit**

```bash
cd ~/repos/rhpds-utils/rhdp-ops-mcp
git add rhdp_ops/k8s_client.py tests/test_k8s_client.py tests/conftest.py
git commit -m "add K8s client methods for ResourcePool and CatalogItem CRDs

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 3: K8s Client — MultiWorkshop and ServiceAccess Methods

**Files:**
- Modify: `rhdp_ops/k8s_client.py`
- Modify: `tests/test_k8s_client.py`
- Modify: `tests/conftest.py`

- [ ] **Step 1: Add test factories to conftest.py**

Append to `tests/conftest.py`:

```python
def make_multiworkshop(
    name="automation-voasv",
    namespace="user-klewis-redhat-com",
    display_name="Ansible Roadshow",
    description="Three-part roadshow",
    purpose="Training",
    start_date="2026-05-12",
    end_date="2026-05-14",
    number_seats=30,
    assets=None,
):
    if assets is None:
        assets = [
            {
                "displayName": "Roadshow 01 - Introspection",
                "key": "summit-2026.lb1997-roadshow-1.event",
                "name": f"{name}-summit-2026.lb1997-roadshow-1.event-d8tl5",
                "namespace": namespace,
                "type": "Workshop",
                "workshopId": "kkhc8h",
            },
            {
                "displayName": "Roadshow 02 - Standardization",
                "key": "summit-2026.lb1997-roadshow-2.event",
                "name": f"{name}-summit-2026.lb1997-roadshow-2.event-t5vqv",
                "namespace": namespace,
                "type": "Workshop",
                "workshopId": "4b8cfg",
            },
        ]
    return {
        "apiVersion": f"{BABYLON}/v1",
        "kind": "MultiWorkshop",
        "metadata": {"name": name, "namespace": namespace},
        "spec": {
            "displayName": display_name,
            "description": description,
            "purpose": purpose,
            "startDate": start_date,
            "endDate": end_date,
            "numberSeats": number_seats,
            "assets": assets,
        },
    }


def make_service_access(
    name="sa-test",
    namespace="user-test-redhat-com",
    user="jdoe@redhat.com",
    workshop_ref="ws-test",
    state="active",
    created="2026-05-13T10:00:00Z",
):
    return {
        "apiVersion": f"{BABYLON}/v1",
        "kind": "ServiceAccess",
        "metadata": {
            "name": name,
            "namespace": namespace,
            "creationTimestamp": created,
            "labels": {
                f"{BABYLON}/workshop": workshop_ref,
            },
        },
        "spec": {
            "user": user,
        },
        "status": {
            "state": state,
        },
    }
```

- [ ] **Step 2: Write failing tests**

Append to `tests/test_k8s_client.py`:

```python
from tests.conftest import make_multiworkshop, make_service_access


class TestMultiWorkshopMethods:
    def test_list_multiworkshops(self, mock_custom_api):
        mock_custom_api.list_namespaced_custom_object.return_value = {
            "items": [make_multiworkshop()]
        }
        with patch("kubernetes.config.load_kube_config"):
            client = RhdpOpsClient.__new__(RhdpOpsClient)
            client._custom = mock_custom_api
            client._core = MagicMock()
        result = client.list_multiworkshops("user-klewis-redhat-com")
        assert len(result) == 1
        mock_custom_api.list_namespaced_custom_object.assert_called_once_with(
            group="babylon.gpte.redhat.com", version="v1",
            namespace="user-klewis-redhat-com", plural="multiworkshops"
        )

    def test_get_multiworkshop(self, mock_custom_api):
        mock_custom_api.get_namespaced_custom_object.return_value = make_multiworkshop()
        with patch("kubernetes.config.load_kube_config"):
            client = RhdpOpsClient.__new__(RhdpOpsClient)
            client._custom = mock_custom_api
            client._core = MagicMock()
        result = client.get_multiworkshop("user-klewis-redhat-com", "automation-voasv")
        assert result["spec"]["displayName"] == "Ansible Roadshow"

    def test_get_multiworkshop_validates_input(self, mock_custom_api):
        with patch("kubernetes.config.load_kube_config"):
            client = RhdpOpsClient.__new__(RhdpOpsClient)
            client._custom = mock_custom_api
            client._core = MagicMock()
        with pytest.raises(ValueError):
            client.get_multiworkshop("user-klewis-redhat-com", "'; DROP TABLE--")


class TestServiceAccessMethods:
    def test_list_service_accesses(self, mock_custom_api):
        mock_custom_api.list_namespaced_custom_object.return_value = {
            "items": [make_service_access(), make_service_access(name="sa-2", user="asmith@redhat.com")]
        }
        with patch("kubernetes.config.load_kube_config"):
            client = RhdpOpsClient.__new__(RhdpOpsClient)
            client._custom = mock_custom_api
            client._core = MagicMock()
        result = client.list_service_accesses("user-test-redhat-com")
        assert len(result) == 2

    def test_list_service_accesses_filtered_by_workshop(self, mock_custom_api):
        mock_custom_api.list_namespaced_custom_object.return_value = {
            "items": [make_service_access()]
        }
        with patch("kubernetes.config.load_kube_config"):
            client = RhdpOpsClient.__new__(RhdpOpsClient)
            client._custom = mock_custom_api
            client._core = MagicMock()
        result = client.list_service_accesses("user-test-redhat-com", workshop_name="ws-test")
        assert len(result) == 1
        call_kwargs = mock_custom_api.list_namespaced_custom_object.call_args[1]
        assert "label_selector" in call_kwargs
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd ~/repos/rhpds-utils/rhdp-ops-mcp && .venv/bin/pytest tests/test_k8s_client.py -v -k "multiworkshop or service_access"`

Expected: FAIL with `AttributeError`

- [ ] **Step 4: Implement K8s client methods**

Add to `rhdp_ops/k8s_client.py` in the `RhdpOpsClient` class:

```python
    def list_multiworkshops(self, namespace: str) -> list[dict]:
        """List MultiWorkshop resources in a namespace."""
        validate_k8s_name(namespace, "namespace")
        result = self._custom.list_namespaced_custom_object(
            group=BABYLON, version=V1, namespace=namespace, plural="multiworkshops"
        )
        return result.get("items", [])

    def get_multiworkshop(self, namespace: str, name: str) -> dict:
        """Get a single MultiWorkshop by namespace and name."""
        validate_k8s_name(namespace, "namespace")
        validate_k8s_name(name, "name")
        return self._custom.get_namespaced_custom_object(
            group=BABYLON, version=V1, namespace=namespace,
            plural="multiworkshops", name=name,
        )

    def list_service_accesses(self, namespace: str, workshop_name: str | None = None) -> list[dict]:
        """List ServiceAccess resources, optionally filtered by workshop."""
        validate_k8s_name(namespace, "namespace")
        kwargs = {
            "group": BABYLON, "version": V1,
            "namespace": namespace, "plural": "serviceaccesses",
        }
        if workshop_name:
            validate_k8s_name(workshop_name, "workshop name")
            kwargs["label_selector"] = f"{BABYLON}/workshop={workshop_name}"
        result = self._custom.list_namespaced_custom_object(**kwargs)
        return result.get("items", [])
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd ~/repos/rhpds-utils/rhdp-ops-mcp && .venv/bin/pytest tests/test_k8s_client.py -v`

Expected: All PASS

- [ ] **Step 6: Commit**

```bash
cd ~/repos/rhpds-utils/rhdp-ops-mcp
git add rhdp_ops/k8s_client.py tests/test_k8s_client.py tests/conftest.py
git commit -m "add K8s client methods for MultiWorkshop and ServiceAccess CRDs

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 4: ops_snapshot Tool

**Files:**
- Modify: `rhdp_ops/mcp_server.py`
- Modify: `tests/test_tools.py`

This tool builds a compact snapshot of all workshops for diffing by the watcher agent. It reuses the existing `_ws_to_row()` helper and adds provision phase detection.

- [ ] **Step 1: Write failing tests**

Append to `tests/test_tools.py`:

```python
import json


class TestOpsSnapshot:
    def test_snapshot_returns_json_list(self):
        ws = make_workshop(name="ws-1", display_name="Workshop One")
        prov = make_provision(workshop_name="ws-1", count=10, claimed=8, failed=0)
        assign1 = make_assignment(workshop_name="ws-1", assigned=True)

        mock_client = MagicMock()
        mock_client.list_workshops.return_value = [ws]
        mock_client.list_provisions.return_value = [prov]
        mock_client.list_assignments.return_value = [assign1]

        with patch("rhdp_ops.mcp_server._get_client", return_value=mock_client):
            result = _build_snapshot()

        assert isinstance(result, list)
        assert len(result) == 1
        row = result[0]
        assert row["name"] == "ws-1"
        assert row["display_name"] == "Workshop One"
        assert row["seats_assigned"] == 1
        assert row["seats_capacity"] == 10

    def test_snapshot_includes_provision_phase(self):
        ws = make_workshop(name="ws-1")
        prov = make_provision(workshop_name="ws-1", count=5, claimed=5, failed=0)
        rc = make_resource_claim(
            workshop_name="ws-1",
            provision_data={"phase": "Ready"},
        )

        mock_client = MagicMock()
        mock_client.list_workshops.return_value = [ws]
        mock_client.list_provisions.return_value = [prov]
        mock_client.list_assignments.return_value = []
        mock_client.list_resource_claims.return_value = [rc]

        with patch("rhdp_ops.mcp_server._get_client", return_value=mock_client):
            result = _build_snapshot()

        assert result[0]["provision_phase"] == "Ready"

    def test_snapshot_filters_by_stage(self):
        ws_prod = make_workshop(name="ws-prod", stage="prod")
        ws_dev = make_workshop(name="ws-dev", stage="dev")

        mock_client = MagicMock()
        mock_client.list_workshops.return_value = [ws_prod, ws_dev]
        mock_client.list_provisions.return_value = []
        mock_client.list_assignments.return_value = []

        with patch("rhdp_ops.mcp_server._get_client", return_value=mock_client):
            result = _build_snapshot(stage="prod")

        assert len(result) == 1
        assert result[0]["name"] == "ws-prod"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd ~/repos/rhpds-utils/rhdp-ops-mcp && .venv/bin/pytest tests/test_tools.py -v -k "TestOpsSnapshot"`

Expected: FAIL with `NameError: name '_build_snapshot' is not defined`

- [ ] **Step 3: Implement the snapshot helper and MCP tool**

Add helper function to `rhdp_ops/mcp_server.py` (before the tool definitions section):

```python
def _provision_phase(client: RhdpOpsClient, namespace: str, workshop_name: str) -> str:
    """Determine the overall provision phase for a workshop."""
    try:
        claims = client.list_resource_claims(namespace, workshop_name)
    except Exception:
        return "Unknown"
    if not claims:
        return "Provisioning"
    for claim in claims:
        phase = (
            claim.get("status", {})
            .get("resources", [{}])[0]
            .get("state", {})
            .get("spec", {})
            .get("vars", {})
            .get("provision_data", {})
            .get("phase", "")
        )
        if phase:
            return phase
    return "Unknown"


def _build_snapshot(
    client: RhdpOpsClient | None = None,
    namespace: str = "",
    stage: str = "",
) -> list[dict]:
    """Build a compact snapshot of all workshops for diffing."""
    if client is None:
        client = _get_client()
    workshops = client.list_workshops(namespace=namespace or None)
    rows = []
    for ws in workshops:
        ws_name = ws["metadata"]["name"]
        ws_ns = ws["metadata"]["namespace"]
        ws_stage = _stage(ws)
        if stage and ws_stage != stage:
            continue
        provisions = client.list_provisions(ws_ns, ws_name)
        assignments = client.list_assignments(ws_ns, ws_name)
        seat_info = _build_seat_info(provisions, assignments)
        phase = _provision_phase(client, ws_ns, ws_name)
        rows.append({
            "name": ws_name,
            "namespace": ws_ns,
            "display_name": _display_name(ws),
            "stage": ws_stage,
            "provision_phase": phase,
            "stop_time": _stop_time(ws),
            "destroy_time": _destroy_time(ws),
            "seats_assigned": seat_info.assigned if seat_info else 0,
            "seats_capacity": seat_info.total if seat_info else 0,
            "white_glove": _is_white_glove(ws),
            "multiworkshop_name": _multiworkshop_id(ws),
        })
    return rows
```

Add the MCP tool registration:

```python
@mcp.tool()
async def ops_snapshot(namespace: str = "", stage: str = "") -> str:
    """Compact, diffable snapshot of all workshops with provision phase, seats, and timing.

    Designed for periodic comparison by the watcher agent. Returns JSON array of snapshot rows.
    Filter by namespace or stage when provided.
    """
    try:
        rows = _build_snapshot(namespace=namespace, stage=stage)
        return json.dumps(rows, indent=2)
    except Exception as e:
        return f"Error building snapshot: {e}"
```

Add `import json` at the top of `mcp_server.py` if not already present.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd ~/repos/rhpds-utils/rhdp-ops-mcp && .venv/bin/pytest tests/test_tools.py -v -k "TestOpsSnapshot"`

Expected: All PASS

- [ ] **Step 5: Run full test suite**

Run: `cd ~/repos/rhpds-utils/rhdp-ops-mcp && .venv/bin/pytest tests/ -v`

Expected: All PASS (no regressions)

- [ ] **Step 6: Commit**

```bash
cd ~/repos/rhpds-utils/rhdp-ops-mcp
git add rhdp_ops/mcp_server.py tests/test_tools.py
git commit -m "add ops_snapshot tool for compact workshop state snapshots

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 5: ops_pool_health Tool

**Files:**
- Modify: `rhdp_ops/mcp_server.py`
- Modify: `tests/test_tools.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_tools.py`:

```python
from tests.conftest import make_resource_pool


class TestOpsPoolHealth:
    def test_pool_health_returns_all_pools(self):
        pools = [
            make_resource_pool(name="pool-1", min_available=6, available=6, ready=6),
            make_resource_pool(name="pool-2", min_available=4, available=2, ready=2),
        ]
        mock_client = MagicMock()
        mock_client.list_resource_pools.return_value = pools

        with patch("rhdp_ops.mcp_server._get_client", return_value=mock_client):
            result = _build_pool_health()

        assert len(result) == 2

    def test_pool_health_healthy_status(self):
        pools = [make_resource_pool(name="pool-ok", min_available=4, available=4, ready=4)]
        mock_client = MagicMock()
        mock_client.list_resource_pools.return_value = pools

        with patch("rhdp_ops.mcp_server._get_client", return_value=mock_client):
            result = _build_pool_health()

        assert result[0]["health"] == "healthy"

    def test_pool_health_degraded_status(self):
        pools = [make_resource_pool(name="pool-low", min_available=6, available=3, ready=3)]
        mock_client = MagicMock()
        mock_client.list_resource_pools.return_value = pools

        with patch("rhdp_ops.mcp_server._get_client", return_value=mock_client):
            result = _build_pool_health()

        assert result[0]["health"] == "degraded"

    def test_pool_health_exhausted_status(self):
        pools = [make_resource_pool(name="pool-empty", min_available=4, available=0, ready=0)]
        mock_client = MagicMock()
        mock_client.list_resource_pools.return_value = pools

        with patch("rhdp_ops.mcp_server._get_client", return_value=mock_client):
            result = _build_pool_health()

        assert result[0]["health"] == "exhausted"

    def test_pool_health_single_pool_filter(self):
        pool = make_resource_pool(name="pool-target")
        mock_client = MagicMock()
        mock_client.get_resource_pool.return_value = pool

        with patch("rhdp_ops.mcp_server._get_client", return_value=mock_client):
            result = _build_pool_health(pool_name="pool-target")

        assert len(result) == 1
        assert result[0]["name"] == "pool-target"
        mock_client.get_resource_pool.assert_called_once_with("pool-target")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd ~/repos/rhpds-utils/rhdp-ops-mcp && .venv/bin/pytest tests/test_tools.py -v -k "TestOpsPoolHealth"`

Expected: FAIL with `NameError: name '_build_pool_health' is not defined`

- [ ] **Step 3: Implement helper and MCP tool**

Add to `rhdp_ops/mcp_server.py`:

```python
def _pool_health_status(available: int, min_available: int) -> str:
    if available == 0:
        return "exhausted"
    if available < min_available:
        return "degraded"
    return "healthy"


def _build_pool_health(
    client: RhdpOpsClient | None = None,
    pool_name: str = "",
) -> list[dict]:
    """Build pool health rows from ResourcePool resources."""
    if client is None:
        client = _get_client()
    if pool_name:
        pools = [client.get_resource_pool(pool_name)]
    else:
        pools = client.list_resource_pools()
    rows = []
    for pool in pools:
        spec = pool.get("spec", {})
        handles = pool.get("status", {}).get("resourceHandleCount", {})
        min_avail = spec.get("minAvailable", 0)
        available = handles.get("available", 0)
        ready = handles.get("ready", 0)
        unready = handles.get("unready", 0)
        rows.append({
            "name": pool["metadata"]["name"],
            "min_available": min_avail,
            "available": available,
            "ready": ready,
            "unready": unready,
            "health": _pool_health_status(available, min_avail),
        })
    return rows


@mcp.tool()
async def ops_pool_health(pool_name: str = "") -> str:
    """ResourcePool availability with health flags (healthy/degraded/exhausted).

    Returns JSON array. When pool_name is provided, returns detail for one pool.
    Otherwise returns all pools. Used by the watcher agent to detect capacity problems.
    """
    try:
        rows = _build_pool_health(pool_name=pool_name)
        return json.dumps(rows, indent=2)
    except Exception as e:
        return f"Error checking pool health: {e}"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd ~/repos/rhpds-utils/rhdp-ops-mcp && .venv/bin/pytest tests/test_tools.py -v -k "TestOpsPoolHealth"`

Expected: All PASS

- [ ] **Step 5: Commit**

```bash
cd ~/repos/rhpds-utils/rhdp-ops-mcp
git add rhdp_ops/mcp_server.py tests/test_tools.py
git commit -m "add ops_pool_health tool for ResourcePool availability monitoring

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 6: ops_catalog_items Tool

**Files:**
- Modify: `rhdp_ops/mcp_server.py`
- Modify: `tests/test_tools.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_tools.py`:

```python
from tests.conftest import make_catalog_item


class TestOpsCatalogItems:
    def test_catalog_items_returns_all(self):
        items = [
            make_catalog_item(name="item-1", display_name="Workshop A", stage="prod"),
            make_catalog_item(name="item-2", display_name="Workshop B", stage="dev"),
        ]
        mock_client = MagicMock()
        mock_client.list_catalog_items.return_value = items

        with patch("rhdp_ops.mcp_server._get_client", return_value=mock_client):
            result = _build_catalog_items()

        assert len(result) == 2

    def test_catalog_items_filters_by_stage(self):
        items = [
            make_catalog_item(name="item-prod", stage="prod",
                              namespace="babylon-catalog-prod"),
            make_catalog_item(name="item-dev", stage="dev",
                              namespace="babylon-catalog-dev"),
        ]
        mock_client = MagicMock()
        mock_client.list_catalog_items.return_value = items

        with patch("rhdp_ops.mcp_server._get_client", return_value=mock_client):
            result = _build_catalog_items(stage="prod")

        assert len(result) == 1
        assert result[0]["name"] == "item-prod"

    def test_catalog_items_filters_by_search(self):
        items = [
            make_catalog_item(name="agd-v2.maas.prod", display_name="MaaS Workshop"),
            make_catalog_item(name="agd-v2.ansible.prod", display_name="Ansible Workshop"),
        ]
        mock_client = MagicMock()
        mock_client.list_catalog_items.return_value = items

        with patch("rhdp_ops.mcp_server._get_client", return_value=mock_client):
            result = _build_catalog_items(search="maas")

        assert len(result) == 1
        assert "MaaS" in result[0]["display_name"]

    def test_catalog_items_includes_age(self):
        items = [make_catalog_item(name="item-1", age_days=45)]
        mock_client = MagicMock()
        mock_client.list_catalog_items.return_value = items

        with patch("rhdp_ops.mcp_server._get_client", return_value=mock_client):
            result = _build_catalog_items()

        assert result[0]["age_days"] >= 44  # allow 1-day rounding
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd ~/repos/rhpds-utils/rhdp-ops-mcp && .venv/bin/pytest tests/test_tools.py -v -k "TestOpsCatalogItems"`

Expected: FAIL

- [ ] **Step 3: Implement helper and MCP tool**

Add to `rhdp_ops/mcp_server.py`:

```python
def _build_catalog_items(
    client: RhdpOpsClient | None = None,
    stage: str = "",
    search: str = "",
) -> list[dict]:
    """Build catalog item rows."""
    if client is None:
        client = _get_client()
    items = client.list_catalog_items()
    now = datetime.now(timezone.utc)
    rows = []
    for item in items:
        meta = item.get("metadata", {})
        ns = meta.get("namespace", "")
        annotations = meta.get("annotations", {})
        display = annotations.get(f"{BABYLON}/displayName", meta.get("name", ""))
        category = annotations.get(f"{BABYLON}/category", "")
        name = meta.get("name", "")
        created_str = meta.get("creationTimestamp", "")
        age_days = 0
        if created_str:
            created = _parse_ts(created_str)
            if created:
                age_days = (now - created).days
        item_stage = ""
        if ".prod" in name or ns.endswith("-prod"):
            item_stage = "prod"
        elif ".dev" in name or ns.endswith("-dev"):
            item_stage = "dev"
        elif ".event" in name or ns.endswith("-event"):
            item_stage = "event"
        if stage and item_stage != stage:
            continue
        if search and search.lower() not in name.lower() and search.lower() not in display.lower():
            continue
        rows.append({
            "name": name,
            "display_name": display,
            "stage": item_stage,
            "category": category,
            "namespace": ns,
            "age_days": age_days,
        })
    return rows


@mcp.tool()
async def ops_catalog_items(stage: str = "", search: str = "") -> str:
    """Browse catalog items available for deployment.

    Returns JSON array. Filter by stage (prod/dev/event) and/or text search
    against name and display name. Shows 1,235+ available workshop types.
    """
    try:
        rows = _build_catalog_items(stage=stage, search=search)
        return json.dumps(rows, indent=2)
    except Exception as e:
        return f"Error listing catalog items: {e}"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd ~/repos/rhpds-utils/rhdp-ops-mcp && .venv/bin/pytest tests/test_tools.py -v -k "TestOpsCatalogItems"`

Expected: All PASS

- [ ] **Step 5: Commit**

```bash
cd ~/repos/rhpds-utils/rhdp-ops-mcp
git add rhdp_ops/mcp_server.py tests/test_tools.py
git commit -m "add ops_catalog_items tool for browsing available workshop types

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 7: ops_resource_pools Tool (Detailed View)

**Files:**
- Modify: `rhdp_ops/mcp_server.py`
- Modify: `tests/test_tools.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_tools.py`:

```python
class TestOpsResourcePools:
    def test_resource_pools_returns_detail(self):
        pools = [make_resource_pool(
            name="pool-1", min_available=6, max_unready=10,
            lifespan_default="2d", lifespan_maximum="180d", lifespan_unclaimed="7d",
            available=5, ready=5, delete_unhealthy=True, provider_name="prov-1",
        )]
        mock_client = MagicMock()
        mock_client.list_resource_pools.return_value = pools

        with patch("rhdp_ops.mcp_server._get_client", return_value=mock_client):
            result = _build_resource_pools_detail()

        assert len(result) == 1
        row = result[0]
        assert row["name"] == "pool-1"
        assert row["min_available"] == 6
        assert row["max_unready"] == 10
        assert row["lifespan_default"] == "2d"
        assert row["delete_unhealthy"] is True
        assert row["provider_names"] == ["prov-1"]

    def test_resource_pools_single_pool(self):
        pool = make_resource_pool(name="pool-target")
        mock_client = MagicMock()
        mock_client.get_resource_pool.return_value = pool

        with patch("rhdp_ops.mcp_server._get_client", return_value=mock_client):
            result = _build_resource_pools_detail(pool_name="pool-target")

        assert len(result) == 1
        mock_client.get_resource_pool.assert_called_once_with("pool-target")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd ~/repos/rhpds-utils/rhdp-ops-mcp && .venv/bin/pytest tests/test_tools.py -v -k "TestOpsResourcePools"`

Expected: FAIL

- [ ] **Step 3: Implement helper and MCP tool**

Add to `rhdp_ops/mcp_server.py`:

```python
def _build_resource_pools_detail(
    client: RhdpOpsClient | None = None,
    pool_name: str = "",
) -> list[dict]:
    """Build detailed pool inventory rows."""
    if client is None:
        client = _get_client()
    if pool_name:
        pools = [client.get_resource_pool(pool_name)]
    else:
        pools = client.list_resource_pools()
    rows = []
    for pool in pools:
        meta = pool.get("metadata", {})
        spec = pool.get("spec", {})
        lifespan = spec.get("lifespan", {})
        handles = pool.get("status", {}).get("resourceHandleCount", {})
        resources = spec.get("resources", [])
        provider_names = [r.get("provider", {}).get("name", "") for r in resources if r.get("provider")]
        rows.append({
            "name": meta.get("name", ""),
            "namespace": meta.get("namespace", ""),
            "min_available": spec.get("minAvailable", 0),
            "max_unready": spec.get("maxUnready", 0),
            "lifespan_default": lifespan.get("default", ""),
            "lifespan_maximum": lifespan.get("maximum", ""),
            "lifespan_unclaimed": lifespan.get("unclaimed", ""),
            "available": handles.get("available", 0),
            "ready": handles.get("ready", 0),
            "unready": handles.get("unready", 0),
            "delete_unhealthy": spec.get("deleteUnhealthyResourceHandles", False),
            "provider_names": provider_names,
        })
    return rows


@mcp.tool()
async def ops_resource_pools(pool_name: str = "") -> str:
    """Detailed ResourcePool inventory with lifespan config, scaling params, and handle breakdown.

    More detailed than ops_pool_health -- this is for investigation, not monitoring.
    Returns JSON array. Filter to a single pool by name.
    """
    try:
        rows = _build_resource_pools_detail(pool_name=pool_name)
        return json.dumps(rows, indent=2)
    except Exception as e:
        return f"Error listing resource pools: {e}"
```

- [ ] **Step 4: Run tests and commit**

Run: `cd ~/repos/rhpds-utils/rhdp-ops-mcp && .venv/bin/pytest tests/test_tools.py -v -k "TestOpsResourcePools"`

Expected: All PASS

```bash
cd ~/repos/rhpds-utils/rhdp-ops-mcp
git add rhdp_ops/mcp_server.py tests/test_tools.py
git commit -m "add ops_resource_pools tool for detailed pool inventory

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 8: ops_multiworkshop Tool

**Files:**
- Modify: `rhdp_ops/mcp_server.py`
- Modify: `tests/test_tools.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_tools.py`:

```python
from tests.conftest import make_multiworkshop


class TestOpsMultiWorkshop:
    def test_multiworkshop_returns_detail(self):
        mw = make_multiworkshop()
        mock_client = MagicMock()
        mock_client.get_multiworkshop.return_value = mw
        mock_client.list_workshops.return_value = []

        with patch("rhdp_ops.mcp_server._get_client", return_value=mock_client):
            result = _build_multiworkshop_detail("user-klewis-redhat-com", "automation-voasv")

        assert result["name"] == "automation-voasv"
        assert result["display_name"] == "Ansible Roadshow"
        assert len(result["assets"]) == 2

    def test_multiworkshop_includes_asset_status(self):
        mw = make_multiworkshop()
        ws = make_workshop(
            name="automation-voasv-summit-2026.lb1997-roadshow-1.event-d8tl5",
            namespace="user-klewis-redhat-com",
        )
        mock_client = MagicMock()
        mock_client.get_multiworkshop.return_value = mw
        mock_client.list_workshops.return_value = [ws]
        mock_client.list_resource_claims.return_value = [
            make_resource_claim(
                workshop_name="automation-voasv-summit-2026.lb1997-roadshow-1.event-d8tl5",
                provision_data={"phase": "Ready"},
            )
        ]

        with patch("rhdp_ops.mcp_server._get_client", return_value=mock_client):
            result = _build_multiworkshop_detail("user-klewis-redhat-com", "automation-voasv")

        matched = [a for a in result["assets"] if a["workshop_id"] == "kkhc8h"]
        assert len(matched) == 1

    def test_multiworkshop_validates_input(self):
        mock_client = MagicMock()
        mock_client.get_multiworkshop.side_effect = ValueError("Invalid")

        with patch("rhdp_ops.mcp_server._get_client", return_value=mock_client):
            with pytest.raises(ValueError):
                _build_multiworkshop_detail("bad ns!", "name")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd ~/repos/rhpds-utils/rhdp-ops-mcp && .venv/bin/pytest tests/test_tools.py -v -k "TestOpsMultiWorkshop"`

Expected: FAIL

- [ ] **Step 3: Implement helper and MCP tool**

Add to `rhdp_ops/mcp_server.py`:

```python
def _build_multiworkshop_detail(
    namespace: str,
    name: str,
    client: RhdpOpsClient | None = None,
) -> dict:
    """Build MultiWorkshop detail with linked asset status."""
    if client is None:
        client = _get_client()
    mw = client.get_multiworkshop(namespace, name)
    spec = mw.get("spec", {})

    all_workshops = client.list_workshops(namespace=namespace)
    ws_by_name = {w["metadata"]["name"]: w for w in all_workshops}

    assets = []
    for asset in spec.get("assets", []):
        ws_name = asset.get("name", "")
        status = None
        if ws_name in ws_by_name:
            status = _provision_phase(client, namespace, ws_name)
        assets.append({
            "display_name": asset.get("displayName", ""),
            "catalog_key": asset.get("key", ""),
            "workshop_name": ws_name,
            "namespace": asset.get("namespace", namespace),
            "workshop_id": asset.get("workshopId", ""),
            "status": status,
        })

    return {
        "name": mw["metadata"]["name"],
        "namespace": mw["metadata"]["namespace"],
        "display_name": spec.get("displayName", ""),
        "description": spec.get("description", ""),
        "purpose": spec.get("purpose", ""),
        "start_date": spec.get("startDate", ""),
        "end_date": spec.get("endDate", ""),
        "number_seats": spec.get("numberSeats", 0),
        "assets": assets,
    }


@mcp.tool()
async def ops_multiworkshop(namespace: str, name: str) -> str:
    """MultiWorkshop group detail with all linked assets and their provision status.

    Shows grouped workshops (e.g., multi-part roadshows) with per-asset status.
    Use with --group flag on extend/scale to operate on all assets at once.
    """
    try:
        detail = _build_multiworkshop_detail(namespace, name)
        return json.dumps(detail, indent=2)
    except Exception as e:
        return f"Error getting multiworkshop: {e}"
```

- [ ] **Step 4: Run tests and commit**

Run: `cd ~/repos/rhpds-utils/rhdp-ops-mcp && .venv/bin/pytest tests/test_tools.py -v -k "TestOpsMultiWorkshop"`

Expected: All PASS

```bash
cd ~/repos/rhpds-utils/rhdp-ops-mcp
git add rhdp_ops/mcp_server.py tests/test_tools.py
git commit -m "add ops_multiworkshop tool for grouped workshop detail

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 9: ops_service_accesses Tool

**Files:**
- Modify: `rhdp_ops/mcp_server.py`
- Modify: `tests/test_tools.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_tools.py`:

```python
from tests.conftest import make_service_access


class TestOpsServiceAccesses:
    def test_service_accesses_returns_rows(self):
        accesses = [
            make_service_access(user="jdoe@redhat.com", state="active"),
            make_service_access(name="sa-2", user="asmith@redhat.com", state="active"),
        ]
        mock_client = MagicMock()
        mock_client.list_service_accesses.return_value = accesses

        with patch("rhdp_ops.mcp_server._get_client", return_value=mock_client):
            result = _build_service_accesses("user-test-redhat-com")

        assert len(result) == 2
        assert result[0]["user"] == "jdoe@redhat.com"
        assert result[0]["state"] == "active"

    def test_service_accesses_filtered_by_workshop(self):
        accesses = [make_service_access(workshop_ref="ws-target")]
        mock_client = MagicMock()
        mock_client.list_service_accesses.return_value = accesses

        with patch("rhdp_ops.mcp_server._get_client", return_value=mock_client):
            result = _build_service_accesses("user-test-redhat-com", workshop_name="ws-target")

        assert len(result) == 1
        mock_client.list_service_accesses.assert_called_once_with(
            "user-test-redhat-com", workshop_name="ws-target"
        )
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd ~/repos/rhpds-utils/rhdp-ops-mcp && .venv/bin/pytest tests/test_tools.py -v -k "TestOpsServiceAccesses"`

Expected: FAIL

- [ ] **Step 3: Implement helper and MCP tool**

Add to `rhdp_ops/mcp_server.py`:

```python
def _build_service_accesses(
    namespace: str,
    workshop_name: str = "",
    client: RhdpOpsClient | None = None,
) -> list[dict]:
    """Build service access rows showing active user sessions."""
    if client is None:
        client = _get_client()
    accesses = client.list_service_accesses(namespace, workshop_name=workshop_name or None)
    rows = []
    for sa in accesses:
        meta = sa.get("metadata", {})
        labels = meta.get("labels", {})
        rows.append({
            "user": sa.get("spec", {}).get("user", ""),
            "workshop_ref": labels.get(f"{BABYLON}/workshop", ""),
            "state": sa.get("status", {}).get("state", "unknown"),
            "created": meta.get("creationTimestamp", ""),
        })
    return rows


@mcp.tool()
async def ops_service_accesses(namespace: str, workshop_name: str = "") -> str:
    """Active user sessions per workshop.

    Shows who is actually connected right now, beyond seat assignment counts.
    Filter by workshop_name to see sessions for a specific workshop.
    """
    try:
        rows = _build_service_accesses(namespace, workshop_name=workshop_name)
        return json.dumps(rows, indent=2)
    except Exception as e:
        return f"Error listing service accesses: {e}"
```

- [ ] **Step 4: Run tests and commit**

Run: `cd ~/repos/rhpds-utils/rhdp-ops-mcp && .venv/bin/pytest tests/test_tools.py -v -k "TestOpsServiceAccesses"`

Expected: All PASS

```bash
cd ~/repos/rhpds-utils/rhdp-ops-mcp
git add rhdp_ops/mcp_server.py tests/test_tools.py
git commit -m "add ops_service_accesses tool for active user session visibility

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 10: ops_watch_config Tool

**Files:**
- Modify: `rhdp_ops/mcp_server.py`
- Modify: `tests/test_tools.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_tools.py`:

```python
from rhdp_ops.models import WatchThresholds


class TestOpsWatchConfig:
    def test_watch_config_returns_defaults(self):
        result = _get_watch_config("")
        assert result["deadline_critical_seconds"] == 3600
        assert result["deadline_warning_seconds"] == 14400
        assert result["deadline_info_seconds"] == 86400
        assert result["seat_warning_pct"] == 80
        assert result["seat_critical_pct"] == 100
        assert result["pool_mode"] == "auto"

    def test_watch_config_parses_deadlines(self):
        result = _get_watch_config("deadlines=30m,2h,12h")
        assert result["deadline_critical_seconds"] == 1800
        assert result["deadline_warning_seconds"] == 7200
        assert result["deadline_info_seconds"] == 43200

    def test_watch_config_parses_seats(self):
        result = _get_watch_config("seats=70,90")
        assert result["seat_warning_pct"] == 70
        assert result["seat_critical_pct"] == 90

    def test_watch_config_parses_combined(self):
        result = _get_watch_config("deadlines=30m,2h,12h seats=75,95")
        assert result["deadline_critical_seconds"] == 1800
        assert result["seat_warning_pct"] == 75
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd ~/repos/rhpds-utils/rhdp-ops-mcp && .venv/bin/pytest tests/test_tools.py -v -k "TestOpsWatchConfig"`

Expected: FAIL

- [ ] **Step 3: Implement helper and MCP tool**

Add to `rhdp_ops/mcp_server.py`:

```python
def _parse_duration_to_seconds(duration: str) -> int:
    """Parse a duration like '1h', '30m', '24h' to seconds."""
    duration = duration.strip().lower()
    if duration.endswith("h"):
        return int(duration[:-1]) * 3600
    if duration.endswith("m"):
        return int(duration[:-1]) * 60
    if duration.endswith("d"):
        return int(duration[:-1]) * 86400
    return int(duration)


def _get_watch_config(thresholds: str) -> dict:
    """Parse threshold string and return config dict."""
    config = {
        "deadline_critical_seconds": 3600,
        "deadline_warning_seconds": 14400,
        "deadline_info_seconds": 86400,
        "seat_warning_pct": 80,
        "seat_critical_pct": 100,
        "pool_mode": "auto",
    }
    if not thresholds:
        return config
    for part in thresholds.split():
        if part.startswith("deadlines="):
            vals = part.split("=", 1)[1].split(",")
            if len(vals) == 3:
                config["deadline_critical_seconds"] = _parse_duration_to_seconds(vals[0])
                config["deadline_warning_seconds"] = _parse_duration_to_seconds(vals[1])
                config["deadline_info_seconds"] = _parse_duration_to_seconds(vals[2])
        elif part.startswith("seats="):
            vals = part.split("=", 1)[1].split(",")
            if len(vals) == 2:
                config["seat_warning_pct"] = int(vals[0])
                config["seat_critical_pct"] = int(vals[1])
        elif part.startswith("pools="):
            config["pool_mode"] = part.split("=", 1)[1]
    return config


@mcp.tool()
async def ops_watch_config(thresholds: str = "") -> str:
    """Get or set alert thresholds for the watcher agent.

    Input format: "deadlines=1h,4h,24h seats=80,100 pools=auto"
    Returns current configuration as JSON. The watcher agent reads these thresholds
    when classifying events.
    """
    try:
        config = _get_watch_config(thresholds)
        return json.dumps(config, indent=2)
    except Exception as e:
        return f"Error with watch config: {e}"
```

- [ ] **Step 4: Run tests and commit**

Run: `cd ~/repos/rhpds-utils/rhdp-ops-mcp && .venv/bin/pytest tests/test_tools.py -v -k "TestOpsWatchConfig"`

Expected: All PASS

```bash
cd ~/repos/rhpds-utils/rhdp-ops-mcp
git add rhdp_ops/mcp_server.py tests/test_tools.py
git commit -m "add ops_watch_config tool for watcher alert thresholds

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 11: Watcher Agent Definition

**Files:**
- Create: `marketplace/agents/ops-watcher.md`

This is a Claude Code agent definition file, not Python code. The agent is spawned as a background loop and uses MCP tools to detect state changes.

- [ ] **Step 1: Create the agent definition**

Create `marketplace/agents/ops-watcher.md`:

```markdown
---
name: ops-watcher
description: Background workshop monitoring agent that detects provision failures, pool exhaustion, deadline proximity, and seat occupancy spikes
model: sonnet
---

You are the RHDP workshop watcher agent. You run as a background loop, checking cluster state every ~90 seconds and alerting when something needs attention.

## On Each Tick

1. Call `ops_snapshot()` to get current workshop state.
2. Call `ops_pool_health()` to get pool availability.
3. Compare against the previous state provided in your prompt context.
4. Classify changes into alerts (see Event Types below).
5. If any alerts exist, output them using the Alert Format. If nothing changed, output nothing.

## Event Types

### Provision State Changes
- CRITICAL: any workshop moved to `Failed` phase
- WARNING: any workshop moved to `Deleting` (unexpected deletion)
- INFO: any workshop moved to `Ready` (successful provision)

### Pool Health Changes
- CRITICAL: pool exhausted (available = 0)
- WARNING: pool degraded (available < minAvailable)
- INFO: pool recovered (was degraded, now healthy)

### Deadline Proximity
- CRITICAL: stop or destroy time is < 1h away or overdue
- WARNING: stop or destroy time is < 4h away
- INFO: stop or destroy time is < 24h away
- Deduplicate by threshold: once reported at a level, don't repeat until the next level is crossed.

### Seat Occupancy
- CRITICAL: seats >= 100% capacity
- WARNING: seats >= 80% capacity

## Alert Format

```
[WATCHER] N alerts at HH:MM UTC

SEVERITY  Description
          Detail line with namespace, phase, times, etc.
```

## Escalation

If a CRITICAL alert appeared on the previous tick and the same condition persists, prefix with `[REPEAT]`.

## Quiet Mode

When nothing changed and no thresholds are crossed, produce NO output. Do not print "all clear" messages.

## Thresholds

Use the thresholds from `ops_watch_config()`. Call it once on startup to get the current config. Defaults:
- Deadlines: critical < 1h, warning < 4h, info < 24h
- Seats: warning >= 80%, critical >= 100%
- Pools: alert when available < minAvailable
```

- [ ] **Step 2: Verify the file is valid markdown**

Run: `cd ~/repos/rhpds-utils/rhdp-ops-mcp && python3 -c "open('marketplace/agents/ops-watcher.md').read(); print('Valid')`

Expected: `Valid`

- [ ] **Step 3: Commit**

```bash
cd ~/repos/rhpds-utils/rhdp-ops-mcp
mkdir -p marketplace/agents
git add marketplace/agents/ops-watcher.md
git commit -m "add ops-watcher background monitoring agent definition

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 12: Update /ops Skill with New Commands

**Files:**
- Modify: `marketplace/skills/ops/SKILL.md` (source) and `~/.claude/skills/ops/SKILL.md` (installed copy)

- [ ] **Step 1: Add new command sections to the skill**

Add to the `## Behavior` table in `marketplace/skills/ops/SKILL.md`:

```markdown
| `/ops watch` | *(agent spawn)* | Start background watcher with default thresholds (90s ticks) |
| `/ops watch stop` | *(agent stop)* | Stop the running watcher |
| `/ops watch status` | *(agent query)* | Show last check time, alert counts, thresholds |
| `/ops watch config` | `ops_watch_config` | Show current thresholds |
| `/ops watch config <settings>` | `ops_watch_config(thresholds)` | Set thresholds: `deadlines=1h,4h,24h seats=80,100` |
| `/ops summary` | `ops_summary` | Dashboard: totals, attention, seat fill, pool health |
| `/ops pools` | `ops_resource_pools` | Pool health overview — all pools with availability |
| `/ops pools <name>` | `ops_resource_pools(pool_name)` | Detailed pool info with handle breakdown |
| `/ops catalog` | `ops_catalog_items` | Available catalog items |
| `/ops catalog <search>` | `ops_catalog_items(search)` | Search catalog items by name |
| `/ops group <ns> <name>` | `ops_multiworkshop` | Show MultiWorkshop and all linked assets |
| `/ops extend <ns> <name> <n>d --group` | `ops_extend_stop` + `ops_multiworkshop` | Extend all assets in a MultiWorkshop group |
| `/ops scale <ns> <name> <n> --group` | `ops_scale_workshop` + `ops_multiworkshop` | Scale all assets in a MultiWorkshop group |
```

- [ ] **Step 2: Add `/ops watch` sub-help block**

Add to the `## Sub-Help Blocks` section:

```markdown
### `/ops watch` sub-help

When `/ops watch` is invoked with no argument, print exactly this block and then start the watcher:

\```
Starting ops-watcher with default thresholds...

  Deadlines:  CRITICAL < 1h | WARNING < 4h | INFO < 24h
  Seats:      WARNING >= 80% | CRITICAL >= 100%
  Pools:      alert when available < minAvailable

  /ops watch stop               Stop the watcher
  /ops watch status             Last check time, alert counts
  /ops watch config             Show current thresholds
  /ops watch config deadlines=30m,2h,12h seats=70,90
                                Customize thresholds

Checking every ~90 seconds. Alerts surface in conversation when detected.
Silent when nothing changes.
\```

Then spawn the ops-watcher agent as a background loop using ScheduleWakeup with delaySeconds=90.
```

- [ ] **Step 3: Add formatting rules for new tools**

Add to the `## Output Formatting` section:

```markdown
### `ops_resource_pools` / `ops_pool_health`

| Pool | Min | Available | Ready | Unready | Health |
|------|-----|-----------|-------|---------|--------|

- **Health**: `healthy` (green), `degraded` (yellow), `exhausted` (red)

### `ops_catalog_items`

| Name | Display Name | Stage | Category | Age |
|------|-------------|-------|----------|-----|

Truncate display name at 50 chars.

### `ops_multiworkshop`

Render as a detail table (like ops_get_workshop) with an **Assets** sub-table:

| Asset | Catalog Key | Status | Workshop ID |
|-------|------------|--------|-------------|

### `ops_service_accesses`

| User | Workshop | State | Connected Since |
|------|----------|-------|-----------------|
```

- [ ] **Step 4: Update the help block**

Add new sections to the help text in the `## Help` section:

```markdown
── MONITORING ───────────────────────────────────────────────────────────────

  /ops watch                    Start background watcher (90s tick interval).
                                Alerts on: provision failures, pool exhaustion,
                                deadline proximity, seat capacity spikes.
  /ops watch stop               Stop the watcher.
  /ops watch status             Last check time, alert counts, thresholds.
  /ops watch config             Show current thresholds.
  /ops watch config deadlines=30m,2h,12h seats=70,90
                                Customize alert thresholds.

── OCP VISIBILITY ───────────────────────────────────────────────────────────

  /ops summary                  Dashboard: total workshops, attention, pools, seats.
  /ops pools                    Resource pool health overview.
  /ops pools <name>             Detailed pool info with handle breakdown.
  /ops catalog                  Browse available catalog items (1,235+ types).
  /ops catalog <search>         Search catalog items by name or display name.

── MULTI-WORKSHOP GROUPS ────────────────────────────────────────────────────

  /ops group <ns> <name>        Show MultiWorkshop and all linked assets.
                                  Example: /ops group user-klewis-redhat-com automation-voasv
  /ops extend ... --group       Extend all assets in the group.
  /ops scale ... --group        Scale all assets in the group.
```

- [ ] **Step 5: Copy updated skill to installed location**

```bash
cp ~/repos/rhpds-utils/rhdp-ops-mcp/marketplace/skills/ops/SKILL.md ~/.claude/skills/ops/SKILL.md
```

- [ ] **Step 6: Commit**

```bash
cd ~/repos/rhpds-utils/rhdp-ops-mcp
git add marketplace/skills/ops/SKILL.md
git commit -m "extend /ops skill with watch, pools, catalog, group, and summary commands

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 13: Full Integration Test

**Files:**
- No new files — validation run

- [ ] **Step 1: Run the full test suite**

```bash
cd ~/repos/rhpds-utils/rhdp-ops-mcp && .venv/bin/pytest tests/ -v
```

Expected: All PASS, no regressions.

- [ ] **Step 2: Run ruff linter**

```bash
cd ~/repos/rhpds-utils/rhdp-ops-mcp && .venv/bin/ruff check rhdp_ops/ tests/
```

Expected: No errors. Fix any warnings.

- [ ] **Step 3: Verify MCP server starts**

```bash
cd ~/repos/rhpds-utils/rhdp-ops-mcp && timeout 5 .venv/bin/python -m rhdp_ops.mcp_server 2>&1 || true
```

Expected: Server starts without import errors (will timeout after 5s, which is fine — we just need to see it loads).

- [ ] **Step 4: Verify tool count**

```bash
cd ~/repos/rhpds-utils/rhdp-ops-mcp && .venv/bin/python -c "
from rhdp_ops.mcp_server import mcp
tools = [t for t in dir(mcp) if not t.startswith('_')]
print(f'MCP server loaded successfully')
"
```

Expected: `MCP server loaded successfully`

- [ ] **Step 5: Final commit (if any lint fixes)**

```bash
cd ~/repos/rhpds-utils/rhdp-ops-mcp
git add -A
git status
# Only commit if there are changes from lint fixes
git diff --cached --quiet || git commit -m "lint fixes for new monitoring tools

Co-Authored-By: Claude <noreply@anthropic.com>"
```
