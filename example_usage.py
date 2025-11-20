"""
End-to-End Example: Legal Risk Analysis System

This script demonstrates the complete workflow for analyzing legal documents:
1. Index a data room of documents (preprocessing)
2. Create the Legal Risk Analysis Agent
3. Run a comprehensive analysis
4. Access the generated reports and dashboard

This example uses mock data for demonstration purposes, but in production
you would point to real documents and use actual AI models for summarization.
"""

import json
from pathlib import Path
from legal_risk_analysis_agent import create_legal_risk_analysis_agent
from data_room_indexer import DataRoomIndexer


def create_mock_data_room():
    """
    Create a mock data room index for demonstration purposes.
    
    In production, you would generate this using the DataRoomIndexer class
    by pointing it at your folder of legal documents. This mock version
    simulates what that output would look like so you can test the agent
    functionality without needing actual documents.
    """
    return {
        "metadata": {
            "total_documents": 5,
            "created_at": "2025-01-15T10:00:00",
            "model_used": "gpt-4o-mini"
        },
        "documents": [
            {
                "doc_id": "doc_001",
                "original_file": "/dataroom/master_service_agreement.docx",
                "pdf_file": "/dataroom/pdfs/master_service_agreement.pdf",
                "summdesc": "Master Service Agreement between TechCorp Inc. and DataServices LLC, establishing a three-year software development partnership. The agreement covers service scope, payment terms of $500,000 annually, intellectual property ownership provisions, and includes standard indemnification and limitation of liability clauses. Notable provisions include automatic renewal clauses and a restrictive non-compete agreement.",
                "pages": [
                    {
                        "page_num": 1,
                        "summdesc": "Title page identifying parties: TechCorp Inc. (Client) and DataServices LLC (Provider), with execution date of January 1, 2024, and a three-year term ending December 31, 2026.",
                        "page_image": "/dataroom/pages/doc_001/page_001.png"
                    },
                    {
                        "page_num": 2,
                        "summdesc": "Definitions section establishing key terms including 'Services', 'Deliverables', 'Confidential Information', and 'Intellectual Property'. Also includes interpretation clause stating that singular includes plural.",
                        "page_image": "/dataroom/pages/doc_001/page_002.png"
                    },
                    {
                        "page_num": 3,
                        "summdesc": "Scope of Services section describing custom software development services, monthly deliverable schedules, and requirement that all work must meet Client specifications. Includes provision that scope changes require written amendment.",
                        "page_image": "/dataroom/pages/doc_001/page_003.png"
                    },
                    {
                        "page_num": 4,
                        "summdesc": "Payment terms specifying $500,000 annual fee payable in monthly installments of $41,666.67, due within 30 days of invoice. Late payments subject to 1.5% monthly interest. Contains provision allowing Provider to suspend services if payment is more than 60 days overdue.",
                        "page_image": "/dataroom/pages/doc_001/page_004.png"
                    },
                    {
                        "page_num": 5,
                        "summdesc": "Intellectual property clause stating that all work product and deliverables become the exclusive property of Client upon full payment. However, Provider retains rights to pre-existing materials and general methodologies.",
                        "page_image": "/dataroom/pages/doc_001/page_005.png"
                    },
                    {
                        "page_num": 6,
                        "summdesc": "Confidentiality obligations requiring both parties to protect confidential information for a period of five years. Standard exclusions apply for publicly available information and independently developed materials.",
                        "page_image": "/dataroom/pages/doc_001/page_006.png"
                    },
                    {
                        "page_num": 7,
                        "summdesc": "Indemnification provisions where Provider agrees to indemnify Client against third-party IP claims, but only up to the amount of fees paid in the twelve months preceding the claim. Client must provide prompt notice and control of defense.",
                        "page_image": "/dataroom/pages/doc_001/page_007.png"
                    },
                    {
                        "page_num": 8,
                        "summdesc": "Limitation of liability clause capping each party's liability at the total fees paid in the preceding twelve months, excluding liability for breach of confidentiality or IP indemnification. Consequential damages are excluded.",
                        "page_image": "/dataroom/pages/doc_001/page_008.png"
                    },
                    {
                        "page_num": 9,
                        "summdesc": "Term and termination provisions allowing either party to terminate with 90 days written notice. Client may terminate for convenience with 30 days notice but must pay for work completed. Contains automatic renewal clause unless either party provides 60 days notice before term end.",
                        "page_image": "/dataroom/pages/doc_001/page_009.png"
                    },
                    {
                        "page_num": 10,
                        "summdesc": "General provisions including non-compete clause preventing Provider from working with Client's competitors for one year after termination, governing law clause selecting New York law, and arbitration requirement for disputes. Contains severability and entire agreement clauses.",
                        "page_image": "/dataroom/pages/doc_001/page_010.png"
                    }
                ]
            },
            {
                "doc_id": "doc_002",
                "original_file": "/dataroom/nda_mutual.pdf",
                "pdf_file": "/dataroom/pdfs/nda_mutual.pdf",
                "summdesc": "Mutual Non-Disclosure Agreement between TechCorp Inc. and DataServices LLC executed concurrently with the Master Service Agreement. Five-year term for confidentiality obligations. Contains standard NDA provisions but lacks carve-outs for regulatory disclosures and has a problematic restriction on hiring each other's employees.",
                "pages": [
                    {
                        "page_num": 1,
                        "summdesc": "Title and parties section for Mutual NDA between TechCorp Inc. and DataServices LLC, dated January 1, 2024. States that confidentiality obligations survive for five years after termination.",
                        "page_image": "/dataroom/pages/doc_002/page_001.png"
                    },
                    {
                        "page_num": 2,
                        "summdesc": "Definition of confidential information as any non-public information disclosed by either party, whether oral or written. Includes information about business operations, customers, technology, and financial data.",
                        "page_image": "/dataroom/pages/doc_002/page_002.png"
                    },
                    {
                        "page_num": 3,
                        "summdesc": "Obligations section requiring both parties to use reasonable care to protect confidential information and restrict disclosure to employees with need to know. Receiving party may not use confidential information except for evaluating or pursuing business relationship.",
                        "page_image": "/dataroom/pages/doc_002/page_003.png"
                    },
                    {
                        "page_num": 4,
                        "summdesc": "Exclusions from confidential information: publicly available information, information known prior to disclosure, independently developed information, and information rightfully received from third parties. Notably missing: carve-out for legally required disclosures such as regulatory inquiries or court orders.",
                        "page_image": "/dataroom/pages/doc_002/page_004.png"
                    },
                    {
                        "page_num": 5,
                        "summdesc": "Non-solicitation clause preventing either party from hiring or soliciting the other's employees for two years after the agreement ends. Applies to any employee either party became aware of during the business relationship, which is unusually broad.",
                        "page_image": "/dataroom/pages/doc_002/page_005.png"
                    },
                    {
                        "page_num": 6,
                        "summdesc": "Remedies section emphasizing that breach may cause irreparable harm and injunctive relief may be sought without posting bond. Contains New York choice of law provision and jurisdiction clause requiring New York courts.",
                        "page_image": "/dataroom/pages/doc_002/page_006.png"
                    }
                ]
            },
            {
                "doc_id": "doc_003",
                "original_file": "/dataroom/sow_initial.xlsx",
                "pdf_file": "/dataroom/pdfs/sow_initial.pdf",
                "summdesc": "Statement of Work for the first project under the Master Service Agreement, describing development of a customer data management system. Budget of $150,000 over six months with specific deliverables and milestones. Contains aggressive timelines and does not adequately address handling of scope changes or delays.",
                "pages": [
                    {
                        "page_num": 1,
                        "summdesc": "Cover sheet identifying this as Statement of Work #1 under the Master Service Agreement dated January 1, 2024. Project title: Customer Data Management System. Overall budget: $150,000. Timeline: Six months from February 1 to July 31, 2024.",
                        "page_image": "/dataroom/pages/doc_003/page_001.png"
                    },
                    {
                        "page_num": 2,
                        "summdesc": "Project objectives describing the need for a centralized customer database that integrates with existing CRM and supports real-time reporting. System must handle 100,000 customer records initially with capacity to scale to 1 million within two years.",
                        "page_image": "/dataroom/pages/doc_003/page_002.png"
                    },
                    {
                        "page_num": 3,
                        "summdesc": "Technical requirements spreadsheet listing database schema design, API development for CRUD operations, user authentication and authorization system, reporting dashboard, and data migration from three legacy systems. Each requirement has an estimated effort in hours.",
                        "page_image": "/dataroom/pages/doc_003/page_003.png"
                    },
                    {
                        "page_num": 4,
                        "summdesc": "Project milestones and payment schedule: Month 1 - Requirements gathering and design ($25,000), Month 2-3 - Core development ($50,000), Month 4-5 - Integration and testing ($50,000), Month 6 - Deployment and training ($25,000). Each milestone payment due within 15 days of completion.",
                        "page_image": "/dataroom/pages/doc_003/page_004.png"
                    },
                    {
                        "page_num": 5,
                        "summdesc": "Deliverables list including technical design documents, source code with documentation, testing reports, user manuals, and training materials. Acceptance criteria state that Client has ten business days to review deliverables, with acceptance deemed if no written objections provided.",
                        "page_image": "/dataroom/pages/doc_003/page_005.png"
                    },
                    {
                        "page_num": 6,
                        "summdesc": "Project governance section describing weekly status meetings, monthly steering committee reviews, and escalation procedures for issues. Provider has project manager assigned full-time. Client must provide timely feedback and access to necessary resources and systems.",
                        "page_image": "/dataroom/pages/doc_003/page_006.png"
                    },
                    {
                        "page_num": 7,
                        "summdesc": "Assumptions and dependencies listing Provider's assumptions including availability of Client resources, timely decisions from Client stakeholders, stable requirements, and access to legacy systems. Notable absence: no clear process for handling scope changes or timeline extensions if assumptions prove incorrect.",
                        "page_image": "/dataroom/pages/doc_003/page_007.png"
                    }
                ]
            },
            {
                "doc_id": "doc_004",
                "original_file": "/dataroom/insurance_cert.pdf",
                "pdf_file": "/dataroom/pdfs/insurance_cert.pdf",
                "summdesc": "Certificate of Insurance from DataServices LLC showing general liability coverage of $2 million per occurrence, professional liability coverage of $1 million per claim, and cyber liability coverage of $1 million per incident. Policy expires in six months and requires renewal. Coverage amounts may be insufficient for the contract value and potential exposure.",
                "pages": [
                    {
                        "page_num": 1,
                        "summdesc": "Certificate of Liability Insurance for DataServices LLC issued by SecureInsure Company. Certificate holder listed as TechCorp Inc. General liability policy provides $2 million per occurrence and $4 million aggregate coverage for bodily injury and property damage.",
                        "page_image": "/dataroom/pages/doc_004/page_001.png"
                    },
                    {
                        "page_num": 2,
                        "summdesc": "Professional liability (errors and omissions) coverage listed at $1 million per claim with $2 million annual aggregate. Coverage is claims-made basis with retroactive date of January 1, 2022. Notable: this coverage may be insufficient given the $500,000 annual contract value and potential damages from data system failures.",
                        "page_image": "/dataroom/pages/doc_004/page_002.png"
                    },
                    {
                        "page_num": 3,
                        "summdesc": "Cyber liability and data breach coverage showing $1 million per incident limit with $2 million aggregate. Covers costs of breach notification, credit monitoring, regulatory fines, and liability for unauthorized access to client data. Policy expires July 31, 2024, which is only six months away and in the middle of the project timeline.",
                        "page_image": "/dataroom/pages/doc_004/page_003.png"
                    },
                    {
                        "page_num": 4,
                        "summdesc": "Workers compensation coverage showing statutory limits as required by state law. Covers employee injuries during work activities. TechCorp Inc. is listed as certificate holder and should receive 30 days notice of policy cancellation or non-renewal.",
                        "page_image": "/dataroom/pages/doc_004/page_004.png"
                    }
                ]
            },
            {
                "doc_id": "doc_005",
                "original_file": "/dataroom/amendment_01.docx",
                "pdf_file": "/dataroom/pdfs/amendment_01.pdf",
                "summdesc": "First Amendment to Master Service Agreement dated October 15, 2024, extending the payment terms from 30 to 45 days but adding a 2% early payment discount. Also adds new termination rights allowing Client to terminate without cause with only 10 days notice, which significantly weakens Provider's position and creates uncertainty for long-term planning.",
                "pages": [
                    {
                        "page_num": 1,
                        "summdesc": "Amendment cover page identifying this as First Amendment to Master Service Agreement between TechCorp Inc. and DataServices LLC. Effective date October 15, 2024. States that all other terms of original agreement remain in full force except as specifically modified herein.",
                        "page_image": "/dataroom/pages/doc_005/page_001.png"
                    },
                    {
                        "page_num": 2,
                        "summdesc": "Section 1: Payment Terms Modification. Extends payment due date from 30 to 45 days after invoice date. Adds new early payment discount of 2% if paid within 15 days. Removes the late payment interest provision that was in original agreement, which eliminates Provider's remedy for late payments.",
                        "page_image": "/dataroom/pages/doc_005/page_002.png"
                    },
                    {
                        "page_num": 3,
                        "summdesc": "Section 2: Termination Rights Modification. Adds new subsection allowing Client to terminate agreement at any time with just 10 days written notice, even without cause. Client must pay for work completed and accepted as of termination date but has no obligation to pay for work in progress. This creates significant business uncertainty for Provider.",
                        "page_image": "/dataroom/pages/doc_005/page_003.png"
                    },
                    {
                        "page_num": 4,
                        "summdesc": "Section 3: Miscellaneous provisions including confirmation that amendment constitutes entire understanding regarding modified provisions, that amendment may be executed in counterparts, and signatures of authorized representatives from both parties. Amendment signed by same executives who signed original agreement.",
                        "page_image": "/dataroom/pages/doc_005/page_004.png"
                    }
                ]
            }
        ]
    }


