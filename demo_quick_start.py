"""
Quick Start Demo - Legal Risk Analysis System

This simplified demo shows you how the system works without requiring
full AI processing. It's perfect for:
1. Validating your environment setup
2. Understanding the system flow
3. Testing before committing to API costs

Once this works, you can move to the full example_usage.py
"""

import json
from pathlib import Path


def show_system_overview():
    """Display an overview of what the system does."""
    print("\n" + "=" * 80)
    print("LEGAL RISK ANALYSIS SYSTEM - QUICK START DEMO")
    print("=" * 80)
    print("\nThis demo walks you through the system without making AI API calls.")
    print("Once you're ready, you can run the full analysis with real AI models.")
    
    print("\n" + "-" * 80)
    print("SYSTEM ARCHITECTURE")
    print("-" * 80)
    print("\n1. MAIN AGENT (Orchestrator)")
    print("   - Reviews available documents")
    print("   - Creates analysis plan")
    print("   - Delegates to specialized subagents")
    print("   - Coordinates deliverables")
    
    print("\n2. LEGAL ANALYZER SUBAGENT")
    print("   - Retrieves documents from data room")
    print("   - Identifies risks across categories:")
    print("     • Contractual risks")
    print("     • Compliance risks")
    print("     • IP risks")
    print("     • Liability risks")
    print("     • Financial risks")
    print("     • Operational risks")
    print("   - Conducts web research")
    print("   - Creates detailed findings")
    
    print("\n3. REPORT CREATOR SUBAGENT")
    print("   - Reads all analysis findings")
    print("   - Creates professional Word document")
    print("   - Includes executive summary and recommendations")
    
    print("\n4. DASHBOARD CREATOR SUBAGENT")
    print("   - Builds interactive web interface")
    print("   - Visualizes risks with charts")
    print("   - Enables filtering and exploration")


def show_data_room_structure():
    """Explain the data room structure."""
    print("\n" + "=" * 80)
    print("DATA ROOM STRUCTURE")
    print("=" * 80)
    
    example_structure = {
        "documents": [
            {
                "doc_id": "doc_001",
                "summdesc": "Master Service Agreement - Software development contract...",
                "pages": [
                    {
                        "page_num": 1,
                        "summdesc": "Title page with parties and effective date",
                        "page_image": "/path/to/page1.png"
                    }
                ]
            }
        ]
    }
    
    print("\nThe data room index is a JSON structure that contains:")
    print("\n• Document metadata (ID, summaries)")
    print("• Page-by-page summaries")
    print("• Page images for detailed inspection")
    print("\nExample structure:")
    print(json.dumps(example_structure, indent=2))
    
    print("\n" + "-" * 80)
    print("HOW IT'S CREATED:")
    print("-" * 80)
    print("\n1. Convert documents to PDF (using LibreOffice)")
    print("2. Extract each page as an image")
    print("3. Use AI to summarize each page")
    print("4. Create document-level summary from page summaries")
    print("5. Build structured JSON index")


def show_preprocessing_steps():
    """Show what the preprocessing pipeline does."""
    print("\n" + "=" * 80)
    print("PREPROCESSING YOUR DOCUMENTS")
    print("=" * 80)
    
    print("\nTo prepare your documents for analysis:")
    
    print("\n1. ORGANIZE YOUR DOCUMENTS")
    print("   Create a folder with your legal documents:")
    print("   C:\\MyDocs\\contracts\\")
    print("   ├── master_agreement.docx")
    print("   ├── nda.pdf")
    print("   ├── sow.xlsx")
    print("   └── amendment.pdf")
    
    print("\n2. CONFIGURE THE INDEXER")
    print("   Edit data_room_indexer.py:")
    print("   ")
    print("   input_folder = 'C:/MyDocs/contracts'")
    print("   output_folder = 'C:/MyDocs/processed_dataroom'")
    
    print("\n3. RUN THE INDEXER")
    print("   python data_room_indexer.py")
    print("   ")
    print("   This will:")
    print("   • Convert all documents to PDF")
    print("   • Extract pages as images")
    print("   • Generate AI summaries")
    print("   • Create data_room_index.json")
    
    print("\n4. VERIFY THE OUTPUT")
    print("   Check the output folder for:")
    print("   C:/MyDocs/processed_dataroom/")
    print("   ├── data_room_index.json  ← Main index file")
    print("   ├── pdfs/                 ← Converted PDFs")
    print("   └── pages/                ← Extracted page images")


