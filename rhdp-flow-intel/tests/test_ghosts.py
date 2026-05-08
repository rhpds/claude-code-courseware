"""Tests for ghost workshop detector."""

from rhdp_flow_intel.ghosts import detect_ghosts


class TestDetectGhosts:
    def test_finds_ghost_workshops(self, sample_deploy_results):
        result = detect_ghosts(sample_deploy_results)
        assert result["count"] == 1
        assert result["ghosts"][0]["name"] == "ws-ghost-003"

    def test_generates_cleanup_commands(self, sample_deploy_results):
        result = detect_ghosts(sample_deploy_results)
        assert len(result["cleanup_commands"]) == 1
        assert "oc delete" in result["cleanup_commands"][0]
        assert "ws-ghost-003" in result["cleanup_commands"][0]

    def test_no_ghosts(self):
        results = [{"name": "ws-1", "phase": "READY", "namespace": "ns1", "ci": "test.event"}]
        result = detect_ghosts(results)
        assert result["count"] == 0
        assert result["ghosts"] == []

    def test_multiple_ghosts(self):
        results = [
            {"name": "g1", "phase": "<none>", "namespace": "ns1", "ci": "a.event"},
            {"name": "g2", "phase": "none", "namespace": "ns2", "ci": "b.event"},
        ]
        result = detect_ghosts(results)
        assert result["count"] == 2
