"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_session, routes_ws
from app.db.database import init_db

app = FastAPI(title="Eye Strain Detection System", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


app.include_router(routes_session.router)
app.include_router(routes_ws.router)
