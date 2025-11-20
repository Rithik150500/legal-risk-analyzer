# Quick Reference: Human-in-the-Loop Operations

## The Four Key Operations Requiring Approval

### 1. write_todos - Planning & Task Management

**What it does:** Agent creates or updates its analysis plan with a list of tasks

**Why approval matters:** 
- Ensures comprehensive coverage of all relevant documents and risk areas
- Validates priorities align with business objectives
- Confirms efficient sequencing of analysis work
- Prevents wasted effort on low-priority items

**What to review:**
```
✓ All relevant documents included?
✓ Critical risk areas covered?
✓ Priorities appropriate?
✓ Sequence logical?
✓ Any missing tasks?
```

**Example:**
```json
{
  "tool": "write_todos",
  "todos": [
    {
      "task": "Analyze Master Service Agreement for contractual risks",
      "status": "pending",
      "priority": "high"
    },
    {
      "task": "Review NDA for confidentiality obligations",
      "status": "pending", 
      "priority": "high"
    },
    {
      "task": "Examine Statement of Work for operational risks",
      "status": "pending",
      "priority": "medium"
    }
  ]
}
```

**Common edits:**
- Adjust priorities (upgrade/downgrade urgency)
- Add forgotten tasks (e.g., "Review recent amendments")
- Reorder sequence (e.g., "Analyze amendment first before MSA")
- Add context (e.g., "Focus on risks from Provider perspective")

**Decision matrix:**
- **Approve:** Plan is comprehensive, priorities correct, sequence logical
- **Edit:** Missing tasks, wrong priorities, or need additional context
- **Reject:** Plan fundamentally flawed, needs complete rethinking

---

### 2. task - Subagent Delegation

**What it does:** Main agent delegates a specific analysis task to a specialized subagent

**Why approval matters:**
- Validates correct subagent selected for the work
- Ensures task scope is clear and achievable  
- Confirms sufficient context provided
- Prevents miscommunication of requirements

**What to review:**
```
✓ Right subagent for this task?
✓ Scope well-defined?
✓ Clear instructions?
✓ Sufficient context?
✓ Expected outputs specified?
```

**Example:**
```json
{
  "tool": "task",
  "name": "legal-analyzer",
  "task": "Conduct comprehensive analysis of Master Service Agreement (doc_001) 
  focusing on:
  
  1. Contractual Risks: payment terms, termination provisions, ambiguous clauses
  2. IP Risks: ownership, assignment, licensing terms
  3. Liability Risks: indemnification, caps, insurance requirements
  
  For each risk, provide severity assessment, specific clause references, 
  and mitigation recommendations. Save findings to /analysis/doc_001_risks.txt"
}
```

**Common edits:**
- Add context: "Note: We are the Provider in this contract"
- Refine scope: "Focus specifically on payment term modifications in the amendment"
- Add constraints: "Only analyze pages 5-10 which contain the problematic clauses"
- Change subagent: Switch to "general-purpose" for simpler tasks

**Decision matrix:**
- **Approve:** Correct subagent, clear scope, adequate context
- **Edit:** Need additional context, scope refinement, or clearer instructions
- **Reject:** Wrong subagent, inappropriate task, or fundamentally unclear delegation

---

### 3. get_document / get_document_pages - Document Access

**What it does:** Agent retrieves documents or specific pages from the data room

**Why approval matters:**
- Ensures access is authorized and necessary
- Validates no privilege or confidentiality issues
- Maintains audit trail for compliance
- Prevents unauthorized data exposure

**What to review:**
```
✓ Document relevant to current task?
✓ Access authorized?
✓ Privilege concerns?
✓ Confidentiality issues?
✓ Should be logged?
```

**Example:**
```json
{
  "tool": "get_document",
  "doc_id": "doc_001",
  "context": "Retrieving Master Service Agreement to analyze contractual risks"
}
```

**Common actions:**
- **Approve + Log:** Grant access and record in compliance system
- **Approve with note:** "This contains privileged communications, handle carefully"
- **Reject with redirect:** "Use doc_002 instead, which is the amended version"
- **Reject with feedback:** "That document is outside the scope of this engagement"

**Decision matrix:**
- **Approve:** Relevant, authorized, no privilege issues, logging enabled
- **Reject:** Unnecessary for task, privileged content, unauthorized scope

