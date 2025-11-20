# CLAUDE.md - Legal Risk Analysis Deep Agent System

## Project Overview

This is a **Legal Risk Analysis Deep Agent System** built on the deepagents/langgraph/langchain framework. The system automates legal document review using a multi-agent architecture with human-in-the-loop (HITL) approval workflows.

### Core Purpose
- Analyze legal documents (contracts, NDAs, SOWs) for risks across 7 categories
- Generate professional Word document reports
- Create interactive web dashboards for risk visualization
- Provide human oversight at critical decision points

### Technology Stack
- **Python 3.9+** - Runtime environment
- **deepagents** - Agent harness framework
- **langgraph/langchain** - Agent orchestration
- **Claude claude-sonnet-4-5-20250929** - AI model for analysis
- **LibreOffice** - Document to PDF conversion
- **pdf2image/Pillow** - PDF page extraction
- **python-docx** - Word document generation

---

## Project Structure

```
legal-risk-analyzer/
├── CLAUDE.md                      # This file - AI assistant guide
├── README.md                      # Full system documentation
├── START_HERE.md                  # Quick start guide
├── SYSTEM_OVERVIEW.md             # Architecture diagrams
├── FILES_GUIDE.md                 # File navigation guide
├── HITL_QUICK_REFERENCE.md        # Human-in-the-loop reference
├── human_in_the_loop_guide.md     # Comprehensive HITL guide
├── requirements.txt               # Python dependencies
│
├── legal_risk_analysis_agent.py   # Main agent system (core)
├── data_room_indexer.py           # Document preprocessing
├── hitl_implementation.py         # Human approval workflows
├── example_usage.py               # Usage patterns and examples
└── demo_quick_start.py            # Quick validation demo
```

---

## Architecture

### Multi-Agent Hierarchy

```
                    Main Orchestrator Agent
                    (Plans & Coordinates)
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    Legal Analyzer    Report Creator   Dashboard Creator
       Subagent          Subagent          Subagent
            │               │                   │
      [Findings]     [Report.docx]      [Dashboard.html]
```

### Agent Responsibilities

1. **Main Agent** (`legal_risk_analysis_agent.py`)
   - Reviews data room index
   - Creates analysis plan using `write_todos`
   - Delegates to specialized subagents using `task`
   - Coordinates final deliverables

2. **Legal Analyzer Subagent**
   - Retrieves documents from data room
   - Analyzes risks across categories
   - Conducts web research for context
   - Creates findings files

3. **Report Creator Subagent**
   - Reads analysis findings
   - Creates professional Word document
   - Includes executive summary, recommendations

4. **Dashboard Creator Subagent**
   - Creates interactive React dashboard
   - Visualizes risks with charts
   - Enables filtering and exploration

---

## Key Files and Their Purpose

### Core Implementation

**`legal_risk_analysis_agent.py`** (Primary)
- `DataRoom` class - Manages document access
- `create_data_room_tools()` - Tools for document retrieval
- `create_legal_risk_analysis_agent()` - Main factory function
- System prompts for all agents
- Model: `claude-sonnet-4-5-20250929`

**`data_room_indexer.py`**
- `DataRoomIndexer` class - Full preprocessing pipeline
- Converts documents to PDF using LibreOffice
- Extracts pages as images
- Generates AI summaries (page-level and document-level)
- Outputs JSON data room index

**`hitl_implementation.py`**
- `ApprovalLevel` class - Pre-defined oversight configurations
- `ReviewInterface` classes - CLI, Auto-approve interfaces
- `AuditLogger` class - Compliance logging
- `create_agent_with_hitl()` - HITL-enabled agent factory
- `run_agent_with_hitl()` - Execution with approval handling

### Usage Examples

**`example_usage.py`** - Three usage patterns:
1. Comprehensive analysis (full system)
2. Targeted analysis (specific focus)
3. Interactive follow-up (conversational)

**`demo_quick_start.py`** - Environment validation without API calls

---

## Development Workflow

### Initial Setup

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install system dependencies
# Ubuntu/Debian:
sudo apt-get install libreoffice poppler-utils

# macOS:
brew install --cask libreoffice
brew install poppler

# 3. Set API key
export ANTHROPIC_API_KEY="your-key-here"
# or
export OPENAI_API_KEY="your-key-here"
```

### Standard Development Flow

1. **Preprocess Documents**
   ```bash
   python data_room_indexer.py
   ```

2. **Run Analysis**
   ```bash
   python example_usage.py
   # Choose option 1 for comprehensive analysis
   ```

3. **Run with Human Oversight**
   ```bash
   python hitl_implementation.py
   ```

### Testing Changes

```bash
# Quick validation (no API calls)
python demo_quick_start.py

