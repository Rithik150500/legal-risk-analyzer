"""
Pytest fixtures for Legal Risk Analysis System tests.
"""

import pytest
import json
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# ============================================================================
# MOCK EXTERNAL DEPENDENCIES
# ============================================================================
# Mock heavy dependencies that may not be installed in test environment

# Create mock modules for deepagents
mock_deepagents = MagicMock()
sys.modules['deepagents'] = mock_deepagents
sys.modules['deepagents.backends'] = MagicMock()

# Create mock modules for langgraph
mock_langgraph = MagicMock()
sys.modules['langgraph'] = mock_langgraph
sys.modules['langgraph.store'] = MagicMock()
sys.modules['langgraph.store.memory'] = MagicMock()
sys.modules['langgraph.checkpoint'] = MagicMock()
sys.modules['langgraph.checkpoint.memory'] = MagicMock()
sys.modules['langgraph.types'] = MagicMock()

# Create mock modules for langchain
sys.modules['langchain_core'] = MagicMock()
sys.modules['langchain_core.tools'] = MagicMock()

# Setup a proper tool decorator mock that preserves function metadata
def mock_tool_decorator(func):
    """Mock @tool decorator that creates a tool-like object."""
    class MockTool:
        def __init__(self, f):
            self.name = f.__name__
            self._func = f
            self.__doc__ = f.__doc__

        def invoke(self, args):
            if args:
                return self._func(**args)
            return self._func()

    return MockTool(func)

sys.modules['langchain_core.tools'].tool = mock_tool_decorator

# Mock pdf2image and PIL
sys.modules['pdf2image'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()


# ============================================================================
# DATA ROOM FIXTURES
# ============================================================================

@pytest.fixture
def sample_data_room_index():
    """Provides a sample data room index for testing."""
    return {
        "documents": [
            {
                "doc_id": "doc_001",
                "summdesc": "Master Service Agreement between Company A and Company B",
                "pages": [
                    {
                        "page_num": 1,
                        "summdesc": "Title page with parties and effective date",
                        "page_image": "/path/to/doc_001/page_001.png"
                    },
                    {
                        "page_num": 2,
                        "summdesc": "Scope of services and deliverables",
                        "page_image": "/path/to/doc_001/page_002.png"
                    },
                    {
                        "page_num": 3,
                        "summdesc": "Payment terms and conditions",
                        "page_image": "/path/to/doc_001/page_003.png"
                    }
                ]
            },
            {
                "doc_id": "doc_002",
                "summdesc": "Non-Disclosure Agreement with confidentiality terms",
                "pages": [
                    {
                        "page_num": 1,
                        "summdesc": "NDA definitions and scope",
                        "page_image": "/path/to/doc_002/page_001.png"
                    },
                    {
                        "page_num": 2,
                        "summdesc": "Obligations and exclusions",
                        "page_image": "/path/to/doc_002/page_002.png"
                    }
                ]
            },
            {
                "doc_id": "doc_003",
                "summdesc": "Statement of Work for software development project",
                "pages": [
                    {
                        "page_num": 1,
                        "summdesc": "Project overview and timeline",
                        "page_image": "/path/to/doc_003/page_001.png"
                    }
                ]
            }
        ]
    }


@pytest.fixture
def empty_data_room_index():
    """Provides an empty data room index."""
    return {"documents": []}


@pytest.fixture
def single_document_index():
    """Provides a data room with single document."""
    return {
        "documents": [
            {
                "doc_id": "doc_001",
                "summdesc": "Single document for testing",
                "pages": [
                    {
                        "page_num": 1,
                        "summdesc": "Single page content",
                        "page_image": "/path/to/page.png"
                    }
                ]
            }
        ]
    }


# ============================================================================
# TEMPORARY DIRECTORY FIXTURES
# ============================================================================

@pytest.fixture
def temp_dir():
    """Provides a temporary directory for file operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_input_folder(temp_dir):
    """Provides a temporary input folder with sample files."""
    input_folder = temp_dir / "input"
    input_folder.mkdir()

    # Create a sample text file
    sample_file = input_folder / "sample.txt"
    sample_file.write_text("Sample document content for testing.")

    return input_folder


@pytest.fixture
def temp_output_folder(temp_dir):
    """Provides a temporary output folder."""
    output_folder = temp_dir / "output"
    output_folder.mkdir()
    return output_folder


# ============================================================================
# AUDIT LOG FIXTURES
# ============================================================================

@pytest.fixture
def temp_audit_log(temp_dir):
    """Provides a temporary audit log file path."""
    return str(temp_dir / "test_audit.jsonl")


@pytest.fixture
def sample_audit_entries():
    """Provides sample audit log entries."""
    return [
        {
            "timestamp": "2024-01-01T10:00:00",
            "thread_id": "test_001",
            "reviewer": "test_user",
            "action_tool": "write_todos",
            "action_args": {"todos": [{"task": "Test task", "status": "pending"}]},
            "decision_type": "approve",
            "edited_args": None,
            "context": {"stage": "planning"}
        },
        {
            "timestamp": "2024-01-01T10:05:00",
            "thread_id": "test_001",
            "reviewer": "test_user",
            "action_tool": "task",
            "action_args": {"name": "legal-analyzer", "task": "Analyze risks"},
            "decision_type": "edit",
            "edited_args": {"name": "legal-analyzer", "task": "Analyze risks in detail"},
            "context": {"stage": "delegation"}
        },
        {
            "timestamp": "2024-01-01T10:10:00",
            "thread_id": "test_001",
            "reviewer": "test_user",
            "action_tool": "write_file",
            "action_args": {"file_path": "/output/report.docx", "content": "Report content"},
            "decision_type": "reject",
            "edited_args": None,
            "context": {"stage": "output"}
        }
    ]


# ============================================================================
# ACTION REQUEST FIXTURES
# ============================================================================

@pytest.fixture
def sample_action_request_todos():
    """Sample action request for write_todos."""
    return {
        "name": "write_todos",
        "args": {
            "todos": [
                {"task": "Analyze contractual risks", "status": "pending", "priority": "high"},
                {"task": "Review compliance issues", "status": "pending", "priority": "medium"}
            ]
        }
    }


@pytest.fixture
def sample_action_request_task():
    """Sample action request for task delegation."""
    return {
        "name": "task",
        "args": {
            "name": "legal-analyzer",
            "task": "Analyze doc_001 for contractual risks"
        }
    }


@pytest.fixture
def sample_action_request_write_file():
    """Sample action request for file write."""
    return {
        "name": "write_file",
        "args": {
            "file_path": "/analysis/contractual_findings.txt",
            "content": "Findings content here..."
        }
    }


@pytest.fixture
def sample_review_config():
    """Sample review configuration."""
    return {
        "action_name": "write_todos",
        "allowed_decisions": ["approve", "edit", "reject"]
    }


# ============================================================================
# MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_subprocess():
    """Mock subprocess for LibreOffice conversion tests."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
            stderr=""
        )
        yield mock_run


