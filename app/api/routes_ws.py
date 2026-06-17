"""WebSocket: streams the latest metrics + annotated frame at ~15 fps."""
import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.session_manager import manager

router = APIRouter()


@router.websocket("/ws/live")
async def ws_live(ws: WebSocket):
    await ws.accept()
    last_ts = 0.0
    try:
        while True:
            latest = manager.get_latest()
            if latest and latest["ts"] != last_ts:
                last_ts = latest["ts"]
                await ws.send_json(latest)
            await asyncio.sleep(1 / 15)
    except WebSocketDisconnect:
        pass
