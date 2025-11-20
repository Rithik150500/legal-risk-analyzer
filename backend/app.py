"""
Legal Risk Analyzer - Backend API Server

FastAPI application providing REST API and WebSocket endpoints for the
legal risk analysis system.
"""

import asyncio
import json
import os
import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum

from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Import from existing agent system
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from legal_risk_analysis_agent import create_legal_risk_analysis_agent, DataRoom
from data_room_indexer import DataRoomIndexer
from hitl_implementation import (
    create_agent_with_hitl,
    run_agent_with_hitl,
    ApprovalLevel,
    AutoApproveInterface,
    AuditLogger
)

# ============================================================================
# APPLICATION SETUP
# ============================================================================

app = FastAPI(
    title="Legal Risk Analyzer API",
    description="API for legal document risk analysis with AI agents",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# STORAGE CONFIGURATION
# ============================================================================

BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
DATA_ROOM_DIR = BASE_DIR / "data_room"
ANALYSIS_DIR = BASE_DIR / "analysis"

# Create directories
for directory in [UPLOAD_DIR, OUTPUT_DIR, DATA_ROOM_DIR, ANALYSIS_DIR]:
    directory.mkdir(exist_ok=True)

# ============================================================================
# IN-MEMORY STATE STORAGE
# ============================================================================

# Analysis sessions storage
analysis_sessions: Dict[str, Dict[str, Any]] = {}

# WebSocket connections for real-time updates
active_connections: Dict[str, List[WebSocket]] = {}

# HITL pending approvals
pending_approvals: Dict[str, Dict[str, Any]] = {}

# Data room index cache
data_room_index_cache: Optional[Dict] = None

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class ApprovalLevelEnum(str, Enum):
    HIGH = "high"
    MODERATE = "moderate"
    MINIMAL = "minimal"

class AnalysisRequest(BaseModel):
    """Request to start a new analysis"""
    message: str = Field(..., description="Analysis request message")
    approval_level: ApprovalLevelEnum = Field(default=ApprovalLevelEnum.MODERATE, description="HITL approval level")
    documents: Optional[List[str]] = Field(default=None, description="Specific document IDs to analyze")

class ApprovalDecision(BaseModel):
    """Human approval decision for HITL"""
    session_id: str
    approval_id: str
    decision: str = Field(..., description="approve, reject, or edit")
    edited_value: Optional[Any] = Field(default=None, description="Edited value if decision is edit")
    reason: Optional[str] = Field(default=None, description="Reason for decision")

class SessionStatus(BaseModel):
    """Analysis session status"""
    session_id: str
    status: str
    progress: int
    current_step: str
    started_at: str
    completed_at: Optional[str] = None
    has_pending_approval: bool = False
    error: Optional[str] = None

class DocumentInfo(BaseModel):
    """Document information"""
    doc_id: str
    filename: str
    summary: str
    page_count: int
    uploaded_at: str

# ============================================================================
# WEBSOCKET MANAGER
# ============================================================================

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)

    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def send_update(self, session_id: str, message: Dict):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

manager = ConnectionManager()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_data_room_index() -> Optional[Dict]:
    """Load the data room index from disk"""
    global data_room_index_cache
    index_path = DATA_ROOM_DIR / "data_room_index.json"
    if index_path.exists():
        with open(index_path, 'r') as f:
            data_room_index_cache = json.load(f)
        return data_room_index_cache
    return None

def get_approval_level_config(level: ApprovalLevelEnum) -> Dict:
    """Get approval level configuration"""
    if level == ApprovalLevelEnum.HIGH:
        return ApprovalLevel.high_oversight()
    elif level == ApprovalLevelEnum.MODERATE:
        return ApprovalLevel.moderate_oversight()
    else:
        return ApprovalLevel.minimal_oversight()

async def update_session_status(
    session_id: str,
    status: str,
    progress: int,
    current_step: str,
    **kwargs
):
    """Update session status and notify connected clients"""
    if session_id in analysis_sessions:
        analysis_sessions[session_id].update({
            "status": status,
            "progress": progress,
            "current_step": current_step,
            **kwargs
        })

        await manager.send_update(session_id, {
            "type": "status_update",
            "session_id": session_id,
            "status": status,
            "progress": progress,
            "current_step": current_step,
            **kwargs
        })

# ============================================================================
# WEB REVIEW INTERFACE FOR HITL
# ============================================================================

