"""Oura Ring biometric provider stub."""

from typing import Any, Dict

from app.config import settings
from app.services.providers.base import BaseBiometricProvider


class OuraProvider(BaseBiometricProvider):
    """Oura Ring integration. Returns mock data when credentials missing."""

    def __init__(self) -> None:
        self.client_id = settings.OURA_CLIENT_ID
        self.client_secret = settings.OURA_CLIENT_SECRET
        self.is_configured = bool(self.client_id and self.client_secret)

    async def fetch_data(self, user_id: str) -> Dict[str, Any]:
        """Fetch Oura readiness/sleep data or return mock."""
        if not self.is_configured:
            return self._mock_data()
        return self._mock_data()

    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Oura data to standard schema."""
        return {
            "recovery_percent": raw_data.get("readiness_score", 75.0),
            "hrv": raw_data.get("average_hrv", 58.0),
            "strain_score": raw_data.get("activity_score", 60.0) / 5,
            "vo2_max_estimate": None,
            "training_load": raw_data.get("activity_score", 60.0),
            "source_provider": "oura",
        }

    def _mock_data(self) -> Dict[str, Any]:
        """Return synthetic Oura-style data."""
        return {
            "readiness_score": 78.0,
            "average_hrv": 61.5,
            "activity_score": 65.0,
            "sleep_score": 82.0,
        }