**Special note:** In production with proper document management integration, you might:
- Automatically log all accesses to compliance database
- Check user permissions against document classification
- Trigger alerts for sensitive document access
- Enforce time-based access windows

---

### 4. write_file / edit_file - Creating and Modifying Findings

**What it does:** Agent writes analysis findings, risk assessments, or modifications to files

**Why approval matters:**
- Validates accuracy of risk identification
- Confirms appropriateness of severity ratings
- Ensures legal reasoning is sound
- Verifies recommendations are actionable
- Maintains professional quality before reports

**What to review:**
```
✓ Risks accurately identified?
✓ Severity ratings justified?
✓ Document references correct?
✓ Legal reasoning sound?
✓ Recommendations practical?
✓ Writing clear and professional?
```

**Example:**
```json
{
  "tool": "write_file",
  "file_path": "/analysis/contractual_risks_doc_001.txt",
  "content": "CONTRACTUAL RISK ANALYSIS - Master Service Agreement

Risk #1: Automatic Renewal Without Cap
Severity: HIGH
Location: Page 9, Section 12.3
Description: Agreement contains automatic renewal clause extending the three-year 
term indefinitely unless either party provides 60 days notice before term end. 
No maximum number of renewal cycles specified.

Impact: Company could remain bound to unfavorable terms indefinitely if renewal 
notices are missed. Single missed 60-day window commits to another three years.

Affected Party: DataServices LLC (Provider) - our company

Mitigation: 
1. Negotiate maximum of 2-3 renewal cycles
2. Reduce renewal term to one year instead of three
3. Implement calendar reminder system with multiple alerts

Supporting Research: Industry standard is to limit automatic renewals or use 
shorter renewal periods after initial term (Source: ABA Model Contract Terms)

---

Risk #2: Unilateral Termination Rights (Post-Amendment)
Severity: HIGH
Location: Amendment doc_005, Page 3, Section 2
Description: Recent amendment added unilateral termination allowing Client 
(TechCorp) to terminate without cause with only 10 days notice. Provider 
(us) still requires 90 days notice and can only terminate for cause.

Impact: Creates significant business uncertainty. Client can terminate with 
minimal notice, preventing resource planning or long-term investment in the 
relationship. No equivalent protection for Provider.

Affected Party: DataServices LLC (Provider) - our company

Mitigation:
1. URGENT: Renegotiate to remove unilateral termination
2. Extend notice period to 90 days to match Provider's requirement
3. Add termination fee of 3-6 months fees to compensate disruption
4. At minimum, require written justification even for 'no cause' termination

Supporting Research: Unequal termination rights often negotiable when one party 
has made specific investments (Source: Contract Law Review Q4 2023)
..."
}
```

**Common edits:**

1. **Severity adjustments:**
   ```
   Original: Severity: HIGH
   Edited:   Severity: MEDIUM
   Reason: "Our renewal tracking system mitigates this risk significantly"
   ```

2. **Adding context:**
   ```
   Added: "CLIENT NOTE: This contract was signed before we implemented our 
   current contract review process. Future agreements should avoid this issue."
   ```

3. **Refining wording:**
   ```
   Original: "This is a terrible clause that will definitely cause problems"
   Edited:   "This clause presents significant risk and should be prioritized 
   for renegotiation"
   Reason: More professional tone appropriate for client-facing documents
   ```

4. **Adding legal nuance:**
   ```
   Added: "Under New York law (governing law of this contract), automatic 
   renewal clauses may be subject to special disclosure requirements. 
   Verify compliance with NY GBL § 527."
   ```

5. **Correcting references:**
   ```
   Original: Location: Page 9, Section 12.3
   Edited:   Location: Page 9, Section 12.3 (as amended by doc_005, Page 3)
   ```

**Decision matrix:**
- **Approve:** Risks accurate, severity justified, reasoning sound, professionally written
- **Edit:** Severity needs adjustment, missing context, wording improvements needed
- **Reject:** Significant errors, misinterpretation of clauses, needs complete revision

---

## Configuration Quick Start

### Copy-paste configurations for different scenarios:

**Initial Deployment (Maximum Oversight):**
```python
from hitl_implementation import ApprovalLevel

interrupt_on = ApprovalLevel.high_oversight()
# Approves: write_todos, task, get_document, get_document_pages, write_file, edit_file
```

