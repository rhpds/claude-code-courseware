"""Tests for the 5 new rhdp-flow-mcp API client methods."""

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


def make_client(routes: dict[tuple[str, str], httpx.Response | Exception]):
    transport = make_transport(routes)
    return FlowApiClient(API_URL, transport=transport)


class TestValidateCatalogNamespacesFull:
    @pytest.mark.asyncio
    async def test_returns_validation_and_catalog(self):
        client = make_client({
            ("POST", "/api/schedules/validate-catalog-namespaces"): httpx.Response(
                200, json={"results": [{"ci": "test.event", "status": "ok"}]}
            ),
            ("GET", "/api/catalog/items"): httpx.Response(
                200, json=[{"id": "test.event", "display_name": "Test"}]
            ),
        })
        result = await client.validate_catalog_namespaces_full()
        assert "validation" in result
        assert "catalog_items" in result
        assert result["catalog_items"] == ["test.event"]


class TestPreDeploymentChecklist:
    @pytest.mark.asyncio
    async def test_all_pass(self):
        client = make_client({
            ("GET", "/api/health"): httpx.Response(200, json={"status": "ok"}),
            ("POST", "/api/schedules/validate-catalog-namespaces"): httpx.Response(
                200, json={"results": []}
            ),
            ("GET", "/api/pools/all"): httpx.Response(200, json={"pools": []}),
        })
        result = await client.pre_deployment_checklist()
        assert result["ready_to_deploy"] is True
        assert result["health"]["status"] == "pass"
        assert result["catalog_namespaces"]["status"] == "pass"
        assert result["pools"]["status"] == "pass"

    @pytest.mark.asyncio
    async def test_health_fail(self):
        client = make_client({
            ("GET", "/api/health"): httpx.Response(500, json={"error": "down"}),
            ("POST", "/api/schedules/validate-catalog-namespaces"): httpx.Response(
                200, json={"results": []}
            ),
            ("GET", "/api/pools/all"): httpx.Response(200, json={"pools": []}),
        })
        result = await client.pre_deployment_checklist()
        assert result["ready_to_deploy"] is False
        assert result["health"]["status"] == "fail"

    @pytest.mark.asyncio
    async def test_catalog_error_marks_fail(self):
        client = make_client({
            ("GET", "/api/health"): httpx.Response(200, json={"status": "ok"}),
            ("POST", "/api/schedules/validate-catalog-namespaces"): httpx.Response(
                200, json={"results": [{"ci": "bad.ci", "status": "error"}]}
            ),
            ("GET", "/api/pools/all"): httpx.Response(200, json={"pools": []}),
        })
        result = await client.pre_deployment_checklist()
        assert result["ready_to_deploy"] is False
        assert result["catalog_namespaces"]["status"] == "fail"


class TestBulkOperation:
    @pytest.mark.asyncio
    async def test_bulk_lock(self):
        client = make_client({
            ("POST", "/api/operations/lock"): httpx.Response(
                200, json={"status": "locked"}
            ),
        })
        result = await client.bulk_operation("lock", ["ci1.event", "ci2.event"])
        assert result["action"] == "lock"
        assert result["total"] == 2
        assert all(r["status"] == "success" for r in result["results"])

    @pytest.mark.asyncio
    async def test_bulk_with_error(self):
        call_count = 0

        async def handler(request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return httpx.Response(200, json={"status": "locked"})
            return httpx.Response(500, json={"error": "failed"})

        transport = httpx.MockTransport(handler)
        client = FlowApiClient(API_URL, transport=transport)
        result = await client.bulk_operation("lock", ["ci1.event", "ci2.event"])
        assert result["total"] == 2
        assert result["results"][0]["status"] == "success"
        assert result["results"][1]["status"] == "error"


class TestQaRunAll:
    @pytest.mark.asyncio
    async def test_run_and_results(self):
        client = make_client({
            ("POST", "/api/qa/run"): httpx.Response(200, json={"status": "started"}),
            ("GET", "/api/qa/results"): httpx.Response(
                200, json={"checks": [{"name": "setup", "status": "pass"}]}
            ),
        })
        result = await client.qa_run_all()
        assert "run" in result
        assert "results" in result
        assert result["run"]["status"] == "started"

    @pytest.mark.asyncio
    async def test_run_with_namespace(self):
        client = make_client({
            ("POST", "/api/qa/run"): httpx.Response(200, json={"status": "started"}),
            ("GET", "/api/qa/results"): httpx.Response(200, json={"checks": []}),
        })
        result = await client.qa_run_all(namespace="test-ns")
        assert "run" in result


class TestSessionExport:
    @pytest.mark.asyncio
    async def test_export(self):
        client = make_client({
            ("GET", "/api/export/results"): httpx.Response(
                200, text="CI,Status\ntest.event,deployed\n"
            ),
        })
        result = await client.session_export("results")
        assert "CI,Status" in result
        assert "test.event" in result

    @pytest.mark.asyncio
    async def test_export_students(self):
        client = make_client({
            ("GET", "/api/export/students"): httpx.Response(
                200, text="Name,Email\nJohn,john@test.com\n"
            ),
        })
        result = await client.session_export("students")
        assert "Name,Email" in result