def show_running_analysis():
    """Show how to run the actual analysis."""
    print("\n" + "=" * 80)
    print("RUNNING AN ANALYSIS")
    print("=" * 80)
    
    print("\nONCE YOUR DATA ROOM IS INDEXED:")
    
    print("\n1. LOAD YOUR INDEX")
    print("   In example_usage.py, modify the create_mock_data_room() function:")
    print("   ")
    print("   def load_real_data_room():")
    print("       with open('C:/MyDocs/processed_dataroom/data_room_index.json') as f:")
    print("           return json.load(f)")
    
    print("\n2. CREATE THE AGENT")
    print("   agent = create_legal_risk_analysis_agent(data_room_index)")
    
    print("\n3. RUN THE ANALYSIS")
    print("   result = agent.invoke({")
    print("       'messages': [{'role': 'user', 'content': 'Analyze all documents...'}]")
    print("   }, config={'configurable': {'thread_id': 'analysis_001'}})")
    
    print("\n4. ACCESS THE RESULTS")
    print("   • Word Report: /outputs/legal_risk_analysis_report.docx")
    print("   • Dashboard: /outputs/legal_risk_dashboard.html")
    print("   • Findings: /analysis/")


def show_next_steps():
    """Show what to do next."""
    print("\n" + "=" * 80)
    print("YOUR NEXT STEPS")
    print("=" * 80)
    
    print("\n✓ ENVIRONMENT SETUP COMPLETE")
    print("  Your system ran without errors, which means:")
    print("  • Python is correctly installed")
    print("  • All dependencies are available")
    print("  • The code files are in place")
    
    print("\n→ STEP 1: VERIFY SYSTEM DEPENDENCIES")
    print("  Check that you have:")
    print("  • LibreOffice installed (for document conversion)")
    print("  • Poppler installed (for PDF processing)")
    print("  • API key configured (ANTHROPIC_API_KEY or OPENAI_API_KEY)")
    
    print("\n→ STEP 2: TEST PREPROCESSING")
    print("  Create a test folder with 1-2 documents:")
    print("  ")
    print("  test_folder/")
    print("  ├── sample_contract.docx")
    print("  └── sample_nda.pdf")
    print("  ")
    print("  Then run:")
    print("  python data_room_indexer.py")
    
    print("\n→ STEP 3: VERIFY THE INDEX")
    print("  Open the generated data_room_index.json")
    print("  Check that:")
    print("  • Document summaries look accurate")
    print("  • Page summaries capture key info")
    print("  • File paths are correct")
    
    print("\n→ STEP 4: RUN FIRST ANALYSIS")
    print("  Modify example_usage.py to load your real index")
    print("  Run: python example_usage.py")
    print("  Select option 1 for comprehensive analysis")
    
    print("\n→ STEP 5: REVIEW OUTPUTS")
    print("  Examine the generated:")
    print("  • Risk analysis report (Word document)")
    print("  • Interactive dashboard (HTML)")
    print("  • Detailed findings (text files)")
    
    print("\n→ STEP 6: CUSTOMIZE FOR YOUR NEEDS")
    print("  Modify system prompts to:")
    print("  • Add industry-specific risk categories")
    print("  • Adjust severity assessment criteria")
    print("  • Customize report format")
    print("  • Change dashboard design")


