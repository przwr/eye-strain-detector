"""FastAPI application entry point."""
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import routes_session, routes_ws
from app.db.database import init_db

app = FastAPI(title="Eye Strain Detection System", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    # The dashboard is also hosted on Netlify; the backend stays on the
    # user's machine because it needs the local webcam.
    allow_origin_regex=r"https://.*\.netlify\.app",
    allow_methods=["*"],
    allow_headers=["*"],
    # Chrome sends a private-network preflight when a public site (the
    # Netlify-hosted dashboard) talks to localhost; reject it and the
    # browser reports net::ERR_FAILED.
    allow_private_network=True,
)


@app.on_event("startup")
def _startup() -> None:
    init_db()
    # Start monitoring with the service; the dashboard is only a viewer.
    # Non-fatal: a busy/missing camera must not prevent the API from booting.
    from app.services.session_manager import manager
    try:
        manager.start()
    except Exception as e:  # noqa: BLE001
        logging.getLogger(__name__).warning("Auto-start monitoring failed: %s", e)


@app.on_event("shutdown")
def _shutdown() -> None:
    # Close the open session row so restarts don't leave phantom "open" sessions.
    # stop() is a no-op when nothing is open (also covers a failed camera start).
    from app.services.session_manager import manager
    manager.stop()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


app.include_router(routes_session.router)
app.include_router(routes_ws.router)

# Serve the built dashboard from the backend itself (same origin — no CORS
# or local-network restrictions). Build with: cd frontend && npm run build
_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if _dist.is_dir():
    app.mount("/", StaticFiles(directory=_dist, html=True), name="dashboard")
