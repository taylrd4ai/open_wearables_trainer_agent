"""WHOOP biometric provider stub."""

from typing import Any, Dict

from app.config import settings
from app.services.providers.base import BaseBiometricProvider


class WhoopProvider(BaseBiometricProvider):
    """WHOOP strap integration. Returns mock data when credentials missing."""

    def __init__(self) -> None:
        self.client_id = settings.WHOOP_CLIENT_ID
        self.client_secret = settings.WHOOP_CLIENT_SECRET
        self.is_configured = bool(self.client_id and self.client_secret)

    async def fetch_data(self, user_id: str) -> Dict[str, Any]:
        """Fetch WHOOP recovery/strain data or return mock."""
        if not self.is_configured:
            return self._mock_data()
        # Real implementation would call WHOOP OAuth API here
        return self._mock_data()

    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize WHOOP data to standard schema."""
        return {
            "recovery_percent": raw_data.get("recovery", 65.0),
            "hrv": raw_data.get("hrv_ms", 55.0),
            "strain_score": raw_data.get("strain", 12.0),
            "vo2_max_estimate": None,
            "training_load": raw_data.get("strain", 12.0) * 10,
            "source_provider": "whoop",
        }

    def _mock_data(self) -> Dict[str, Any]:
        """Return synthetic WHOOP-style data."""
        return {
            "recovery": 72.5,
            "hrv_ms": 62.3,
            "strain": 14.2,
            "sleep_hours": 7.8,
        }
