"""Dashboard API routes."""

from typing import Any, Dict
from datetime import datetime

from fastapi import APIRouter

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/stats")
async def get_dashboard_stats() -> Dict[str, Any]:
    """Return summary statistics for the dashboard.

    In production this queries the DB and calls get_biometric_summary();
    here returns mock-safe defaults using the canonical biometric schema
    (recovery_percent, hrv, vo2_max_estimate, training_load, source_provider,
    is_mock) that matches biometric_services.py and the BiometricData model.
    """
    return {
        "total_workouts": 0,
        "total_volume_kg": 0.0,
        "avg_rpe": None,
        "recent_workouts": [],
        "biometrics": {
            "recovery_percent": 0.0,
            "hrv": 0.0,
            "strain_score": 0.0,
            "vo2_max_estimate": 0.0,
            "resting_hr": 0,
            "sleep_hours": 0.0,
            "sleep_quality": "unknown",
            "training_load": 0.0,
            "source_provider": "none",
            "is_mock": True,
            "last_updated": datetime.now().isoformat(),
        },
        "trainer_message": {
            "message": "Connect a database and log workouts to see stats.",
            "persona_mode": "standard",
            "timestamp": datetime.now().isoformat(),
        },
        "recommendations": [],
    }
