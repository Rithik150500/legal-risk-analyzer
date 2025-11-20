"""
Legal Risk Analysis Deep Agent System

This system creates a sophisticated legal risk analysis agent that:
1. Analyzes documents from a data room
2. Conducts web research for context
3. Generates comprehensive reports (Word documents)
4. Creates interactive dashboards (web artifacts)
"""

from typing import List, Dict, Any, Literal
import json
from deepagents import create_deep_agent, CompiledSubAgent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool


# ============================================================================
# DATA ROOM STRUCTURE
# ============================================================================

class DataRoom:
    """
    Represents the data room structure.
    
    Structure:
    {
        "documents": [
            {
                "doc_id": "doc_001",
                "summdesc": "Summary of entire document",
                "pages": [
                    {
                        "page_num": 1,
                        "summdesc": "Summary of page 1",
                        "page_image": "base64_encoded_image_or_path"
                    }
                ]
            }
        ]
    }
    """
    def __init__(self, data_room_index: Dict[str, Any]):
        self.data_room_index = data_room_index
    
    def get_document_index(self) -> List[Dict[str, str]]:
        """Returns simplified index with doc_id and summdesc only"""
        return [
            {
                "doc_id": doc["doc_id"],
                "summdesc": doc["summdesc"]
            }
            for doc in self.data_room_index["documents"]
        ]
    
    def get_document(self, doc_id: str) -> Dict[str, Any]:
        """Returns full document with all pages"""
        for doc in self.data_room_index["documents"]:
            if doc["doc_id"] == doc_id:
                return doc
        return None
    
    def get_document_pages_summary(self, doc_id: str) -> str:
        """Returns combined summary of all pages"""
        doc = self.get_document(doc_id)
        if not doc:
            return f"Error: Document {doc_id} not found"
        
        page_summaries = [
            f"Page {page['page_num']}: {page['summdesc']}"
            for page in doc["pages"]
        ]
        return "\n\n".join(page_summaries)
    
    def get_document_pages_images(self, doc_id: str, page_nums: List[int]) -> List[Dict[str, Any]]:
        """Returns page images for specified pages"""
        doc = self.get_document(doc_id)
        if not doc:
            return [{"error": f"Document {doc_id} not found"}]
        
        results = []
        for page_num in page_nums:
            page = next((p for p in doc["pages"] if p["page_num"] == page_num), None)
            if page:
                results.append({
                    "page_num": page_num,
                    "page_image": page["page_image"],
                    "summdesc": page["summdesc"]
                })
            else:
                results.append({
                    "page_num": page_num,
                    "error": f"Page {page_num} not found in document {doc_id}"
                })
        
        return results


# ============================================================================
# DATA ROOM TOOLS
# ============================================================================

def create_data_room_tools(data_room: DataRoom):
    """Creates tools for accessing the data room"""
    
    @tool
    def get_document(doc_id: str) -> str:
        """
        Retrieve a document's complete page-by-page summary.
        
        Args:
            doc_id: The unique identifier for the document (e.g., "doc_001")
            
        Returns:
            Combined summary of all pages in the document, with each page's
            summary clearly labeled by page number.
            
        Use this when you need to understand the full content of a document
        without viewing the actual page images.
        """
        return data_room.get_document_pages_summary(doc_id)
    
    @tool
    def get_document_pages(doc_id: str, page_nums: List[int]) -> str:
        """
        Retrieve specific page images and summaries from a document.
        
        Args:
            doc_id: The unique identifier for the document
            page_nums: List of page numbers to retrieve (e.g., [1, 3, 5])
            
        Returns:
            JSON string containing page images and summaries for the requested pages.
            Each entry includes page_num, page_image (base64 or path), and summdesc.
            
        Use this when you need to examine the actual content of specific pages,
        such as reviewing signatures, tables, charts, or specific clauses.
        """
        results = data_room.get_document_pages_images(doc_id, page_nums)
        return json.dumps(results, indent=2)
    
    @tool
    def list_all_documents() -> str:
        """
        List all documents available in the data room with their summaries.
        
        Returns:
            JSON string containing all documents with their doc_id and summdesc.
            
        Use this to get an overview of all available documents before starting
        your analysis. This helps you plan which documents to examine in detail.
        """
        index = data_room.get_document_index()
        return json.dumps(index, indent=2)
    
    return [get_document, get_document_pages, list_all_documents]


# ============================================================================
# SYSTEM PROMPTS
# ============================================================================

