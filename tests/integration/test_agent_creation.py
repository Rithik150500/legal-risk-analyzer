"""
Integration tests for agent creation in legal_risk_analysis_agent.py
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Get reference to the mocked create_deep_agent from conftest
import tests.conftest
mock_deepagents = sys.modules['deepagents']


class TestCreateLegalRiskAnalysisAgent:
    """Integration tests for create_legal_risk_analysis_agent function."""

    def test_agent_creation_with_valid_index(self, sample_data_room_index):
        """Test agent creation with valid data room index."""
        from legal_risk_analysis_agent import create_legal_risk_analysis_agent

        mock_agent = MagicMock()
        mock_deepagents.create_deep_agent.return_value = mock_agent
        mock_deepagents.create_deep_agent.reset_mock()

        agent = create_legal_risk_analysis_agent(sample_data_room_index)

        # Verify create_deep_agent was called
        mock_deepagents.create_deep_agent.assert_called_once()

        # Verify agent was returned
        assert agent is mock_agent

    def test_agent_creation_uses_correct_model(self, sample_data_room_index):
        """Test that correct model is used."""
        from legal_risk_analysis_agent import create_legal_risk_analysis_agent

        mock_deepagents.create_deep_agent.return_value = MagicMock()
        mock_deepagents.create_deep_agent.reset_mock()

        create_legal_risk_analysis_agent(sample_data_room_index)

        call_kwargs = mock_deepagents.create_deep_agent.call_args[1]
        assert call_kwargs["model"] == "claude-sonnet-4-5-20250929"

    def test_agent_creation_includes_tools(self, sample_data_room_index):
        """Test that data room tools are included."""
        from legal_risk_analysis_agent import create_legal_risk_analysis_agent

        mock_deepagents.create_deep_agent.return_value = MagicMock()
        mock_deepagents.create_deep_agent.reset_mock()

        create_legal_risk_analysis_agent(sample_data_room_index)

        call_kwargs = mock_deepagents.create_deep_agent.call_args[1]
        tools = call_kwargs["tools"]

        # Should have 3 data room tools
        assert len(tools) == 3
        tool_names = [t.name for t in tools]
        assert "get_document" in tool_names
        assert "get_document_pages" in tool_names
        assert "list_all_documents" in tool_names

    def test_agent_creation_includes_subagents(self, sample_data_room_index):
        """Test that subagents are configured."""
        from legal_risk_analysis_agent import create_legal_risk_analysis_agent

        mock_deepagents.create_deep_agent.return_value = MagicMock()
        mock_deepagents.create_deep_agent.reset_mock()

        create_legal_risk_analysis_agent(sample_data_room_index)

        call_kwargs = mock_deepagents.create_deep_agent.call_args[1]
        subagents = call_kwargs["subagents"]

        # Should have 3 subagents
        assert len(subagents) == 3

        subagent_names = [s["name"] for s in subagents]
        assert "legal-analyzer" in subagent_names
        assert "report-creator" in subagent_names
        assert "dashboard-creator" in subagent_names

    def test_agent_creation_subagents_use_correct_model(self, sample_data_room_index):
        """Test that subagents use the correct model."""
        from legal_risk_analysis_agent import create_legal_risk_analysis_agent

        mock_deepagents.create_deep_agent.return_value = MagicMock()
        mock_deepagents.create_deep_agent.reset_mock()

        create_legal_risk_analysis_agent(sample_data_room_index)

        call_kwargs = mock_deepagents.create_deep_agent.call_args[1]
        subagents = call_kwargs["subagents"]

        for subagent in subagents:
            assert subagent["model"] == "claude-sonnet-4-5-20250929"

    def test_agent_creation_system_prompt_includes_index(self, sample_data_room_index):
        """Test that system prompt includes data room index."""
        from legal_risk_analysis_agent import create_legal_risk_analysis_agent

        mock_deepagents.create_deep_agent.return_value = MagicMock()
        mock_deepagents.create_deep_agent.reset_mock()

        create_legal_risk_analysis_agent(sample_data_room_index)

        call_kwargs = mock_deepagents.create_deep_agent.call_args[1]
        system_prompt = call_kwargs["system_prompt"]

        # Should contain document IDs from index
        assert "doc_001" in system_prompt
        assert "doc_002" in system_prompt
        assert "doc_003" in system_prompt

    def test_agent_creation_with_empty_index(self, empty_data_room_index):
        """Test agent creation with empty data room."""
        from legal_risk_analysis_agent import create_legal_risk_analysis_agent

        mock_deepagents.create_deep_agent.return_value = MagicMock()
        mock_deepagents.create_deep_agent.reset_mock()

        agent = create_legal_risk_analysis_agent(empty_data_room_index)

        # Should still create agent
        assert agent is not None
        mock_deepagents.create_deep_agent.assert_called_once()

    def test_agent_creation_includes_checkpointer(self, sample_data_room_index):
        """Test that checkpointer is included for state management."""
        from legal_risk_analysis_agent import create_legal_risk_analysis_agent

        mock_deepagents.create_deep_agent.return_value = MagicMock()
        mock_deepagents.create_deep_agent.reset_mock()

        create_legal_risk_analysis_agent(sample_data_room_index)

        call_kwargs = mock_deepagents.create_deep_agent.call_args[1]
        assert "checkpointer" in call_kwargs
        assert call_kwargs["checkpointer"] is not None

    def test_agent_creation_includes_store(self, sample_data_room_index):
        """Test that store is included for memory."""
        from legal_risk_analysis_agent import create_legal_risk_analysis_agent

        mock_deepagents.create_deep_agent.return_value = MagicMock()
        mock_deepagents.create_deep_agent.reset_mock()

        create_legal_risk_analysis_agent(sample_data_room_index)

        call_kwargs = mock_deepagents.create_deep_agent.call_args[1]
        assert "store" in call_kwargs
        assert call_kwargs["store"] is not None


class TestAgentSubagentConfiguration:
    """Tests for subagent configuration details."""

    def test_legal_analyzer_has_data_room_tools(self, sample_data_room_index):
        """Test that legal-analyzer subagent has data room tools."""
        from legal_risk_analysis_agent import create_legal_risk_analysis_agent

        mock_deepagents.create_deep_agent.return_value = MagicMock()
        mock_deepagents.create_deep_agent.reset_mock()

        create_legal_risk_analysis_agent(sample_data_room_index)

        call_kwargs = mock_deepagents.create_deep_agent.call_args[1]
        subagents = call_kwargs["subagents"]

        legal_analyzer = next(s for s in subagents if s["name"] == "legal-analyzer")
        assert len(legal_analyzer["tools"]) == 3

    def test_report_creator_no_data_room_tools(self, sample_data_room_index):
        """Test that report-creator doesn't have data room tools."""
        from legal_risk_analysis_agent import create_legal_risk_analysis_agent

        mock_deepagents.create_deep_agent.return_value = MagicMock()
        mock_deepagents.create_deep_agent.reset_mock()

        create_legal_risk_analysis_agent(sample_data_room_index)

        call_kwargs = mock_deepagents.create_deep_agent.call_args[1]
        subagents = call_kwargs["subagents"]

        report_creator = next(s for s in subagents if s["name"] == "report-creator")
        assert len(report_creator["tools"]) == 0

    def test_subagents_have_system_prompts(self, sample_data_room_index):
        """Test that all subagents have system prompts."""
        from legal_risk_analysis_agent import create_legal_risk_analysis_agent

        mock_deepagents.create_deep_agent.return_value = MagicMock()
        mock_deepagents.create_deep_agent.reset_mock()

        create_legal_risk_analysis_agent(sample_data_room_index)

        call_kwargs = mock_deepagents.create_deep_agent.call_args[1]
        subagents = call_kwargs["subagents"]

        for subagent in subagents:
            assert "system_prompt" in subagent
            assert len(subagent["system_prompt"]) > 0

    def test_subagents_have_descriptions(self, sample_data_room_index):
        """Test that all subagents have descriptions."""
        from legal_risk_analysis_agent import create_legal_risk_analysis_agent

        mock_deepagents.create_deep_agent.return_value = MagicMock()
        mock_deepagents.create_deep_agent.reset_mock()

        create_legal_risk_analysis_agent(sample_data_room_index)

        call_kwargs = mock_deepagents.create_deep_agent.call_args[1]
        subagents = call_kwargs["subagents"]

        for subagent in subagents:
            assert "description" in subagent
            assert len(subagent["description"]) > 0


