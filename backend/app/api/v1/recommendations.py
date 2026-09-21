"""Workout recommendation API routes."""

from typing import Any, Dict, List

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


@router.get("/recommendations")
async def get_recommendations(user_id: str = "default") -> List[Dict[str, Any]]:
    """Return personalized recommendations for a user.

    Stub: returns empty list until DB integration is complete.
    """
    return []


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
"""Workout recommendation endpoint.

Assembles the OW-backed readiness snapshot, applies the client's
coaching decision rules, and (optionally) calls an LLM purely to
narrate the prescription in plain language. The LLM never overrides
the numeric/rule-based decision -- it explains it.
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Query

from app.services.health_engine import recommend_workout
from app.services.client_profile import CLIENT_PROFILE, INJURY_CONTEXT

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


def _narrate(decision: Dict[str, Any], snapshot: Dict[str, Any]) -> str:
    """
    Deterministic plain-language narration (no LLM call by default).

    Swap this for an LLM call if you want richer phrasing -- pass
    `decision` and `snapshot` as grounding context in the prompt and
    instruct the model not to change the prescription, only explain it.
    """
    situation = decision["situation"]
    tier = decision.get("recovery_tier", "unknown")

    if situation == "day_after_soccer_or_poor_readiness":
        return (
            f"Recovery is {tier} today, and/or you played soccer yesterday. "
            "Defaulting to a recovery day: light Zone 2 cardio plus mobility/core. "
            "No hard lower-body lifting."
        )
    if situation == "good_readiness_thursday":
        return "Recovery looks good and it's your primary strength day -- machine template, 1-2 sets per exercise."
    if situation == "good_readiness_friday":
        return "Recovery is solid for a second strength session. Use the machine or dumbbell template; keep to 1-2 sets if soccer fatigue lingers."
    if situation == "home_no_equipment_time_constrained":
        return "No gym access today -- use the home bodyweight/band template. Completing it counts as a full session."
    if situation == "high_fatigue_poor_sleep_or_soreness":
        return f"Recovery is {tier} or you're carrying high strain from yesterday. Zone 2 only, plus mobility and light core -- skip strength work."
    if situation == "scheduled_zone2":
        return f"Scheduled Zone 2 day: {decision['detail']}"
    if situation == "scheduled_rest":
        return "Scheduled rest day: walk or short home mobility/stability only."
    if situation == "scheduled_recovery":
        return f"Scheduled recovery day: {decision['detail']}"
    if situation == "scheduled_soccer":
        return "Competitive soccer today -- no separate gym prescription needed."
    return "No specific rule matched; defaulting to conservative Zone 2 + mobility."


@router.get("/workout")
async def get_workout_recommendation(no_gym_access: bool = Query(False)) -> Dict[str, Any]:
    """
    Today's workout recommendation, grounded in OW readiness data and
    the client's coaching handoff decision rules.
    """
    result = await recommend_workout(no_gym_access=no_gym_access)
    narration = _narrate(result["decision"], result["snapshot"])

    return {
        "client": CLIENT_PROFILE["name"],
        "date": result["snapshot"]["date"],
        "weekday": result["snapshot"]["weekday"],
        "recovery_tier": result["decision"].get("recovery_tier"),
        "situation": result["decision"]["situation"],
        "template": result["decision"]["template"],
        "prescription": result["decision"]["detail"],
        "narration": narration,
        "safety_reminders": {
            "priorities": result["injury_context"]["priorities"],
            "escalate_if": result["injury_context"]["escalation_triggers"],
        },
        "snapshot": result["snapshot"],
    }