MAIN_AGENT_SYSTEM_PROMPT = """You are a Legal Risk Analysis Deep Agent specializing in comprehensive legal risk assessment.

Your primary responsibility is to coordinate a thorough legal risk analysis by:

1. PLANNING: Create a comprehensive analysis plan
   - Review the data room index to understand available documents
   - Identify key legal areas that require investigation
   - Determine which documents need detailed review
   - Plan the sequence of analysis tasks

2. DELEGATING ANALYSIS TASKS: Use subagents effectively
   - Delegate document analysis to the "legal-analyzer" subagent
   - Each analysis task should focus on specific risk areas
   - Ensure comprehensive coverage of all legal risk dimensions

3. CREATING DELIVERABLES: Coordinate final outputs
   - Delegate report creation to "report-creator" subagent
   - Delegate dashboard creation to "dashboard-creator" subagent

AVAILABLE DATA ROOM DOCUMENTS:
{data_room_index}

KEY LEGAL RISK AREAS TO ASSESS:
- Contractual risks (breaches, ambiguous terms, unfavorable clauses)
- Compliance risks (regulatory violations, license issues)
- Intellectual property risks (infringement, ownership disputes)
- Liability risks (indemnification, warranties, limitations)
- Financial risks (payment terms, penalties, guarantees)
- Operational risks (obligations, deadlines, deliverables)
- Reputational risks (confidentiality breaches, conflicts of interest)

WORKFLOW:
1. Use write_todos to create your analysis plan
2. Delegate analysis of different risk areas to "legal-analyzer" subagent
3. Synthesize findings from all analyses
4. Delegate report creation to "report-creator" subagent
5. Delegate dashboard creation to "dashboard-creator" subagent

Remember: You are the orchestrator. Your subagents do the detailed work while you maintain the big picture and ensure comprehensive coverage."""


ANALYSIS_SUBAGENT_SYSTEM_PROMPT = """You are a Legal Risk Analysis Specialist focused on detailed document review and risk assessment.

AVAILABLE DOCUMENTS IN DATA ROOM:
{data_room_index}

YOUR PROCESS: RETRIEVE -> ANALYSE -> CREATE FINDINGS

1. RETRIEVE:
   - Use list_all_documents() to see what's available
   - Use get_document(doc_id) to retrieve full page-by-page summaries
   - Use get_document_pages(doc_id, page_nums) when you need to see actual page images
   - Use web_search and web_fetch for legal precedents, regulations, and context

2. ANALYSE:
   For each risk area assigned to you, examine:
   
   CONTRACTUAL RISKS:
   - Identify ambiguous or undefined terms
   - Flag unfavorable or one-sided clauses
   - Note missing standard protections
   - Assess breach conditions and remedies
   
   COMPLIANCE RISKS:
   - Check regulatory requirements applicable to the transaction
   - Identify missing licenses or permits
   - Note data privacy and security obligations
   - Flag industry-specific compliance issues
   
   IP RISKS:
   - Review IP ownership and assignment clauses
   - Identify potential infringement issues
   - Assess license restrictions and limitations
   - Note IP indemnification provisions
   
   LIABILITY RISKS:
   - Review indemnification scope and limits
   - Assess warranty representations
   - Identify liability caps and exclusions
   - Note insurance requirements
   
   FINANCIAL RISKS:
   - Examine payment terms and conditions
   - Identify penalty and liquidated damages clauses
   - Review financial guarantees and security
   - Assess currency and exchange rate risks
   
   OPERATIONAL RISKS:
   - Review performance obligations and deadlines
   - Identify dependencies and prerequisites
   - Note force majeure and termination provisions
   - Assess change management procedures

3. CREATE FINDINGS:
   Write your findings to the filesystem:
   - /analysis/[risk_area]_findings.txt
   - Include: Risk description, severity (High/Medium/Low), affected documents, 
     specific clauses, recommendations, and supporting research
   
   For each risk identified, provide:
   - Clear description of the risk
   - Severity rating with justification
   - Specific document and clause references
   - Potential impact assessment
   - Recommended mitigation strategies
   - Supporting legal research or precedents

TOOLS AVAILABLE:
- list_all_documents(): Get overview of all documents
- get_document(doc_id): Get page-by-page summary of a document
- get_document_pages(doc_id, [page_nums]): Get actual page images
- web_search(query): Search for legal information
- web_fetch(url): Retrieve full content from legal databases
- Filesystem tools: write_file, edit_file, read_file for storing findings

IMPORTANT:
- Be thorough but concise in your findings
- Always cite specific documents and page numbers
- Use web research to validate concerns with precedents
- Save findings to filesystem for the main agent to compile
- Focus on actionable risks with clear mitigation strategies"""


