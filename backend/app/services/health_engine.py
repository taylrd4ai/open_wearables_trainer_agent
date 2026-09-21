"""Rules-based workout recommendation engine.

Combines the day-of-week schedule, OW-derived readiness signals, and
recent training history (soccer strain, gym sessions) with the
decision rules from the client's coaching handoff. This produces a
grounded prescription BEFORE any LLM narration is layered on top.
"""

from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from app.services.ow_data import fetch_health_scores, fetch_sleep_summary, fetch_workouts
from app.services.client_profile import (
    WEEKLY_SCHEDULE,
    MACHINE_TEMPLATE,
    DUMBBELL_TEMPLATE,
    HOME_TEMPLATE,
    RECOVERY_CARDIO,
    AGENT_DECISION_RULES,
    INJURY_CONTEXT,
)

# Recovery score thresholds (0-100 scale, Whoop-style recovery %).
RECOVERY_GREEN_MIN = 67
RECOVERY_YELLOW_MIN = 34


def _latest(items: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    return items[-1] if items else None


def _played_soccer_yesterday(workouts: List[Dict[str, Any]], today: date) -> bool:
    yesterday = today - timedelta(days=1)
    for w in workouts:
        w_date = w.get("start_date") or w.get("date")
        w_type = (w.get("type") or w.get("workout_type") or "").lower()
        if w_date == yesterday.isoformat() and "soccer" in w_type:
            return True
    return False


def _high_strain_yesterday(workouts: List[Dict[str, Any]], today: date, threshold: float = 12.0) -> bool:
    yesterday = today - timedelta(days=1)
    for w in workouts:
        w_date = w.get("start_date") or w.get("date")
        strain = w.get("strain") or w.get("strain_score")
        if w_date == yesterday.isoformat() and strain is not None and strain >= threshold:
            return True
    return False


async def build_readiness_snapshot(days: int = 14) -> Dict[str, Any]:
    """Pull OW data needed to evaluate the decision rules."""
    end = date.today()
    start = end - timedelta(days=days)

    scores = await fetch_health_scores(start, end)
    sleep = await fetch_sleep_summary(start, end)
    workouts = await fetch_workouts(start, end)

    latest_scores = _latest(scores) or {}
    latest_sleep = _latest(sleep) or {}

    return {
        "date": end.isoformat(),
        "weekday": end.strftime("%A").lower(),
        "recovery_score": latest_scores.get("recovery_score"),
        "sleep_score": latest_scores.get("sleep_score"),
        "resilience_score": latest_scores.get("resilience_score"),
        "sleep_last_night": latest_sleep,
        "played_soccer_yesterday": _played_soccer_yesterday(workouts, end),
        "high_strain_yesterday": _high_strain_yesterday(workouts, end),
        "recent_workouts": workouts[-5:] if workouts else [],
    }


def _recovery_tier(recovery_score: Optional[float]) -> str:
    if recovery_score is None:
        return "unknown"
    if recovery_score >= RECOVERY_GREEN_MIN:
        return "green"
    if recovery_score >= RECOVERY_YELLOW_MIN:
        return "yellow"
    return "red"


def evaluate_decision_rule(snapshot: Dict[str, Any], no_gym_access: bool = False) -> Dict[str, Any]:
    """
    Apply the Agent Decision Rules table to today's snapshot.

    Returns the situation key, template to use, and whether to
    escalate for clinical reassessment.
    """
    weekday = snapshot["weekday"]
    tier = _recovery_tier(snapshot.get("recovery_score"))
    poor_readiness = tier == "red"
    high_fatigue = tier in ("red",) or snapshot.get("high_strain_yesterday")

    # Highest-priority safety rule is handled elsewhere (symptom check-in,
    # not derivable from wearable data) — flagged here as a placeholder.
    # if user reports pain/swelling/locking/instability -> escalate.

    if snapshot.get("played_soccer_yesterday") or poor_readiness:
        return {
            "situation": "day_after_soccer_or_poor_readiness",
            "template": "recovery_default",
            "detail": RECOVERY_CARDIO["wednesday_default"],
            "recovery_tier": tier,
        }

    if no_gym_access:
        return {
            "situation": "home_no_equipment_time_constrained",
            "template": "home",
            "detail": HOME_TEMPLATE,
            "recovery_tier": tier,
        }

    if high_fatigue:
        return {
            "situation": "high_fatigue_poor_sleep_or_soreness",
            "template": "zone2_only",
            "detail": "Zone 2 + mobility + light core; no strength work today.",
            "recovery_tier": tier,
        }

    if weekday == "thursday":
        return {
            "situation": "good_readiness_thursday",
            "template": "machine",
            "detail": MACHINE_TEMPLATE,
            "recovery_tier": tier,
        }

    if weekday == "friday":
        return {
            "situation": "good_readiness_friday",
            "template": "machine_or_dumbbell",
            "detail": MACHINE_TEMPLATE,
            "recovery_tier": tier,
        }

    if weekday in ("monday", "saturday"):
        zone2 = RECOVERY_CARDIO["zone2_schedule"].get(f"{weekday}_min", "25-35")
        return {
            "situation": "scheduled_zone2",
            "template": "zone2",
            "detail": f"Zone 2 cardio, {zone2} min, RPE 3-4/10.",
            "recovery_tier": tier,
        }

    if weekday == "sunday":
        return {
            "situation": "scheduled_rest",
            "template": "rest_or_mobility",
            "detail": "Rest, walk, or short home mobility/stability.",
            "recovery_tier": tier,
        }

    if weekday == "wednesday":
        return {
            "situation": "scheduled_recovery",
            "template": "recovery_default",
            "detail": RECOVERY_CARDIO["wednesday_default"],
            "recovery_tier": tier,
        }

    # Tuesday: soccer day, no gym prescription needed.
    return {
        "situation": "scheduled_soccer",
        "template": "soccer",
        "detail": "Competitive soccer 60-90 min.",
        "recovery_tier": tier,
    }


async def recommend_workout(no_gym_access: bool = False) -> Dict[str, Any]:
    """Full pipeline: snapshot + decision rule, ready for LLM narration."""
    snapshot = await build_readiness_snapshot()
    decision = evaluate_decision_rule(snapshot, no_gym_access=no_gym_access)

    return {
        "snapshot": snapshot,
        "decision": decision,
        "injury_context": {
            "priorities": INJURY_CONTEXT["priorities"],
            "escalation_triggers": INJURY_CONTEXT["escalation_triggers"],
        },
    }