**Routine Work (Balanced):**
```python
interrupt_on = ApprovalLevel.moderate_oversight()
# Approves: write_todos, task, write_file, edit_file
# Auto-allows: get_document, get_document_pages
```

**Mature Deployment (Minimal Oversight):**
```python
interrupt_on = ApprovalLevel.minimal_oversight()
# Approves: write_file, edit_file only
# Auto-allows: everything else
```

**Custom Configuration:**
```python
interrupt_on = ApprovalLevel.custom(
    planning=True,           # Approve write_todos
    delegation=True,         # Approve task
    document_access=False,   # Auto-allow document retrieval
    file_operations=True     # Approve write_file/edit_file
)
```

---

## Running with HITL

### Basic usage:
```python
from hitl_implementation import (
    create_agent_with_hitl,
    run_agent_with_hitl,
    ApprovalLevel,
    CLIReviewInterface
)

# Create agent with HITL
agent_config = create_agent_with_hitl(
    data_room_index=your_data_room,
    approval_level=ApprovalLevel.moderate_oversight(),
    review_interface=CLIReviewInterface(),
    reviewer_name="jane_doe",
    enable_audit=True
)

# Run analysis
result = run_agent_with_hitl(
    agent_config=agent_config,
    user_message="Analyze doc_001 for contractual risks",
    thread_id="analysis_001"
)
```

### Checking audit logs:
```python
stats = agent_config["audit_logger"].get_review_stats()
print(json.dumps(stats, indent=2))
# {
#   "total_reviews": 12,
#   "by_decision": {"approve": 8, "edit": 3, "reject": 1},
#   "by_tool": {"write_todos": 2, "task": 4, "write_file": 6},
#   "by_reviewer": {"jane_doe": 12}
# }
```

---

## Common Scenarios

### Scenario 1: Agent proposes comprehensive plan
```
Agent: write_todos([
  "Analyze all documents for contractual risks",
  "Analyze all documents for IP risks",
  "Create report and dashboard"
])

✓ Good plan structure
✗ Too broad - break down by document

Decision: EDIT
→ Split into document-specific tasks
→ Prioritize key documents first
→ Add specific risk focus areas per document
```

### Scenario 2: Agent delegates analysis
```
Agent: task(
  name="legal-analyzer",
  task="Analyze doc_001 for risks"
)

✓ Correct subagent
✗ Task too vague
✗ Missing context

Decision: EDIT
→ Specify which risk categories
→ Add context about our role (Provider vs Client)
→ Note any relevant amendments
```

### Scenario 3: Agent creates findings
```
Agent: write_file("/analysis/risks.txt", "Risk: AUTO-RENEWAL, Severity: HIGH...")

✓ Risk correctly identified
✓ Good analysis
✗ Severity too high given our mitigation systems

Decision: EDIT
→ Downgrade HIGH to MEDIUM
→ Add note about existing mitigation controls
→ Keep the rest as-is
```

---

## Tips for Efficient Review

1. **Trust but verify:** Agent is usually right, but double-check critical items
2. **Focus on impact:** Prioritize review of high-severity findings
3. **Provide feedback:** When editing, explain why to improve future performance
4. **Batch reviews:** Review multiple actions together when possible
5. **Time-box reviews:** Set limits (e.g., 5 minutes per review) to stay efficient
6. **Use templates:** Create standard edits for common issues
7. **Log patterns:** Track what gets edited to identify training needs
8. **Escalate when unsure:** Get second opinion on complex legal questions

---

## Troubleshooting

**Problem:** Too many approvals slowing down work
**Solution:** Reduce approval level after agent proves reliable

**Problem:** Agent keeps getting rejected
**Solution:** Improve system prompts or add more context upfront

**Problem:** Reviews taking too long
**Solution:** Set up Slack/email notifications for async review

**Problem:** Inconsistent review decisions
**Solution:** Document clear review criteria and train all reviewers

**Problem:** Can't decide whether to approve
**Solution:** Default to EDIT with clarifying questions rather than REJECT

---

## Remember

The goal of HITL is **human-AI collaboration**, not human replacement or AI replacement. 

The agent handles:
- Document processing at scale
- Pattern identification across many documents  
- Consistent application of analysis framework
- Initial drafting and synthesis

Humans provide:
- Strategic oversight
- Contextual judgment
- Legal expertise validation
- Risk calibration
- Final quality assurance

Together, they produce better results than either could alone.