def run_comprehensive_analysis():
    """
    Demonstrates the complete workflow for legal risk analysis.
    
    This function shows how to load or create a data room index, instantiate
    the agent with all its subagents, and run a comprehensive analysis that
    generates both a detailed report and an interactive dashboard.
    """
    
    print("=" * 80)
    print("Legal Risk Analysis System - End-to-End Example")
    print("=" * 80)
    
    # Step 1: Create or load the data room index
    # In production, you would use the DataRoomIndexer to process real documents
    print("\n[Step 1] Creating data room index...")
    data_room_index = create_mock_data_room()
    print(f"  ✓ Loaded {data_room_index['metadata']['total_documents']} documents")
    
    # Step 2: Create the Legal Risk Analysis Agent
    print("\n[Step 2] Creating Legal Risk Analysis Agent...")
    agent = create_legal_risk_analysis_agent(data_room_index)
    print("  ✓ Main agent created with 3 specialized subagents:")
    print("    - legal-analyzer: Document analysis and risk assessment")
    print("    - report-creator: Professional report generation")
    print("    - dashboard-creator: Interactive dashboard creation")
    
    # Step 3: Run the analysis
    print("\n[Step 3] Running comprehensive legal risk analysis...")
    print("  This will:")
    print("  - Review all documents in the data room")
    print("  - Identify risks across 7 major categories")
    print("  - Conduct web research for legal context")
    print("  - Generate detailed findings")
    print("  - Create a professional Word document report")
    print("  - Build an interactive web dashboard")
    print("\n  Starting analysis...\n")
    
    # Configure the agent run
    config = {
        "configurable": {
            "thread_id": "legal_analysis_demo_001"
        }
    }
    
    # The analysis request that gets sent to the main agent
    analysis_request = """Please conduct a comprehensive legal risk analysis of all documents in the data room.

I need you to identify and assess risks across all major categories including:
- Contractual risks (ambiguous terms, unfavorable clauses, breach conditions)
- Compliance risks (regulatory requirements, licensing issues)
- Intellectual property risks (ownership, infringement, licensing)
- Liability risks (indemnification, warranties, limitations)
- Financial risks (payment terms, penalties, guarantees)
- Operational risks (obligations, deadlines, dependencies)
- Reputational risks (confidentiality, conflicts of interest)

For each risk you identify, I need:
1. Clear description of the risk
2. Severity rating (High, Medium, or Low) with justification
3. Specific document and clause references
4. Assessment of potential impact
5. Recommended mitigation strategies

After completing the analysis, please:
1. Create a comprehensive Word document report suitable for executive review
2. Build an interactive dashboard for stakeholders to explore the findings

Focus on actionable insights that will help in contract negotiations and risk mitigation planning."""

    try:
        # Invoke the agent with the analysis request
        result = agent.invoke({
            "messages": [{
                "role": "user",
                "content": analysis_request
            }]
        }, config=config)
        
        # Extract and display the results
        print("\n" + "=" * 80)
        print("Analysis Complete!")
        print("=" * 80)
        
        # Get the final message from the agent
        final_message = result["messages"][-1]["content"]
        print("\nAgent Response:")
        print("-" * 80)
        print(final_message)
        print("-" * 80)
        
        # Step 4: Explain how to access the outputs
        print("\n[Step 4] Accessing Results:")
        print("\nYour analysis outputs are available at:")
        print("  📄 Report: /outputs/legal_risk_analysis_report.docx")
        print("     Professional Word document with executive summary, detailed")
        print("     risk analysis, and recommendations")
        print("\n  📊 Dashboard: /outputs/legal_risk_dashboard.html")
        print("     Interactive web interface for exploring risks, filtering by")
        print("     severity and category, and viewing affected documents")
        print("\n  📁 Detailed Findings: /analysis/")
        print("     Raw analysis files organized by risk category, containing")
        print("     complete findings with supporting research")
        
        print("\n" + "=" * 80)
        print("Next Steps:")
        print("=" * 80)
        print("\n1. Review the executive summary in the Word document for high-level")
        print("   understanding of critical risks")
        print("\n2. Open the dashboard in your browser to interactively explore")
        print("   risks by category and severity")
        print("\n3. For any high-severity risks, review the detailed findings in")
        print("   /analysis/ to understand the full context and research")
        print("\n4. Share the report with legal counsel and stakeholders for")
        print("   review and decision-making")
        print("\n5. Use the recommendations to guide contract negotiations or")
        print("   risk mitigation strategies")
        
        return result
        
    except Exception as e:
        print(f"\n✗ Error during analysis: {e}")
        print("\nTroubleshooting tips:")
        print("1. Verify your API keys are correctly set in environment variables")
        print("2. Check that all required dependencies are installed")
        print("3. Ensure the data room index structure is valid")
        print("4. Review the error message above for specific issues")
        raise


