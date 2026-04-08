from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlmodel import Session
import json
import redis
from src.backend.core.config import settings
from src.backend.models.schema import FileEvent

router = APIRouter()
redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

class ConnectionManager:
    """Manages active WebSockets ensuring secure connections and memory cleanup on disconnect."""
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, device_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[device_id] = websocket

    def disconnect(self, device_id: str):
        if device_id in self.active_connections:
            del self.active_connections[device_id]

manager = ConnectionManager()

@router.websocket("/ws/agent/{device_id}")
async def agent_log_stream(websocket: WebSocket, device_id: str):
    """
    Subscribes a device into a live socket stream. Local agents dispatch JSON events
    (e.g., File Moved) through here, which are then passed into Redis and SQLite.
    """
    await manager.connect(device_id, websocket)
    try:
        while True:
            # Agent streams payload: {"filename": "x", "source": "y", "dest": "z"}
            data = await websocket.receive_text()
            log_data = json.loads(data)
            
            # Asynchronous persistence block (simulated directly onto SQLModel session)
            with Session(engine) as session:
                new_event = FileEvent(
                    device_id=device_id,
                    filename=log_data["filename"],
                    source_path=log_data["source"],
                    dest_path=log_data["dest"]
                )
                session.add(new_event)
                session.commit()
            
            # Broadcast the live event to Redis Pub/Sub so web dashboards can react
            redis_client.publish(f"user_events_channel", json.dumps(log_data))
            
    except WebSocketDisconnect:
        manager.disconnect(device_id)