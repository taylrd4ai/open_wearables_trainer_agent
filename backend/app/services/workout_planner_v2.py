"""Workout planner V2 integrating all services."""

from typing import Any, Dict, List, Optional

from app.services.recommendation_engine import generate_recommendation
from app.services.location_equipment_service import (
    get_available_equipment,
    substitute_equipment,
)
from app.services.biometric_services import get_biometric_summary


async def generate_workout_v2(
    user_id: str,
    objective: str,
    location: str = "gym",
    muscle_group: str = "full_body",
    history_volume: float = 0.0,
) -> Dict[str, Any]:
    """Generate a complete workout plan V2.

    Integrates training objectives, biometrics, location/equipment
    availability, and progression rules.
    """
    # Fetch biometrics (mock-safe)
    biometrics = await get_biometric_summary(user_id)

    # Generate base recommendation
    recommendation = generate_recommendation(
        objective_str=objective,
        muscle_group=muscle_group,
        biometrics=biometrics,
        history_volume=history_volume,
    )

    # Apply equipment substitutions for location
    available = get_available_equipment(location)
    exercises: List[Dict[str, Any]] = recommendation.get("exercises", [])
    for ex in exercises:
        ex["available_equipment"] = available
        ex["location"] = location

    recommendation["location"] = location
    recommendation["biometrics_source"] = biometrics.get("source_provider", "mock")
    recommendation["recovery_percent"] = biometrics.get("recovery_percent")

    return recommendation