class WebReviewInterface:
    """Review interface that stores approvals for web UI"""

    def __init__(self, session_id: str):
        self.session_id = session_id

    def review_action(
        self,
        action_request: Dict,
        review_config: Dict,
        context: Optional[Dict] = None
    ) -> Dict:
        """Store action for web review and wait for decision"""
        approval_id = str(uuid.uuid4())

        # Store pending approval
        pending_approvals[approval_id] = {
            "session_id": self.session_id,
            "action_request": action_request,
            "review_config": review_config,
            "context": context,
            "created_at": datetime.now().isoformat(),
            "decision": None
        }

        # Update session to indicate pending approval
        if self.session_id in analysis_sessions:
            analysis_sessions[self.session_id]["pending_approval_id"] = approval_id
            analysis_sessions[self.session_id]["has_pending_approval"] = True

        # Return placeholder - actual decision comes from API
        return {
            "decision": "pending",
            "approval_id": approval_id
        }

# ============================================================================
# API ENDPOINTS - HEALTH & INFO
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "name": "Legal Risk Analyzer API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "data_room_loaded": data_room_index_cache is not None
    }

# ============================================================================
# API ENDPOINTS - DATA ROOM & DOCUMENTS
# ============================================================================

@app.get("/api/documents")
async def list_documents():
    """List all documents in the data room"""
    index = load_data_room_index()
    if not index:
        return {"documents": [], "total": 0}

    documents = []
    for doc in index.get("documents", []):
        documents.append({
            "doc_id": doc["doc_id"],
            "summary": doc.get("summdesc", "No summary available"),
            "page_count": len(doc.get("pages", [])),
            "filename": doc.get("filename", doc["doc_id"])
        })

    return {
        "documents": documents,
        "total": len(documents),
        "metadata": index.get("metadata", {})
    }

@app.get("/api/documents/{doc_id}")
async def get_document(doc_id: str):
    """Get detailed information about a specific document"""
    index = load_data_room_index()
    if not index:
        raise HTTPException(status_code=404, detail="Data room not found")

    for doc in index.get("documents", []):
        if doc["doc_id"] == doc_id:
            return doc

    raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")

@app.post("/api/documents/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None
):
    """Upload documents for processing"""
    uploaded_files = []

    for file in files:
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        uploaded_files.append({
            "filename": file.filename,
            "size": len(content),
            "path": str(file_path)
        })

    return {
        "message": f"Uploaded {len(files)} files",
        "files": uploaded_files
    }

@app.post("/api/documents/process")
async def process_documents(background_tasks: BackgroundTasks):
    """Process uploaded documents and build data room index"""

    # Check for uploaded files
    uploaded_files = list(UPLOAD_DIR.glob("*"))
    if not uploaded_files:
        raise HTTPException(status_code=400, detail="No documents uploaded")

    task_id = str(uuid.uuid4())

    async def process_task():
        try:
            indexer = DataRoomIndexer(
                input_folder=str(UPLOAD_DIR),
                output_folder=str(DATA_ROOM_DIR),
                summarization_model="gpt-4o-mini",
                dpi=200
            )

            index = indexer.build_data_room_index()

            # Clear cache to reload
            global data_room_index_cache
            data_room_index_cache = None

            return index
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Run processing in background
    background_tasks.add_task(process_task)

    return {
        "message": "Document processing started",
        "task_id": task_id,
        "file_count": len(uploaded_files)
    }

