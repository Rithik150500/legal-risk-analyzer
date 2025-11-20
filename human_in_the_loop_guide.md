# Human-in-the-Loop Approval for Legal Risk Analysis

## Overview

Human-in-the-loop (HITL) approval provides critical oversight for sensitive legal analysis operations. This guide explains how to implement approval workflows for key operations in the Legal Risk Analysis system, ensuring human experts can review and validate agent actions before they are executed.

## Why Human-in-the-Loop Matters for Legal Analysis

Legal risk analysis involves high-stakes decision-making where errors or misinterpretations can have significant consequences. While AI agents are powerful tools for processing and analyzing large volumes of legal documents, they should not operate completely autonomously in production legal workflows. Human oversight ensures that:

- **Critical findings are validated** before being included in official reports
- **Risk severity assessments** are reviewed by legal professionals
- **Document interpretations** are confirmed to be accurate
- **Final deliverables** receive approval before distribution to stakeholders
- **Delegation decisions** are appropriate and well-reasoned

## Key Operations Requiring Approval

In the Legal Risk Analysis system, there are four primary categories of operations where human approval adds significant value:

### 1. Planning and Task Management (write_todos)

The agent uses the `write_todos` tool to create and update its analysis plan. This is a critical operation because the plan determines:
- Which documents receive attention
- What risk areas are prioritized
- How analysis resources are allocated
- The sequence and approach for the investigation

**Why approval matters:** A poorly structured plan can lead to incomplete analysis, wasted effort on low-priority areas, or missed critical risks. Human review ensures the plan is comprehensive and aligned with business priorities.

### 2. Subagent Task Delegation (task tool)

The main agent delegates work to specialized subagents using the `task` tool. Each delegation involves:
- Selecting the appropriate subagent
- Defining the scope of work
- Providing context and instructions
- Determining what deliverables are expected

**Why approval matters:** Inappropriate delegation can result in tasks being handled by the wrong specialist, incomplete context being provided, or critical nuances being missed. Human review ensures delegations are appropriate and well-scoped.

### 3. Document Access (get_document, get_document_pages)

The agent retrieves documents from the data room using specialized tools. This involves:
- Selecting which documents to review
- Determining which pages need detailed examination
- Accessing potentially sensitive or confidential information

**Why approval matters:** In regulated environments or when handling privileged documents, access controls and audit trails are critical. Human approval ensures document access is authorized and properly logged.

### 4. File Creation and Findings (write_file, edit_file)

The agent creates and modifies files containing:
- Analysis findings and risk assessments
- Severity ratings and impact assessments
- Recommendations and mitigation strategies
- Draft reports and executive summaries

**Why approval matters:** These files form the basis of official reports and business decisions. Human review ensures findings are accurate, appropriately worded, and ready for stakeholder consumption.

## Implementation Architecture

The human-in-the-loop system uses LangGraph's interrupt mechanism to pause agent execution at configured points. When an interrupt occurs:

1. Agent executes normally until it attempts to use a tool configured for approval
2. Execution pauses and returns control to the calling code
3. Human reviewer receives the pending action details
4. Reviewer can approve, edit, or reject the action
5. Execution resumes with the human's decision

This architecture maintains full conversation context and agent state, allowing seamless resumption after human input.

## Configuration Levels

The system supports three levels of approval stringency, allowing you to balance oversight needs with operational efficiency:

### Level 1: High Oversight (All Operations)

Appropriate for: Initial deployment, high-stakes analyses, regulated environments, learning phase

```python
interrupt_on = {
    "write_todos": True,               # Approve all planning updates
    "task": True,                      # Approve all subagent delegations
    "get_document": True,              # Approve all document access
    "get_document_pages": True,        # Approve page-level access
    "write_file": True,                # Approve all file creation
    "edit_file": True,                 # Approve all file modifications
}
```

**Use when:** You need maximum control and visibility into every agent action, such as during initial deployment or when analyzing highly sensitive matters.

### Level 2: Moderate Oversight (Critical Operations Only)

Appropriate for: Routine analyses, trusted agents, efficiency-focused workflows

```python
interrupt_on = {
    "write_todos": True,               # Still review planning
    "task": True,                      # Still review delegations
    "get_document": False,             # Allow automatic document access
    "get_document_pages": False,       # Allow automatic page access
    "write_file": True,                # Review final outputs
    "edit_file": {                     # Selective editing approval
        "allowed_decisions": ["approve", "reject"]  # No editing by human
    },
}
```

**Use when:** The agent has proven reliable at document review, but you want oversight on planning and final outputs.

### Level 3: Minimal Oversight (Outputs Only)

