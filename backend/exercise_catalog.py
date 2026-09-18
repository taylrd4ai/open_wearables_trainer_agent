"""Canonical exercise catalog with 20 exercises."""

from typing import Any, Dict

EXERCISE_CATALOG: Dict[int, Dict[str, Any]] = {
    1: {"name": "Barbell Bench Press", "muscle_group": "chest", "equipment_needed": "barbell", "substitution_id": 2},
    2: {"name": "Dumbbell Bench Press", "muscle_group": "chest", "equipment_needed": "dumbbell", "substitution_id": 3},
    3: {"name": "Push-Up", "muscle_group": "chest", "equipment_needed": "bodyweight", "substitution_id": None},
    4: {"name": "Barbell Row", "muscle_group": "back", "equipment_needed": "barbell", "substitution_id": 5},
    5: {"name": "Dumbbell Row", "muscle_group": "back", "equipment_needed": "dumbbell", "substitution_id": 6},
    6: {"name": "Pull-Up", "muscle_group": "back", "equipment_needed": "pull_up_bar", "substitution_id": 5},
    7: {"name": "Barbell Back Squat", "muscle_group": "legs", "equipment_needed": "barbell", "substitution_id": 8},
    8: {"name": "Goblet Squat", "muscle_group": "legs", "equipment_needed": "kettlebell", "substitution_id": 9},
    9: {"name": "Bodyweight Squat", "muscle_group": "legs", "equipment_needed": "bodyweight", "substitution_id": None},
    10: {"name": "Romanian Deadlift", "muscle_group": "legs", "equipment_needed": "barbell", "substitution_id": 8},
    11: {"name": "Overhead Press", "muscle_group": "shoulders", "equipment_needed": "barbell", "substitution_id": 12},
    12: {"name": "Dumbbell Lateral Raise", "muscle_group": "shoulders", "equipment_needed": "dumbbell", "substitution_id": 13},
    13: {"name": "Resistance Band Pull-Apart", "muscle_group": "shoulders", "equipment_needed": "resistance_band", "substitution_id": None},
    14: {"name": "Barbell Bicep Curl", "muscle_group": "arms", "equipment_needed": "barbell", "substitution_id": 15},
    15: {"name": "Dumbbell Hammer Curl", "muscle_group": "arms", "equipment_needed": "dumbbell", "substitution_id": 14},
    16: {"name": "Tricep Dip", "muscle_group": "arms", "equipment_needed": "parallel_bars", "substitution_id": 3},
    17: {"name": "Plank", "muscle_group": "core", "equipment_needed": "bodyweight", "substitution_id": None},
    18: {"name": "Cable Woodchop", "muscle_group": "core", "equipment_needed": "cable_machine", "substitution_id": 19},
    19: {"name": "Russian Twist", "muscle_group": "core", "equipment_needed": "bodyweight", "substitution_id": 17},
    20: {"name": "Deadlift", "muscle_group": "full_body", "equipment_needed": "barbell", "substitution_id": 10},
}


def get_exercise(exercise_id: int) -> Dict[str, Any] | None:
    """Look up an exercise by its catalog ID."""
    return EXERCISE_CATALOG.get(exercise_id)


def get_substitution(exercise_id: int) -> Dict[str, Any] | None:
    """Get the substitution exercise for a given exercise ID."""
    ex = EXERCISE_CATALOG.get(exercise_id)
    if ex and ex.get("substitution_id"):
        return EXERCISE_CATALOG.get(ex["substitution_id"])
    return None
