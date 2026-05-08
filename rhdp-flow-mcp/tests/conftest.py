"""Shared test fixtures for rhdp-flow-mcp tests."""

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_catalog_items():
    return [
        {
            "id": "openshift-cnv.ocp-virt-roadshow-multi-user.prod",
            "display_name": "OCP Virt Roadshow",
            "catalog_namespace": "babylon-catalog-prod",
            "description": "OpenShift Virtualization Roadshow",
            "category": "OpenShift",
            "parameters": [
                {
                    "name": "num_users",
                    "type": "integer",
                    "default": 1,
                    "minimum": 1,
                    "maximum": 20,
                    "description": "Number of users",
                }
            ],
        },
        {
            "id": "summit-2026.lb2655.event",
            "display_name": "Summit 2026 LB2655",
            "catalog_namespace": "babylon-catalog-event",
            "description": "Summit lab",
            "category": "Events",
            "parameters": [
                {
                    "name": "num_users",
                    "type": "integer",
                    "default": 1,
                    "minimum": 1,
                    "maximum": 60,
                }
            ],
        },
    ]


@pytest.fixture
def sample_health_response():
    return {
        "status": "ok",
        "oc_installed": True,
        "oc_connected": True,
        "cluster_url": "https://api.cluster.example.com:6443",
        "user": "admin",
        "message": "Connected to cluster",
        "base_domain": "cluster.example.com",
        "rhdp_api_reachable": True,
    }


@pytest.fixture
def sample_pools():
    return {
        "pools": [
            {
                "pool_name": "virt-roadshow-pool",
                "min_available": 5,
                "max_available": 20,
                "ready": 8,
                "available": 8,
                "claimed": 2,
                "provisioning": 0,
                "lifespan_default": "3d",
                "lifespan_unclaimed": "1d",
                "lifespan_maximum": "7d",
                "provider_name": "virt-roadshow-provider",
                "exists": True,
            }
        ]
    }