Appropriate for: Mature deployments, preliminary analyses, time-sensitive situations

```python
interrupt_on = {
    "write_todos": False,              # Trust agent planning
    "task": False,                     # Trust delegation decisions
    "get_document": False,             # Allow document access
    "get_document_pages": False,       # Allow page access
    "write_file": True,                # Review final findings
    "edit_file": True,                 # Review modifications
}
```

**Use when:** You primarily want to review and validate final outputs before they are distributed, while letting the agent work autonomously during analysis.

## Detailed Operation Examples

### Example 1: Reviewing a Planning Update (write_todos)

When the agent attempts to update its todo list, execution pauses:

```python
# Agent attempts to create analysis plan
# Execution pauses with interrupt

interrupts = result["__interrupt__"][0].value
action_request = interrupts["action_requests"][0]

# Display for human review:
{
    "tool": "write_todos",
    "arguments": {
        "todos": [
            {
                "task": "Analyze Master Service Agreement (doc_001) for contractual risks",
                "status": "pending",
                "priority": "high"
            },
            {
                "task": "Review NDA (doc_002) for confidentiality obligations",
                "status": "pending",
                "priority": "high"
            },
            {
                "task": "Examine Statement of Work (doc_003) for operational risks",
                "status": "pending",
                "priority": "medium"
            },
            {
                "task": "Verify insurance coverage adequacy (doc_004)",
                "status": "pending",
                "priority": "medium"
            },
            {
                "task": "Assess impact of Amendment (doc_005) on overall risk profile",
                "status": "pending",
                "priority": "high"
            }
        ]
    }
}
```

**Human reviewer evaluates:**
- Is the plan comprehensive? Are any documents or risk areas missing?
- Are priorities appropriate given the business context?
- Is the sequence logical and efficient?
- Should any tasks be added, removed, or reprioritized?

**Possible decisions:**

**Approve:** The plan looks good as-is
```python
decisions = [{"type": "approve"}]
```

**Edit:** Adjust priorities or add tasks
```python
decisions = [{
    "type": "edit",
    "edited_action": {
        "name": "write_todos",
        "args": {
            "todos": [
                {
                    "task": "Analyze Master Service Agreement (doc_001) for contractual risks",
                    "status": "pending",
                    "priority": "high"
                },
                {
                    "task": "URGENT: Review Amendment (doc_005) first - may affect interpretation of other docs",
                    "status": "pending",
                    "priority": "critical"  # Human upgraded priority
                },
                # ... rest of tasks with human adjustments
            ]
        }
    }
}]
```

**Reject:** Plan needs significant revision
```python
decisions = [{"type": "reject"}]
# Agent will need to create a new plan
```

### Example 2: Reviewing Subagent Delegation (task)

When the agent attempts to delegate work to a subagent:

```python
interrupts = result["__interrupt__"][0].value
action_request = interrupts["action_requests"][0]

# Display for human review:
{
    "tool": "task",
    "arguments": {
        "name": "legal-analyzer",
        "task": """Conduct a comprehensive analysis of the Master Service Agreement (doc_001) 
        focusing on the following risk areas:
        
        1. Contractual Risks:
           - Review all payment terms and conditions
           - Identify any ambiguous or undefined terms
           - Assess termination provisions and notice periods
           
        2. Intellectual Property Risks:
           - Analyze IP ownership and assignment clauses
           - Review work product rights
           - Identify any problematic licensing terms
           
        3. Liability Risks:
           - Examine indemnification scope and limits
           - Review liability caps and exclusions
           - Assess insurance requirements
        
        For each risk identified, provide specific clause references, severity assessment, 
        and mitigation recommendations. Save findings to /analysis/doc_001_contractual_ip_liability.txt"""
    }
}
```

**Human reviewer evaluates:**
- Is the legal-analyzer the right subagent for this task?
- Is the scope appropriate and well-defined?
- Are the instructions clear and comprehensive?
- Is the expected output format suitable?
- Should any additional context be provided?

**Possible decisions:**

**Approve:** Delegation is appropriate
```python
decisions = [{"type": "approve"}]
```

**Edit:** Refine scope or add guidance
```python
decisions = [{
    "type": "edit",
    "edited_action": {
        "name": "task",
        "args": {
            "name": "legal-analyzer",
            "task": """Conduct a comprehensive analysis of the Master Service Agreement (doc_001)...
            
            ADDITIONAL CONTEXT: This contract was recently amended (see doc_005). 
            Be sure to consider how the amendment affects the original terms, particularly 
            the payment terms and termination provisions which were modified.
            
            Also note: Our company is the Provider (DataServices LLC), not the Client, 
            so evaluate risks from that perspective."""
        }
    }
}]
```

