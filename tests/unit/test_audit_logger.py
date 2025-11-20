"""
Unit tests for AuditLogger class in hitl_implementation.py
"""

import pytest
import json
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from hitl_implementation import AuditLogger


class TestAuditLoggerInit:
    """Tests for AuditLogger initialization."""

    def test_init_default_file(self, temp_dir):
        """Test default log file creation."""
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            logger = AuditLogger()
            assert logger.log_file.name == "review_audit.jsonl"
        finally:
            os.chdir(original_cwd)

    def test_init_custom_file(self, temp_audit_log):
        """Test custom log file path."""
        logger = AuditLogger(log_file=temp_audit_log)
        assert str(logger.log_file) == temp_audit_log

    def test_init_creates_parent_directories(self, temp_dir):
        """Test that parent directories are created."""
        log_path = str(temp_dir / "nested" / "deep" / "audit.jsonl")
        logger = AuditLogger(log_file=log_path)

        assert logger.log_file.parent.exists()


class TestLogReview:
    """Tests for log_review method."""

    def test_log_review_creates_file(self, temp_audit_log):
        """Test that logging creates the file."""
        logger = AuditLogger(log_file=temp_audit_log)

        logger.log_review(
            action_request={"name": "test", "args": {}},
            decision={"type": "approve"},
            reviewer="test_user",
            thread_id="test_001"
        )

        assert Path(temp_audit_log).exists()

    def test_log_review_writes_json(self, temp_audit_log):
        """Test that entries are valid JSON."""
        logger = AuditLogger(log_file=temp_audit_log)

        logger.log_review(
            action_request={"name": "test", "args": {"key": "value"}},
            decision={"type": "approve"},
            reviewer="test_user",
            thread_id="test_001"
        )

        with open(temp_audit_log) as f:
            entry = json.loads(f.readline())

        assert entry["action_tool"] == "test"
        assert entry["decision_type"] == "approve"
        assert entry["reviewer"] == "test_user"
        assert entry["thread_id"] == "test_001"

    def test_log_review_includes_timestamp(self, temp_audit_log):
        """Test that timestamp is included."""
        logger = AuditLogger(log_file=temp_audit_log)

        logger.log_review(
            action_request={"name": "test", "args": {}},
            decision={"type": "approve"},
            reviewer="test_user",
            thread_id="test_001"
        )

        with open(temp_audit_log) as f:
            entry = json.loads(f.readline())

        assert "timestamp" in entry
        # Should be ISO format
        assert "T" in entry["timestamp"]

    def test_log_review_includes_context(self, temp_audit_log):
        """Test that context is logged."""
        logger = AuditLogger(log_file=temp_audit_log)

        context = {"stage": "planning", "extra": "info"}

        logger.log_review(
            action_request={"name": "test", "args": {}},
            decision={"type": "approve"},
            reviewer="test_user",
            thread_id="test_001",
            context=context
        )

        with open(temp_audit_log) as f:
            entry = json.loads(f.readline())

        assert entry["context"] == context

    def test_log_review_includes_edited_args(self, temp_audit_log):
        """Test that edited args are logged for edit decisions."""
        logger = AuditLogger(log_file=temp_audit_log)

        logger.log_review(
            action_request={"name": "test", "args": {"original": "value"}},
            decision={
                "type": "edit",
                "edited_action": {"args": {"edited": "value"}}
            },
            reviewer="test_user",
            thread_id="test_001"
        )

        with open(temp_audit_log) as f:
            entry = json.loads(f.readline())

        assert entry["edited_args"] == {"edited": "value"}

    def test_log_review_appends_entries(self, temp_audit_log):
        """Test that multiple entries are appended."""
        logger = AuditLogger(log_file=temp_audit_log)

        for i in range(3):
            logger.log_review(
                action_request={"name": f"test_{i}", "args": {}},
                decision={"type": "approve"},
                reviewer="test_user",
                thread_id=f"test_{i:03d}"
            )

        with open(temp_audit_log) as f:
            lines = f.readlines()

        assert len(lines) == 3

        # Each line should be valid JSON
        for line in lines:
            entry = json.loads(line)
            assert "action_tool" in entry

    def test_log_review_all_decision_types(self, temp_audit_log):
        """Test logging all decision types."""
        logger = AuditLogger(log_file=temp_audit_log)

        decision_types = ["approve", "edit", "reject"]

        for dtype in decision_types:
            logger.log_review(
                action_request={"name": "test", "args": {}},
                decision={"type": dtype},
                reviewer="test_user",
                thread_id="test_001"
            )

        with open(temp_audit_log) as f:
            entries = [json.loads(line) for line in f]

        logged_types = [e["decision_type"] for e in entries]
        assert logged_types == decision_types


