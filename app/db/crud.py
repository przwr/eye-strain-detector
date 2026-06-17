"""Database queries: create/end sessions, append samples, build summaries."""
from datetime import datetime

from sqlalchemy.orm import Session as OrmSession

from app.db.models import MetricSample, Session


def create_session(db: OrmSession) -> Session:
    s = Session(started_at=datetime.utcnow())
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def end_session(db: OrmSession, session_id: int) -> None:
    s = db.get(Session, session_id)
    if s and s.ended_at is None:
        s.ended_at = datetime.utcnow()
        db.commit()


def add_sample(db: OrmSession, session_id: int, m, ts: float) -> None:
    db.add(MetricSample(
        session_id=session_id, ts=ts,
        blink_rate=m.blink_rate, perclos=m.perclos,
        proximity=m.proximity, strain=m.strain,
    ))
    db.commit()


def _summarize(db: OrmSession, s: Session, with_samples: bool = False) -> dict:
    samples = s.samples
    n = len(samples)
    avg_rate = sum(x.blink_rate for x in samples) / n if n else 0.0
    avg_perclos = sum(x.perclos for x in samples) / n if n else 0.0
    high_min = sum(1 for x in samples if x.strain == "high") / 60.0  # ~1 sample/sec
    duration = 0.0
    if s.ended_at:
        duration = (s.ended_at - s.started_at).total_seconds() / 60.0
    out = {
        "id": s.id,
        "started_at": s.started_at.isoformat() if s.started_at else None,
        "ended_at": s.ended_at.isoformat() if s.ended_at else None,
        "duration_min": round(duration, 1),
        "avg_blink_rate": round(avg_rate, 1),
        "avg_perclos": round(avg_perclos, 3),
        "high_strain_min": round(high_min, 1),
        "sample_count": n,
    }
    if with_samples:
        out["samples"] = [
            {"ts": x.ts, "blink_rate": x.blink_rate, "perclos": x.perclos, "strain": x.strain}
            for x in samples
        ]
    return out


def list_sessions(db: OrmSession) -> list[dict]:
    rows = db.query(Session).order_by(Session.started_at.desc()).all()
    return [_summarize(db, r) for r in rows]


def get_session_summary(db: OrmSession, session_id: int) -> dict | None:
    s = db.get(Session, session_id)
    return _summarize(db, s, with_samples=True) if s else None