**Reject:** Wrong subagent or inappropriate scope
```python
decisions = [{"type": "reject"}]
```

### Example 3: Reviewing Document Access (get_document)

When the agent attempts to access a document:

```python
interrupts = result["__interrupt__"][0].value
action_request = interrupts["action_requests"][0]

# Display for human review:
{
    "tool": "get_document",
    "arguments": {
        "doc_id": "doc_001"
    },
    "context": "Agent is retrieving Master Service Agreement to analyze contractual risks"
}
```

**Human reviewer evaluates:**
- Is this document relevant to the current analysis task?
- Is the agent authorized to access this document?
- Should access be logged for compliance purposes?
- Are there any privilege or confidentiality concerns?

**Possible decisions:**

**Approve:** Access is appropriate
```python
decisions = [{"type": "approve"}]
# Optional: Log access in compliance system
log_document_access(doc_id="doc_001", accessed_by="legal-risk-agent", purpose="risk analysis")
```

**Reject:** Access should not be granted
```python
decisions = [{"type": "reject"}]
# Provide feedback to agent
provide_agent_feedback("Document doc_001 contains privileged communications. Please analyze other documents first.")
```

### Example 4: Reviewing Findings Creation (write_file)

When the agent attempts to write analysis findings to a file:

```python
interrupts = result["__interrupt__"][0].value
action_request = interrupts["action_requests"][0]

# Display for human review:
{
    "tool": "write_file",
    "arguments": {
        "file_path": "/analysis/contractual_risks_doc_001.txt",
        "content": """CONTRACTUAL RISK ANALYSIS - Master Service Agreement (doc_001)
        
Risk #1: Automatic Renewal Without Notice Cap
Severity: HIGH
Location: Page 9, Termination Section
Description: The agreement contains an automatic renewal clause that continues the 
three-year term indefinitely unless either party provides 60 days notice before the 
term end. However, there is no maximum number of renewal cycles specified.
Impact: Company could remain bound to unfavorable terms indefinitely if renewal 
notices are missed. Given the three-year term, missing a single 60-day window 
commits to another three years.
Affected Parties: DataServices LLC (Provider) - our company
Mitigation: Negotiate to add maximum of 2-3 renewal cycles, or reduce renewal 
term to one year instead of three years.
Supporting Research: Standard practice in service agreements is to limit automatic 
renewals or switch to shorter renewal periods after initial term.

Risk #2: One-Sided Termination Rights (Post-Amendment)
Severity: HIGH
Location: Amendment doc_005, Page 3
Description: The recent amendment added unilateral termination rights allowing 
TechCorp (Client) to terminate without cause with only 10 days notice. We 
(Provider) still require 90 days notice and can only terminate for cause.
Impact: Creates significant business uncertainty. Client can terminate with 
minimal notice, leaving us unable to plan resources or make long-term investments 
in the relationship. We have no equivalent protection.
Affected Parties: DataServices LLC (Provider) - our company
Mitigation: URGENT - Negotiate to either remove the unilateral termination right, 
extend notice period to 90 days to match ours, or add termination fee equal to 
3-6 months of fees to compensate for disruption.
Supporting Research: Unequal termination rights are generally disfavored and may 
be negotiable, especially when one party has made specific investments.

[... additional risks ...]

SUMMARY: Identified 5 HIGH severity risks, 3 MEDIUM severity risks, 2 LOW severity risks.
Priority action required on automatic renewal and termination rights imbalance."""
    }
}
```

**Human reviewer evaluates:**
- Are the risks accurately identified and described?
- Are severity ratings appropriate and justified?
- Are document references correct and complete?
- Is the legal reasoning sound?
- Are recommendations practical and actionable?
- Is the writing clear and professional?
- Should any findings be reworded or reconsidered?

**Possible decisions:**

**Approve:** Findings are accurate and well-presented
```python
decisions = [{"type": "approve"}]
```

**Edit:** Adjust severity, add context, or refine wording
```python
decisions = [{
    "type": "edit",
    "edited_action": {
        "name": "write_file",
        "args": {
            "file_path": "/analysis/contractual_risks_doc_001.txt",
            "content": """CONTRACTUAL RISK ANALYSIS - Master Service Agreement (doc_001)
            
Risk #1: Automatic Renewal Without Notice Cap
Severity: MEDIUM  # Human downgraded from HIGH
Location: Page 9, Termination Section
Description: [same as above]
Impact: While renewal could continue indefinitely, our legal team has calendar 
reminders set for all contract renewals, making the risk of missing the notice 
window relatively low in practice.  # Human added context
[... rest of content with human refinements ...]"""
        }
    }
}]
```

