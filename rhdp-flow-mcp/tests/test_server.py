"""Integration tests for the MCP server tools."""

from rhdp_flow_mcp.server import mcp


class TestServerTools:
    def test_server_has_expected_tools(self):
        tool_names = [t.name for t in mcp._tool_manager.list_tools()]
        expected = [
            "flow_health",
            "flow_catalog_items",
            "flow_pools",
            "flow_pool_lookup",
            "flow_generate_csv",
            "flow_upload_csv",
            "flow_validate",
            "flow_deploy",
            "flow_deploy_status",
            "flow_qa_run",
            "flow_qa_results",
            "flow_operations",
            "flow_export_results",
            "flow_template",
            "flow_diff",
            "flow_validate_catalog_namespaces",
            "flow_pre_deployment_checklist",
            "flow_bulk_operations",
            "flow_qa_verification_runner",
            "flow_session_export",
        ]
        for name in expected:
            assert name in tool_names, f"Missing tool: {name}"

    def test_tool_count(self):
        tools = mcp._tool_manager.list_tools()
        assert len(tools) == 20
