"""
Integration tests for HITL workflow in hitl_implementation.py
"""

import pytest
import json
import sys
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from hitl_implementation import (
    create_agent_with_hitl,
    run_agent_with_hitl,
    ApprovalLevel,
    CLIReviewInterface,
    AutoApproveInterface,
    AuditLogger
)


class TestCreateAgentWithHITL:
    """Tests for create_agent_with_hitl function."""

    @patch('hitl_implementation.create_legal_risk_analysis_agent')
    def test_returns_config_dict(self, mock_create_agent, sample_data_room_index):
        """Test that function returns configuration dictionary."""
        mock_create_agent.return_value = MagicMock()

        config = create_agent_with_hitl(
            data_room_index=sample_data_room_index,
            approval_level=ApprovalLevel.high_oversight(),
            review_interface=AutoApproveInterface()
        )

        assert isinstance(config, dict)
        assert "agent" in config
        assert "approval_level" in config
        assert "review_interface" in config
        assert "reviewer_name" in config
        assert "audit_logger" in config

    @patch('hitl_implementation.create_legal_risk_analysis_agent')
    def test_creates_base_agent(self, mock_create_agent, sample_data_room_index):
        """Test that base agent is created."""
        mock_agent = MagicMock()
        mock_create_agent.return_value = mock_agent

        config = create_agent_with_hitl(
            data_room_index=sample_data_room_index,
            approval_level=ApprovalLevel.high_oversight(),
            review_interface=AutoApproveInterface()
        )

        mock_create_agent.assert_called_once_with(sample_data_room_index)
        assert config["agent"] is mock_agent

    @patch('hitl_implementation.create_legal_risk_analysis_agent')
    def test_stores_approval_level(self, mock_create_agent, sample_data_room_index):
        """Test that approval level is stored."""
        mock_create_agent.return_value = MagicMock()

        approval = ApprovalLevel.moderate_oversight()

        config = create_agent_with_hitl(
            data_room_index=sample_data_room_index,
            approval_level=approval,
            review_interface=AutoApproveInterface()
        )

        assert config["approval_level"] == approval

    @patch('hitl_implementation.create_legal_risk_analysis_agent')
    def test_stores_review_interface(self, mock_create_agent, sample_data_room_index):
        """Test that review interface is stored."""
        mock_create_agent.return_value = MagicMock()

        interface = CLIReviewInterface()

        config = create_agent_with_hitl(
            data_room_index=sample_data_room_index,
            approval_level=ApprovalLevel.high_oversight(),
            review_interface=interface
        )

        assert config["review_interface"] is interface

    @patch('hitl_implementation.create_legal_risk_analysis_agent')
    def test_default_reviewer_name(self, mock_create_agent, sample_data_room_index):
        """Test default reviewer name."""
        mock_create_agent.return_value = MagicMock()

        config = create_agent_with_hitl(
            data_room_index=sample_data_room_index,
            approval_level=ApprovalLevel.high_oversight(),
            review_interface=AutoApproveInterface()
        )

        assert config["reviewer_name"] == "human"

    @patch('hitl_implementation.create_legal_risk_analysis_agent')
    def test_custom_reviewer_name(self, mock_create_agent, sample_data_room_index):
        """Test custom reviewer name."""
        mock_create_agent.return_value = MagicMock()

        config = create_agent_with_hitl(
            data_room_index=sample_data_room_index,
            approval_level=ApprovalLevel.high_oversight(),
            review_interface=AutoApproveInterface(),
            reviewer_name="legal_team"
        )

        assert config["reviewer_name"] == "legal_team"

    @patch('hitl_implementation.create_legal_risk_analysis_agent')
    def test_audit_enabled_by_default(self, mock_create_agent, sample_data_room_index):
        """Test that audit logging is enabled by default."""
        mock_create_agent.return_value = MagicMock()

        config = create_agent_with_hitl(
            data_room_index=sample_data_room_index,
            approval_level=ApprovalLevel.high_oversight(),
            review_interface=AutoApproveInterface()
        )

        assert config["audit_logger"] is not None
        assert isinstance(config["audit_logger"], AuditLogger)

    @patch('hitl_implementation.create_legal_risk_analysis_agent')
    def test_audit_can_be_disabled(self, mock_create_agent, sample_data_room_index):
        """Test that audit logging can be disabled."""
        mock_create_agent.return_value = MagicMock()

        config = create_agent_with_hitl(
            data_room_index=sample_data_room_index,
            approval_level=ApprovalLevel.high_oversight(),
            review_interface=AutoApproveInterface(),
            enable_audit=False
        )

        assert config["audit_logger"] is None


