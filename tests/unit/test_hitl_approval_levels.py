"""
Unit tests for ApprovalLevel class in hitl_implementation.py
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from hitl_implementation import ApprovalLevel


class TestHighOversight:
    """Tests for high_oversight configuration."""

    def test_high_oversight_returns_dict(self):
        """Test that high_oversight returns a dictionary."""
        result = ApprovalLevel.high_oversight()
        assert isinstance(result, dict)

    def test_high_oversight_all_true(self):
        """Test that all operations require approval in high oversight."""
        result = ApprovalLevel.high_oversight()

        assert result["write_todos"] is True
        assert result["task"] is True
        assert result["get_document"] is True
        assert result["get_document_pages"] is True
        assert result["write_file"] is True
        assert result["edit_file"] is True

    def test_high_oversight_has_all_keys(self):
        """Test that high oversight has all expected keys."""
        result = ApprovalLevel.high_oversight()
        expected_keys = {
            "write_todos", "task", "get_document",
            "get_document_pages", "write_file", "edit_file"
        }
        assert set(result.keys()) == expected_keys


class TestModerateOversight:
    """Tests for moderate_oversight configuration."""

    def test_moderate_oversight_returns_dict(self):
        """Test that moderate_oversight returns a dictionary."""
        result = ApprovalLevel.moderate_oversight()
        assert isinstance(result, dict)

    def test_moderate_oversight_planning_delegation_approved(self):
        """Test that planning and delegation require approval."""
        result = ApprovalLevel.moderate_oversight()

        assert result["write_todos"] is True
        assert result["task"] is True

    def test_moderate_oversight_document_access_not_approved(self):
        """Test that document access doesn't require approval."""
        result = ApprovalLevel.moderate_oversight()

        assert result["get_document"] is False
        assert result["get_document_pages"] is False

    def test_moderate_oversight_file_operations_approved(self):
        """Test that file operations require approval."""
        result = ApprovalLevel.moderate_oversight()

        assert result["write_file"] is True

    def test_moderate_oversight_edit_file_config(self):
        """Test that edit_file has specific configuration."""
        result = ApprovalLevel.moderate_oversight()

        # edit_file should have allowed_decisions config
        assert isinstance(result["edit_file"], dict)
        assert "allowed_decisions" in result["edit_file"]
        assert "approve" in result["edit_file"]["allowed_decisions"]
        assert "reject" in result["edit_file"]["allowed_decisions"]


class TestMinimalOversight:
    """Tests for minimal_oversight configuration."""

    def test_minimal_oversight_returns_dict(self):
        """Test that minimal_oversight returns a dictionary."""
        result = ApprovalLevel.minimal_oversight()
        assert isinstance(result, dict)

    def test_minimal_oversight_planning_not_approved(self):
        """Test that planning doesn't require approval."""
        result = ApprovalLevel.minimal_oversight()
        assert result["write_todos"] is False

    def test_minimal_oversight_delegation_not_approved(self):
        """Test that delegation doesn't require approval."""
        result = ApprovalLevel.minimal_oversight()
        assert result["task"] is False

    def test_minimal_oversight_document_access_not_approved(self):
        """Test that document access doesn't require approval."""
        result = ApprovalLevel.minimal_oversight()

        assert result["get_document"] is False
        assert result["get_document_pages"] is False

    def test_minimal_oversight_only_outputs_approved(self):
        """Test that only file outputs require approval."""
        result = ApprovalLevel.minimal_oversight()

        assert result["write_file"] is True
        assert result["edit_file"] is True


