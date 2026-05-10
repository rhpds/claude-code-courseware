"""Async HTTP client for the RHDP-Flow API."""

from __future__ import annotations

from io import BytesIO
from typing import Any, Optional

import httpx


class FlowApiClient:
    """Wraps the Flow REST API with typed async methods."""

    def __init__(self, base_url: str, timeout: float = 30.0, transport: Optional[Any] = None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._transport = transport

    def _client(self) -> httpx.AsyncClient:
        kwargs: dict[str, Any] = {"base_url": self.base_url, "timeout": self.timeout}
        if self._transport is not None:
            kwargs["transport"] = self._transport
        return httpx.AsyncClient(**kwargs)

    async def health(self) -> dict[str, Any]:
        try:
            async with self._client() as client:
                resp = await client.get("/api/health")
                resp.raise_for_status()
                return resp.json()
        except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError) as exc:
            return {"status": "error", "message": str(exc)}

    async def catalog_items(self) -> list[dict[str, Any]]:
        async with self._client() as client:
            resp = await client.get("/api/catalog/items")
            resp.raise_for_status()
            return resp.json()

    async def pools(self) -> dict[str, Any]:
        async with self._client() as client:
            resp = await client.get("/api/pools/all")
            resp.raise_for_status()
            return resp.json()

    async def pool_lookup(self, catalog_item: str) -> dict[str, Any]:
        async with self._client() as client:
            resp = await client.get("/api/pools/lookup", params={"catalog_item": catalog_item})
            resp.raise_for_status()
            return resp.json()

    async def upload_csv(self, csv_content: str) -> dict[str, Any]:
        async with self._client() as client:
            files = {"file": ("schedule.csv", BytesIO(csv_content.encode()), "text/csv")}
            resp = await client.post("/api/schedules/upload", files=files)
            resp.raise_for_status()
            return resp.json()

    async def validate_num_users(self) -> dict[str, Any]:
        async with self._client() as client:
            resp = await client.post("/api/schedules/validate-num-users")
            resp.raise_for_status()
            return resp.json()

    async def validate_catalog_namespaces(self) -> dict[str, Any]:
        async with self._client() as client:
            resp = await client.post("/api/schedules/validate-catalog-namespaces")
            resp.raise_for_status()
            return resp.json()

    async def deploy(self, dry_run: bool = False, **kwargs: Any) -> dict[str, Any]:
        body = {"dry_run": dry_run, **kwargs}
        async with self._client() as client:
            resp = await client.post("/api/deploy", json=body)
            resp.raise_for_status()
            return resp.json()

    async def deploy_status(self) -> list[dict[str, Any]]:
        async with self._client() as client:
            resp = await client.get("/api/results")
            resp.raise_for_status()
            return resp.json()

    async def qa_run(self, qa_type: str = "all", namespace: Optional[str] = None) -> dict[str, Any]:
        body: dict[str, Any] = {"type": qa_type}
        if namespace:
            body["namespace"] = namespace
        async with self._client() as client:
            resp = await client.post("/api/qa/run", json=body)
            resp.raise_for_status()
            return resp.json()

    async def qa_results(self) -> dict[str, Any]:
        async with self._client() as client:
            resp = await client.get("/api/qa/results")
            resp.raise_for_status()
            return resp.json()

    async def operation(self, action: str, **kwargs: Any) -> dict[str, Any]:
        async with self._client() as client:
            resp = await client.post(f"/api/operations/{action}", json=kwargs or {})
            resp.raise_for_status()
            return resp.json()

    async def export_results(self, export_type: str = "results") -> str:
        async with self._client() as client:
            resp = await client.get(f"/api/export/{export_type}")
            resp.raise_for_status()
            return resp.text

    async def template(self) -> str:
        async with self._client() as client:
            resp = await client.get("/api/templates/schedule")
            resp.raise_for_status()
            return resp.text

    async def diff(self, csv_content: str) -> dict[str, Any]:
        async with self._client() as client:
            files = {"file": ("new_schedule.csv", BytesIO(csv_content.encode()), "text/csv")}
            resp = await client.post("/api/schedules/diff", files=files)
            resp.raise_for_status()
            return resp.json()

    async def validate_catalog_namespaces_full(self) -> dict[str, Any]:
        """Extended catalog namespace validation with cross-reference."""
        async with self._client() as client:
            validation = await client.post("/api/schedules/validate-catalog-namespaces")
            validation.raise_for_status()
            catalog = await client.get("/api/catalog/items")
            catalog.raise_for_status()
            return {
                "validation": validation.json(),
                "catalog_items": [item["id"] for item in catalog.json()],
            }

    async def pre_deployment_checklist(self) -> dict[str, Any]:
        """Run comprehensive pre-deployment checks."""
        checks: dict[str, Any] = {}
        async with self._client() as client:
            # Health
            try:
                resp = await client.get("/api/health")
                resp.raise_for_status()
                checks["health"] = {"status": "pass", "details": resp.json()}
            except Exception as exc:
                checks["health"] = {"status": "fail", "error": str(exc)}

            # Catalog namespace validation
            try:
                resp = await client.post("/api/schedules/validate-catalog-namespaces")
                resp.raise_for_status()
                data = resp.json()
                has_errors = any(
                    item.get("status") == "error" for item in data.get("results", [])
                )
                checks["catalog_namespaces"] = {
                    "status": "fail" if has_errors else "pass",
                    "details": data,
                }
            except Exception as exc:
                checks["catalog_namespaces"] = {"status": "fail", "error": str(exc)}

            # Pools
            try:
                resp = await client.get("/api/pools/all")
                resp.raise_for_status()
                checks["pools"] = {"status": "pass", "details": resp.json()}
            except Exception as exc:
                checks["pools"] = {"status": "fail", "error": str(exc)}

        checks["ready_to_deploy"] = all(
            c.get("status") == "pass"
            for c in checks.values()
            if isinstance(c, dict) and "status" in c
        )
        return checks

    async def bulk_operation(
        self, action: str, ci_filters: list[str], **kwargs: Any
    ) -> dict[str, Any]:
        """Apply operation to multiple CIs."""
        results = []
        async with self._client() as client:
            for ci in ci_filters:
                body = {"ci_filter": ci, **kwargs}
                try:
                    resp = await client.post(f"/api/operations/{action}", json=body)
                    resp.raise_for_status()
                    results.append({"ci": ci, "status": "success", "result": resp.json()})
                except Exception as exc:
                    results.append({"ci": ci, "status": "error", "error": str(exc)})
        return {"action": action, "results": results, "total": len(results)}

    async def qa_run_all(self, namespace: str | None = None) -> dict[str, Any]:
        """Run all QA checks and return results."""
        body: dict[str, Any] = {"type": "all"}
        if namespace:
            body["namespace"] = namespace
        async with self._client() as client:
            run_resp = await client.post("/api/qa/run", json=body)
            run_resp.raise_for_status()
            results_resp = await client.get("/api/qa/results")
            results_resp.raise_for_status()
            return {"run": run_resp.json(), "results": results_resp.json()}

    async def session_export(self, export_type: str = "results") -> str:
        """Export session data as CSV."""
        async with self._client() as client:
            resp = await client.get(f"/api/export/{export_type}")
            resp.raise_for_status()
            return resp.text