@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document from the data room"""
    index = load_data_room_index()
    if not index:
        raise HTTPException(status_code=404, detail="Data room not found")

    # Find and remove document
    documents = index.get("documents", [])
    for i, doc in enumerate(documents):
        if doc["doc_id"] == doc_id:
            documents.pop(i)

            # Save updated index
            index_path = DATA_ROOM_DIR / "data_room_index.json"
            with open(index_path, 'w') as f:
                json.dump(index, f, indent=2)

            # Clear cache
            global data_room_index_cache
            data_room_index_cache = None

            return {"message": f"Document {doc_id} deleted"}

    raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")

# ============================================================================
# API ENDPOINTS - ANALYSIS
# ============================================================================

@app.post("/api/analysis/start")
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Start a new legal risk analysis"""

    # Load data room
    index = load_data_room_index()
    if not index:
        raise HTTPException(status_code=400, detail="No data room available. Please upload and process documents first.")

    # Create session
    session_id = str(uuid.uuid4())

    analysis_sessions[session_id] = {
        "session_id": session_id,
        "status": "initializing",
        "progress": 0,
        "current_step": "Starting analysis",
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "has_pending_approval": False,
        "pending_approval_id": None,
        "request": request.model_dump(),
        "results": None,
        "error": None
    }

    # Run analysis in background
    async def run_analysis():
        try:
            await update_session_status(session_id, "running", 10, "Creating agent")

            # Get approval level
            approval_config = get_approval_level_config(request.approval_level)

            # Create agent with HITL
            agent_config = create_agent_with_hitl(
                data_room_index=index,
                approval_level=approval_config,
                review_interface=AutoApproveInterface(),  # Auto-approve for web demo
                reviewer_name="web_user",
                enable_audit=True
            )

            await update_session_status(session_id, "running", 20, "Running analysis")

            # Build analysis message
            message = request.message
            if request.documents:
                doc_list = ", ".join(request.documents)
                message += f"\n\nFocus on these documents: {doc_list}"

            # Run analysis
            result = run_agent_with_hitl(
                agent_config=agent_config,
                user_message=message,
                thread_id=session_id,
                max_iterations=50
            )

            await update_session_status(session_id, "running", 80, "Collecting results")

            # Extract results
            findings = collect_analysis_findings(session_id)

            await update_session_status(
                session_id,
                "completed",
                100,
                "Analysis complete",
                completed_at=datetime.now().isoformat(),
                results={
                    "findings": findings,
                    "message_count": len(result.get("messages", [])),
                    "has_report": (OUTPUT_DIR / "legal_risk_analysis_report.docx").exists(),
                    "has_dashboard": (OUTPUT_DIR / "legal_risk_analysis_dashboard.html").exists()
                }
            )

        except Exception as e:
            await update_session_status(
                session_id,
                "failed",
                0,
                "Analysis failed",
                error=str(e)
            )

    background_tasks.add_task(run_analysis)

    return {
        "session_id": session_id,
        "message": "Analysis started",
        "status": "initializing"
    }

def collect_analysis_findings(session_id: str) -> Dict:
    """Collect all analysis findings from filesystem"""
    findings = {
        "categories": {},
        "summary": {},
        "risk_count": {"high": 0, "medium": 0, "low": 0}
    }

    # Look for findings files
    for finding_file in ANALYSIS_DIR.glob("*.txt"):
        category = finding_file.stem
        with open(finding_file, 'r') as f:
            content = f.read()
            findings["categories"][category] = content

            # Count risks (simple heuristic)
            content_lower = content.lower()
            findings["risk_count"]["high"] += content_lower.count("high risk") + content_lower.count("critical")
            findings["risk_count"]["medium"] += content_lower.count("medium risk") + content_lower.count("moderate")
            findings["risk_count"]["low"] += content_lower.count("low risk") + content_lower.count("minor")

    return findings

@app.get("/api/analysis/{session_id}")
async def get_analysis_status(session_id: str):
    """Get the status of an analysis session"""
    if session_id not in analysis_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    return analysis_sessions[session_id]

@app.get("/api/analysis/{session_id}/results")
async def get_analysis_results(session_id: str):
    """Get the results of a completed analysis"""
    if session_id not in analysis_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = analysis_sessions[session_id]
    if session["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis not yet completed")

    return {
        "session_id": session_id,
        "results": session.get("results", {}),
        "completed_at": session.get("completed_at")
    }

@app.get("/api/analysis")
async def list_analysis_sessions():
    """List all analysis sessions"""
    sessions = []
    for session_id, session in analysis_sessions.items():
        sessions.append({
            "session_id": session_id,
            "status": session["status"],
            "progress": session["progress"],
            "started_at": session["started_at"],
            "completed_at": session.get("completed_at")
        })

    return {
        "sessions": sorted(sessions, key=lambda x: x["started_at"], reverse=True),
        "total": len(sessions)
    }

@app.delete("/api/analysis/{session_id}")
async def delete_analysis_session(session_id: str):
    """Delete an analysis session"""
    if session_id not in analysis_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    del analysis_sessions[session_id]
    return {"message": f"Session {session_id} deleted"}

# ============================================================================
# API ENDPOINTS - HITL APPROVALS
# ============================================================================

@app.get("/api/approvals")
async def list_pending_approvals():
    """List all pending HITL approvals"""
    approvals = []
    for approval_id, approval in pending_approvals.items():
        if approval["decision"] is None:
            approvals.append({
                "approval_id": approval_id,
                "session_id": approval["session_id"],
                "action_type": approval["action_request"].get("tool_name", "unknown"),
                "created_at": approval["created_at"]
            })

    return {"approvals": approvals, "total": len(approvals)}

