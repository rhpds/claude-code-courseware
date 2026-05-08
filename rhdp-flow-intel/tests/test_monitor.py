"""Tests for deployment monitor."""

from rhdp_flow_intel.monitor import monitor_deployments


class TestMonitorDeployments:
    def test_aggregates_by_status(self, sample_deploy_results):
        result = monitor_deployments(sample_deploy_results)
        assert result["total"] == 3
        assert result["by_status"]["READY"] == 1
        assert result["by_status"]["PROVISIONING"] == 1
        assert result["by_status"]["<none>"] == 1

    def test_detects_ghost_issues(self, sample_deploy_results):
        result = monitor_deployments(sample_deploy_results)
        assert len(result["issues"]) == 1
        assert result["issues"][0]["severity"] == "CRITICAL"
        assert "ghost" in result["issues"][0]["issue"].lower()

    def test_empty_results(self):
        result = monitor_deployments([])
        assert result["total"] == 0
        assert result["issues"] == []

    def test_summary_contains_counts(self, sample_deploy_results):
        result = monitor_deployments(sample_deploy_results)
        assert "3 workshops" in result["summary"]
        assert "1/3" in result["summary"]
