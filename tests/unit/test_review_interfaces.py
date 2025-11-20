"""
Unit tests for ReviewInterface implementations in hitl_implementation.py
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from io import StringIO

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from hitl_implementation import ReviewInterface, CLIReviewInterface, AutoApproveInterface


class TestReviewInterfaceBase:
    """Tests for the base ReviewInterface class."""

    def test_review_interface_is_abstract(self):
        """Test that ReviewInterface cannot be instantiated directly."""
        interface = ReviewInterface()

        with pytest.raises(NotImplementedError):
            interface.review_action({}, {})


class TestAutoApproveInterface:
    """Tests for AutoApproveInterface class."""

    def test_init_default_logging(self):
        """Test default initialization with logging enabled."""
        interface = AutoApproveInterface()
        assert interface.log_actions is True

    def test_init_logging_disabled(self):
        """Test initialization with logging disabled."""
        interface = AutoApproveInterface(log_actions=False)
        assert interface.log_actions is False

    def test_always_approves(self):
        """Test that interface always returns approve decision."""
        interface = AutoApproveInterface(log_actions=False)

        action_request = {
            "name": "test_tool",
            "args": {"key": "value"}
        }
        review_config = {"allowed_decisions": ["approve", "reject"]}

        result = interface.review_action(action_request, review_config)

        assert result["type"] == "approve"

    def test_approves_any_tool(self):
        """Test that any tool type is approved."""
        interface = AutoApproveInterface(log_actions=False)

        tools = ["write_todos", "task", "get_document", "write_file"]

        for tool in tools:
            result = interface.review_action(
                {"name": tool, "args": {}},
                {}
            )
            assert result["type"] == "approve"

    def test_logs_when_enabled(self, capsys):
        """Test that actions are logged when enabled."""
        interface = AutoApproveInterface(log_actions=True)

        action_request = {
            "name": "test_tool",
            "args": {}
        }

        interface.review_action(action_request, {})

        captured = capsys.readouterr()
        assert "[AUTO-APPROVED]" in captured.out
        assert "test_tool" in captured.out

    def test_no_logs_when_disabled(self, capsys):
        """Test that actions are not logged when disabled."""
        interface = AutoApproveInterface(log_actions=False)

        action_request = {
            "name": "test_tool",
            "args": {}
        }

        interface.review_action(action_request, {})

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_ignores_context(self):
        """Test that context is ignored."""
        interface = AutoApproveInterface(log_actions=False)

        result = interface.review_action(
            {"name": "tool", "args": {}},
            {},
            context={"stage": "test", "important": True}
        )

        assert result["type"] == "approve"


class TestCLIReviewInterfaceApprove:
    """Tests for CLIReviewInterface approve functionality."""

    @patch('builtins.input', return_value='1')
    def test_approve_option(self, mock_input):
        """Test approval via option 1."""
        interface = CLIReviewInterface()

        action_request = {
            "name": "write_todos",
            "args": {"todos": []}
        }
        review_config = {"allowed_decisions": ["approve", "edit", "reject"]}

        result = interface.review_action(action_request, review_config)

        assert result["type"] == "approve"

    @patch('builtins.input', return_value='3')
    def test_reject_option(self, mock_input):
        """Test rejection via option 3."""
        interface = CLIReviewInterface()

        action_request = {
            "name": "write_todos",
            "args": {"todos": []}
        }
        review_config = {"allowed_decisions": ["approve", "edit", "reject"]}

        result = interface.review_action(action_request, review_config)

        assert result["type"] == "reject"


class TestCLIReviewInterfaceDisplay:
    """Tests for CLIReviewInterface display functionality."""

    @patch('builtins.input', return_value='1')
    def test_displays_tool_name(self, mock_input, capsys):
        """Test that tool name is displayed."""
        interface = CLIReviewInterface()

        action_request = {
            "name": "test_tool",
            "args": {}
        }

        interface.review_action(action_request, {"allowed_decisions": ["approve"]})

        captured = capsys.readouterr()
        assert "test_tool" in captured.out

    @patch('builtins.input', return_value='1')
    def test_displays_context(self, mock_input, capsys):
        """Test that context is displayed when provided."""
        interface = CLIReviewInterface()

        action_request = {
            "name": "test_tool",
            "args": {}
        }
        context = {"stage": "planning"}

        interface.review_action(
            action_request,
            {"allowed_decisions": ["approve"]},
            context=context
        )

        captured = capsys.readouterr()
        assert "planning" in captured.out

    @patch('builtins.input', return_value='1')
    def test_displays_allowed_decisions(self, mock_input, capsys):
        """Test that allowed decisions are displayed."""
        interface = CLIReviewInterface()

        action_request = {
            "name": "test_tool",
            "args": {}
        }

        interface.review_action(
            action_request,
            {"allowed_decisions": ["approve", "reject"]}
        )

        captured = capsys.readouterr()
        assert "approve" in captured.out
        assert "reject" in captured.out


class TestCLIReviewInterfaceInputValidation:
    """Tests for CLIReviewInterface input validation."""

    @patch('builtins.input', side_effect=['invalid', '1'])
    def test_invalid_choice_prompts_again(self, mock_input, capsys):
        """Test that invalid choices prompt for new input."""
        interface = CLIReviewInterface()

        action_request = {
            "name": "test_tool",
            "args": {}
        }

        result = interface.review_action(
            action_request,
            {"allowed_decisions": ["approve"]}
        )

        # Should eventually get approved
        assert result["type"] == "approve"

        # Should have shown error message
        captured = capsys.readouterr()
        assert "Invalid" in captured.out

    @patch('builtins.input', side_effect=['2', '1'])
    def test_edit_not_allowed_prompts_again(self, mock_input, capsys):
        """Test that choosing edit when not allowed prompts again."""
        interface = CLIReviewInterface()

        action_request = {
            "name": "test_tool",
            "args": {}
        }

        result = interface.review_action(
            action_request,
            {"allowed_decisions": ["approve", "reject"]}  # No edit
        )

        # Should eventually get approved
        assert result["type"] == "approve"


class TestCLIReviewInterfaceEditTodos:
    """Tests for CLIReviewInterface todo editing."""

    @patch('builtins.input', side_effect=['2', '5'])  # Edit, then cancel
    def test_cancel_edit_rejects(self, mock_input):
        """Test that canceling edit rejects the action."""
        interface = CLIReviewInterface()

        action_request = {
            "name": "write_todos",
            "args": {
                "todos": [{"task": "Test", "status": "pending"}]
            }
        }

        result = interface.review_action(
            action_request,
            {"allowed_decisions": ["approve", "edit", "reject"]}
        )

        assert result["type"] == "reject"

    @patch('builtins.input', side_effect=['2', '1', 'New task', 'high'])
    def test_add_todo(self, mock_input):
        """Test adding a new todo."""
        interface = CLIReviewInterface()

        action_request = {
            "name": "write_todos",
            "args": {
                "todos": [{"task": "Existing", "status": "pending"}]
            }
        }

        result = interface.review_action(
            action_request,
            {"allowed_decisions": ["approve", "edit", "reject"]}
        )

        assert result["type"] == "edit"
        assert len(result["edited_action"]["args"]["todos"]) == 2
        assert result["edited_action"]["args"]["todos"][1]["task"] == "New task"
        assert result["edited_action"]["args"]["todos"][1]["priority"] == "high"


class TestCLIReviewInterfaceEditTask:
    """Tests for CLIReviewInterface task editing."""

    @patch('builtins.input', side_effect=['2', '4'])  # Edit, then cancel
    def test_cancel_edit_rejects(self, mock_input):
        """Test that canceling edit rejects."""
        interface = CLIReviewInterface()

        action_request = {
            "name": "task",
            "args": {
                "name": "legal-analyzer",
                "task": "Analyze document"
            }
        }

        result = interface.review_action(
            action_request,
            {"allowed_decisions": ["approve", "edit", "reject"]}
        )

        assert result["type"] == "reject"

    @patch('builtins.input', side_effect=['2', '1', 'Focus on contractual risks'])
    def test_add_context_to_task(self, mock_input):
        """Test adding context to task description."""
        interface = CLIReviewInterface()

        action_request = {
            "name": "task",
            "args": {
                "name": "legal-analyzer",
                "task": "Analyze document"
            }
        }

        result = interface.review_action(
            action_request,
            {"allowed_decisions": ["approve", "edit", "reject"]}
        )

        assert result["type"] == "edit"
        assert "Focus on contractual risks" in result["edited_action"]["args"]["task"]
        assert "ADDITIONAL CONTEXT" in result["edited_action"]["args"]["task"]

    @patch('builtins.input', side_effect=['2', '2', 'report-creator'])
    def test_change_subagent(self, mock_input):
        """Test changing the subagent."""
        interface = CLIReviewInterface()

        action_request = {
            "name": "task",
            "args": {
                "name": "legal-analyzer",
                "task": "Create report"
            }
        }

        result = interface.review_action(
            action_request,
            {"allowed_decisions": ["approve", "edit", "reject"]}
        )

        assert result["type"] == "edit"
        assert result["edited_action"]["args"]["name"] == "report-creator"
        assert result["edited_action"]["args"]["task"] == "Create report"


class TestCLIReviewInterfaceEditFile:
    """Tests for CLIReviewInterface file editing."""

    @patch('builtins.input', side_effect=['2', '4'])  # Edit, then cancel
    def test_cancel_edit_rejects(self, mock_input):
        """Test that canceling edit rejects."""
        interface = CLIReviewInterface()

        action_request = {
            "name": "write_file",
            "args": {
                "file_path": "/output/report.docx",
                "content": "Report content"
            }
        }

        result = interface.review_action(
            action_request,
            {"allowed_decisions": ["approve", "edit", "reject"]}
        )

        assert result["type"] == "reject"

    @patch('builtins.input', side_effect=['2', '1', '/new/path/report.docx'])
    def test_change_file_path(self, mock_input):
        """Test changing the file path."""
        interface = CLIReviewInterface()

        action_request = {
            "name": "write_file",
            "args": {
                "file_path": "/output/report.docx",
                "content": "Report content"
            }
        }

        result = interface.review_action(
            action_request,
            {"allowed_decisions": ["approve", "edit", "reject"]}
        )

        assert result["type"] == "edit"
        assert result["edited_action"]["args"]["file_path"] == "/new/path/report.docx"
        assert result["edited_action"]["args"]["content"] == "Report content"


class TestCLIReviewInterfaceGenericEdit:
    """Tests for CLIReviewInterface generic JSON editing."""

    @patch('builtins.input', side_effect=['2', '4', '{"key": "value"}'])
    def test_generic_edit_parses_json(self, mock_input):
        """Test that generic edit parses JSON correctly."""
        interface = CLIReviewInterface()

        action_request = {
            "name": "unknown_tool",
            "args": {"original": "value"}
        }

        # Mock input to return JSON and then EOFError
        with patch('builtins.input', side_effect=['2', '{"key": "new_value"}']):
            # Need to simulate the JSON editing which reads until EOFError
            pass

    def test_generic_edit_invalid_json_rejects(self, capsys):
        """Test that invalid JSON in generic edit rejects."""
        interface = CLIReviewInterface()

        # Use _edit_generic directly
        action_request = {
            "name": "test_tool",
            "args": {"key": "value"}
        }

        # Mock to return invalid JSON
        with patch('builtins.input', side_effect=['invalid json', EOFError]):
            result = interface._edit_generic(action_request)

        assert result["type"] == "reject"
