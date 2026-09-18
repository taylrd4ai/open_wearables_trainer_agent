"""BiometricData model."""

import uuid
from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class BiometricData(Base):
    """Biometric data from wearable devices."""

    __tablename__ = "biometric_data"

    id: uuid.UUID = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    date: date = Column(Date, nullable=False, default=date.today)
    recovery_percent: float | None = Column(Float, nullable=True)
    hrv: float | None = Column(Float, nullable=True)
    strain_score: float | None = Column(Float, nullable=True)
    vo2_max_estimate: float | None = Column(Float, nullable=True)
    training_load: float | None = Column(Float, nullable=True)
    source_provider: str = Column(String(50), nullable=False, default="mock")
    created_at: datetime = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    user = relationship("User", back_populates="biometric_data")

    def to_dict(self) -> dict:
        """Serialize biometric data to dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "date": self.date.isoformat(),
            "recovery_percent": self.recovery_percent,
            "hrv": self.hrv,
            "strain_score": self.strain_score,
            "vo2_max_estimate": self.vo2_max_estimate,
            "training_load": self.training_load,
            "source_provider": self.source_provider,
            "created_at": self.created_at.isoformat(),
        }
