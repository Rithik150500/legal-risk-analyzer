"""
Unit tests for DataRoom class in legal_risk_analysis_agent.py
"""

import pytest
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import after conftest.py has set up mocks
from legal_risk_analysis_agent import DataRoom, create_data_room_tools


class TestDataRoom:
    """Tests for the DataRoom class."""

    def test_init(self, sample_data_room_index):
        """Test DataRoom initialization."""
        data_room = DataRoom(sample_data_room_index)
        assert data_room.data_room_index == sample_data_room_index
        assert len(data_room.data_room_index["documents"]) == 3

    def test_init_empty(self, empty_data_room_index):
        """Test DataRoom with empty index."""
        data_room = DataRoom(empty_data_room_index)
        assert data_room.data_room_index == empty_data_room_index
        assert len(data_room.data_room_index["documents"]) == 0


class TestGetDocumentIndex:
    """Tests for get_document_index method."""

    def test_get_document_index_returns_simplified_list(self, sample_data_room_index):
        """Test that get_document_index returns simplified doc info."""
        data_room = DataRoom(sample_data_room_index)
        index = data_room.get_document_index()

        assert len(index) == 3
        for doc in index:
            assert "doc_id" in doc
            assert "summdesc" in doc
            assert "pages" not in doc

    def test_get_document_index_preserves_ids(self, sample_data_room_index):
        """Test that document IDs are preserved."""
        data_room = DataRoom(sample_data_room_index)
        index = data_room.get_document_index()

        doc_ids = [doc["doc_id"] for doc in index]
        assert "doc_001" in doc_ids
        assert "doc_002" in doc_ids
        assert "doc_003" in doc_ids

    def test_get_document_index_empty(self, empty_data_room_index):
        """Test get_document_index with empty data room."""
        data_room = DataRoom(empty_data_room_index)
        index = data_room.get_document_index()
        assert index == []

    def test_get_document_index_single_document(self, single_document_index):
        """Test get_document_index with single document."""
        data_room = DataRoom(single_document_index)
        index = data_room.get_document_index()

        assert len(index) == 1
        assert index[0]["doc_id"] == "doc_001"


class TestGetDocument:
    """Tests for get_document method."""

    def test_get_document_found(self, sample_data_room_index):
        """Test retrieving an existing document."""
        data_room = DataRoom(sample_data_room_index)
        doc = data_room.get_document("doc_001")

        assert doc is not None
        assert doc["doc_id"] == "doc_001"
        assert "summdesc" in doc
        assert "pages" in doc
        assert len(doc["pages"]) == 3

    def test_get_document_not_found(self, sample_data_room_index):
        """Test retrieving a non-existent document."""
        data_room = DataRoom(sample_data_room_index)
        doc = data_room.get_document("doc_999")
        assert doc is None

    def test_get_document_returns_full_structure(self, sample_data_room_index):
        """Test that full document structure is returned."""
        data_room = DataRoom(sample_data_room_index)
        doc = data_room.get_document("doc_002")

        assert doc["doc_id"] == "doc_002"
        assert len(doc["pages"]) == 2
        assert doc["pages"][0]["page_num"] == 1
        assert doc["pages"][1]["page_num"] == 2

    def test_get_document_empty_data_room(self, empty_data_room_index):
        """Test get_document with empty data room."""
        data_room = DataRoom(empty_data_room_index)
        doc = data_room.get_document("doc_001")
        assert doc is None


class TestGetDocumentPagesSummary:
    """Tests for get_document_pages_summary method."""

    def test_get_pages_summary_success(self, sample_data_room_index):
        """Test getting page summaries for existing document."""
        data_room = DataRoom(sample_data_room_index)
        summary = data_room.get_document_pages_summary("doc_001")

        assert "Page 1:" in summary
        assert "Page 2:" in summary
        assert "Page 3:" in summary
        assert "Title page" in summary

    def test_get_pages_summary_not_found(self, sample_data_room_index):
        """Test getting summary for non-existent document."""
        data_room = DataRoom(sample_data_room_index)
        summary = data_room.get_document_pages_summary("doc_999")

        assert "Error:" in summary
        assert "doc_999" in summary
        assert "not found" in summary

    def test_get_pages_summary_format(self, sample_data_room_index):
        """Test summary format with page separators."""
        data_room = DataRoom(sample_data_room_index)
        summary = data_room.get_document_pages_summary("doc_002")

        # Check that pages are separated
        pages = summary.split("\n\n")
        assert len(pages) == 2

    def test_get_pages_summary_single_page(self, sample_data_room_index):
        """Test summary for single-page document."""
        data_room = DataRoom(sample_data_room_index)
        summary = data_room.get_document_pages_summary("doc_003")

        assert "Page 1:" in summary
        # Should not have multiple page separators
        assert summary.count("\n\n") == 0