def run_targeted_analysis():
    """
    Example of running a more targeted analysis focused on specific risk areas.
    
    Sometimes you do not need a comprehensive analysis of everything. This example
    shows how to request analysis of specific documents or specific risk categories,
    which can be more efficient when you have particular concerns.
    """
    
    print("\n" + "=" * 80)
    print("Targeted Analysis Example")
    print("=" * 80)
    
    data_room_index = create_mock_data_room()
    agent = create_legal_risk_analysis_agent(data_room_index)
    
    config = {"configurable": {"thread_id": "targeted_analysis_001"}}
    
    # This request focuses on specific areas of concern
    targeted_request = """I need you to focus on analyzing the intellectual property and liability provisions in our Master Service Agreement (doc_001) and the recent Amendment (doc_005).

Specifically, I am concerned about:
1. IP ownership and rights assignment - are we getting full ownership of work product?
2. Indemnification scope and caps - are we adequately protected?
3. Liability limitations - are the caps reasonable given the contract value?
4. The impact of the amendment on our ability to enforce terms

Please provide a focused analysis of these areas with specific recommendations for negotiation points."""

    result = agent.invoke({
        "messages": [{"role": "user", "content": targeted_request}]
    }, config=config)
    
    print("\nTargeted analysis complete. The agent has focused on the specific")
    print("concerns you raised rather than conducting a comprehensive review of")
    print("all documents and all risk categories.")
    
    return result


