# Legal Risk Analyzer - Web Interface

Full-stack web interface for the Legal Risk Analysis Deep Agent System.

## Overview

The web interface provides a modern, interactive way to:
- Upload and manage legal documents
- Run AI-powered risk analysis
- Review and approve HITL (Human-in-the-Loop) decisions
- Download generated reports and dashboards
- Monitor analysis progress in real-time

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  React Frontend │────▶│  FastAPI Backend│────▶│  Agent System   │
│  (Port 5173)    │     │  (Port 8000)    │     │  (LangGraph)    │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                      │                       │
         │                      │                       │
         ▼                      ▼                       ▼
   Tailwind CSS            WebSocket              Claude API
   Recharts               REST API             Document Processing
   React Router           File Storage          Risk Analysis
```

## Quick Start

### Prerequisites

1. **Python 3.9+** with pip
2. **Node.js 18+** with npm
3. **LibreOffice** (for document conversion)
4. **Poppler** (for PDF processing)
5. **API Key**: `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`

### Installation

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install frontend dependencies
cd frontend && npm install && cd ..

# 3. Set your API key
export ANTHROPIC_API_KEY="your-key-here"
```

### Running the Application

**Option 1: Run Both Servers (Recommended for Development)**

```bash
chmod +x run_dev.sh
./run_dev.sh
```

**Option 2: Run Separately**

Terminal 1 (Backend):
```bash
chmod +x run_backend.sh
./run_backend.sh
```

Terminal 2 (Frontend):
```bash
chmod +x run_frontend.sh
./run_frontend.sh
```

### Access Points

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Features

### Dashboard

Overview of the system with:
- Document count and pages
- Analysis session statistics
- Pending approval count
- Recent session activity
- Quick action buttons

### Documents

- **Upload**: Drag-and-drop or file picker for documents
- **Process**: Trigger AI-powered document indexing
- **View**: Browse documents with summaries
- **Delete**: Remove documents from data room

Supported formats: PDF, DOCX, DOC, XLSX, XLS, PPTX, PPT, TXT, RTF, ODT

### Analysis

- **Start Analysis**: Configure and launch risk analysis
  - Custom analysis message
  - Approval level selection (High/Moderate/Minimal)
  - Document selection
- **Monitor Progress**: Real-time status via WebSocket
- **View Results**: Risk summary with visualizations

### Approvals (HITL)

- **Pending Approvals**: Review actions awaiting human decision
- **Decision Making**: Approve, reject, or edit actions
- **Audit Logs**: Complete history of all decisions

### Outputs

- **Reports**: Download Word documents
- **Dashboards**: Open interactive HTML dashboards
- **File Browser**: Access all generated files

## API Endpoints

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/documents` | List all documents |
| GET | `/api/documents/{id}` | Get document details |
| POST | `/api/documents/upload` | Upload documents |
| POST | `/api/documents/process` | Process uploaded documents |
| DELETE | `/api/documents/{id}` | Delete a document |

### Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analysis` | List all sessions |
| GET | `/api/analysis/{id}` | Get session status |
| GET | `/api/analysis/{id}/results` | Get analysis results |
| POST | `/api/analysis/start` | Start new analysis |
| DELETE | `/api/analysis/{id}` | Delete session |

### Approvals

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/approvals` | List pending approvals |
| GET | `/api/approvals/{id}` | Get approval details |
| POST | `/api/approvals/{id}/decide` | Submit decision |

### Outputs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/outputs` | List output files |
| GET | `/api/outputs/{filename}` | Download file |
| GET | `/api/outputs/report/latest` | Get latest report |
| GET | `/api/outputs/dashboard/latest` | Get latest dashboard |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `ws://localhost:8000/ws/{session_id}` | Real-time updates |

## Frontend Technology Stack

- **React 18** - UI framework
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first styling
- **Recharts** - Data visualization
- **Lucide React** - Icons
- **Axios** - HTTP client
- **date-fns** - Date formatting

## Backend Technology Stack

- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **WebSockets** - Real-time communication

## Project Structure

```
legal-risk-analyzer/
├── backend/
│   └── app.py              # FastAPI application
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Documents.jsx
│   │   │   ├── Analysis.jsx
│   │   │   ├── Approvals.jsx
│   │   │   └── Outputs.jsx
│   │   ├── App.jsx
│   │   ├── api.js
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── run_backend.sh          # Backend start script
├── run_frontend.sh         # Frontend start script
├── run_dev.sh              # Combined dev script
└── WEB_INTERFACE.md        # This file
```

## Configuration

### Backend Configuration

Environment variables:
- `ANTHROPIC_API_KEY` - Claude API key
- `OPENAI_API_KEY` - OpenAI API key (alternative)

### Frontend Configuration

The frontend proxies API requests to the backend. Configuration is in `vite.config.js`.

## Approval Levels

| Level | Planning | Delegation | Doc Access | File Ops |
|-------|----------|------------|------------|----------|
| High | Yes | Yes | Yes | Yes |
| Moderate | Yes | Yes | No | Yes |
| Minimal | No | No | No | Yes |

## Risk Categories

The system analyzes documents for:

1. **Contractual Risks** - Breaches, unfavorable terms
2. **Compliance Risks** - Regulatory violations
3. **IP Risks** - Intellectual property issues
4. **Liability Risks** - Indemnification, warranties
5. **Financial Risks** - Payment terms, penalties
6. **Operational Risks** - Deadlines, deliverables
7. **Reputational Risks** - Confidentiality breaches

## Troubleshooting

### Backend Issues

**Port 8000 in use**:
```bash
lsof -i :8000
kill -9 <PID>
```

**Module not found**:
```bash
pip install -r requirements.txt
```

### Frontend Issues

**Port 5173 in use**:
```bash
lsof -i :5173
kill -9 <PID>
```

**Build errors**:
```bash
rm -rf node_modules
npm install
```

### API Connection Issues

Ensure the backend is running before starting the frontend.

## Production Deployment

For production deployment:

1. Build the frontend:
   ```bash
   cd frontend && npm run build
   ```

2. Serve the built frontend with the backend or a reverse proxy

3. Configure environment variables for production

4. Use a process manager like PM2 or systemd

5. Set up HTTPS with a reverse proxy (nginx, caddy)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

See the main project LICENSE file.