class TestGetDocumentPagesImages:
    """Tests for get_document_pages_images method."""

    def test_get_pages_images_success(self, sample_data_room_index):
        """Test getting specific pages."""
        data_room = DataRoom(sample_data_room_index)
        results = data_room.get_document_pages_images("doc_001", [1, 3])

        assert len(results) == 2
        assert results[0]["page_num"] == 1
        assert results[1]["page_num"] == 3
        assert "page_image" in results[0]
        assert "summdesc" in results[0]

    def test_get_pages_images_document_not_found(self, sample_data_room_index):
        """Test with non-existent document."""
        data_room = DataRoom(sample_data_room_index)
        results = data_room.get_document_pages_images("doc_999", [1])

        assert len(results) == 1
        assert "error" in results[0]
        assert "doc_999" in results[0]["error"]

    def test_get_pages_images_page_not_found(self, sample_data_room_index):
        """Test with non-existent page number."""
        data_room = DataRoom(sample_data_room_index)
        results = data_room.get_document_pages_images("doc_001", [99])

        assert len(results) == 1
        assert results[0]["page_num"] == 99
        assert "error" in results[0]
        assert "not found" in results[0]["error"]

    def test_get_pages_images_mixed_results(self, sample_data_room_index):
        """Test with mix of existing and non-existing pages."""
        data_room = DataRoom(sample_data_room_index)
        results = data_room.get_document_pages_images("doc_001", [1, 99, 2])

        assert len(results) == 3
        assert "page_image" in results[0]  # Page 1 exists
        assert "error" in results[1]        # Page 99 doesn't exist
        assert "page_image" in results[2]  # Page 2 exists

    def test_get_pages_images_empty_list(self, sample_data_room_index):
        """Test with empty page list."""
        data_room = DataRoom(sample_data_room_index)
        results = data_room.get_document_pages_images("doc_001", [])
        assert results == []

    def test_get_pages_images_all_pages(self, sample_data_room_index):
        """Test getting all pages of a document."""
        data_room = DataRoom(sample_data_room_index)
        results = data_room.get_document_pages_images("doc_001", [1, 2, 3])

        assert len(results) == 3
        for i, result in enumerate(results, 1):
            assert result["page_num"] == i
            assert "page_image" in result


class TestCreateDataRoomTools:
    """Tests for create_data_room_tools function."""

    def test_creates_three_tools(self, sample_data_room_index):
        """Test that three tools are created."""
        data_room = DataRoom(sample_data_room_index)
        tools = create_data_room_tools(data_room)
        assert len(tools) == 3

    def test_tool_names(self, sample_data_room_index):
        """Test that tools have correct names."""
        data_room = DataRoom(sample_data_room_index)
        tools = create_data_room_tools(data_room)
        tool_names = [tool.name for tool in tools]

        assert "get_document" in tool_names
        assert "get_document_pages" in tool_names
        assert "list_all_documents" in tool_names

    def test_get_document_tool(self, sample_data_room_index):
        """Test the get_document tool."""
        data_room = DataRoom(sample_data_room_index)
        tools = create_data_room_tools(data_room)

        get_doc_tool = next(t for t in tools if t.name == "get_document")
        result = get_doc_tool.invoke({"doc_id": "doc_001"})

        assert "Page 1:" in result
        assert "Title page" in result

    def test_list_all_documents_tool(self, sample_data_room_index):
        """Test the list_all_documents tool."""
        data_room = DataRoom(sample_data_room_index)
        tools = create_data_room_tools(data_room)

        list_tool = next(t for t in tools if t.name == "list_all_documents")
        result = list_tool.invoke({})

        # Result should be JSON string
        parsed = json.loads(result)
        assert len(parsed) == 3
        assert all("doc_id" in doc for doc in parsed)

    def test_get_document_pages_tool(self, sample_data_room_index):
        """Test the get_document_pages tool."""
        data_room = DataRoom(sample_data_room_index)
        tools = create_data_room_tools(data_room)

        get_pages_tool = next(t for t in tools if t.name == "get_document_pages")
        result = get_pages_tool.invoke({"doc_id": "doc_001", "page_nums": [1, 2]})

        # Result should be JSON string
        parsed = json.loads(result)
        assert len(parsed) == 2
        assert parsed[0]["page_num"] == 1
        assert parsed[1]["page_num"] == 2


class TestDataRoomEdgeCases:
    """Edge case tests for DataRoom."""

    def test_unicode_content(self):
        """Test handling of Unicode content in documents."""
        index = {
            "documents": [
                {
                    "doc_id": "doc_unicode",
                    "summdesc": "Document with Unicode: 日本語 emoji 🎉",
                    "pages": [
                        {
                            "page_num": 1,
                            "summdesc": "Page with special chars: é à ü ñ",
                            "page_image": "/path/to/page.png"
                        }
                    ]
                }
            ]
        }
        data_room = DataRoom(index)
        doc_index = data_room.get_document_index()
        assert "日本語" in doc_index[0]["summdesc"]
        assert "🎉" in doc_index[0]["summdesc"]

    def test_very_long_summary(self):
        """Test handling of very long summaries."""
        long_summary = "A" * 10000
        index = {
            "documents": [
                {
                    "doc_id": "doc_long",
                    "summdesc": long_summary,
                    "pages": [
                        {
                            "page_num": 1,
                            "summdesc": long_summary,
                            "page_image": "/path/to/page.png"
                        }
                    ]
                }
            ]
        }
        data_room = DataRoom(index)
        summary = data_room.get_document_pages_summary("doc_long")
        assert len(summary) > 10000

    def test_duplicate_page_numbers(self):
        """Test handling of duplicate page numbers (malformed data)."""
        index = {
            "documents": [
                {
                    "doc_id": "doc_dup",
                    "summdesc": "Document with duplicate pages",
                    "pages": [
                        {"page_num": 1, "summdesc": "First page 1", "page_image": "/p1.png"},
                        {"page_num": 1, "summdesc": "Second page 1", "page_image": "/p2.png"}
                    ]
                }
            ]
        }
        data_room = DataRoom(index)
        # get_document_pages_images returns the first match
        results = data_room.get_document_pages_images("doc_dup", [1])
        assert len(results) == 1
        assert results[0]["summdesc"] == "First page 1"
