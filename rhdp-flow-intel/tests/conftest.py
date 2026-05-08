"""Shared test fixtures for rhdp-flow-intel tests."""

import pytest


@pytest.fixture
def sample_deploy_results():
    return [
        {
            "name": "ws-image-mode-001",
            "ci": "summit-2026.lb1234-image-mode.event",
            "namespace": "user-jsmith-redhat-com",
            "status": "deployed_verified",
            "phase": "READY",
            "provision_time": "2026-06-15T09:00:00Z",
            "users": 25,
        },
        {
            "name": "ws-ocp-virt-002",
            "ci": "summit-2026.lb5678-ocp-virt.event",
            "namespace": "user-jdoe-redhat-com",
            "status": "deployed_unverified",
            "phase": "PROVISIONING",
            "provision_time": "2026-06-15T13:00:00Z",
            "users": 30,
        },
        {
            "name": "ws-ghost-003",
            "ci": "summit-2026.lb9012-ansible.event",
            "namespace": "user-asmith-redhat-com",
            "status": "deployed_unverified",
            "phase": "<none>",
            "provision_time": "2026-06-15T10:00:00Z",
            "users": 20,
        },
    ]


@pytest.fixture
def sample_pool_data():
    return {
        "pools": [
            {
                "pool_name": "image-mode-pool",
                "ready": 5,
                "claimed": 10,
                "provisioning": 3,
            },
            {
                "pool_name": "ocp-virt-pool",
                "ready": 0,
                "claimed": 8,
                "provisioning": 2,
            },
        ]
    }


@pytest.fixture
def sample_qa_results():
    return {
        "checks": [
            {"name": "ws-image-mode-001", "setup": "pass", "deployment": "pass", "showroom": "pass"},
            {"name": "ws-ocp-virt-002", "setup": "pass", "deployment": "fail", "showroom": "not_run"},
        ]
    }
