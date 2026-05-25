from fastapi import WebSocket, WebSocketDisconnect, Depends
from fastapi.routing import APIRouter
import json
import asyncio
from typing import Set
from src.api.utils import verify_token
from src.db.connection import get_db
from src.models import User, Scan
from sqlalchemy.orm import Session

router = APIRouter()

# Store active WebSocket connections per scan
active_connections: dict[str, Set[WebSocket]] = {}

class ConnectionManager:
    """Manage WebSocket connections for real-time updates."""

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, scan_id: str, websocket: WebSocket):
        """Add a new WebSocket connection."""
        await websocket.accept()
        if scan_id not in self.active_connections:
            self.active_connections[scan_id] = []
        self.active_connections[scan_id].append(websocket)

    def disconnect(self, scan_id: str, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if scan_id in self.active_connections:
            self.active_connections[scan_id].remove(websocket)
            if not self.active_connections[scan_id]:
                del self.active_connections[scan_id]

    async def broadcast(self, scan_id: str, message: dict):
        """Send message to all connections for a scan."""
        if scan_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[scan_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    disconnected.append(connection)

            # Remove disconnected clients
            for connection in disconnected:
                self.disconnect(scan_id, connection)

manager = ConnectionManager()

@router.websocket("/ws/scan/{scan_id}")
async def websocket_endpoint(scan_id: str, websocket: WebSocket):
    """WebSocket endpoint for real-time scan updates."""

    await manager.connect(scan_id, websocket)
    try:
        while True:
            # Wait for messages from client (keep-alive)
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(scan_id, websocket)
    except Exception as e:
        manager.disconnect(scan_id, websocket)

async def send_scan_progress(
    scan_id: str,
    stage: str,
    progress: int,
    message: str
):
    """Send progress update to all connected clients."""
    await manager.broadcast(scan_id, {
        "type": "progress",
        "stage": stage,
        "progress": progress,
        "message": message
    })

async def send_scan_complete(
    scan_id: str,
    results: dict
):
    """Send completion message to all connected clients."""
    await manager.broadcast(scan_id, {
        "type": "complete",
        "results": results
    })

async def send_scan_error(
    scan_id: str,
    error: str
):
    """Send error message to all connected clients."""
    await manager.broadcast(scan_id, {
        "type": "error",
        "error": error
    })