def demonstrate_interactive_followup():
    """
    Example of having a conversation with the agent to dig deeper into findings.
    
    The agent maintains context within a thread, so you can ask follow-up
    questions, request clarification, or dive deeper into specific risks
    without starting over.
    """
    
    print("\n" + "=" * 80)
    print("Interactive Follow-up Example")
    print("=" * 80)
    
    data_room_index = create_mock_data_room()
    agent = create_legal_risk_analysis_agent(data_room_index)
    
    # Use the same thread_id to maintain conversation context
    config = {"configurable": {"thread_id": "interactive_session_001"}}
    
    # Initial analysis
    print("\n[Initial Request]")
    result1 = agent.invoke({
        "messages": [{
            "role": "user",
            "content": "Please analyze doc_001 and identify the top 3 highest risks."
        }]
    }, config=config)
    
    print("Agent identified top risks in Master Service Agreement.")
    
    # Follow-up question in the same thread
    print("\n[Follow-up Question 1]")
    result2 = agent.invoke({
        "messages": [{
            "role": "user",
            "content": "For the highest risk you identified, what specific language in the contract creates that risk? Please show me the exact clause."
        }]
    }, config=config)
    
    print("Agent provided specific clause references and language.")
    
    # Another follow-up
    print("\n[Follow-up Question 2]")
    result3 = agent.invoke({
        "messages": [{
            "role": "user",
            "content": "What changes would you recommend to that clause to mitigate the risk? Can you draft alternative language?"
        }]
    }, config=config)
    
    print("Agent provided recommended revisions to the problematic clause.")
    
    print("\nThis demonstrates how you can have an ongoing conversation with")
    print("the agent, drilling down into specific concerns and getting detailed")
    print("guidance on mitigation strategies.")
    
    return result3


