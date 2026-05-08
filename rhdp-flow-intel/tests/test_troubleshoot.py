"""Tests for workshop troubleshooter."""

from rhdp_flow_intel.troubleshoot import troubleshoot_workshop


class TestTroubleshootWorkshop:
    def test_matches_ghost_pattern(self):
        workshop = {"name": "ws-1", "ci": "test.event", "namespace": "ns1", "phase": "PHASE: <none>", "status": "deployed_unverified"}
        result = troubleshoot_workshop(workshop)
        assert len(result["matches"]) > 0
        pattern_ids = [m["pattern_id"] for m in result["matches"]]
        assert "ghost_workshop" in pattern_ids or "catalog_namespace_mismatch" in pattern_ids

    def test_matches_permission_error(self):
        workshop = {"name": "ws-1", "ci": "test.event", "namespace": "ns1", "phase": "ERROR", "status": "forbidden"}
        result = troubleshoot_workshop(workshop)
        assert any(m["pattern_id"] == "permission_error" for m in result["matches"])

    def test_no_match(self):
        workshop = {"name": "ws-1", "ci": "test.event", "namespace": "ns1", "phase": "READY", "status": "deployed_verified"}
        result = troubleshoot_workshop(workshop)
        assert result["matches"] == []
        assert result["top_match"] is None

    def test_log_scanning(self):
        workshop = {"name": "ws-1", "ci": "test.event", "namespace": "ns1", "phase": "ERROR", "status": "error"}
        result = troubleshoot_workshop(workshop, logs="num_users validation failed exceeds maximum")
        assert any(m["pattern_id"] == "seats_exceed_max" for m in result["matches"])

    def test_high_confidence_first(self):
        workshop = {"name": "ws-1", "ci": "test.event", "namespace": "ns1", "phase": "PHASE: <none>", "status": "stuck"}
        result = troubleshoot_workshop(workshop)
        if len(result["matches"]) > 1:
            assert result["matches"][0]["confidence"] == "high" or len(result["matches"][0]["matched_indicators"]) >= len(result["matches"][1]["matched_indicators"])
