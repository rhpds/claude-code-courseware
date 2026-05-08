"""Tests for the Flow API client."""

import httpx
import pytest

from rhdp_flow_mcp.api_client import FlowApiClient

API_URL = "http://localhost:8000"


def make_transport(routes: dict[tuple[str, str], httpx.Response | Exception]):
    """Create a mock transport that matches (method, path) to responses."""

    async def handler(request: httpx.Request) -> httpx.Response:
        key = (request.method, request.url.path)
        match = routes.get(key)
        if match is None:
            raise AssertionError(f"Unmocked request: {request.method} {request.url}")
        if isinstance(match, Exception):
            raise match
        return match

    return httpx.MockTransport(handler)


@pytest.fixture
def make_client():
    def _make(routes: dict[tuple[str, str], httpx.Response | Exception]):
        transport = make_transport(routes)
        return FlowApiClient(API_URL, transport=transport)
    return _make


class TestHealth:
    @pytest.mark.asyncio
    async def test_health_ok(self, make_client, sample_health_response):
        client = make_client({
            ("GET", "/api/health"): httpx.Response(200, json=sample_health_response),
        })
        result = await client.health()
        assert result["status"] == "ok"
        assert result["oc_connected"] is True

    @pytest.mark.asyncio
    async def test_health_unreachable(self, make_client):
        client = make_client({
            ("GET", "/api/health"): httpx.ConnectError("refused"),
        })
        result = await client.health()
        assert result["status"] == "error"


class TestCatalogItems:
    @pytest.mark.asyncio
    async def test_list_catalog_items(self, make_client, sample_catalog_items):
        client = make_client({
            ("GET", "/api/catalog/items"): httpx.Response(200, json=sample_catalog_items),
        })
        result = await client.catalog_items()
        assert len(result) == 2
        assert result[0]["id"] == "openshift-cnv.ocp-virt-roadshow-multi-user.prod"


class TestPools:
    @pytest.mark.asyncio
    async def test_list_pools(self, make_client, sample_pools):
        client = make_client({
            ("GET", "/api/pools/all"): httpx.Response(200, json=sample_pools),
        })
        result = await client.pools()
        assert len(result["pools"]) == 1

    @pytest.mark.asyncio
    async def test_pool_lookup(self, make_client):
        pool_resp = {"catalog_item": "test.prod", "has_pool": True, "pool": {"pool_name": "test-pool", "ready": 5}}
        client = make_client({
            ("GET", "/api/pools/lookup"): httpx.Response(200, json=pool_resp),
        })
        result = await client.pool_lookup("test.prod")
        assert result["has_pool"] is True


class TestUpload:
    @pytest.mark.asyncio
    async def test_upload_csv(self, make_client):
        upload_resp = {"count": 1, "total_rows": 1, "skipped_rows": 0, "schedules": []}
        client = make_client({
            ("POST", "/api/schedules/upload"): httpx.Response(200, json=upload_resp),
        })
        result = await client.upload_csv("CI Name,CI\nTest,test.prod")
        assert result["count"] == 1


class TestDeploy:
    @pytest.mark.asyncio
    async def test_deploy(self, make_client):
        deploy_resp = {"job_id": "abc123", "status": "running", "progress": 0}
        client = make_client({
            ("POST", "/api/deploy"): httpx.Response(200, json=deploy_resp),
        })
        result = await client.deploy(dry_run=False)
        assert result["job_id"] == "abc123"

    @pytest.mark.asyncio
    async def test_deploy_status(self, make_client):
        client = make_client({
            ("GET", "/api/results"): httpx.Response(200, json=[]),
        })
        result = await client.deploy_status()
        assert result == []


class TestOperations:
    @pytest.mark.asyncio
    async def test_lock(self, make_client):
        client = make_client({
            ("POST", "/api/operations/lock"): httpx.Response(200, json={"success": True, "message": "Locked"}),
        })
        result = await client.operation("lock")
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_extend_stop(self, make_client):
        client = make_client({
            ("POST", "/api/operations/extend-stop"): httpx.Response(200, json={"success": True, "message": "Extended"}),
        })
        result = await client.operation("extend-stop", days=3, hours=0)
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_scale(self, make_client):
        client = make_client({
            ("POST", "/api/operations/scale"): httpx.Response(200, json={"success": True, "message": "Scaled"}),
        })
        result = await client.operation("scale", target_count=50)
        assert result["success"] is True
