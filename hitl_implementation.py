"""
Human-in-the-Loop Implementation for Legal Risk Analysis System

This module provides practical implementations of approval workflows for
the Legal Risk Analysis agent, with working examples for different
deployment scenarios.
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from langgraph.types import Command
from legal_risk_analysis_agent import create_legal_risk_analysis_agent


# ============================================================================
# APPROVAL CONFIGURATIONS
# ============================================================================

class ApprovalLevel:
    """Pre-defined approval levels for different use cases."""
    
    @staticmethod
    def high_oversight():
        """
        Maximum oversight - approve all operations.
        Use during: Initial deployment, high-stakes analyses, learning phase.
        """
        return {
            "write_todos": True,
            "task": True,
            "get_document": True,
            "get_document_pages": True,
            "write_file": True,
            "edit_file": True,
        }
    
    @staticmethod
    def moderate_oversight():
        """
        Moderate oversight - approve planning, delegation, and outputs.
        Use during: Routine analyses with trusted agent, efficiency focus.
        """
        return {
            "write_todos": True,
            "task": True,
            "get_document": False,
            "get_document_pages": False,
            "write_file": True,
            "edit_file": {"allowed_decisions": ["approve", "reject"]},
        }
    
    @staticmethod
    def minimal_oversight():
        """
        Minimal oversight - approve only final outputs.
        Use during: Mature deployments, preliminary analyses, time-sensitive work.
        """
        return {
            "write_todos": False,
            "task": False,
            "get_document": False,
            "get_document_pages": False,
            "write_file": True,
            "edit_file": True,
        }
    
    @staticmethod
    def custom(
        planning: bool = True,
        delegation: bool = True,
        document_access: bool = False,
        file_operations: bool = True
    ):
        """
        Custom approval configuration.
        
        Args:
            planning: Approve write_todos operations
            delegation: Approve task delegation to subagents
            document_access: Approve document retrieval
            file_operations: Approve file creation/modification
        """
        return {
            "write_todos": planning,
            "task": delegation,
            "get_document": document_access,
            "get_document_pages": document_access,
            "write_file": file_operations,
            "edit_file": file_operations,
        }


# ============================================================================
# REVIEW INTERFACES
# ============================================================================

class ReviewInterface:
    """Base class for review interfaces."""
    
    def review_action(
        self,
        action_request: Dict[str, Any],
        review_config: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Present action for review and get human decision.
        
        Args:
            action_request: The action the agent wants to take
            review_config: Configuration for this review
            context: Additional context for the reviewer
            
        Returns:
            Decision dict with 'type' and optionally 'edited_action'
        """
        raise NotImplementedError