# Full example with mock data
python example_usage.py
```

---

## Code Conventions

### Python Style

- **Type Hints**: Use `typing` module throughout
  ```python
  def get_document(self, doc_id: str) -> Dict[str, Any]:
  ```

- **Docstrings**: Comprehensive docstrings for all classes and functions
  ```python
  def convert_to_pdf(self, file_path: Path) -> Path:
      """
      Convert a file to PDF using LibreOffice.

      Args:
          file_path: Path to the file to convert

      Returns:
          Path to the converted PDF file
      """
  ```

- **Section Separators**: Use comment blocks for major sections
  ```python
  # ============================================================================
  # DATA ROOM TOOLS
  # ============================================================================
  ```

- **Path Handling**: Use `pathlib.Path` not string paths
  ```python
  from pathlib import Path
  self.output_folder = Path(output_folder)
  ```

### Tool Definitions

Use `@tool` decorator from `langchain_core.tools`:
```python
from langchain_core.tools import tool

@tool
def get_document(doc_id: str) -> str:
    """
    Retrieve a document's complete page-by-page summary.

    Args:
        doc_id: The unique identifier for the document

    Returns:
        Combined summary of all pages in the document
    """
    return data_room.get_document_pages_summary(doc_id)
```

### System Prompts

- Use multi-line strings with clear structure
- Include available tools/documents in context
- Define specific workflows and processes
- Example format:
  ```python
  MAIN_AGENT_SYSTEM_PROMPT = """You are a Legal Risk Analysis Deep Agent...

  1. PLANNING: Create a comprehensive analysis plan
     - Review the data room index...

  AVAILABLE DATA ROOM DOCUMENTS:
  {data_room_index}

  WORKFLOW:
  1. Use write_todos to create your analysis plan
  ...
  """
  ```

### JSON Data Structures

Data room index format:
```json
{
  "documents": [
    {
      "doc_id": "doc_001",
      "summdesc": "Document summary...",
      "pages": [
        {
          "page_num": 1,
          "summdesc": "Page summary...",
          "page_image": "path/to/image.png"
        }
      ]
    }
  ]
}
```

---

## Risk Categories Analyzed

The system analyzes 7 major legal risk categories:

1. **Contractual Risks** - Breaches, ambiguous terms, unfavorable clauses
2. **Compliance Risks** - Regulatory violations, license issues
3. **IP Risks** - Infringement, ownership disputes
4. **Liability Risks** - Indemnification, warranties, limitations
5. **Financial Risks** - Payment terms, penalties, guarantees
6. **Operational Risks** - Obligations, deadlines, deliverables
7. **Reputational Risks** - Confidentiality breaches, conflicts

---

## Human-in-the-Loop (HITL) System

### Approval Points

Four critical operations require human approval:

| Operation | Purpose | Tool |
|-----------|---------|------|
| Planning | Review analysis plan | `write_todos` |
| Delegation | Validate task scope | `task` |
| Document Access | Audit trail | `get_document` |
| File Operations | Verify accuracy | `write_file` |

### Approval Levels

```python
# High Oversight - All operations
ApprovalLevel.high_oversight()

# Moderate Oversight - Planning, delegation, outputs
ApprovalLevel.moderate_oversight()

# Minimal Oversight - Only final outputs
ApprovalLevel.minimal_oversight()

# Custom configuration
ApprovalLevel.custom(
    planning=True,
    delegation=True,
    document_access=False,
    file_operations=True
)
```

---

## Common Tasks for AI Assistants

### Adding a New Risk Category

1. Update `ANALYSIS_SUBAGENT_SYSTEM_PROMPT` in `legal_risk_analysis_agent.py`
2. Add category to the analysis section
3. Add category to `DASHBOARD_CREATOR_SYSTEM_PROMPT` tabs

### Modifying Report Format

1. Edit `REPORT_CREATOR_SYSTEM_PROMPT` in `legal_risk_analysis_agent.py`
2. Update the report structure section

### Adding New Tools

1. Define tool with `@tool` decorator in `legal_risk_analysis_agent.py`
2. Add to `create_data_room_tools()` return list
3. Document in relevant system prompt

### Changing AI Model

Update model in `create_legal_risk_analysis_agent()`:
```python
agent = create_deep_agent(
    model="claude-sonnet-4-5-20250929",  # Change here
    ...
)
```

And in subagent definitions:
```python
{
    "name": "legal-analyzer",
    "model": "claude-sonnet-4-5-20250929",  # And here
    ...
}
```

### Adding New Subagent

1. Create system prompt constant
2. Add to `subagents` list in `create_legal_risk_analysis_agent()`
3. Document in main agent system prompt

---

## Important Implementation Details

### Storage Backends

```python
def create_backend(runtime):
    return CompositeBackend(
        default=StateBackend(runtime),
        routes={
            "/memories/": StoreBackend(runtime),
            "/analysis/": StoreBackend(runtime),  # Persist findings
        }
    )
