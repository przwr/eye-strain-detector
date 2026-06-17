"""ORM tables: a Session and its per-interval MetricSample rows."""
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base


class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    samples = relationship("MetricSample", back_populates="session")


class MetricSample(Base):
    __tablename__ = "metric_samples"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    ts = Column(Float)
    blink_rate = Column(Float)
    perclos = Column(Float)
    proximity = Column(String)
    strain = Column(String)
    session = relationship("Session", back_populates="samples")
