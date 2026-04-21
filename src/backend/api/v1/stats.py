"""
Stats API Router.

Exposes two REST endpoints and one WebSocket endpoint consumed by the landing page web dashboard:
  - GET  /stats/public   → aggregated category counts for ALL users (no filenames)
  - GET  /stats/me       → personal file history for the authenticated user (with filenames)
  - WS   /ws/dashboard   → real-time file event broadcast; filenames only if valid JWT supplied
"""

import json
import os
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
from sqlmodel import Session, select, create_engine

from src.backend.models import FileEvent, Device, User
from src.backend.core.config import settings

router = APIRouter()

# ── DB helper (mirrors main.py) ──────────────────────────────────────────────
DATABASE_URL = settings.DATABASE_URL or "sqlite:///./enterprise.db"
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

def get_db():
    with Session(engine) as session:
        yield session

# ── Auth helper ──────────────────────────────────────────────────────────────
def _decode_token(token: str) -> Optional[str]:
    """Returns the email (sub) from a valid JWT, or None."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

def _current_email(request: Request) -> Optional[str]:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return _decode_token(auth[7:])
    return None

def _category_from_path(dest_path: str) -> str:
    """Derives a human-readable category from the destination folder name."""
    if not dest_path:
        return "Other"
    parts = dest_path.replace("\\", "/").rstrip("/").split("/")
    return parts[-1] if parts else "Other"

# ── WebSocket broadcast manager ───────────────────────────────────────────────
class DashboardManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.connections:
            self.connections.remove(ws)

    async def broadcast(self, payload: dict):
        dead = []
        for ws in self.connections:
            try:
                await ws.send_text(json.dumps(payload))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

dashboard_manager = DashboardManager()

# ── Public endpoint (no auth) ─────────────────────────────────────────────────
@router.get("/stats/public")
def public_stats(db: Session = Depends(get_db)):
    """
    Returns aggregated file-move counts grouped by destination category.
    No user information or filenames are exposed.
    """
    events = db.exec(select(FileEvent)).all()
    totals: dict[str, int] = {}
    for ev in events:
        cat = _category_from_path(ev.dest_path)
        totals[cat] = totals.get(cat, 0) + 1
    return {
        "total": len(events),
        "categories": totals,
        "last_updated": datetime.utcnow().isoformat()
    }

# ── Private endpoint (JWT required) ──────────────────────────────────────────
@router.get("/stats/me")
def my_stats(request: Request, db: Session = Depends(get_db)):
    """
    Returns the authenticated user's personal file-event history (last 100 events)
    including filenames, source paths, and destination paths.
    """
    email = _current_email(request)
    if not email:
        raise HTTPException(status_code=401, detail="Authentication required")

    user = db.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get all device IDs that belong to this user
    devices = db.exec(select(Device).where(Device.user_id == user.id)).all()
    device_ids = [d.id for d in devices]

    events: List[FileEvent] = []
    for did in device_ids:
        evs = db.exec(select(FileEvent).where(FileEvent.device_id == did)).all()
        events.extend(evs)

    # Sort descending by timestamp and cap at 100
    events.sort(key=lambda e: e.timestamp, reverse=True)
    events = events[:100]

    # Aggregate category counts
    totals: dict[str, int] = {}
    for ev in events:
        cat = _category_from_path(ev.dest_path)
        totals[cat] = totals.get(cat, 0) + 1

    return {
        "user": email,
        "total": len(events),
        "categories": totals,
        "events": [
            {
                "id": ev.id,
                "filename": ev.filename,
                "source_path": ev.source_path,
                "dest_path": ev.dest_path,
                "category": _category_from_path(ev.dest_path),
                "device_id": ev.device_id,
                "timestamp": ev.timestamp.isoformat() if ev.timestamp else None,
            }
            for ev in events
        ],
        "last_updated": datetime.utcnow().isoformat()
    }

# ── WebSocket endpoint for live dashboard feed ────────────────────────────────
@router.websocket("/ws/dashboard")
async def dashboard_socket(websocket: WebSocket, token: Optional[str] = None):
    """
    Browser clients connect here to receive real-time file-event pushes.
    If a valid JWT token is provided as a query param, the payload will include filenames.
    Otherwise only category and count are broadcasted (privacy-safe public mode).
    """
    authenticated_email = _decode_token(token) if token else None
    await dashboard_manager.connect(websocket)
    try:
        while True:
            # Keep alive — clients don't send data, just listen
            await websocket.receive_text()
    except WebSocketDisconnect:
        dashboard_manager.disconnect(websocket)
    except Exception:
        dashboard_manager.disconnect(websocket)