class CLIReviewInterface(ReviewInterface):
    """Command-line interface for reviewing agent actions."""
    
    def review_action(
        self,
        action_request: Dict[str, Any],
        review_config: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Present action in terminal and get user input."""
        
        print("\n" + "=" * 80)
        print("🔍 HUMAN REVIEW REQUIRED")
        print("=" * 80)
        
        print(f"\n📋 Tool: {action_request['name']}")
        
        # Show context if available
        if context:
            print("\n📍 Context:")
            if 'stage' in context:
                print(f"   Analysis Stage: {context['stage']}")
            if 'documents_accessed' in context:
                print(f"   Documents Accessed: {len(context['documents_accessed'])}")
        
        print("\n📝 Proposed Action:")
        print(json.dumps(action_request['args'], indent=2))
        
        # Show allowed decisions
        allowed = review_config.get('allowed_decisions', ['approve', 'edit', 'reject'])
        print(f"\n✅ Allowed Decisions: {', '.join(allowed)}")
        
        # Present options
        print("\n" + "-" * 80)
        print("Options:")
        options = []
        if 'approve' in allowed:
            options.append("1")
            print("  [1] ✅ APPROVE - Execute as proposed")
        if 'edit' in allowed:
            options.append("2")
            print("  [2] ✏️  EDIT - Modify before execution")
        if 'reject' in allowed:
            options.append("3")
            print("  [3] ❌ REJECT - Skip this action")
        
        # Get user choice
        while True:
            choice = input(f"\nYour decision ({'/'.join(options)}): ").strip()
            
            if choice == "1" and 'approve' in allowed:
                print("\n✅ Action approved")
                return {"type": "approve"}
            
            elif choice == "2" and 'edit' in allowed:
                return self._handle_edit(action_request)
            
            elif choice == "3" and 'reject' in allowed:
                print("\n❌ Action rejected")
                return {"type": "reject"}
            
            else:
                print(f"❌ Invalid choice. Please enter one of: {', '.join(options)}")
    
    def _handle_edit(self, action_request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle editing of action arguments."""
        print("\n" + "=" * 80)
        print("✏️  EDIT MODE")
        print("=" * 80)
        
        tool_name = action_request['name']
        
        # Different editing interfaces for different tools
        if tool_name == "write_todos":
            return self._edit_todos(action_request)
        elif tool_name == "task":
            return self._edit_task(action_request)
        elif tool_name == "write_file":
            return self._edit_file(action_request)
        else:
            return self._edit_generic(action_request)
    
    def _edit_todos(self, action_request: Dict[str, Any]) -> Dict[str, Any]:
        """Edit todo list."""
        todos = action_request['args']['todos']
        
        print("\nCurrent todos:")
        for i, todo in enumerate(todos, 1):
            print(f"\n{i}. Task: {todo['task']}")
            print(f"   Status: {todo['status']}")
            print(f"   Priority: {todo.get('priority', 'medium')}")
        
        print("\n" + "-" * 80)
        print("Edit options:")
        print("  [1] Add a todo")
        print("  [2] Remove a todo")
        print("  [3] Change priority")
        print("  [4] Manually edit JSON")
        print("  [5] Cancel editing")
        
        choice = input("\nChoice: ").strip()
        
        if choice == "1":
            task = input("New task description: ")
            priority = input("Priority (low/medium/high/critical): ").strip() or "medium"
            todos.append({
                "task": task,
                "status": "pending",
                "priority": priority
            })
        
        elif choice == "2":
            num = int(input("Remove todo number: "))
            if 1 <= num <= len(todos):
                todos.pop(num - 1)
        
        elif choice == "3":
            num = int(input("Change priority for todo number: "))
            if 1 <= num <= len(todos):
                priority = input("New priority (low/medium/high/critical): ")
                todos[num - 1]['priority'] = priority
        
        elif choice == "4":
            return self._edit_generic(action_request)
        
        elif choice == "5":
            print("❌ Editing cancelled, rejecting action")
            return {"type": "reject"}
        
        return {
            "type": "edit",
            "edited_action": {
                "name": "write_todos",
                "args": {"todos": todos}
            }
        }
    
    def _edit_task(self, action_request: Dict[str, Any]) -> Dict[str, Any]:
        """Edit task delegation."""
        print("\nCurrent delegation:")
        print(f"  Subagent: {action_request['args']['name']}")
        print(f"  Task: {action_request['args']['task']}")
        
        print("\n" + "-" * 80)
        print("What would you like to edit?")
        print("  [1] Add context to task description")
        print("  [2] Change subagent")
        print("  [3] Manually edit JSON")
        print("  [4] Cancel editing")
        
        choice = input("\nChoice: ").strip()
        
        if choice == "1":
            additional_context = input("\nEnter additional context to add:\n")
            current_task = action_request['args']['task']
            new_task = f"{current_task}\n\nADDITIONAL CONTEXT:\n{additional_context}"
            
            return {
                "type": "edit",
                "edited_action": {
                    "name": "task",
                    "args": {
                        "name": action_request['args']['name'],
                        "task": new_task
                    }
                }
            }
        
        elif choice == "2":
            print("\nAvailable subagents:")
            print("  - legal-analyzer")
            print("  - report-creator")
            print("  - dashboard-creator")
            print("  - general-purpose")
            new_subagent = input("\nNew subagent: ").strip()
            
            return {
                "type": "edit",
                "edited_action": {
                    "name": "task",
                    "args": {
                        "name": new_subagent,
                        "task": action_request['args']['task']
                    }
                }
            }
        
        elif choice == "3":
            return self._edit_generic(action_request)
        
        else:
            print("❌ Editing cancelled, rejecting action")
            return {"type": "reject"}
    
    def _edit_file(self, action_request: Dict[str, Any]) -> Dict[str, Any]:
        """Edit file write operation."""
        print("\nCurrent file write:")
        print(f"  Path: {action_request['args']['file_path']}")
        print(f"  Content length: {len(action_request['args']['content'])} characters")
        print("\nFirst 500 characters:")
        print("-" * 80)
        print(action_request['args']['content'][:500])
        if len(action_request['args']['content']) > 500:
            print("\n... (truncated)")
        print("-" * 80)
        
        print("\n" + "-" * 80)
        print("Edit options:")
        print("  [1] Change file path")
        print("  [2] Edit content in text editor")
        print("  [3] Manually edit JSON")
        print("  [4] Cancel editing")
        
        choice = input("\nChoice: ").strip()
        
        if choice == "1":
            new_path = input("New file path: ").strip()
            return {
                "type": "edit",
                "edited_action": {
                    "name": "write_file",
                    "args": {
                        "file_path": new_path,
                        "content": action_request['args']['content']
                    }
                }
            }
        
        elif choice == "2":
            # Save to temp file for editing
            temp_file = "/tmp/edit_content.txt"
            with open(temp_file, 'w') as f:
                f.write(action_request['args']['content'])
            
            # Open in editor
            editor = os.environ.get('EDITOR', 'nano')
            os.system(f"{editor} {temp_file}")
            
            # Read edited content
            with open(temp_file, 'r') as f:
                edited_content = f.read()
            
            return {
                "type": "edit",
                "edited_action": {
                    "name": "write_file",
                    "args": {
                        "file_path": action_request['args']['file_path'],
                        "content": edited_content
                    }
                }
            }
        
        elif choice == "3":
            return self._edit_generic(action_request)
        
        else:
            print("❌ Editing cancelled, rejecting action")
            return {"type": "reject"}
    
    def _edit_generic(self, action_request: Dict[str, Any]) -> Dict[str, Any]:
        """Generic JSON editing."""
        print("\nCurrent arguments:")
        print(json.dumps(action_request['args'], indent=2))
        
        print("\nEnter edited arguments as JSON:")
        print("(Paste JSON and press Ctrl+D when done)")
        
        try:
            lines = []
            while True:
                try:
                    line = input()
                    lines.append(line)
                except EOFError:
                    break
            
            edited_json = '\n'.join(lines)
            edited_args = json.loads(edited_json)
            
            return {
                "type": "edit",
                "edited_action": {
                    "name": action_request['name'],
                    "args": edited_args
                }
            }
        
        except json.JSONDecodeError as e:
            print(f"\n❌ Invalid JSON: {e}")
            print("Rejecting action")
            return {"type": "reject"}


class AutoApproveInterface(ReviewInterface):
    """Auto-approve interface for testing or low-risk operations."""
    
    def __init__(self, log_actions: bool = True):
        self.log_actions = log_actions
    
    def review_action(
        self,
        action_request: Dict[str, Any],
        review_config: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Automatically approve all actions with optional logging."""
        if self.log_actions:
            print(f"[AUTO-APPROVED] {action_request['name']}")
        
        return {"type": "approve"}


# ============================================================================
# AUDIT LOGGING
# ============================================================================

class AuditLogger:
    """Log all review decisions for compliance and analysis."""
    
    def __init__(self, log_file: str = "review_audit.jsonl"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log_review(
        self,
        action_request: Dict[str, Any],
        decision: Dict[str, Any],
        reviewer: str,
        thread_id: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Log a review decision."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "thread_id": thread_id,
            "reviewer": reviewer,
            "action_tool": action_request["name"],
            "action_args": action_request["args"],
            "decision_type": decision["type"],
            "edited_args": decision.get("edited_action", {}).get("args"),
            "context": context
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def get_review_stats(self) -> Dict[str, Any]:
        """Get statistics on review decisions."""
        if not self.log_file.exists():
            return {}
        
        stats = {
            "total_reviews": 0,
            "by_decision": {"approve": 0, "edit": 0, "reject": 0},
            "by_tool": {},
            "by_reviewer": {}
        }
        
        with open(self.log_file, 'r') as f:
            for line in f:
                entry = json.loads(line)
                stats["total_reviews"] += 1
                
                # By decision type
                decision = entry["decision_type"]
                stats["by_decision"][decision] = stats["by_decision"].get(decision, 0) + 1
                
                # By tool
                tool = entry["action_tool"]
                stats["by_tool"][tool] = stats["by_tool"].get(tool, 0) + 1
                
                # By reviewer
                reviewer = entry["reviewer"]
                stats["by_reviewer"][reviewer] = stats["by_reviewer"].get(reviewer, 0) + 1
        
        return stats


# ============================================================================
# AGENT WITH HITL
# ============================================================================

def create_agent_with_hitl(
    data_room_index: Dict[str, Any],
    approval_level: Dict[str, Any],
    review_interface: ReviewInterface,
    reviewer_name: str = "human",
    enable_audit: bool = True
):
    """
    Create Legal Risk Analysis Agent with human-in-the-loop approval.
    
    Args:
        data_room_index: The data room structure
        approval_level: Dict mapping tool names to interrupt configs
        review_interface: Interface for human review
        reviewer_name: Name of the reviewer for audit logs
        enable_audit: Whether to log all review decisions
        
    Returns:
        Configured agent with HITL enabled
    """
    # Create the base agent with interrupts configured
    agent = create_legal_risk_analysis_agent(data_room_index)
    
    # Note: The agent's interrupt_on configuration would be set during creation
    # For this example, we'll show how to wrap the invocation with HITL handling
    
    audit_logger = AuditLogger() if enable_audit else None
    
    return {
        "agent": agent,
        "approval_level": approval_level,
        "review_interface": review_interface,
        "reviewer_name": reviewer_name,
        "audit_logger": audit_logger
    }


def run_agent_with_hitl(
    agent_config: Dict[str, Any],
    user_message: str,
    thread_id: str,
    max_iterations: int = 50
) -> Dict[str, Any]:
    """
    Run agent with human-in-the-loop approval handling.
    
    Args:
        agent_config: Configuration from create_agent_with_hitl
        user_message: User's request
        thread_id: Thread identifier for this conversation
        max_iterations: Maximum number of approval cycles
        
    Returns:
        Final agent result
    """
    agent = agent_config["agent"]
    review_interface = agent_config["review_interface"]
    reviewer_name = agent_config["reviewer_name"]
    audit_logger = agent_config["audit_logger"]
    
    config = {"configurable": {"thread_id": thread_id}}
    
    # Initial invocation
    result = agent.invoke({
        "messages": [{"role": "user", "content": user_message}]
    }, config=config)
    
    iteration = 0
    
    # Handle interrupts
    while result.get("__interrupt__") and iteration < max_iterations:
        iteration += 1
        print(f"\n{'='*80}")
        print(f"Interrupt {iteration}/{max_iterations}")
        print(f"{'='*80}")
        
        interrupts = result["__interrupt__"][0].value
        action_requests = interrupts["action_requests"]
        review_configs = interrupts["review_configs"]
        
        # Create lookup for configs
        config_map = {cfg["action_name"]: cfg for cfg in review_configs}
        
        # Get decisions for all pending actions
        decisions = []
        for action in action_requests:
            review_config = config_map[action["name"]]
            
            # Get context for reviewer
            context = {
                "stage": f"iteration {iteration}",
                "thread_id": thread_id
            }
            
            # Get human decision
            decision = review_interface.review_action(
                action_request=action,
                review_config=review_config,
                context=context
            )
            
            decisions.append(decision)
            
            # Log if enabled
            if audit_logger:
                audit_logger.log_review(
                    action_request=action,
                    decision=decision,
                    reviewer=reviewer_name,
                    thread_id=thread_id,
                    context=context
                )
        
        # Resume with decisions
        result = agent.invoke(
            Command(resume={"decisions": decisions}),
            config=config
        )
    
    if iteration >= max_iterations:
        print(f"\n⚠️  Warning: Reached maximum iterations ({max_iterations})")
    
    return result


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def example_cli_review():
    """Example: Run agent with CLI review interface."""
    from example_usage import create_mock_data_room
    
    print("=" * 80)
    print("Legal Risk Analysis with Human-in-the-Loop (CLI)")
    print("=" * 80)
    
    # Create data room
    data_room_index = create_mock_data_room()
    
    # Configure HITL
    agent_config = create_agent_with_hitl(
        data_room_index=data_room_index,
        approval_level=ApprovalLevel.moderate_oversight(),
        review_interface=CLIReviewInterface(),
        reviewer_name="legal_team_member",
        enable_audit=True
    )
    
    # Run analysis with human approval
    result = run_agent_with_hitl(
        agent_config=agent_config,
        user_message="Analyze doc_001 and identify the top 3 contractual risks.",
        thread_id="cli_review_example_001",
        max_iterations=20
    )
    
    print("\n" + "=" * 80)
    print("Analysis Complete!")
    print("=" * 80)
    print(result["messages"][-1]["content"])
    
    # Show audit stats
    if agent_config["audit_logger"]:
        stats = agent_config["audit_logger"].get_review_stats()
        print("\n" + "=" * 80)
        print("Review Statistics")
        print("=" * 80)
        print(json.dumps(stats, indent=2))


def example_auto_approve():
    """Example: Run agent with auto-approve (for testing)."""
    from example_usage import create_mock_data_room
    
    print("=" * 80)
    print("Legal Risk Analysis with Auto-Approve (Testing Mode)")
    print("=" * 80)
    
    # Create data room
    data_room_index = create_mock_data_room()
    
    # Configure with auto-approve
    agent_config = create_agent_with_hitl(
        data_room_index=data_room_index,
        approval_level=ApprovalLevel.high_oversight(),
        review_interface=AutoApproveInterface(log_actions=True),
        reviewer_name="auto_approve_system",
        enable_audit=True
    )
    
    # Run analysis
    result = run_agent_with_hitl(
        agent_config=agent_config,
        user_message="Conduct comprehensive risk analysis of all documents.",
        thread_id="auto_approve_example_001",
        max_iterations=50
    )
    
    print("\n" + "=" * 80)
    print("Analysis Complete!")
    print("=" * 80)


if __name__ == "__main__":
    import sys
    
    print("\nHuman-in-the-Loop Examples:")
    print("1. CLI Review Interface")
    print("2. Auto-Approve (Testing)")
    
    choice = input("\nSelect example (1/2): ").strip()
    
    if choice == "1":
        example_cli_review()
    elif choice == "2":
        example_auto_approve()
    else:
        print("Invalid choice")
