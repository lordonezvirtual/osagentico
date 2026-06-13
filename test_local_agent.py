import os
import json
import sqlite3
import asyncio
from fastapi.testclient import TestClient

# Import app components
from app.main import app
from app.config import settings
from app.infrastructure.database import get_db
from app.core.models import Workspace, Agent

client = TestClient(app)

def setup_module():
    # Force local mode for testing
    settings.DB_MODE = "local"
    # Ensure any previous sqlite test DB is cleaned up
    db_path = settings.SQLITE_URL.replace("sqlite:///", "")
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass
    # Force re-initialization of tables
    db = get_db()
    if hasattr(db, "_init_db"):
        db._init_db()
    
    # Seed default workspace and agent for tests
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    if loop.is_running():
        # Fallback if loop is already running (unlikely for sync setup_module)
        asyncio.ensure_future(db.save_workspace(Workspace(id="default_workspace", name="Test Workspace", config={})))
        asyncio.ensure_future(db.save_agent(Agent(
            id="hermes_coder",
            name="Hermes Coder",
            system_prompt="Test prompt",
            model_name="gemma:2b",
            provider="ollama",
            temperature=0.1,
            tool_ids=["code_execution", "terminal", "file_operations", "web_search"],
            is_active=True
        )))
    else:
        loop.run_until_complete(db.save_workspace(Workspace(id="default_workspace", name="Test Workspace", config={})))
        loop.run_until_complete(db.save_agent(Agent(
            id="hermes_coder",
            name="Hermes Coder",
            system_prompt="Test prompt",
            model_name="gemma:2b",
            provider="ollama",
            temperature=0.1,
            tool_ids=["code_execution", "terminal", "file_operations", "web_search"],
            is_active=True
        )))

def test_health():
    """Verify health check returns standard online status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["db_mode"] == "local"

def test_toggle_tool():
    """Verify endpoint toggles tool active state in SQLite database."""
    # First get, to ensure seed ran
    db = get_db()
    
    # Enable web_search (it defaults to active)
    response = client.put("/api/v1/tools/web_search/toggle")
    if response.status_code != 200:
        print("Toggle tool failure response:", response.status_code, response.text)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "web_search"
    assert data["is_active"] is False  # Toggled from True to False

    # Toggle it back
    response = client.put("/api/v1/tools/web_search/toggle")
    assert response.status_code == 200
    assert response.json()["is_active"] is True

def test_orchestrate_simulation():
    """Verify the ReAct loop starts, executes steps, logs to db, and streams tokens."""
    payload = {
        "agent_id": "hermes_coder",
        "query": "Write a python script",
        "workspace_id": "default_workspace"
    }
    
    # Trigger orchestration (streams response)
    response = client.post("/api/v1/agent/orchestrate", json=payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    
    # Read streamed chunks
    chunks = []
    for chunk in response.iter_bytes():
        if chunk:
            chunks.append(chunk.decode("utf-8"))
    
    full_output = "".join(chunks)
    if "Thought:" not in full_output or "Final Answer:" not in full_output:
        print("Orchestration simulation output:", repr(full_output))
    assert len(full_output) > 0
    assert "Thought:" in full_output
    assert "Final Answer:" in full_output

def test_websocket_telemetry():
    """Verify system health metrics streaming over websocket."""
    with client.websocket_connect("/ws/telemetry") as websocket:
        # Receive first metrics packet broadcast
        data = websocket.receive_text()
        metrics = json.loads(data)
        
        assert metrics["type"] == "system_metrics"
        assert "cpu_percent" in metrics
        assert "ram_percent" in metrics
        assert "system_status" in metrics

def test_service_manager():
    """Verify Service Manager status listing, individual deployments, and global lifecycle toggles."""
    # 1. Get services list
    response = client.get("/api/v1/services")
    assert response.status_code == 200
    services = response.json()
    assert len(services) == 5
    
    # Assert initial states (desktop is active by default in fallback, others inactive)
    desktop = next(s for s in services if s["id"] == "hermes-desktop")
    n8n = next(s for s in services if s["id"] == "n8n")
    assert desktop["status"] == "active"
    assert n8n["status"] == "inactive"

    # 2. Deploy individual service (n8n)
    response = client.post("/api/v1/services/n8n/deploy")
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Check state updated
    response = client.get("/api/v1/services")
    n8n = next(s for s in response.json() if s["id"] == "n8n")
    assert n8n["status"] == "active"

    # 3. Shutdown individual service (n8n)
    response = client.post("/api/v1/services/n8n/shutdown")
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Check state updated
    response = client.get("/api/v1/services")
    n8n = next(s for s in response.json() if s["id"] == "n8n")
    assert n8n["status"] == "inactive"

    # 4. Global Deploy All (Prender Todo)
    response = client.post("/api/v1/services/deploy-all")
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Check all active
    response = client.get("/api/v1/services")
    for s in response.json():
        assert s["status"] == "active"

    # 5. Global Shutdown All (Apagar Todo)
    response = client.post("/api/v1/services/shutdown-all")
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Check all inactive
    response = client.get("/api/v1/services")
    for s in response.json():
        assert s["status"] == "inactive"


if __name__ == "__main__":
    print("Running local endpoint verification tests...")
    setup_module()
    
    try:
        print("1. Testing Health Endpoint...")
        test_health()
        print("[OK] Health endpoint OK.")
        
        print("2. Testing Tool Toggle...")
        test_toggle_tool()
        print("[OK] Tool toggle OK.")
        
        print("3. Testing WebSocket Telemetry...")
        test_websocket_telemetry()
        print("[OK] WebSocket telemetry OK.")
        
        print("4. Testing ReAct Orchestration Stream...")
        test_orchestrate_simulation()
        print("[OK] ReAct Orchestration Stream OK.")

        print("5. Testing Service Manager Lifecycle...")
        test_service_manager()
        print("[OK] Service Manager Lifecycle OK.")
        
        print("\nAll verification tests completed successfully!")
    except Exception as e:
        print(f"\nVerification test failed: {e}")
        import traceback
        traceback.print_exc()
