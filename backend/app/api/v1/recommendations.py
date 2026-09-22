"""Workout recommendation endpoint with LLM narration.

Assembles the OW-backed readiness snapshot, applies the client's
coaching decision rules (health_engine.recommend_workout), and calls
an LLM purely to narrate the prescription in plain language. The LLM
never overrides the rule-based decision -- it only explains it. If the
LLM call fails for any reason, falls back to a deterministic template
string so the endpoint never breaks.
"""

from typing import Any, Dict

from fastapi import APIRouter, Query

from app.services.health_engine import recommend_workout
from app.services.client_profile import CLIENT_PROFILE, INJURY_CONTEXT
from app.services.llm_client import generate_coaching_narration

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


def _narrate_fallback(decision: Dict[str, Any], snapshot: Dict[str, Any]) -> str:
    """Deterministic plain-language narration, used if the LLM call fails."""
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


async def _narrate_with_llm(decision: Dict[str, Any], snapshot: Dict[str, Any]) -> str:
    prompt = f"""Today's prescription: {decision['situation']} -> {decision['template']}
Detail: {decision['detail']}
Recovery tier: {decision.get('recovery_tier')}
Recovery score: {snapshot.get('recovery_score')}
Sleep score: {snapshot.get('sleep_score')}
Played soccer yesterday: {snapshot.get('played_soccer_yesterday')}
High strain yesterday: {snapshot.get('high_strain_yesterday')}

Explain why this is today's recommendation in a short, encouraging way.
"""
    try:
        return await generate_coaching_narration(prompt)
    except Exception:
        return _narrate_fallback(decision, snapshot)


@router.get("/workout")
async def get_workout_recommendation(no_gym_access: bool = Query(False)) -> Dict[str, Any]:
    """
    Today's workout recommendation, grounded in OW readiness data and
    the client's coaching handoff decision rules, narrated by an LLM.
    """
    result = await recommend_workout(no_gym_access=no_gym_access)
    narration = await _narrate_with_llm(result["decision"], result["snapshot"])

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