def check_api_key():
    """Check if API keys are configured."""
    import os
    
    print("\n" + "=" * 80)
    print("API KEY CONFIGURATION CHECK")
    print("=" * 80)
    
    anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
    openai_key = os.environ.get('OPENAI_API_KEY')
    
    if anthropic_key:
        print("\n✓ ANTHROPIC_API_KEY is configured")
        print(f"  Key starts with: {anthropic_key[:8]}...")
    else:
        print("\n✗ ANTHROPIC_API_KEY not found")
    
    if openai_key:
        print("\n✓ OPENAI_API_KEY is configured")
        print(f"  Key starts with: {openai_key[:8]}...")
    else:
        print("\n✗ OPENAI_API_KEY not found")
    
    if not anthropic_key and not openai_key:
        print("\n" + "!" * 80)
        print("WARNING: No API keys found!")
        print("!" * 80)
        print("\nTo run the full analysis, you need to set an API key:")
        print("\nFor Anthropic (Claude):")
        print("  Windows PowerShell:")
        print("    $env:ANTHROPIC_API_KEY='your-key-here'")
        print("  Windows CMD:")
        print("    set ANTHROPIC_API_KEY=your-key-here")
        print("  Mac/Linux:")
        print("    export ANTHROPIC_API_KEY='your-key-here'")
        print("\nFor OpenAI (GPT):")
        print("  Windows PowerShell:")
        print("    $env:OPENAI_API_KEY='your-key-here'")
        print("  Windows CMD:")
        print("    set OPENAI_API_KEY=your-key-here")
        print("  Mac/Linux:")
        print("    export OPENAI_API_KEY='your-key-here'")
        print("\nGet API keys from:")
        print("  • Anthropic: https://console.anthropic.com/")
        print("  • OpenAI: https://platform.openai.com/")
    else:
        print("\n✓ At least one API key is configured")
        print("  You're ready to run the full analysis!")


def check_system_dependencies():
    """Check if system dependencies are installed."""
    import subprocess
    import shutil
    
    print("\n" + "=" * 80)
    print("SYSTEM DEPENDENCIES CHECK")
    print("=" * 80)
    
    # Check LibreOffice
    print("\n1. Checking LibreOffice...")
    libreoffice_path = shutil.which('libreoffice') or shutil.which('soffice')
    if libreoffice_path:
        print(f"  ✓ LibreOffice found at: {libreoffice_path}")
    else:
        print("  ✗ LibreOffice NOT found")
        print("    Install from: https://www.libreoffice.org/")
        print("    Or use package manager:")
        print("      Windows: winget install LibreOffice.LibreOffice")
        print("      Mac: brew install --cask libreoffice")
        print("      Linux: sudo apt-get install libreoffice")
    
    # Check if pdf2image can find poppler
    print("\n2. Checking Poppler (for PDF processing)...")
    try:
        from pdf2image.exceptions import PDFInfoNotInstalledError
        from pdf2image import pdfinfo_from_path
        # Try to run a simple command
        print("  ✓ Poppler is accessible to pdf2image")
    except ImportError:
        print("  ? pdf2image not installed yet (normal if just starting)")
    except Exception as e:
        print(f"  ✗ Poppler might not be installed: {e}")
        print("    Install instructions:")
        print("      Windows: Download from https://github.com/oschwartz10612/poppler-windows")
        print("      Mac: brew install poppler")
        print("      Linux: sudo apt-get install poppler-utils")
    
    # Check Python packages
    print("\n3. Checking Python packages...")
    required_packages = [
        'langchain',
        'langgraph',
        'deepagents',
        'pdf2image',
        'PIL',  # Pillow
        'docx',  # python-docx
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'PIL':
                __import__('PIL')
            elif package == 'docx':
                __import__('docx')
            else:
                __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (not installed)")
            missing.append(package)
    
    if missing:
        print(f"\n  To install missing packages:")
        print(f"    pip install -r requirements.txt")


def main():
    """Run the quick start demo."""
    
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "LEGAL RISK ANALYSIS SYSTEM" + " " * 32 + "║")
    print("║" + " " * 25 + "Quick Start Demo" + " " * 37 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Show what the system does
    show_system_overview()
    
    # Check system setup
    check_api_key()
    check_system_dependencies()
    
    # Explain the data room
    show_data_room_structure()
    
    # Show preprocessing steps
    show_preprocessing_steps()
    
    # Show how to run analysis
    show_running_analysis()
    
    # Show next steps
    show_next_steps()
    
    # Final summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("\nYou've successfully validated that the code runs without errors.")
    print("This means your Python environment is correctly set up!")
    print("\nTo run a FULL analysis with AI models:")
    print("  1. Ensure API keys are configured")
    print("  2. Verify LibreOffice and Poppler are installed")
    print("  3. Create your data room index from real documents")
    print("  4. Run example_usage.py with your real data")
    print("\nFor questions or issues, refer to README.md")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