class TestAgentBackendConfiguration:
    """Tests for backend configuration."""

    def test_backend_is_callable(self, sample_data_room_index):
        """Test that backend is a callable factory."""
        from legal_risk_analysis_agent import create_legal_risk_analysis_agent

        mock_deepagents.create_deep_agent.return_value = MagicMock()
        mock_deepagents.create_deep_agent.reset_mock()

        create_legal_risk_analysis_agent(sample_data_room_index)

        call_kwargs = mock_deepagents.create_deep_agent.call_args[1]
        backend = call_kwargs["backend"]

        # Backend should be a callable
        assert callable(backend)


class TestDataRoomToolsFunctionality:
    """Tests for data room tools functionality with agent."""

    def test_tools_access_data_room(self, sample_data_room_index):
        """Test that tools can access data room content."""
        from legal_risk_analysis_agent import DataRoom, create_data_room_tools
        import json

        data_room = DataRoom(sample_data_room_index)
        tools = create_data_room_tools(data_room)

        # Test list_all_documents
        list_tool = next(t for t in tools if t.name == "list_all_documents")
        result = list_tool.invoke({})
        parsed = json.loads(result)
        assert len(parsed) == 3

        # Test get_document
        get_doc_tool = next(t for t in tools if t.name == "get_document")
        result = get_doc_tool.invoke({"doc_id": "doc_001"})
        assert "Page 1:" in result

        # Test get_document_pages
        get_pages_tool = next(t for t in tools if t.name == "get_document_pages")
        result = get_pages_tool.invoke({"doc_id": "doc_001", "page_nums": [1]})
        parsed = json.loads(result)
        assert len(parsed) == 1
