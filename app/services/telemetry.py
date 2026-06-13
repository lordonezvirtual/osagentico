import asyncio
import json
import logging
from typing import List, Dict, Any, Set, Optional
from fastapi import WebSocket
import psutil

logger = logging.getLogger("telemetry")

class TelemetryManager:
    def __init__(self):
        # Active connections for general system telemetry
        self.system_connections: Set[WebSocket] = set()
        # Active connections mapped by session ID for granular agent streaming
        self.session_connections: Dict[str, Set[WebSocket]] = {}
        self.metrics_loop_task: Optional[asyncio.Task] = None

    async def connect_system(self, websocket: WebSocket):
        await websocket.accept()
        self.system_connections.add(websocket)
        logger.info(f"System telemetry socket connected. Total clients: {len(self.system_connections)}")
        try:
            initial_metrics = self.get_system_metrics()
            await websocket.send_text(json.dumps(initial_metrics))
        except Exception as e:
            logger.warning(f"Failed to send initial telemetry metrics: {e}")

    def disconnect_system(self, websocket: WebSocket):
        if websocket in self.system_connections:
            self.system_connections.remove(websocket)
            logger.info(f"System telemetry socket disconnected. Total clients: {len(self.system_connections)}")

    async def connect_session(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        if session_id not in self.session_connections:
            self.session_connections[session_id] = set()
        self.session_connections[session_id].add(websocket)
        logger.info(f"Session '{session_id}' streaming socket connected.")

    def disconnect_session(self, session_id: str, websocket: WebSocket):
        if session_id in self.session_connections and websocket in self.session_connections[session_id]:
            self.session_connections[session_id].remove(websocket)
            if not self.session_connections[session_id]:
                del self.session_connections[session_id]
            logger.info(f"Session '{session_id}' streaming socket disconnected.")

    async def broadcast_system(self, data: Dict[str, Any]):
        if not self.system_connections:
            return
        
        # Avoid mutating set during iteration
        clients = list(self.system_connections)
        payload = json.dumps(data)
        
        for client in clients:
            try:
                await client.send_text(payload)
            except Exception as e:
                logger.warning(f"Error broadcasting to client, removing: {e}")
                self.disconnect_system(client)

    async def stream_agent_event(self, session_id: str, step: str, message: str, extra: Dict[str, Any] = None):
        """Send a ReAct trace event or LLM token stream to clients listening to a specific session."""
        if session_id not in self.session_connections:
            return

        payload = {
            "session_id": session_id,
            "step": step,  # planning, execution, waiting, token, output, error
            "message": message,
            **(extra or {})
        }
        
        clients = list(self.session_connections[session_id])
        json_data = json.dumps(payload)
        
        for client in clients:
            try:
                await client.send_text(json_data)
            except Exception as e:
                logger.warning(f"Error streaming session {session_id} event: {e}")
                self.disconnect_session(session_id, client)

    def get_system_metrics(self) -> Dict[str, Any]:
        """Fetches local resource statistics."""
        virtual_mem = psutil.virtual_memory()
        disk_usage = psutil.disk_usage('/')
        
        return {
            "type": "system_metrics",
            "cpu_percent": psutil.cpu_percent(interval=None),
            "ram_percent": virtual_mem.percent,
            "ram_used_gb": round(virtual_mem.used / (1024**3), 2),
            "ram_total_gb": round(virtual_mem.total / (1024**3), 2),
            "disk_percent": disk_usage.percent,
            "disk_free_gb": round(disk_usage.free / (1024**3), 2),
            "system_status": "healthy" if psutil.cpu_percent(interval=None) < 90 else "high_load"
        }

    async def start_metrics_loop(self):
        """Asynchronous background loop to broadcast health statistics."""
        if self.metrics_loop_task is not None:
            return
        
        async def loop():
            logger.info("Telemetry system metrics loop started.")
            while True:
                try:
                    metrics = self.get_system_metrics()
                    await self.broadcast_system(metrics)
                except Exception as e:
                    logger.error(f"Error in telemetry broadcast loop: {e}")
                await asyncio.sleep(2.0)  # Broadcast interval

        self.metrics_loop_task = asyncio.create_task(loop())

    def stop_metrics_loop(self):
        if self.metrics_loop_task:
            self.metrics_loop_task.cancel()
            self.metrics_loop_task = None
            logger.info("Telemetry system metrics loop stopped.")


# Global Telemetry Instance
telemetry_manager = TelemetryManager()