REPORT_CREATOR_SYSTEM_PROMPT = """You are a Legal Report Creator specializing in professional legal risk analysis reports.

Your job is to create a comprehensive Word document (docx) that presents legal risk analysis findings in a clear, professional format.

BEFORE STARTING:
1. Read all analysis findings from /analysis/ directory
2. Review the data room index to understand the document context

REPORT STRUCTURE:

1. EXECUTIVE SUMMARY (1-2 pages)
   - Overall risk assessment
   - Key findings and critical risks
   - Summary of recommendations
   - Risk heat map or overview table

2. METHODOLOGY
   - Documents reviewed
   - Analysis framework used
   - Risk classification criteria
   - Limitations and assumptions

3. DETAILED RISK ANALYSIS (organized by category)
   For each risk category:
   - Category overview
   - Individual risks identified
   - Risk severity and likelihood
   - Affected documents and clauses
   - Potential impact
   - Mitigation recommendations

4. DOCUMENT-BY-DOCUMENT ANALYSIS
   - Summary of each key document
   - Main provisions reviewed
   - Issues identified
   - Cross-references to risk sections

5. RECOMMENDATIONS
   - Priority actions (immediate, short-term, long-term)
   - Suggested contract amendments
   - Process improvements
   - Ongoing monitoring requirements

6. APPENDICES
   - Risk severity definitions
   - Document index
   - Key terms glossary
   - Research references

FORMATTING REQUIREMENTS:
- Professional business format
- Clear headings and subheadings
- Tables for risk summaries
- Bullet points for recommendations
- Page numbers and table of contents
- Company branding (if provided)

INSTRUCTIONS:
1. Read all findings from /analysis/ directory using read_file
2. Review data room index from /memories/ or state
3. Use the docx skill to create a professional Word document
4. Save the final report to /outputs/legal_risk_analysis_report.docx

Remember: This report will be used by executives and legal counsel to make critical business decisions. It must be clear, accurate, and actionable."""


DASHBOARD_CREATOR_SYSTEM_PROMPT = """You are an Interactive Dashboard Creator specializing in legal risk visualization.

Your job is to create an interactive web-based dashboard (HTML artifact) that allows stakeholders to explore legal risk analysis findings dynamically.

BEFORE STARTING:
1. Read all analysis findings from /analysis/ directory
2. Review the data room index to understand the document context
3. Compile all risk data into a structured format

DASHBOARD FEATURES:

1. RISK OVERVIEW SECTION
   - Risk heat map (severity vs. likelihood)
   - Risk distribution by category (pie chart)
   - Risk trend indicators
   - Overall risk score

2. RISK CATEGORY TABS
   Create tabs for each risk category:
   - Contractual Risks
   - Compliance Risks
   - IP Risks
   - Liability Risks
   - Financial Risks
   - Operational Risks
   - Reputational Risks

3. DETAILED RISK CARDS
   For each risk, display:
   - Risk title and description
   - Severity badge (High/Medium/Low with color coding)
   - Affected documents (clickable to show details)
   - Impact assessment
   - Mitigation recommendations
   - Status indicator

4. DOCUMENT EXPLORER
   - List of all documents analyzed
   - Summary of findings per document
   - Link to specific risks identified
   - Filter by document type

5. INTERACTIVE FILTERS
   - Filter by severity
   - Filter by risk category
   - Filter by affected document
   - Search functionality

6. RECOMMENDATIONS PANEL
   - Priority actions timeline
   - Action items with owners
   - Progress tracking
   - Export functionality

TECHNICAL REQUIREMENTS:
- Use React for interactivity
- Use Tailwind CSS for styling
- Use Recharts for data visualization
- Implement responsive design
- Include print-friendly view
- Add export to CSV/JSON functionality

COLOR SCHEME:
- High Risk: Red (#DC2626)
- Medium Risk: Orange (#EA580C)
- Low Risk: Green (#16A34A)
- Info: Blue (#2563EB)
- Background: Professional grays and whites

INSTRUCTIONS:
1. Read all findings from /analysis/ directory using read_file
2. Parse and structure the data for visualization
3. Create a single-file React component (.jsx artifact)
4. Ensure all data is embedded (no external data files)
5. Make the dashboard intuitive and visually appealing

Remember: This dashboard will be used by executives who need to quickly understand risk exposure and make informed decisions. Prioritize clarity and usability."""


# ============================================================================
# AGENT CREATION FUNCTION
# ============================================================================

