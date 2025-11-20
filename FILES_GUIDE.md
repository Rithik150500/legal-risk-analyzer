# Legal Risk Analysis System - File Guide

## Complete File Listing

### 📋 Core System Files

**legal_risk_analysis_agent.py** (22 KB)
- Main agent implementation with all subagents
- Data room tools (get_document, get_document_pages, list_all_documents)
- System prompts for main agent and all three subagents
- Agent creation and configuration functions
- **Use this:** As the main agent system you import and use

**data_room_indexer.py** (14 KB)  
- Document preprocessing pipeline
- PDF conversion using LibreOffice
- Page extraction and image generation
- AI-powered summarization system
- Data room index builder
- **Use this:** To preprocess your documents before analysis

### 🎯 Usage & Examples

**example_usage.py** (30 KB)
- Three complete usage patterns:
  1. Comprehensive analysis (full system)
  2. Targeted analysis (specific focus)
  3. Interactive follow-up (conversational)
- Mock data room for testing
- Working code examples with explanations
- **Use this:** To understand how to use the system

**demo_quick_start.py** (14 KB)
- Minimal working example for quick testing
- Simplified demonstration of core functionality
- **Use this:** For quick experiments and testing

### 🔐 Human-in-the-Loop System

**hitl_implementation.py** (24 KB)
- Complete HITL implementation with working code
- Multiple review interface options (CLI, Web, Slack)
- Approval level configurations (high/moderate/minimal)
- Audit logging system
- Review statistics and monitoring
- **Use this:** To implement human oversight in your deployment

**human_in_the_loop_guide.md** (27 KB)
- Comprehensive HITL concepts and architecture
- Detailed explanations of why HITL matters
- Extensive examples with before/after scenarios
- Best practices and deployment checklist
- Production deployment guidance
- **Read this:** For deep understanding of HITL system design

**HITL_QUICK_REFERENCE.md** (14 KB)
- Quick reference for the four key operations:
  * write_todos (planning)
  * task (delegation)
  * get_document (access)
  * write_file (findings)
- Copy-paste configurations
- Common scenarios and troubleshooting
- **Use this:** As a desk reference while reviewing actions

### 📚 Documentation

**README.md** (17 KB)
- Complete system overview
- What the system does and why
- Architecture explanation (human-friendly prose)
- Prerequisites and installation
- Usage guide with all steps
- Advanced features and troubleshooting
- **Read this first:** For comprehensive understanding

**SYSTEM_OVERVIEW.md** (22 KB)
- Visual architecture diagrams (ASCII art)
- Complete workflow examples with step-by-step flow
- Human-in-the-loop integration details
- Approval level configurations
- Review interface options
- Key benefits and metrics
- **Use this:** As a reference architecture guide

### ⚙️ Configuration

**requirements.txt** (1.5 KB)
- All Python dependencies
- System requirements notes
- Installation instructions
- **Use this:** With pip install -r requirements.txt

---

## How to Use These Files

### Getting Started Path

1. **Read first:** README.md
   - Understand what the system does
   - Check prerequisites
   - Follow installation steps

2. **Read second:** SYSTEM_OVERVIEW.md  
   - See the architecture visually
   - Understand the workflow
   - Review the examples

3. **Run example:** example_usage.py
   - See the system in action
   - Try different patterns
   - Understand the API

### Adding HITL Path

4. **Read:** human_in_the_loop_guide.md
   - Understand HITL concepts
   - See detailed examples
   - Learn best practices

5. **Reference:** HITL_QUICK_REFERENCE.md
   - Quick lookup while working
   - Common scenarios
   - Configuration options

6. **Implement:** hitl_implementation.py
   - Use the provided interfaces
   - Configure approval levels
   - Set up audit logging

### Production Deployment Path

7. **Preprocess documents:** data_room_indexer.py
   - Convert your documents
   - Generate summaries
   - Build the index

8. **Deploy agent:** legal_risk_analysis_agent.py
   - Configure for production
   - Set up persistence
   - Enable monitoring

9. **Enable HITL:** hitl_implementation.py
   - Choose approval level
   - Set up review interface
   - Configure audit logging

---

## Key Concepts by File

### Main Agent System (legal_risk_analysis_agent.py)

```python
# What it contains:
- DataRoom class (manages document access)
- Data room tools (get_document, get_document_pages, list_all_documents)
- Main agent system prompt
- Legal Analyzer subagent (document analysis)
- Report Creator subagent (Word document generation)  
- Dashboard Creator subagent (web interface creation)
- create_legal_risk_analysis_agent() function

# How to use:
from legal_risk_analysis_agent import create_legal_risk_analysis_agent

agent = create_legal_risk_analysis_agent(your_data_room_index)
result = agent.invoke({"messages": [...]}, config=config)
```

### Document Preprocessing (data_room_indexer.py)

