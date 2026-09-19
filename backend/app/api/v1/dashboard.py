"""Dashboard API routes."""

from typing import Any, Dict
from datetime import datetime

from fastapi import APIRouter

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/stats")
async def get_dashboard_stats() -> Dict[str, Any]:
    """Return summary statistics for the dashboard.

    In production this queries the DB; here returns mock-safe defaults.
    """
    return {
        "total_workouts": 0,
        "total_volume_kg": 0.0,
        "avg_rpe": None,
        "recent_workouts": [],
        "biometrics": {
            "recovery_percentage": 0,
            "hrv_ms": 0,
            "strain_score": 0.0,
            "vo2_max": 0.0,
            "resting_hr": 0,
            "sleep_hours": 0.0,
            "sleep_quality": "unknown",
            "last_updated": datetime.now().isoformat(),
        },
        "trainer_message": {
            "message": "Connect a database and log workouts to see stats.",
            "persona_mode": "standard",
            "timestamp": datetime.now().isoformat(),
        },
        "recommendations": [],
    }
