"""WorkoutSession model."""

import uuid
from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.database import Base


class WorkoutSession(Base):
    """Workout session model tracking a complete training event."""

    __tablename__ = "workout_sessions"

    id: uuid.UUID = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    date: date = Column(Date, nullable=False, default=date.today)
    location: str = Column(String(100), nullable=False, default="gym")
    total_volume: float = Column(Float, nullable=False, default=0.0)
    rpe_avg: float = Column(Float, nullable=True)
    biometric_snapshot: dict | None = Column(JSONB, nullable=True)
    created_at: datetime = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    user = relationship("User", back_populates="workout_sessions")
    exercise_entries = relationship(
        "ExerciseEntry", back_populates="session", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        """Serialize workout session to dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "date": self.date.isoformat(),
            "location": self.location,
            "total_volume": self.total_volume,
            "rpe_avg": self.rpe_avg,
            "biometric_snapshot": self.biometric_snapshot,
            "created_at": self.created_at.isoformat(),
        }
