"""Location and equipment substitution service."""

from typing import Dict, List

LOCATIONS: Dict[str, List[str]] = {
    "gym": [
        "barbell", "dumbbell", "cable_machine", "smith_machine",
        "leg_press", "lat_pulldown", "bench", "squat_rack",
    ],
    "home": [
        "dumbbell", "resistance_band", "kettlebell", "pull_up_bar",
        "yoga_mat", "bodyweight",
    ],
    "outdoor": [
        "bodyweight", "resistance_band", "running_shoes", "pull_up_bar",
    ],
    "park": [
        "bodyweight", "pull_up_bar", "parallel_bars", "resistance_band",
    ],
}

EQUIPMENT_SUBSTITUTIONS: Dict[str, str] = {
    "barbell": "dumbbell",
    "cable_machine": "resistance_band",
    "smith_machine": "squat_rack",
    "leg_press": "bodyweight_squat",
    "lat_pulldown": "pull_up_bar",
    "bench": "floor",
    "kettlebell": "dumbbell",
}


def get_available_equipment(location: str) -> List[str]:
    """Return available equipment for a given location."""
    return LOCATIONS.get(location, LOCATIONS["gym"])


def substitute_equipment(exercise_equipment: str, available: List[str]) -> str:
    """Find a substitution if required equipment is unavailable."""
    if exercise_equipment in available:
        return exercise_equipment
    sub = EQUIPMENT_SUBSTITUTIONS.get(exercise_equipment, "bodyweight")
    return sub if sub in available else "bodyweight"
