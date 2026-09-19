"""Workout logging and history API routes."""

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from app.services.workout_logging_service import (
    WorkoutLogRequest,
    log_workout,
)

router = APIRouter(tags=["workouts"])


@router.post("/workout/complete")
async def complete_workout(request: WorkoutLogRequest) -> Dict[str, Any]:
    """Log a completed workout session with validated exercise entries."""
    try:
        result = log_workout(request)
        return {"status": "logged", "workout": result}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/workouts")
async def get_workouts(
    user_id: str = "", limit: int = 20, offset: int = 0
) -> List[Dict[str, Any]]:
    """Return workout history for a user.

    Stub: returns empty list until DB integration is complete.
    """
    return []


@router.get("/workout/history")
async def get_workout_history(
    user_id: str = "", limit: int = 20, offset: int = 0
) -> List[Dict[str, Any]]:
    """Return workout history for a user (deprecated, use /workouts).

    Stub: returns empty list until DB integration is complete.
    """
    return []
