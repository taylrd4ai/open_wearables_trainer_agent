"""Abstract base class for biometric data providers."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseBiometricProvider(ABC):
    """Abstract base for wearable device integrations."""

    @abstractmethod
    async def fetch_data(self, user_id: str) -> Dict[str, Any]:
        """Fetch raw biometric data from the provider API."""
        ...

    @abstractmethod
    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize raw provider data into standard schema."""
        ...

    def _validate_heart_rate(self, hr: float) -> float:
        """Validate heart rate is within 30-220 bpm range."""
        if not (30 <= hr <= 220):
            raise ValueError(f"Heart rate {hr} outside valid range 30-220 bpm")
        return hr