@pytest.fixture
def mock_pdf2image():
    """Mock pdf2image conversion."""
    with patch('pdf2image.convert_from_path') as mock_convert:
        # Create mock PIL images
        mock_image = MagicMock()
        mock_image.save = MagicMock()
        mock_convert.return_value = [mock_image, mock_image]  # 2 pages
        yield mock_convert


@pytest.fixture
def mock_deep_agent():
    """Mock the deep agent creation."""
    with patch('deepagents.create_deep_agent') as mock_create:
        mock_agent = MagicMock()
        mock_agent.invoke = MagicMock(return_value={
            "messages": [{"role": "assistant", "content": "Analysis complete"}]
        })
        mock_create.return_value = mock_agent
        yield mock_create


# ============================================================================
# HITL FIXTURES
# ============================================================================

@pytest.fixture
def approval_level_high():
    """High oversight approval configuration."""
    return {
        "write_todos": True,
        "task": True,
        "get_document": True,
        "get_document_pages": True,
        "write_file": True,
        "edit_file": True,
    }


@pytest.fixture
def approval_level_moderate():
    """Moderate oversight approval configuration."""
    return {
        "write_todos": True,
        "task": True,
        "get_document": False,
        "get_document_pages": False,
        "write_file": True,
        "edit_file": {"allowed_decisions": ["approve", "reject"]},
    }


@pytest.fixture
def approval_level_minimal():
    """Minimal oversight approval configuration."""
    return {
        "write_todos": False,
        "task": False,
        "get_document": False,
        "get_document_pages": False,
        "write_file": True,
        "edit_file": True,
    }
