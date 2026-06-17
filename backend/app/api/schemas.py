"""Pydantic request/response models for the API."""
from pydantic import BaseModel


class LiveMetric(BaseModel):
    ts: float
    blink_rate: float
    perclos: float
    proximity: str
    strain: str


class SessionSummary(BaseModel):
    id: int
    started_at: float
    ended_at: float | None
    avg_blink_rate: float
    avg_perclos: float
    high_strain_minutes: float
