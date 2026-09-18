"""Workout recommendation API routes."""

from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.workout_planner_v2 import generate_workout_v2

router = APIRouter(tags=["recommendations"])


class GenerateRequest(BaseModel):
    """Request body for workout generation."""

    user_id: str = Field(default="default")
    objective: str = Field(default="hypertrophy")
    location: str = Field(default="gym")
    muscle_group: str = Field(default="full_body")
    history_volume: float = Field(default=0.0)


@router.post("/workout/generate-v2")
async def generate_v2(request: GenerateRequest) -> Dict[str, Any]:
    """Generate a personalized workout plan V2."""
    return await generate_workout_v2(
        user_id=request.user_id,
        objective=request.objective,
        location=request.location,
        muscle_group=request.muscle_group,
        history_volume=request.history_volume,
    )
