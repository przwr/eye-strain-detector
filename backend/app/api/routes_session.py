"""REST API: session control + history."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as OrmSession

from app.db import crud
from app.db.database import get_db
from app.services.session_manager import manager

router = APIRouter(prefix="/api", tags=["sessions"])


@router.post("/session/start")
def start_session():
    try:
        sid = manager.start()
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"Could not start monitoring: {e}")
    return {"session_id": sid, "running": True}


@router.post("/session/stop")
def stop_session():
    return {"session_id": manager.stop(), "running": False}


@router.post("/session/calibrate")
def calibrate():
    manager.calibrate()
    return {"ok": True}


@router.get("/session/status")
def status():
    return {"running": manager.running, "session_id": manager.session_id}


@router.get("/sessions")
def list_sessions(db: OrmSession = Depends(get_db)):
    return crud.list_sessions(db)


@router.get("/sessions/{session_id}")
def get_session(session_id: int, db: OrmSession = Depends(get_db)):
    s = crud.get_session_summary(db, session_id)
    if not s:
        raise HTTPException(404, "Session not found")
    return s
