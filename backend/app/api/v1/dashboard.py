"""Dashboard API routes."""

from typing import Any, Dict

from fastapi import APIRouter

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/stats")
async def get_dashboard_stats() -> Dict[str, Any]:
    """Return summary statistics for the dashboard.

    In production this queries the DB; here returns mock-safe defaults.
    """
    return {
        "total_workouts": 0,
        "total_volume": 0.0,
        "avg_rpe": None,
        "streak_days": 0,
        "this_week_sessions": 0,
        "message": "Connect a database and log workouts to see stats.",
    }
