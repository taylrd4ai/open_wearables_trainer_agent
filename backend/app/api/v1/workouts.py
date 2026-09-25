"""Workout logging, history, and planning API routes."""

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.workout_logging_service import (
    WorkoutLogRequest,
    log_workout,
)
from app.services.workout_planner_v2 import generate_workout_v2

router = APIRouter(tags=["workouts"])


class WorkoutPlanRequest(BaseModel):
    """Request body for the V2 workout plan endpoint."""
    user_id: str
    objective: str
    location: str = "gym"
    muscle_group: str = "full_body"
    history_volume: float = 0.0


@router.post("/workout/complete")
async def complete_workout(request: WorkoutLogRequest) -> Dict[str, Any]:
    """Log a completed workout session with validated exercise entries."""
    try:
        result = log_workout(request)
        return {"status": "logged", "workout": result}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/workout/plan")
async def plan_workout(request: WorkoutPlanRequest) -> Dict[str, Any]:
    """Generate a personalised workout plan using the V2 pipeline.

    Integrates biometric readiness (via biometric_services), training
    objective + progression rules (via recommendation_engine), and
    location/equipment availability (via location_equipment_service).

    Body parameters:
    - user_id:        User UUID string (used for biometric lookup)
    - objective:      Training goal, e.g. "hypertrophy", "strength", "endurance"
    - location:       "gym" | "home" | "outdoor" (default: "gym")
    - muscle_group:   Target muscle group (default: "full_body")
    - history_volume: Recent training volume in kg, used for progression (default: 0.0)
    """
    try:
        plan = await generate_workout_v2(
            user_id=request.user_id,
            objective=request.objective,
            location=request.location,
            muscle_group=request.muscle_group,
            history_volume=request.history_volume,
        )
        return plan
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {e}")


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
