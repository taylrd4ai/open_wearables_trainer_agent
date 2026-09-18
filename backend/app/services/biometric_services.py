"""Biometric data aggregation service."""

from typing import Any, Dict, List

from app.config import settings
from app.services.providers.whoop import WhoopProvider
from app.services.providers.garmin import GarminProvider
from app.services.providers.oura import OuraProvider
from app.services.providers.polar import PolarProvider


def _get_configured_providers() -> List[Any]:
    """Return list of configured biometric providers."""
    providers = []
    whoop = WhoopProvider()
    garmin = GarminProvider()
    oura = OuraProvider()
    polar = PolarProvider()

    if whoop.is_configured:
        providers.append(whoop)
    if garmin.is_configured:
        providers.append(garmin)
    if oura.is_configured:
        providers.append(oura)
    if polar.is_configured:
        providers.append(polar)

    return providers


def _generate_mock_summary(user_id: str) -> Dict[str, Any]:
    """Generate synthetic biometric summary when no providers are configured."""
    return {
        "user_id": user_id,
        "recovery_percent": 72.0,
        "hrv": 58.5,
        "strain_score": 12.5,
        "vo2_max_estimate": 45.0,
        "training_load": 350.0,
        "source_provider": "mock",
        "is_mock": True,
    }


async def get_biometric_summary(user_id: str) -> Dict[str, Any]:
    """Get aggregated biometric summary for a user.

    Falls back to mock data if no API keys are configured.
    """
    providers = _get_configured_providers()

    if not providers:
        return _generate_mock_summary(user_id)

    summaries: List[Dict[str, Any]] = []
    for provider in providers:
        try:
            raw = await provider.fetch_data(user_id)
            normalized = provider.normalize(raw)
            summaries.append(normalized)
        except Exception:
            continue

    if not summaries:
        return _generate_mock_summary(user_id)

    # Average across providers
    result: Dict[str, Any] = {"user_id": user_id, "is_mock": False}
    numeric_keys = [
        "recovery_percent", "hrv", "strain_score",
        "vo2_max_estimate", "training_load",
    ]
    for key in numeric_keys:
        values = [s[key] for s in summaries if s.get(key) is not None]
        result[key] = sum(values) / len(values) if values else None

    result["source_provider"] = ",".join(
        s.get("source_provider", "unknown") for s in summaries
    )
    return result
