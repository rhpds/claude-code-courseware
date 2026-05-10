"""Async HTTP client for RHDP-Flow API -- intelligence queries."""

from __future__ import annotations

from typing import Any

import httpx


class FlowIntelClient:
    """Read-only client for deployment intelligence queries."""

    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)

    async def health(self) -> dict[str, Any]:
        try:
            async with self._client() as client:
                resp = await client.get("/api/health")
                resp.raise_for_status()
                return resp.json()
        except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError) as exc:
            return {"status": "error", "message": str(exc)}

    async def deploy_results(self) -> list[dict[str, Any]]:
        async with self._client() as client:
            resp = await client.get("/api/results")
            resp.raise_for_status()
            return resp.json()

    async def qa_results(self) -> dict[str, Any]:
        async with self._client() as client:
            resp = await client.get("/api/qa/results")
            resp.raise_for_status()
            return resp.json()

    async def pools(self) -> dict[str, Any]:
        async with self._client() as client:
            resp = await client.get("/api/pools/all")
            resp.raise_for_status()
            return resp.json()

    async def schedules(self) -> list[dict[str, Any]]:
        async with self._client() as client:
            resp = await client.get("/api/schedules")
            resp.raise_for_status()
            return resp.json()

    async def sessions(self) -> list[dict[str, Any]]:
        async with self._client() as client:
            resp = await client.get("/api/sessions")
            resp.raise_for_status()
            return resp.json()

    async def catalog_items(self) -> list[dict[str, Any]]:
        async with self._client() as client:
            resp = await client.get("/api/catalog/items")
            resp.raise_for_status()
            return resp.json()
