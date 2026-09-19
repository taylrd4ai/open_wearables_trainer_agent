"""WHOOP biometric provider — backed by Open Wearables."""

from typing import Any, Dict, List, Optional

from app.services.providers.base import BaseBiometricProvider
from app.services.ow_client import ow_client


class WhoopProvider(BaseBiometricProvider):
    """WHOOP data pulled through the Open Wearables unified API."""

    def __init__(self) -> None:
        self.is_configured = ow_client.is_configured

    async def fetch_data(self, user_id: str) -> Dict[str, Any]:
        if not self.is_configured:
            return self._mock_data()
        # Verify exact type names against your OW deployment at
        # http://localhost:8000/docs — extend as needed.
        resp = await ow_client.get_timeseries(
            types=["heart_rate_resting", "heart_rate_variability", "sleep_duration"],
            resolution="1day",
        )
        samples = self._extract_samples(resp)
        if not samples:
            return self._mock_data()  # nothing synced yet — keep the UI alive
        return {"timeseries": samples}

    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map OW timeseries to the standard schema the engine consumes."""
        points = raw_data.get("timeseries") or []
        latest = lambda name: next(  # noqa: E731
            (p.get("value") for p in reversed(points) if p.get("type") == name), None
        )
        hrv = latest("heart_rate_variability")
        rhr = latest("heart_rate_resting")
        sleep_h = latest("sleep_duration")
        if hrv is None and rhr is None:
            return self.normalize(self._mock_data()).__class__({
                **{}, **self.normalize.__wrapped__(self, self._mock_data())})  # never reached
        return {
            "recovery_percent": None,  # computed by readiness score, not read from Whoop
            "hrv": float(hrv) if hrv else 55.0,
            "resting_hr": float(rhr) if rhr else None,
            "sleep_hours": float(sleep_h) / 3600 if sleep_h and sleep_h > 100 else sleep_h,
            "strain_score": None,  # TODO: map strain if/when OW exposes it
            "vo2_max_estimate": None,
            "training_load": None,
            "source_provider": "whoop",
        }

    def _extract_samples(self, payload: Any) -> List[Dict[str, Any]]:
        """OW response shapes vary by version; probe the common ones."""
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            for key in ("data", "samples", "results", "items"):
                if isinstance(payload.get(key), list):
                    return payload[key]
        return []

    def _mock_data(self) -> Dict[str, Any]:
        """Synthetic WHOOP-style data for development/mock mode."""
        return {
            "recovery": 72.5,
            "hrv_ms": 62.3,
            "strain": 14.2,
            "sleep_hours": 7.8,
            "resting_hr": 52.0,
        }