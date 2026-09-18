"""Garmin biometric provider stub."""

from typing import Any, Dict

from app.config import settings
from app.services.providers.base import BaseBiometricProvider


class GarminProvider(BaseBiometricProvider):
    """Garmin Connect integration. Returns mock data when credentials missing."""

    def __init__(self) -> None:
        self.client_id = settings.GARMIN_CLIENT_ID
        self.client_secret = settings.GARMIN_CLIENT_SECRET
        self.is_configured = bool(self.client_id and self.client_secret)

    async def fetch_data(self, user_id: str) -> Dict[str, Any]:
        """Fetch Garmin body battery / training data or return mock."""
        if not self.is_configured:
            return self._mock_data()
        return self._mock_data()

    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Garmin data to standard schema."""
        return {
            "recovery_percent": raw_data.get("body_battery", 70.0),
            "hrv": raw_data.get("hrv_status", 48.0),
            "strain_score": raw_data.get("training_load", 350.0) / 30,
            "vo2_max_estimate": raw_data.get("vo2_max", 45.0),
            "training_load": raw_data.get("training_load", 350.0),
            "source_provider": "garmin",
        }

    def _mock_data(self) -> Dict[str, Any]:
        """Return synthetic Garmin-style data."""
        return {
            "body_battery": 68.0,
            "hrv_status": 52.1,
            "training_load": 380.0,
            "vo2_max": 47.2,
        }
