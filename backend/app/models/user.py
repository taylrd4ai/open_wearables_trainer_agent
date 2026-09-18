"""User model."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """User account model."""

    __tablename__ = "users"

    id: uuid.UUID = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: str = Column(String(255), unique=True, nullable=False, index=True)
    created_at: datetime = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    workout_sessions = relationship("WorkoutSession", back_populates="user")
    biometric_data = relationship("BiometricData", back_populates="user")

    def to_dict(self) -> dict:
        """Serialize user to dictionary."""
        return {
            "id": str(self.id),
            "email": self.email,
            "created_at": self.created_at.isoformat(),
        }