**Reject:** Findings need significant revision
```python
decisions = [{"type": "reject"}]
# Provide feedback
provide_agent_feedback("""Risk #2 analysis needs revision. The amendment was executed 
by both parties voluntarily, so characterizing the termination rights as 'one-sided' 
may be too strong. Please reframe as an area for improvement in future negotiations 
rather than an immediately actionable defect.""")
```

## Implementing Review Interfaces

### Command-Line Interface for Reviews

A simple CLI interface for human reviewers:

```python
def review_action_cli(action_request, review_config):
    """Command-line interface for reviewing agent actions."""
    print("\n" + "="*80)
    print("HUMAN REVIEW REQUIRED")
    print("="*80)
    print(f"\nTool: {action_request['name']}")
    print(f"Allowed decisions: {review_config['allowed_decisions']}")
    print(f"\nProposed arguments:")
    print(json.dumps(action_request['args'], indent=2))
    
    if 'context' in action_request:
        print(f"\nContext: {action_request['context']}")
    
    print("\nOptions:")
    if 'approve' in review_config['allowed_decisions']:
        print("  1. Approve - Execute as proposed")
    if 'edit' in review_config['allowed_decisions']:
        print("  2. Edit - Modify before execution")
    if 'reject' in review_config['allowed_decisions']:
        print("  3. Reject - Skip this action")
    
    choice = input("\nYour decision (1/2/3): ").strip()
    
    if choice == "1" and 'approve' in review_config['allowed_decisions']:
        return {"type": "approve"}
    
    elif choice == "2" and 'edit' in review_config['allowed_decisions']:
        print("\nEnter edited arguments as JSON:")
        print("(Press Ctrl+D when done)")
        edited_json = sys.stdin.read()
        edited_args = json.loads(edited_json)
        return {
            "type": "edit",
            "edited_action": {
                "name": action_request['name'],
                "args": edited_args
            }
        }
    
    elif choice == "3" and 'reject' in review_config['allowed_decisions']:
        return {"type": "reject"}
    
    else:
        print("Invalid choice. Defaulting to reject.")
        return {"type": "reject"}
```

### Web-Based Review Interface

For team environments, a web interface provides better UX:

```python
from flask import Flask, render_template, request, jsonify
import threading
import queue

app = Flask(__name__)
review_queue = queue.Queue()
decision_queue = queue.Queue()

@app.route('/review')
def review_page():
    """Display pending actions for review."""
    if not review_queue.empty():
        action_data = review_queue.get()
        return render_template('review.html', action=action_data)
    return "No pending reviews"

@app.route('/submit_decision', methods=['POST'])
def submit_decision():
    """Handle reviewer's decision."""
    decision = request.json
    decision_queue.put(decision)
    return jsonify({"status": "received"})

def review_action_web(action_request, review_config):
    """Web interface for reviewing agent actions."""
    review_data = {
        "action_request": action_request,
        "review_config": review_config,
        "timestamp": datetime.now().isoformat()
    }
    
    # Queue for review
    review_queue.put(review_data)
    
    # Wait for decision
    decision = decision_queue.get(timeout=3600)  # 1 hour timeout
    return decision
```

### Slack Integration for Distributed Teams

For teams that work in Slack:

```python
from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse

def review_action_slack(action_request, review_config, slack_channel):
    """Slack interface for reviewing agent actions."""
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    
    # Create approval message with buttons
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Agent Approval Request*\n\nTool: `{action_request['name']}`"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"```{json.dumps(action_request['args'], indent=2)}```"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "✅ Approve"},
                    "value": "approve",
                    "action_id": "approve_action"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "✏️ Edit"},
                    "value": "edit",
                    "action_id": "edit_action"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "❌ Reject"},
                    "value": "reject",
                    "action_id": "reject_action",
                    "style": "danger"
                }
            ]
        }
    ]
    
    response = client.chat_postMessage(
        channel=slack_channel,
        text="Agent approval request",
        blocks=blocks
    )
    
    # Wait for button click (implementation depends on Slack app setup)
    return wait_for_slack_decision(response['ts'])
```

## Best Practices for Human Review

### 1. Establish Clear Review Criteria

Document what reviewers should check for each operation type:

**Planning Reviews (write_todos):**
- ✓ All relevant documents are included
- ✓ Priorities align with business objectives
- ✓ Sequence is logical and efficient
- ✓ No critical risk areas are overlooked
- ✓ Resource allocation is appropriate