```

### Agent Configuration

```python
config = {"configurable": {"thread_id": "analysis_001"}}
result = agent.invoke({
    "messages": [{"role": "user", "content": "Your request"}]
}, config=config)
```

### Interrupt Handling

```python
while result.get("__interrupt__"):
    # Get human decision
    decisions = [review_interface.review_action(action, config)]

    # Resume with decisions
    result = agent.invoke(
        Command(resume={"decisions": decisions}),
        config=config
    )
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| LibreOffice not found | Install LibreOffice, ensure in PATH |
| PDF extraction fails | Install poppler-utils (Linux) or poppler (macOS) |
| Context window full | Ensure subagents save to filesystem |
| Too many approvals | Lower approval level to moderate/minimal |
| API key errors | Set ANTHROPIC_API_KEY or OPENAI_API_KEY |

### Debug Tips

1. Run `demo_quick_start.py` to validate environment
2. Check API key configuration
3. Verify system dependencies (LibreOffice, Poppler)
4. Review audit logs in `review_audit.jsonl`

---

## Dependencies

### Python Packages (requirements.txt)

- `deepagents>=0.1.0` - Agent framework
- `langgraph>=0.2.0` - Graph-based agents
- `langchain>=0.3.0` - LLM chains
- `langchain-anthropic>=0.3.0` - Claude integration
- `langchain-openai>=0.2.0` - OpenAI integration
- `pdf2image>=1.16.3` - PDF to image
- `Pillow>=10.0.0` - Image processing
- `python-docx>=1.1.0` - Word documents
- `openpyxl>=3.1.0` - Excel files
- `tavily-python>=0.3.0` - Web search

### System Dependencies

- **LibreOffice** - Document conversion
- **Poppler** - PDF processing (poppler-utils on Linux)

---

## Best Practices

1. **Always use thread IDs** for analysis sessions
2. **Save findings to filesystem** to manage context window
3. **Start with high oversight** when deploying
4. **Review the plan first** - catches most issues early
5. **Use subagents for heavy lifting** - main agent stays focused
6. **Log all approvals** for audit compliance
7. **Test with demo_quick_start.py** before full runs

---

## File Reading Order for New Contributors

1. `README.md` - System overview and purpose
2. `SYSTEM_OVERVIEW.md` - Architecture diagrams
3. `legal_risk_analysis_agent.py` - Core implementation
4. `example_usage.py` - Usage patterns
5. `hitl_implementation.py` - Human oversight
6. `data_room_indexer.py` - Preprocessing

---

## Quick Reference

### Create Agent
```python
from legal_risk_analysis_agent import create_legal_risk_analysis_agent
agent = create_legal_risk_analysis_agent(data_room_index)
```

### Run Analysis
```python
config = {"configurable": {"thread_id": "analysis_001"}}
result = agent.invoke({
    "messages": [{"role": "user", "content": "Analyze all documents"}]
}, config=config)
```

### Run with HITL
```python
from hitl_implementation import (
    create_agent_with_hitl,
    run_agent_with_hitl,
    ApprovalLevel,
    CLIReviewInterface
)

agent_config = create_agent_with_hitl(
    data_room_index=data_room_index,
    approval_level=ApprovalLevel.moderate_oversight(),
    review_interface=CLIReviewInterface()
)

result = run_agent_with_hitl(
    agent_config=agent_config,
    user_message="Analyze contractual risks",
    thread_id="analysis_001"
)
```

### Preprocess Documents
```python
from data_room_indexer import DataRoomIndexer

indexer = DataRoomIndexer(
    input_folder="/path/to/documents",
    output_folder="/path/to/output",
    summarization_model="gpt-4o-mini",
    dpi=200
)
data_room_index = indexer.build_data_room_index()
```

---

## Notes for AI Assistants

- This codebase uses `claude-sonnet-4-5-20250929` as the default model
- All agents use the same model for consistency
- The system is designed for legal document analysis but can be adapted
- HITL is critical for production deployments in legal contexts
- Always commit changes with clear, descriptive messages
- Run tests after modifications when available
