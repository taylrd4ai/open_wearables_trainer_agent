"""Biometric data aggregation service."""

from typing import Any, Dict, List
from datetime import datetime, date
import uuid
import logging

from app.config import settings
from app.services.providers.whoop import WhoopProvider
from app.services.providers.garmin import GarminProvider
from app.services.providers.oura import OuraProvider
from app.services.providers.polar import PolarProvider

logger = logging.getLogger("biometric_services")


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


def _provider_name(provider: Any) -> str:
    """Derives a lowercase provider name from its class (e.g. WhoopProvider -> whoop)."""
    return type(provider).__name__.replace("Provider", "").lower()


def _generate_mock_summary(user_id: str) -> Dict[str, Any]:
    """
    Generate synthetic biometric summary when no providers are configured.

    Field names here MUST match get_biometric_summary()'s real-provider
    return schema below (recovery_percent, hrv, vo2_max_estimate, etc.) --
    these were previously out of sync (mock returned raw provider-internal
    names like hrv_ms/recovery_percentage instead of the translated
    frontend schema), which silently broke anything reading the mock
    response on the frontend.
    """
    return {
        "user_id": user_id,
        "recovery_percent": 72.0,
        "hrv": 58.5,
        "strain_score": 12.5,
        "vo2_max_estimate": 45.0,
        "resting_hr": 65,
        "sleep_hours": 7.5,
        "sleep_quality": "good",
        "training_load": 0.0,
        "source_provider": "mock",
        "is_mock": True,
        "last_updated": datetime.now().isoformat(),
    }


async def _persist_biometric_summary(user_id: str, summary: Dict[str, Any]) -> None:
    """
    Upsert today's biometric summary into the biometric_data table.

    Inserts a new BiometricData row for today if one does not already
    exist for this user+date. Skips silently on any DB error so a
    persistence failure never breaks the fetch path.

    Only called for real provider data (not mock), since writing mock
    values to the DB would pollute historical records.
    """
    from app.database import get_session
    from app.models.biometric_data import BiometricData
    from sqlalchemy import select

    try:
        user_uuid = uuid.UUID(user_id)
    except (ValueError, AttributeError):
        logger.warning("_persist_biometric_summary: invalid user_id %r, skipping", user_id)
        return

    try:
        async with get_session() as session:
            existing = await session.execute(
                select(BiometricData).where(
                    BiometricData.user_id == user_uuid,
                    BiometricData.date == date.today(),
                )
            )
            if existing.scalar_one_or_none() is not None:
                return  # already persisted today, skip

            row = BiometricData(
                user_id=user_uuid,
                date=date.today(),
                recovery_percent=summary.get("recovery_percent"),
                hrv=summary.get("hrv"),
                strain_score=summary.get("strain_score"),
                vo2_max_estimate=summary.get("vo2_max_estimate"),
                training_load=summary.get("training_load"),
                source_provider=summary.get("source_provider", "unknown"),
            )
            session.add(row)
            logger.info(
                "Persisted biometric summary for user=%s date=%s provider=%s",
                user_id, date.today(), summary.get("source_provider"),
            )
    except Exception:
        logger.exception(
            "Failed to persist biometric summary for user=%s — fetch result unaffected",
            user_id,
        )


async def get_biometric_summary(user_id: str) -> Dict[str, Any]:
    """
    Get aggregated biometric summary for a user.

    Falls back to mock data if no API keys are configured. Both the mock
    and real-provider paths return an identical schema:
    user_id, recovery_percent, hrv, strain_score, vo2_max_estimate,
    resting_hr, sleep_hours, sleep_quality, training_load,
    source_provider, is_mock, last_updated.

    Real provider results are persisted to the biometric_data table
    (one row per user per day, upsert-safe).
    """
    providers = _get_configured_providers()

    if not providers:
        return _generate_mock_summary(user_id)

    summaries: List[Dict[str, Any]] = []
    contributing_providers: List[str] = []
    for provider in providers:
        try:
            raw = await provider.fetch_data(user_id)
            normalized = provider.normalize(raw)
            summaries.append(normalized)
            contributing_providers.append(_provider_name(provider))
        except Exception:
            continue

    if not summaries:
        return _generate_mock_summary(user_id)

    # Average across providers - normalize to frontend schema
    result: Dict[str, Any] = {"user_id": user_id}
    numeric_keys = [
        ("recovery_percentage", "recovery_percent"),
        ("hrv_ms", "hrv"),
        ("strain_score", "strain_score"),
        ("vo2_max", "vo2_max_estimate"),
        ("resting_hr", "resting_hr"),
        ("sleep_hours", "sleep_hours"),
    ]

    for backend_key, frontend_key in numeric_keys:
        values = [s.get(backend_key) for s in summaries if s.get(backend_key) is not None]
        result[frontend_key] = sum(values) / len(values) if values else 0

    # TODO: training_load isn't computed from any provider field yet --
    # defaulting to 0.0 here to keep the schema consistent with the mock
    # path. If the recommendations engine computes this elsewhere, wire
    # that in instead of this placeholder.
    result["training_load"] = 0.0

    result["sleep_quality"] = summaries[0].get("sleep_quality", "unknown")
    result["source_provider"] = ",".join(contributing_providers) if contributing_providers else "unknown"
    result["is_mock"] = False
    result["last_updated"] = datetime.now().isoformat()

    # Persist to DB (non-blocking on failure)
    await _persist_biometric_summary(user_id, result)

    return result
