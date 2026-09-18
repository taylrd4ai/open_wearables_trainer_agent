"""Polar biometric provider stub."""

from typing import Any, Dict

from app.config import settings
from app.services.providers.base import BaseBiometricProvider


class PolarProvider(BaseBiometricProvider):
    """Polar integration. Returns mock data when credentials missing."""

    def __init__(self) -> None:
        self.client_id = settings.POLAR_CLIENT_ID
        self.client_secret = settings.POLAR_CLIENT_SECRET
        self.is_configured = bool(self.client_id and self.client_secret)

    async def fetch_data(self, user_id: str) -> Dict[str, Any]:
        """Fetch Polar nightly recharge / training data or return mock."""
        if not self.is_configured:
            return self._mock_data()
        return self._mock_data()

    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Polar data to standard schema."""
        return {
            "recovery_percent": raw_data.get("nightly_recharge", 70.0),
            "hrv": raw_data.get("ans_charge", 50.0),
            "strain_score": raw_data.get("cardio_load", 3.5),
            "vo2_max_estimate": raw_data.get("fitness_level", 44.0),
            "training_load": raw_data.get("cardio_load", 3.5) * 100,
            "source_provider": "polar",
        }

    def _mock_data(self) -> Dict[str, Any]:
        """Return synthetic Polar-style data."""
        return {
            "nightly_recharge": 73.0,
            "ans_charge": 55.2,
            "cardio_load": 3.8,
            "fitness_level": 46.0,
        }