class TestRunAgentWithHITL:
    """Tests for run_agent_with_hitl function."""

    def test_runs_without_interrupt(self, sample_data_room_index):
        """Test running agent that doesn't interrupt."""
        # Create mock agent
        mock_agent = MagicMock()
        mock_agent.invoke.return_value = {
            "messages": [{"role": "assistant", "content": "Analysis complete"}]
        }

        config = {
            "agent": mock_agent,
            "approval_level": ApprovalLevel.high_oversight(),
            "review_interface": AutoApproveInterface(log_actions=False),
            "reviewer_name": "test",
            "audit_logger": None
        }

        result = run_agent_with_hitl(
            agent_config=config,
            user_message="Test message",
            thread_id="test_001"
        )

        # Verify initial invoke was called
        mock_agent.invoke.assert_called_once()
        assert "messages" in result

    def test_handles_single_interrupt(self, sample_data_room_index):
        """Test handling a single interrupt."""
        mock_agent = MagicMock()

        # First call returns interrupt, second returns result
        interrupt_value = MagicMock()
        interrupt_value.value = {
            "action_requests": [
                {"name": "write_todos", "args": {"todos": []}}
            ],
            "review_configs": [
                {"action_name": "write_todos", "allowed_decisions": ["approve"]}
            ]
        }

        mock_agent.invoke.side_effect = [
            {"__interrupt__": [interrupt_value]},
            {"messages": [{"role": "assistant", "content": "Done"}]}
        ]

        config = {
            "agent": mock_agent,
            "approval_level": ApprovalLevel.high_oversight(),
            "review_interface": AutoApproveInterface(log_actions=False),
            "reviewer_name": "test",
            "audit_logger": None
        }

        result = run_agent_with_hitl(
            agent_config=config,
            user_message="Test",
            thread_id="test_001"
        )

        # Should have been called twice
        assert mock_agent.invoke.call_count == 2
        assert result["messages"][0]["content"] == "Done"

    def test_respects_max_iterations(self):
        """Test that max_iterations is respected."""
        mock_agent = MagicMock()

        # Always return interrupt
        interrupt_value = MagicMock()
        interrupt_value.value = {
            "action_requests": [
                {"name": "task", "args": {"name": "test", "task": "test"}}
            ],
            "review_configs": [
                {"action_name": "task", "allowed_decisions": ["approve"]}
            ]
        }

        mock_agent.invoke.return_value = {"__interrupt__": [interrupt_value]}

        config = {
            "agent": mock_agent,
            "approval_level": ApprovalLevel.high_oversight(),
            "review_interface": AutoApproveInterface(log_actions=False),
            "reviewer_name": "test",
            "audit_logger": None
        }

        result = run_agent_with_hitl(
            agent_config=config,
            user_message="Test",
            thread_id="test_001",
            max_iterations=3
        )

        # Should stop after max_iterations
        # Initial call + 3 iterations = 4 calls
        assert mock_agent.invoke.call_count == 4

    def test_logs_to_audit_logger(self, temp_dir):
        """Test that decisions are logged to audit logger."""
        mock_agent = MagicMock()

        interrupt_value = MagicMock()
        interrupt_value.value = {
            "action_requests": [
                {"name": "write_todos", "args": {"todos": []}}
            ],
            "review_configs": [
                {"action_name": "write_todos", "allowed_decisions": ["approve"]}
            ]
        }

        mock_agent.invoke.side_effect = [
            {"__interrupt__": [interrupt_value]},
            {"messages": [{"role": "assistant", "content": "Done"}]}
        ]

        audit_log_path = str(temp_dir / "audit.jsonl")
        audit_logger = AuditLogger(log_file=audit_log_path)

        config = {
            "agent": mock_agent,
            "approval_level": ApprovalLevel.high_oversight(),
            "review_interface": AutoApproveInterface(log_actions=False),
            "reviewer_name": "test_user",
            "audit_logger": audit_logger
        }

        run_agent_with_hitl(
            agent_config=config,
            user_message="Test",
            thread_id="test_001"
        )

        # Check audit log
        assert Path(audit_log_path).exists()
        with open(audit_log_path) as f:
            entry = json.loads(f.readline())

        assert entry["action_tool"] == "write_todos"
        assert entry["decision_type"] == "approve"
        assert entry["reviewer"] == "test_user"
        assert entry["thread_id"] == "test_001"