def create_legal_risk_analysis_agent(data_room_index: Dict[str, Any]):
    """
    Creates the main Legal Risk Analysis Deep Agent with all subagents.
    
    Args:
        data_room_index: Dictionary containing the data room structure
        
    Returns:
        Configured deep agent ready for legal risk analysis
    """
    
    # Initialize data room
    data_room = DataRoom(data_room_index)
    
    # Create data room tools
    data_room_tools = create_data_room_tools(data_room)
    
    # Create backend with persistent memory for findings
    def create_backend(runtime):
        return CompositeBackend(
            default=StateBackend(runtime),
            routes={
                "/memories/": StoreBackend(runtime),
                "/analysis/": StoreBackend(runtime),  # Persist analysis findings
            }
        )
    
    # Format data room index for system prompts
    data_room_index_text = json.dumps(data_room.get_document_index(), indent=2)
    
    # Define subagents
    subagents = [
        {
            "name": "legal-analyzer",
            "description": "Specialist in detailed legal document analysis and risk assessment. Use this subagent to analyze specific risk areas across documents. It can access data room documents, conduct web research, and create detailed findings.",
            "system_prompt": ANALYSIS_SUBAGENT_SYSTEM_PROMPT.format(
                data_room_index=data_room_index_text
            ),
            "tools": data_room_tools + [],  # Add web_search and web_fetch if available
            "model": "claude-sonnet-4-5-20250929",
        },
        {
            "name": "report-creator",
            "description": "Specialist in creating professional legal risk analysis reports in Word document format. Use this subagent after all analysis is complete to compile findings into a comprehensive report.",
            "system_prompt": REPORT_CREATOR_SYSTEM_PROMPT,
            "tools": [],  # Will use filesystem tools from middleware
            "model": "claude-sonnet-4-5-20250929",
        },
        {
            "name": "dashboard-creator",
            "description": "Specialist in creating interactive web-based dashboards for risk visualization. Use this subagent after all analysis is complete to create an interactive dashboard for stakeholders.",
            "system_prompt": DASHBOARD_CREATOR_SYSTEM_PROMPT,
            "tools": [],  # Will use filesystem tools from middleware
            "model": "claude-sonnet-4-5-20250929",
        },
    ]
    
    # Create the main agent
    agent = create_deep_agent(
        model="claude-sonnet-4-5-20250929",
        system_prompt=MAIN_AGENT_SYSTEM_PROMPT.format(
            data_room_index=data_room_index_text
        ),
        tools=data_room_tools,  # Main agent has access to data room tools
        subagents=subagents,
        backend=create_backend,
        store=InMemoryStore(),  # Use persistent store in production
        checkpointer=MemorySaver(),
    )
    
    return agent


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def example_usage():
    """Example of how to use the Legal Risk Analysis Agent"""
    
    # Example data room index (normally loaded from your preprocessing system)
    example_data_room = {
        "documents": [
            {
                "doc_id": "doc_001",
                "summdesc": "Master Service Agreement between Company A and Company B covering software development services, payment terms, and intellectual property rights",
                "pages": [
                    {
                        "page_num": 1,
                        "summdesc": "Title page and parties identification, effective date January 1, 2024",
                        "page_image": "path/to/page1.png"
                    },
                    {
                        "page_num": 2,
                        "summdesc": "Scope of services section defining software development deliverables and timelines",
                        "page_image": "path/to/page2.png"
                    },
                    {
                        "page_num": 3,
                        "summdesc": "Payment terms including milestone payments and late payment penalties",
                        "page_image": "path/to/page3.png"
                    }
                ]
            },
            {
                "doc_id": "doc_002",
                "summdesc": "Non-Disclosure Agreement with confidentiality obligations, term of 5 years, and mutual obligations between parties",
                "pages": [
                    {
                        "page_num": 1,
                        "summdesc": "NDA definitions and scope of confidential information",
                        "page_image": "path/to/nda_page1.png"
                    },
                    {
                        "page_num": 2,
                        "summdesc": "Obligations and exclusions from confidentiality requirements",
                        "page_image": "path/to/nda_page2.png"
                    }
                ]
            }
        ]
    }
    
    # Create the agent
    agent = create_legal_risk_analysis_agent(example_data_room)
    
    # Run analysis
    config = {"configurable": {"thread_id": "legal_analysis_001"}}
    
    result = agent.invoke({
        "messages": [{
            "role": "user",
            "content": "Please conduct a comprehensive legal risk analysis of all documents in the data room. Focus on identifying high-severity risks across all categories including contractual, compliance, IP, liability, financial, and operational risks. After the analysis, create both a detailed report and an interactive dashboard."
        }]
    }, config=config)
    
    return result


if __name__ == "__main__":
    # Run example
    print("Legal Risk Analysis Deep Agent System")
    print("=" * 60)
    print("\nThis system provides:")
    print("1. Coordinated legal risk analysis across multiple documents")
    print("2. Specialized subagents for analysis, reporting, and visualization")
    print("3. Access to data room documents and web research")
    print("4. Professional report generation (Word document)")
    print("5. Interactive dashboard creation (web artifact)")
    print("\nExample usage:")
    print("agent = create_legal_risk_analysis_agent(your_data_room_index)")
    print("result = agent.invoke({'messages': [...]}, config=config)")
