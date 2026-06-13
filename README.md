# Hermes Agent OS - Backend Core Boilerplate

This repository contains the backend core engine for the **Hermes Agent Operating System (Agent OS)**. It is built as a high-performance, asynchronous web service responsible for orchestration, memory, telemetry tracking, and sandboxed tool execution.

## Technology Stack
- **Core Framework**: Python 3.11+ with FastAPI.
- **Database (Dual-mode)**: Local SQLite (default for development) with a direct switch to Google Cloud Firestore (Firebase).
- **Semantic Memory**: ChromaDB running in-process locally.
- **LLM Inference**: Ollama running locally (default model `gemma:2b` or `llama3`) or cloud provider APIs.
- **WebSocket Streaming**: Real-time resource metrics tracking & token-by-token reasoning output.
- **Security Sandboxing**: Local restricted subprocess execution with execution timeouts and safety filters.

---

## Directory Structure (Hexagonal/Clean Architecture)
```
d:/pry/osagentico/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI app entry point & lifespan controls
│   ├── config.py              # Configuration via Pydantic Settings
│   ├── core/                  # Domain Core Layer (Business models & interfaces)
│   │   ├── __init__.py
│   │   ├── models.py          # Pydantic Schemas (Workspace, Agent, Tool, Session, Log)
│   │   ├── exceptions.py      # Domain custom exceptions
│   │   └── security.py        # Safe execution constraints & Sandbox interface
│   ├── services/              # Application Logic Layer (Use Cases)
│   │   ├── __init__.py
│   │   ├── orchestrator.py    # ReAct agent reasoning & execution engine
│   │   ├── memory.py          # Semantic memory indexing helper
│   │   ├── telemetry.py       # Metrics publisher & WebSocket manager
│   │   └── sandbox.py         # Subprocess execution sandbox
│   ├── infrastructure/        # Infrastructure Adapters (Drivers)
│   │   ├── __init__.py
│   │   ├── database.py        # SQLite Database & Firestore Database clients
│   │   └── vectordb.py        # ChromaDB Vector client
│   └── api/                   # API Adapters (Controllers)
│       ├── __init__.py
│       ├── deps.py            # API dependencies injection
│       └── v1/
│           ├── __init__.py
│           ├── agent.py       # HTTP POST /api/v1/agent/orchestrate
│           ├── tools.py       # HTTP PUT /api/v1/tools/{tool_id}/toggle
│           └── telemetry.py   # WebSocket endpoints (/ws/telemetry, /ws/session/{id})
├── Dockerfile                 # Contained build setup
├── docker-compose.yml         # Local stack deployment with Ollama
├── requirements.txt           # Python dependencies
├── test_local_agent.py        # Independent API & WebSocket test script
└── README.md                  # Documentation
```

---

## Getting Started (Local Development)

### 1. Prerequisite (Ollama)
Ensure you have Ollama running locally on port `11434` with the default model pulled:
```bash
ollama pull gemma:2b
```

### 2. Local Setup
```bash
# Initialize virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Verification Tests
We have created an automated test script that runs FastAPI in test mode to assert health, database seeding, tool toggles, WebSocket metrics, and ReAct loops:
```bash
python test_local_agent.py
```

### 4. Run the Dev Server
Launch the FastAPI server:
```bash
uvicorn app.main:app --reload --port 8000
```
- Interactive API Swagger docs will be available at: http://127.0.0.1:8000/docs
- Health check endpoint: http://127.0.0.1:8000/health

### 5. Running with Docker Compose
If you prefer running the stack (FastAPI + Ollama) containerized:
```bash
docker-compose up --build
```

---

## Core Modules & APIs

### 1. Tool Toggling
- **Endpoint**: `PUT /api/v1/tools/{tool_id}/toggle`
- **Description**: Dynamically toggles tool availability (`is_active: true/false`) in the database.

### 2. ReAct Agent Orchestrator
- **Endpoint**: `POST /api/v1/agent/orchestrate`
- **Payload**:
  ```json
  {
    "agent_id": "hermes_coder",
    "query": "Create a file named hello.py inside the sandbox and execute it.",
    "workspace_id": "default_workspace"
  }
  ```
- **Output**: Streams reasoning tokens using a Server-Sent Events (SSE) stream (`text/event-stream`).
- **Traceability**: In parallel, the orchestrator logs every planning step, tool execution, observation outcome, latency, and token consumption to the database and streams state updates to the WebSocket.

### 3. WebSocket Streams
- **General Telemetry**: `ws://localhost:8000/ws/telemetry`
  - Broadcasts CPU, RAM, Disk utilization, and Status every 2 seconds.
- **Session Output Streaming**: `ws://localhost:8000/ws/session/{session_id}`
  - Streams detailed reasoning step traces and tokens to client connections for the specified session.