if __name__ == "__main__":
    print("\nLegal Risk Analysis System - Example Usage")
    print("\nThis script demonstrates three different usage patterns:\n")
    
    print("1. Comprehensive Analysis")
    print("   Run a complete analysis of all documents across all risk categories")
    print("   Result: Full report and dashboard\n")
    
    print("2. Targeted Analysis")
    print("   Focus on specific documents or risk areas of concern")
    print("   Result: Focused findings on requested topics\n")
    
    print("3. Interactive Follow-up")
    print("   Have a conversation with the agent to explore findings in depth")
    print("   Result: Detailed answers to specific questions\n")
    
    choice = input("Which example would you like to run? (1, 2, or 3): ")
    
    if choice == "1":
        run_comprehensive_analysis()
    elif choice == "2":
        run_targeted_analysis()
    elif choice == "3":
        demonstrate_interactive_followup()
    else:
        print("\nRunning comprehensive analysis (default)...")
        run_comprehensive_analysis()
    
    print("\n" + "=" * 80)
    print("Example Complete")
    print("=" * 80)
    print("\nFor production use:")
    print("- Replace mock data with actual DataRoomIndexer output")
    print("- Configure production-grade store and checkpointer")
    print("- Set up proper API keys for your chosen AI models")
    print("- Implement error handling and logging")
    print("- Consider adding human-in-the-loop approvals for sensitive operations")