```python
# What it does:
1. Converts files to PDF (LibreOffice)
2. Extracts pages as images
3. Summarizes each page (AI model)
4. Summarizes whole document (AI model)
5. Builds structured index

# How to use:
from data_room_indexer import DataRoomIndexer

indexer = DataRoomIndexer(
    input_folder="/path/to/documents",
    output_folder="/path/to/output"
)
data_room_index = indexer.build_data_room_index()
```

### HITL Implementation (hitl_implementation.py)

```python
# What it provides:
- ApprovalLevel.high_oversight() / moderate / minimal / custom()
- CLIReviewInterface() for terminal review
- AutoApproveInterface() for testing
- AuditLogger() for compliance
- create_agent_with_hitl() wrapper
- run_agent_with_hitl() execution

# How to use:
from hitl_implementation import (
    create_agent_with_hitl,
    run_agent_with_hitl,
    ApprovalLevel,
    CLIReviewInterface
)

agent_config = create_agent_with_hitl(
    data_room_index=index,
    approval_level=ApprovalLevel.moderate_oversight(),
    review_interface=CLIReviewInterface()
)

result = run_agent_with_hitl(
    agent_config=agent_config,
    user_message="Your request here",
    thread_id="analysis_001"
)
```

---

## Quick Navigation by Task

**I want to...**

**Understand the system:**
→ README.md → SYSTEM_OVERVIEW.md

**See code examples:**
→ example_usage.py → demo_quick_start.py

**Learn about HITL:**
→ human_in_the_loop_guide.md → HITL_QUICK_REFERENCE.md

**Implement HITL:**
→ hitl_implementation.py → HITL_QUICK_REFERENCE.md (for config)

**Deploy to production:**
→ README.md (prerequisites) → data_room_indexer.py (preprocess) → legal_risk_analysis_agent.py (deploy)

**Review agent actions:**
→ HITL_QUICK_REFERENCE.md (quick lookup) → human_in_the_loop_guide.md (detailed guidance)

**Troubleshoot issues:**
→ README.md (common issues) → SYSTEM_OVERVIEW.md (architecture) → example_usage.py (working code)

**Customize for my needs:**
→ SYSTEM_OVERVIEW.md (understand components) → legal_risk_analysis_agent.py (modify prompts/tools)

---

## File Sizes & Complexity

**Quick reads (< 5 minutes):**
- requirements.txt (1.5 KB)
- demo_quick_start.py (14 KB)
- HITL_QUICK_REFERENCE.md (14 KB)

**Medium reads (10-15 minutes):**
- data_room_indexer.py (14 KB)
- README.md (17 KB)
- SYSTEM_OVERVIEW.md (22 KB)
- legal_risk_analysis_agent.py (22 KB)

**Deep reads (20-30 minutes):**
- hitl_implementation.py (24 KB)
- human_in_the_loop_guide.md (27 KB)
- example_usage.py (30 KB)

---

## Dependencies Between Files

```
requirements.txt
    ↓ (install)
data_room_indexer.py
    ↓ (creates)
data_room_index.json
    ↓ (used by)
legal_risk_analysis_agent.py
    ↓ (wrapped by)
hitl_implementation.py
    ↓ (demonstrated in)
example_usage.py

Documentation flow:
README.md → SYSTEM_OVERVIEW.md → human_in_the_loop_guide.md → HITL_QUICK_REFERENCE.md
```

---

## Suggested Reading Order

### For Developers
1. README.md (understand the system)
2. example_usage.py (see it working)
3. legal_risk_analysis_agent.py (study implementation)
4. hitl_implementation.py (add oversight)
5. data_room_indexer.py (handle preprocessing)

### For Legal Professionals
1. README.md (understand capabilities)
2. SYSTEM_OVERVIEW.md (see workflows)
3. HITL_QUICK_REFERENCE.md (learn review process)
4. human_in_the_loop_guide.md (understand oversight)
5. example_usage.py (see usage patterns)

### For System Architects
1. SYSTEM_OVERVIEW.md (architecture)
2. legal_risk_analysis_agent.py (implementation)
3. hitl_implementation.py (oversight system)
4. human_in_the_loop_guide.md (deployment)
5. data_room_indexer.py (preprocessing)

### For Quick Start
1. README.md (setup instructions)
2. demo_quick_start.py (run immediately)
3. HITL_QUICK_REFERENCE.md (if adding oversight)

---

## Getting Help

**Problem: Don't know where to start**
→ Start with README.md, then run demo_quick_start.py

**Problem: Need to understand architecture**
→ Read SYSTEM_OVERVIEW.md with visual diagrams

**Problem: HITL not working as expected**
→ Check HITL_QUICK_REFERENCE.md, then human_in_the_loop_guide.md

**Problem: Preprocessing fails**
→ Check README.md prerequisites, review data_room_indexer.py comments

**Problem: Want to customize prompts**
→ Study legal_risk_analysis_agent.py, modify system prompts

**Problem: Need production deployment help**
→ README.md deployment section + SYSTEM_OVERVIEW.md production checklist

---

All files are ready to use. Start with README.md and follow the path that matches your role and needs!