@app.get("/api/approvals/{approval_id}")
async def get_approval_details(approval_id: str):
    """Get details of a pending approval"""
    if approval_id not in pending_approvals:
        raise HTTPException(status_code=404, detail="Approval not found")

    return pending_approvals[approval_id]

@app.post("/api/approvals/{approval_id}/decide")
async def submit_approval_decision(approval_id: str, decision: ApprovalDecision):
    """Submit a decision for a pending approval"""
    if approval_id not in pending_approvals:
        raise HTTPException(status_code=404, detail="Approval not found")

    approval = pending_approvals[approval_id]

    # Record decision
    approval["decision"] = {
        "decision": decision.decision,
        "edited_value": decision.edited_value,
        "reason": decision.reason,
        "decided_at": datetime.now().isoformat()
    }

    # Update session
    session_id = approval["session_id"]
    if session_id in analysis_sessions:
        analysis_sessions[session_id]["has_pending_approval"] = False
        analysis_sessions[session_id]["pending_approval_id"] = None

    return {
        "message": "Decision recorded",
        "approval_id": approval_id,
        "decision": decision.decision
    }

# ============================================================================
# API ENDPOINTS - OUTPUTS & DOWNLOADS
# ============================================================================

@app.get("/api/outputs")
async def list_outputs():
    """List all generated output files"""
    outputs = []

    for output_file in OUTPUT_DIR.glob("*"):
        if output_file.is_file():
            outputs.append({
                "filename": output_file.name,
                "type": output_file.suffix,
                "size": output_file.stat().st_size,
                "modified": datetime.fromtimestamp(output_file.stat().st_mtime).isoformat()
            })

    return {"outputs": outputs, "total": len(outputs)}

@app.get("/api/outputs/{filename}")
async def download_output(filename: str):
    """Download a generated output file"""
    file_path = OUTPUT_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Output file not found")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )

@app.get("/api/outputs/report/latest")
async def get_latest_report():
    """Get the latest generated report"""
    report_path = OUTPUT_DIR / "legal_risk_analysis_report.docx"

    if not report_path.exists():
        raise HTTPException(status_code=404, detail="No report generated yet")

    return FileResponse(
        path=report_path,
        filename="legal_risk_analysis_report.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

@app.get("/api/outputs/dashboard/latest")
async def get_latest_dashboard():
    """Get the latest generated dashboard HTML"""
    dashboard_path = OUTPUT_DIR / "legal_risk_analysis_dashboard.html"

    if not dashboard_path.exists():
        raise HTTPException(status_code=404, detail="No dashboard generated yet")

    return FileResponse(
        path=dashboard_path,
        filename="legal_risk_analysis_dashboard.html",
        media_type="text/html"
    )

# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time analysis updates"""
    await manager.connect(websocket, session_id)

    try:
        # Send current status if session exists
        if session_id in analysis_sessions:
            await websocket.send_json({
                "type": "status_update",
                **analysis_sessions[session_id]
            })

        # Keep connection alive and handle messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle ping/pong for keepalive
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)

# ============================================================================
# AUDIT & STATISTICS
# ============================================================================

@app.get("/api/audit/logs")
async def get_audit_logs():
    """Get HITL audit logs"""
    audit_file = BASE_DIR / "review_audit.jsonl"

    if not audit_file.exists():
        return {"logs": [], "total": 0}

    logs = []
    with open(audit_file, 'r') as f:
        for line in f:
            if line.strip():
                logs.append(json.loads(line))

    return {
        "logs": logs[-100:],  # Return last 100 entries
        "total": len(logs)
    }

@app.get("/api/statistics")
async def get_statistics():
    """Get system statistics"""
    index = load_data_room_index()

    return {
        "documents": {
            "total": len(index.get("documents", [])) if index else 0,
            "pages": sum(len(doc.get("pages", [])) for doc in index.get("documents", [])) if index else 0
        },
        "sessions": {
            "total": len(analysis_sessions),
            "completed": sum(1 for s in analysis_sessions.values() if s["status"] == "completed"),
            "running": sum(1 for s in analysis_sessions.values() if s["status"] == "running"),
            "failed": sum(1 for s in analysis_sessions.values() if s["status"] == "failed")
        },
        "approvals": {
            "pending": sum(1 for a in pending_approvals.values() if a["decision"] is None),
            "total": len(pending_approvals)
        }
    }

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    # Load data room on startup
    load_data_room_index()

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