class TestCustomApprovalLevel:
    """Tests for custom approval level configuration."""

    def test_custom_returns_dict(self):
        """Test that custom returns a dictionary."""
        result = ApprovalLevel.custom()
        assert isinstance(result, dict)

    def test_custom_default_values(self):
        """Test custom configuration with default values."""
        result = ApprovalLevel.custom()

        # Default values
        assert result["write_todos"] is True
        assert result["task"] is True
        assert result["get_document"] is False
        assert result["get_document_pages"] is False
        assert result["write_file"] is True
        assert result["edit_file"] is True

    def test_custom_all_true(self):
        """Test custom with all options enabled."""
        result = ApprovalLevel.custom(
            planning=True,
            delegation=True,
            document_access=True,
            file_operations=True
        )

        assert result["write_todos"] is True
        assert result["task"] is True
        assert result["get_document"] is True
        assert result["get_document_pages"] is True
        assert result["write_file"] is True
        assert result["edit_file"] is True

    def test_custom_all_false(self):
        """Test custom with all options disabled."""
        result = ApprovalLevel.custom(
            planning=False,
            delegation=False,
            document_access=False,
            file_operations=False
        )

        assert result["write_todos"] is False
        assert result["task"] is False
        assert result["get_document"] is False
        assert result["get_document_pages"] is False
        assert result["write_file"] is False
        assert result["edit_file"] is False

    def test_custom_mixed_configuration(self):
        """Test custom with mixed configuration."""
        result = ApprovalLevel.custom(
            planning=False,
            delegation=True,
            document_access=True,
            file_operations=False
        )

        assert result["write_todos"] is False
        assert result["task"] is True
        assert result["get_document"] is True
        assert result["get_document_pages"] is True
        assert result["write_file"] is False
        assert result["edit_file"] is False

    def test_custom_document_access_sets_both(self):
        """Test that document_access controls both document tools."""
        result = ApprovalLevel.custom(document_access=True)

        assert result["get_document"] is True
        assert result["get_document_pages"] is True

        result = ApprovalLevel.custom(document_access=False)

        assert result["get_document"] is False
        assert result["get_document_pages"] is False

    def test_custom_file_operations_sets_both(self):
        """Test that file_operations controls both file tools."""
        result = ApprovalLevel.custom(file_operations=True)

        assert result["write_file"] is True
        assert result["edit_file"] is True

        result = ApprovalLevel.custom(file_operations=False)

        assert result["write_file"] is False
        assert result["edit_file"] is False


class TestApprovalLevelComparison:
    """Tests comparing different approval levels."""

    def test_high_has_more_approvals_than_moderate(self):
        """Test that high oversight has more approvals than moderate."""
        high = ApprovalLevel.high_oversight()
        moderate = ApprovalLevel.moderate_oversight()

        high_true_count = sum(1 for v in high.values() if v is True)
        moderate_true_count = sum(
            1 for v in moderate.values()
            if v is True or isinstance(v, dict)
        )

        assert high_true_count >= moderate_true_count

    def test_moderate_has_more_approvals_than_minimal(self):
        """Test that moderate oversight has more approvals than minimal."""
        moderate = ApprovalLevel.moderate_oversight()
        minimal = ApprovalLevel.minimal_oversight()

        moderate_true_count = sum(
            1 for v in moderate.values()
            if v is True or isinstance(v, dict)
        )
        minimal_true_count = sum(1 for v in minimal.values() if v is True)

        assert moderate_true_count >= minimal_true_count

    def test_all_levels_have_same_keys(self):
        """Test that all approval levels have the same keys."""
        high = ApprovalLevel.high_oversight()
        moderate = ApprovalLevel.moderate_oversight()
        minimal = ApprovalLevel.minimal_oversight()
        custom = ApprovalLevel.custom()

        assert set(high.keys()) == set(moderate.keys())
        assert set(moderate.keys()) == set(minimal.keys())
        assert set(minimal.keys()) == set(custom.keys())

    def test_custom_can_match_high(self):
        """Test that custom can be configured to match high oversight."""
        high = ApprovalLevel.high_oversight()
        custom = ApprovalLevel.custom(
            planning=True,
            delegation=True,
            document_access=True,
            file_operations=True
        )

        assert high == custom

    def test_custom_can_match_minimal(self):
        """Test that custom can be configured to match minimal oversight."""
        minimal = ApprovalLevel.minimal_oversight()
        custom = ApprovalLevel.custom(
            planning=False,
            delegation=False,
            document_access=False,
            file_operations=True
        )

        assert minimal == custom
