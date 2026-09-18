"""ExerciseEntry model."""

import uuid

from sqlalchemy import Column, Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class ExerciseEntry(Base):
    """Individual exercise set entry within a workout session."""

    __tablename__ = "exercise_entries"

    id: uuid.UUID = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: uuid.UUID = Column(
        UUID(as_uuid=True),
        ForeignKey("workout_sessions.id"),
        nullable=False,
        index=True,
    )
    exercise_id: int = Column(Integer, nullable=False)
    set_number: int = Column(Integer, nullable=False)
    reps: int = Column(Integer, nullable=False)
    weight: float = Column(Float, nullable=False, default=0.0)
    rpe: int = Column(Integer, nullable=True)

    session = relationship("WorkoutSession", back_populates="exercise_entries")

    def to_dict(self) -> dict:
        """Serialize exercise entry to dictionary."""
        return {
            "id": str(self.id),
            "session_id": str(self.session_id),
            "exercise_id": self.exercise_id,
            "set_number": self.set_number,
            "reps": self.reps,
            "weight": self.weight,
            "rpe": self.rpe,
        }