class TestGetReviewStats:
    """Tests for get_review_stats method."""

    def test_stats_empty_file(self, temp_audit_log):
        """Test stats for non-existent file."""
        logger = AuditLogger(log_file=temp_audit_log)

        stats = logger.get_review_stats()

        assert stats == {}

    def test_stats_total_reviews(self, temp_audit_log, sample_audit_entries):
        """Test total review count."""
        logger = AuditLogger(log_file=temp_audit_log)

        # Write sample entries
        with open(temp_audit_log, 'w') as f:
            for entry in sample_audit_entries:
                f.write(json.dumps(entry) + '\n')

        stats = logger.get_review_stats()

        assert stats["total_reviews"] == 3

    def test_stats_by_decision(self, temp_audit_log, sample_audit_entries):
        """Test stats grouped by decision type."""
        logger = AuditLogger(log_file=temp_audit_log)

        # Write sample entries
        with open(temp_audit_log, 'w') as f:
            for entry in sample_audit_entries:
                f.write(json.dumps(entry) + '\n')

        stats = logger.get_review_stats()

        assert stats["by_decision"]["approve"] == 1
        assert stats["by_decision"]["edit"] == 1
        assert stats["by_decision"]["reject"] == 1

    def test_stats_by_tool(self, temp_audit_log, sample_audit_entries):
        """Test stats grouped by tool."""
        logger = AuditLogger(log_file=temp_audit_log)

        # Write sample entries
        with open(temp_audit_log, 'w') as f:
            for entry in sample_audit_entries:
                f.write(json.dumps(entry) + '\n')

        stats = logger.get_review_stats()

        assert "write_todos" in stats["by_tool"]
        assert "task" in stats["by_tool"]
        assert "write_file" in stats["by_tool"]

    def test_stats_by_reviewer(self, temp_audit_log):
        """Test stats grouped by reviewer."""
        logger = AuditLogger(log_file=temp_audit_log)

        entries = [
            {"timestamp": "2024-01-01T10:00:00", "thread_id": "t1",
             "reviewer": "alice", "action_tool": "tool", "action_args": {},
             "decision_type": "approve", "edited_args": None, "context": None},
            {"timestamp": "2024-01-01T10:01:00", "thread_id": "t1",
             "reviewer": "bob", "action_tool": "tool", "action_args": {},
             "decision_type": "approve", "edited_args": None, "context": None},
            {"timestamp": "2024-01-01T10:02:00", "thread_id": "t1",
             "reviewer": "alice", "action_tool": "tool", "action_args": {},
             "decision_type": "reject", "edited_args": None, "context": None},
        ]

        with open(temp_audit_log, 'w') as f:
            for entry in entries:
                f.write(json.dumps(entry) + '\n')

        stats = logger.get_review_stats()

        assert stats["by_reviewer"]["alice"] == 2
        assert stats["by_reviewer"]["bob"] == 1

    def test_stats_multiple_same_tool(self, temp_audit_log):
        """Test stats with multiple reviews of same tool."""
        logger = AuditLogger(log_file=temp_audit_log)

        entries = [
            {"timestamp": "2024-01-01T10:00:00", "thread_id": "t1",
             "reviewer": "user", "action_tool": "write_todos", "action_args": {},
             "decision_type": "approve", "edited_args": None, "context": None},
            {"timestamp": "2024-01-01T10:01:00", "thread_id": "t1",
             "reviewer": "user", "action_tool": "write_todos", "action_args": {},
             "decision_type": "approve", "edited_args": None, "context": None},
            {"timestamp": "2024-01-01T10:02:00", "thread_id": "t1",
             "reviewer": "user", "action_tool": "write_todos", "action_args": {},
             "decision_type": "edit", "edited_args": None, "context": None},
        ]

        with open(temp_audit_log, 'w') as f:
            for entry in entries:
                f.write(json.dumps(entry) + '\n')

        stats = logger.get_review_stats()

        assert stats["by_tool"]["write_todos"] == 3
        assert stats["by_decision"]["approve"] == 2
        assert stats["by_decision"]["edit"] == 1


class TestAuditLoggerIntegration:
    """Integration tests for AuditLogger with real workflows."""

    def test_log_and_retrieve_stats(self, temp_audit_log):
        """Test complete workflow of logging and retrieving stats."""
        logger = AuditLogger(log_file=temp_audit_log)

        # Simulate a review session
        actions = [
            ("write_todos", "approve"),
            ("task", "edit"),
            ("get_document", "approve"),
            ("write_file", "reject"),
            ("task", "approve"),
        ]

        for tool, decision in actions:
            logger.log_review(
                action_request={"name": tool, "args": {}},
                decision={"type": decision},
                reviewer="test_user",
                thread_id="session_001"
            )

        stats = logger.get_review_stats()

        assert stats["total_reviews"] == 5
        assert stats["by_decision"]["approve"] == 3
        assert stats["by_decision"]["edit"] == 1
        assert stats["by_decision"]["reject"] == 1
        assert stats["by_tool"]["task"] == 2

    def test_multiple_sessions(self, temp_audit_log):
        """Test stats across multiple sessions."""
        logger = AuditLogger(log_file=temp_audit_log)

        # Session 1
        logger.log_review(
            action_request={"name": "write_todos", "args": {}},
            decision={"type": "approve"},
            reviewer="user_a",
            thread_id="session_001"
        )

        # Session 2
        logger.log_review(
            action_request={"name": "task", "args": {}},
            decision={"type": "approve"},
            reviewer="user_b",
            thread_id="session_002"
        )

        stats = logger.get_review_stats()

        assert stats["total_reviews"] == 2
        assert stats["by_reviewer"]["user_a"] == 1
        assert stats["by_reviewer"]["user_b"] == 1

    def test_persistence_across_instances(self, temp_audit_log):
        """Test that logs persist across logger instances."""
        # First logger
        logger1 = AuditLogger(log_file=temp_audit_log)
        logger1.log_review(
            action_request={"name": "tool1", "args": {}},
            decision={"type": "approve"},
            reviewer="user",
            thread_id="t1"
        )

        # Second logger instance
        logger2 = AuditLogger(log_file=temp_audit_log)
        logger2.log_review(
            action_request={"name": "tool2", "args": {}},
            decision={"type": "reject"},
            reviewer="user",
            thread_id="t1"
        )

        # Stats from third instance
        logger3 = AuditLogger(log_file=temp_audit_log)
        stats = logger3.get_review_stats()

        assert stats["total_reviews"] == 2
