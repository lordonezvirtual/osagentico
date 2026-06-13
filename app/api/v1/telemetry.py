from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.telemetry import telemetry_manager

router = APIRouter()

@router.websocket("/telemetry")
async def system_telemetry_ws(websocket: WebSocket):
    """
    WebSocket endpoint that streams system health metrics (CPU, RAM, Disk load)
    to the frontend in real time.
    """
    await telemetry_manager.connect_system(websocket)
    try:
        # Keep connection open and listen for any incoming client messages (e.g. pings)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        telemetry_manager.disconnect_system(websocket)
    except Exception:
        telemetry_manager.disconnect_system(websocket)


@router.websocket("/session/{session_id}")
async def session_stream_ws(session_id: str, websocket: WebSocket):
    """
    WebSocket endpoint that streams reasoning tokens and step details
    for a specific agent execution session.
    """
    await telemetry_manager.connect_session(session_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        telemetry_manager.disconnect_session(session_id, websocket)
    except Exception:
        telemetry_manager.disconnect_session(session_id, websocket)
