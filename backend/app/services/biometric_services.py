"""Biometric data aggregation service."""

from typing import Any, Dict, List
from datetime import datetime

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
        "recovery_percentage": 72.0,
        "hrv_ms": 58.5,
        "strain_score": 12.5,
        "vo2_max": 45.0,
        "resting_hr": 65,
        "sleep_hours": 7.5,
        "sleep_quality": "good",
        "last_updated": datetime.now().isoformat(),
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

    # Average across providers - normalize to frontend schema
    result: Dict[str, Any] = {}
    numeric_keys = [
        ("recovery_percentage", "recovery_percent"),
        ("hrv_ms", "hrv"),
        ("strain_score", "strain_score"),
        ("vo2_max", "vo2_max_estimate"),
        ("resting_hr", "resting_hr"),
        ("sleep_hours", "sleep_hours"),
    ]
    
    for frontend_key, backend_key in numeric_keys:
        values = [s.get(backend_key) for s in summaries if s.get(backend_key) is not None]
        result[frontend_key] = sum(values) / len(values) if values else 0

    result["sleep_quality"] = summaries[0].get("sleep_quality", "unknown")
    result["last_updated"] = datetime.now().isoformat()
    
    return result
