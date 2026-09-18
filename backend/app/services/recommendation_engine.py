"""Training recommendation engine with 5-layer pipeline."""

from enum import Enum
from typing import Any, Dict, List, Optional


class TrainingObjective(str, Enum):
    """Supported training objectives."""

    STRENGTH = "strength"
    HYPERTROPHY = "hypertrophy"
    ENDURANCE = "endurance"
    POWER = "power"


def safe_objective(value: str) -> TrainingObjective:
    """Parse objective string with graceful fallback to hypertrophy."""
    try:
        return TrainingObjective(value.lower().strip())
    except (ValueError, AttributeError):
        return TrainingObjective.HYPERTROPHY


# Layer configs per objective
OBJECTIVE_CONFIGS: Dict[TrainingObjective, Dict[str, Any]] = {
    TrainingObjective.STRENGTH: {
        "rep_range": (1, 5),
        "set_range": (4, 6),
        "intensity_pct": 85,
        "rest_seconds": 180,
    },
    TrainingObjective.HYPERTROPHY: {
        "rep_range": (8, 12),
        "set_range": (3, 5),
        "intensity_pct": 70,
        "rest_seconds": 90,
    },
    TrainingObjective.ENDURANCE: {
        "rep_range": (15, 25),
        "set_range": (2, 4),
        "intensity_pct": 50,
        "rest_seconds": 45,
    },
    TrainingObjective.POWER: {
        "rep_range": (1, 5),
        "set_range": (3, 5),
        "intensity_pct": 80,
        "rest_seconds": 150,
    },
}


def _layer1_select_exercises(
    objective: TrainingObjective, muscle_group: str
) -> List[int]:
    """Layer 1: Select exercise IDs based on objective and target muscles."""
    group_exercises: Dict[str, List[int]] = {
        "chest": [1, 2, 3],
        "back": [4, 5, 6],
        "legs": [7, 8, 9, 10],
        "shoulders": [11, 12],
        "arms": [13, 14, 15],
        "core": [16, 17],
        "full_body": [1, 5, 7, 11, 16],
    }
    ids = group_exercises.get(muscle_group, group_exercises["full_body"])
    count = 3 if objective == TrainingObjective.STRENGTH else 4
    return ids[:count]


def _layer2_apply_parameters(
    exercise_ids: List[int], objective: TrainingObjective
) -> List[Dict[str, Any]]:
    """Layer 2: Apply rep/set/intensity parameters per objective."""
    config = OBJECTIVE_CONFIGS[objective]
    reps_low, reps_high = config["rep_range"]
    sets_low, sets_high = config["set_range"]
    reps = (reps_low + reps_high) // 2
    sets = (sets_low + sets_high) // 2

    result = []
    for eid in exercise_ids:
        result.append({
            "exercise_id": eid,
            "sets": sets,
            "reps": reps,
            "intensity_pct": config["intensity_pct"],
            "rest_seconds": config["rest_seconds"],
        })
    return result


def _layer3_adjust_for_biometrics(
    plan: List[Dict[str, Any]], biometrics: Optional[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Layer 3: Adjust volume/intensity based on recovery and strain."""
    if not biometrics:
        return plan

    recovery = biometrics.get("recovery_percent", 70.0)
    if recovery < 40:
        for ex in plan:
            ex["sets"] = max(1, ex["sets"] - 1)
            ex["intensity_pct"] = max(40, ex["intensity_pct"] - 15)
    elif recovery > 85:
        for ex in plan:
            ex["sets"] = ex["sets"] + 1

    return plan


def _layer4_apply_progression(
    plan: List[Dict[str, Any]], history_volume: float = 0.0
) -> List[Dict[str, Any]]:
    """Layer 4: Apply progressive overload rules."""
    if history_volume > 0:
        for ex in plan:
            ex["intensity_pct"] = min(100, ex["intensity_pct"] + 2)
    return plan


def _layer5_format_output(
    plan: List[Dict[str, Any]], objective: TrainingObjective
) -> Dict[str, Any]:
    """Layer 5: Format final recommendation output."""
    return {
        "objective": objective.value,
        "exercises": plan,
        "estimated_duration_minutes": len(plan) * 12,
        "notes": f"Program optimized for {objective.value} adaptation.",
    }


def generate_recommendation(
    objective_str: str,
    muscle_group: str = "full_body",
    biometrics: Optional[Dict[str, Any]] = None,
    history_volume: float = 0.0,
) -> Dict[str, Any]:
    """Generate a workout recommendation using the 5-layer pipeline.

    Args:
        objective_str: Training goal string (strength/hypertrophy/endurance/power)
        muscle_group: Target muscle group
        biometrics: Optional biometric summary dict
        history_volume: Previous session total volume for progression

    Returns:
        Complete workout recommendation dict
    """
    objective = safe_objective(objective_str)

    # 5-layer pipeline
    selected = _layer1_select_exercises(objective, muscle_group)
    parameterized = _layer2_apply_parameters(selected, objective)
    adjusted = _layer3_adjust_for_biometrics(parameterized, biometrics)
    progressed = _layer4_apply_progression(adjusted, history_volume)
    result = _layer5_format_output(progressed, objective)

    return result
