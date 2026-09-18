"""Workout logging service with validation."""

from datetime import date
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ExerciseEntrySchema(BaseModel):
    """Validated exercise entry for workout logging."""

    exercise_id: int = Field(..., ge=1, description="Exercise catalog ID")
    set_number: int = Field(..., ge=1, description="Set number within exercise")
    reps: int = Field(..., ge=1, le=100, description="Repetitions (1-100)")
    weight: float = Field(
        ..., ge=0, le=2000, description="Weight in lbs/kg (0-2000)"
    )
    rpe: Optional[int] = Field(
        default=None, ge=1, le=10, description="Rate of perceived exertion (1-10)"
    )

    @field_validator("reps")
    @classmethod
    def validate_reps(cls, v: int) -> int:
        """Ensure reps are within physiological bounds."""
        if not (1 <= v <= 100):
            raise ValueError("Reps must be between 1 and 100")
        return v

    @field_validator("weight")
    @classmethod
    def validate_weight(cls, v: float) -> float:
        """Ensure weight is within safe bounds."""
        if not (0 <= v <= 2000):
            raise ValueError("Weight must be between 0 and 2000")
        return v

    @field_validator("rpe")
    @classmethod
    def validate_rpe(cls, v: Optional[int]) -> Optional[int]:
        """Ensure RPE is within valid scale."""
        if v is not None and not (1 <= v <= 10):
            raise ValueError("RPE must be between 1 and 10")
        return v


class WorkoutLogRequest(BaseModel):
    """Request schema for logging a complete workout."""

    user_id: UUID
    location: str = Field(default="gym")
    workout_date: date = Field(default_factory=date.today)
    exercises: List[ExerciseEntrySchema] = Field(
        ..., min_length=1, description="At least one exercise entry required"
    )


def calculate_total_volume(exercises: List[ExerciseEntrySchema]) -> float:
    """Calculate total training volume (sets x reps x weight)."""
    return sum(e.reps * e.weight for e in exercises)


def calculate_average_rpe(exercises: List[ExerciseEntrySchema]) -> Optional[float]:
    """Calculate average RPE across all entries that have RPE logged."""
    rpes = [e.rpe for e in exercises if e.rpe is not None]
    if not rpes:
        return None
    return sum(rpes) / len(rpes)


def log_workout(request: WorkoutLogRequest) -> Dict[str, Any]:
    """Process and validate a workout log request.

    Returns a summary dict ready for database insertion.
    """
    total_volume = calculate_total_volume(request.exercises)
    avg_rpe = calculate_average_rpe(request.exercises)

    return {
        "user_id": str(request.user_id),
        "date": request.workout_date.isoformat(),
        "location": request.location,
        "total_volume": total_volume,
        "rpe_avg": avg_rpe,
        "exercise_count": len(request.exercises),
        "exercises": [e.model_dump() for e in request.exercises],
    }