class TestHITLWorkflowIntegration:
    """Integration tests for complete HITL workflows."""

    @patch('hitl_implementation.create_legal_risk_analysis_agent')
    def test_complete_workflow_with_auto_approve(self, mock_create_agent, sample_data_room_index, temp_dir):
        """Test complete workflow with auto-approve interface."""
        mock_agent = MagicMock()
        mock_agent.invoke.return_value = {
            "messages": [{"role": "assistant", "content": "Analysis complete"}]
        }
        mock_create_agent.return_value = mock_agent

        config = create_agent_with_hitl(
            data_room_index=sample_data_room_index,
            approval_level=ApprovalLevel.high_oversight(),
            review_interface=AutoApproveInterface(log_actions=False),
            reviewer_name="auto_system",
            enable_audit=False
        )

        result = run_agent_with_hitl(
            agent_config=config,
            user_message="Analyze all documents",
            thread_id="workflow_test_001"
        )

        assert "messages" in result

    @patch('hitl_implementation.create_legal_risk_analysis_agent')
    def test_workflow_preserves_thread_id(self, mock_create_agent, sample_data_room_index):
        """Test that thread_id is preserved throughout workflow."""
        mock_agent = MagicMock()
        mock_agent.invoke.return_value = {
            "messages": [{"role": "assistant", "content": "Done"}]
        }
        mock_create_agent.return_value = mock_agent

        config = create_agent_with_hitl(
            data_room_index=sample_data_room_index,
            approval_level=ApprovalLevel.minimal_oversight(),
            review_interface=AutoApproveInterface(log_actions=False),
            enable_audit=False
        )

        run_agent_with_hitl(
            agent_config=config,
            user_message="Test",
            thread_id="unique_thread_123"
        )

        # Check that thread_id was used in config
        call_kwargs = mock_agent.invoke.call_args[1]
        assert call_kwargs["config"]["configurable"]["thread_id"] == "unique_thread_123"

    @patch('hitl_implementation.create_legal_risk_analysis_agent')
    def test_different_approval_levels(self, mock_create_agent, sample_data_room_index):
        """Test with different approval levels."""
        mock_agent = MagicMock()
        mock_agent.invoke.return_value = {
            "messages": [{"role": "assistant", "content": "Done"}]
        }
        mock_create_agent.return_value = mock_agent

        levels = [
            ApprovalLevel.high_oversight(),
            ApprovalLevel.moderate_oversight(),
            ApprovalLevel.minimal_oversight(),
        ]

        for level in levels:
            config = create_agent_with_hitl(
                data_room_index=sample_data_room_index,
                approval_level=level,
                review_interface=AutoApproveInterface(log_actions=False),
                enable_audit=False
            )

            result = run_agent_with_hitl(
                agent_config=config,
                user_message="Test",
                thread_id="test"
            )

            assert "messages" in result


class TestMultipleInterruptHandling:
    """Tests for handling multiple interrupts in sequence."""

    def test_handles_multiple_interrupts(self):
        """Test handling multiple sequential interrupts."""
        mock_agent = MagicMock()

        # Create interrupt sequence
        def create_interrupt(tool_name):
            interrupt_value = MagicMock()
            interrupt_value.value = {
                "action_requests": [
                    {"name": tool_name, "args": {}}
                ],
                "review_configs": [
                    {"action_name": tool_name, "allowed_decisions": ["approve"]}
                ]
            }
            return {"__interrupt__": [interrupt_value]}

        mock_agent.invoke.side_effect = [
            create_interrupt("write_todos"),
            create_interrupt("task"),
            create_interrupt("write_file"),
            {"messages": [{"role": "assistant", "content": "Done"}]}
        ]

        config = {
            "agent": mock_agent,
            "approval_level": ApprovalLevel.high_oversight(),
            "review_interface": AutoApproveInterface(log_actions=False),
            "reviewer_name": "test",
            "audit_logger": None
        }

        result = run_agent_with_hitl(
            agent_config=config,
            user_message="Test",
            thread_id="test_001",
            max_iterations=10
        )

        # 4 total calls: initial + 3 interrupts
        assert mock_agent.invoke.call_count == 4
        assert result["messages"][0]["content"] == "Done"


class TestApprovalLevelIntegration:
    """Integration tests for approval level configurations."""

    @patch('hitl_implementation.create_legal_risk_analysis_agent')
    def test_custom_approval_level(self, mock_create_agent, sample_data_room_index):
        """Test using custom approval level."""
        mock_agent = MagicMock()
        mock_agent.invoke.return_value = {
            "messages": [{"role": "assistant", "content": "Done"}]
        }
        mock_create_agent.return_value = mock_agent

        custom_level = ApprovalLevel.custom(
            planning=True,
            delegation=False,
            document_access=False,
            file_operations=True
        )

        config = create_agent_with_hitl(
            data_room_index=sample_data_room_index,
            approval_level=custom_level,
            review_interface=AutoApproveInterface(log_actions=False),
            enable_audit=False
        )

        assert config["approval_level"]["write_todos"] is True
        assert config["approval_level"]["task"] is False
        assert config["approval_level"]["write_file"] is True