**Delegation Reviews (task):**
- ✓ Correct subagent selected for the task
- ✓ Scope is clear and achievable
- ✓ Sufficient context provided
- ✓ Expected outputs are well-defined
- ✓ Instructions are unambiguous

**Document Access Reviews:**
- ✓ Access is authorized and necessary
- ✓ No privilege or confidentiality issues
- ✓ Access is logged appropriately
- ✓ Relevant to current analysis scope

**Findings Reviews (write_file):**
- ✓ Risks are accurately identified
- ✓ Severity ratings are justified
- ✓ Document references are correct
- ✓ Legal reasoning is sound
- ✓ Recommendations are actionable
- ✓ Writing is clear and professional

### 2. Set Appropriate Timeouts

Balance responsiveness with reviewer availability:

```python
# Development: Short timeouts for quick iteration
interrupt_timeout = 300  # 5 minutes

# Production: Longer timeouts for business hours response
interrupt_timeout = 3600  # 1 hour

# Async workflows: Very long timeouts with notification
interrupt_timeout = 86400  # 24 hours with email/Slack alerts
```

### 3. Provide Context to Reviewers

Include relevant information with each review request:

```python
def create_review_context(action_request, agent_state):
    """Build context for human reviewer."""
    return {
        "action": action_request,
        "conversation_history": get_recent_messages(agent_state, n=5),
        "current_plan": agent_state.get("todos", []),
        "documents_accessed": agent_state.get("accessed_docs", []),
        "findings_so_far": list_analysis_files(),
        "analysis_stage": determine_stage(agent_state)
    }
```

### 4. Enable Efficient Batch Reviews

When multiple actions are pending, allow batch processing:

```python
# Get all pending actions
interrupts = result["__interrupt__"][0].value
all_actions = interrupts["action_requests"]

# Present all for review at once
decisions = []
for action in all_actions:
    decision = review_action(action, review_config)
    decisions.append(decision)

# Submit all decisions together
result = agent.invoke(
    Command(resume={"decisions": decisions}),
    config=config
)
```

### 5. Log All Review Decisions

Maintain audit trail of human interventions:

```python
def log_review_decision(action_request, decision, reviewer):
    """Log review decision for audit trail."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "reviewer": reviewer,
        "action_tool": action_request["name"],
        "action_args": action_request["args"],
        "decision_type": decision["type"],
        "edited_args": decision.get("edited_action", {}).get("args"),
        "thread_id": config["configurable"]["thread_id"]
    }
    
    # Write to audit log
    with open("review_audit.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    # Also store in database for reporting
    store_review_in_db(log_entry)
```

### 6. Provide Feedback Mechanisms

Allow reviewers to guide agent behavior:

```python
def provide_agent_feedback(agent, feedback_text, config):
    """Send guidance to agent based on review."""
    agent.invoke({
        "messages": [{
            "role": "user",
            "content": f"[REVIEWER FEEDBACK] {feedback_text}"
        }]
    }, config=config)
```

## Production Deployment Checklist

Before deploying HITL approval in production:

- [ ] Review criteria documented for each operation type
- [ ] Reviewer interface implemented and tested
- [ ] Timeout values configured appropriately
- [ ] Notification system set up (email/Slack/webhook)
- [ ] Audit logging implemented and tested
- [ ] Backup reviewers identified for coverage
- [ ] Escalation process defined for urgent reviews
- [ ] Training provided to all potential reviewers
- [ ] Review metrics and SLAs established
- [ ] Feedback mechanism tested and documented

## Monitoring and Metrics

Track these metrics to optimize your HITL workflow:

- **Review Response Time:** Time from interrupt to human decision
- **Approval Rate:** Percentage of actions approved vs edited/rejected
- **Edit Frequency:** How often humans modify proposed actions
- **Bottleneck Analysis:** Which operations create most review burden
- **Reviewer Agreement:** Consistency across different reviewers
- **False Positive Rate:** Actions approved that shouldn't have been

Use these metrics to:
- Identify opportunities to reduce approval requirements
- Improve agent prompts to reduce edits/rejections
- Balance oversight needs with operational efficiency
- Train reviewers on common issues

## Conclusion

Human-in-the-loop approval transforms the Legal Risk Analysis system from a fully autonomous tool into a human-AI collaborative platform. By strategically placing approval points at critical operations—planning, delegation, document access, and findings creation—you ensure that human expertise and judgment remain central to the legal analysis process while still benefiting from AI's speed and analytical capabilities.

The key to successful HITL implementation is finding the right balance between oversight and efficiency for your specific use case, providing reviewers with clear criteria and good tooling, and continuously refining the system based on review patterns and feedback.
