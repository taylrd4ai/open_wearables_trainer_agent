"""Rules-based workout recommendation engine.

Combines the day-of-week schedule, OW-derived readiness signals, and
recent training history (soccer strain, gym sessions) with the
decision rules from the client's coaching handoff. This produces a
grounded prescription BEFORE any LLM narration is layered on top.

`client_profile.py` is the single source of truth for the weekly
schedule and decision rules -- this engine reads WEEKLY_SCHEDULE and
AGENT_DECISION_RULES rather than hardcoding weekday/situation logic,
so edits to the handoff doc's tables actually take effect here.
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

# Lookup of situation -> prescription code, built from the handoff doc's
# Agent Decision Rules table so the table is actually consulted rather
# than duplicated as hardcoded strings.
_PRESCRIPTION_BY_SITUATION: Dict[str, str] = {
    rule["situation"]: rule["prescription"] for rule in AGENT_DECISION_RULES
}


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


def _decision(situation: str, template: str, detail: Any, tier: str) -> Dict[str, Any]:
    """Assembles a decision dict, tagging it with the prescription code
    from AGENT_DECISION_RULES when the handoff doc defines one for this
    situation (some situations, like scheduled rest/soccer days, are
    pure scheduling and intentionally have no entry in that table)."""
    return {
        "situation": situation,
        "template": template,
        "detail": detail,
        "recovery_tier": tier,
        "prescription_code": _PRESCRIPTION_BY_SITUATION.get(situation),
    }


def evaluate_decision_rule(snapshot: Dict[str, Any], no_gym_access: bool = False) -> Dict[str, Any]:
    """
    Apply the Agent Decision Rules table to today's snapshot.

    Returns the situation key, template to use, and whether to
    escalate for clinical reassessment.
    """
    weekday = snapshot["weekday"]
    schedule_default = WEEKLY_SCHEDULE.get(weekday, "")
    tier = _recovery_tier(snapshot.get("recovery_score"))
    poor_readiness = tier == "red"
    soccer_fatigue = snapshot.get("played_soccer_yesterday") or snapshot.get("high_strain_yesterday")
    high_fatigue = tier == "red" or snapshot.get("high_strain_yesterday")

    # Highest-priority safety rule is handled elsewhere (symptom check-in,
    # not derivable from wearable data) -- flagged here as a placeholder.
    # if user reports pain/swelling/locking/instability -> escalate.

    if snapshot.get("played_soccer_yesterday") or poor_readiness:
        return _decision(
            "day_after_soccer_or_poor_readiness",
            "recovery_default",
            RECOVERY_CARDIO["wednesday_default"],
            tier,
        )

    if no_gym_access:
        return _decision(
            "home_no_equipment_time_constrained",
            "home",
            HOME_TEMPLATE,
            tier,
        )

    if high_fatigue:
        return _decision(
            "high_fatigue_poor_sleep_or_soreness",
            "zone2_only",
            "Zone 2 + mobility + light core; no strength work today.",
            tier,
        )

    # Weekday routing driven by WEEKLY_SCHEDULE (client_profile.py) rather
    # than a hardcoded weekday==... chain, so schedule edits there take
    # effect here automatically.
    if "primary_strength" in schedule_default:
        return _decision("good_readiness_thursday", "machine", MACHINE_TEMPLATE, tier)

    if "optional_second_session" in schedule_default:
        # Handoff doc: "machine OR dumbbell; 1-2 sets if soccer fatigue
        # persists" -- use the lighter dumbbell template when fatigued,
        # machine otherwise. Previously this always returned the machine
        # template regardless of fatigue, silently dropping the dumbbell
        # option the situation name promised.
        template_name = "dumbbell" if soccer_fatigue else "machine"
        template_detail = DUMBBELL_TEMPLATE if soccer_fatigue else MACHINE_TEMPLATE
        return _decision("good_readiness_friday", template_name, template_detail, tier)

    if "zone2_cardio" in schedule_default:
        zone2 = RECOVERY_CARDIO["zone2_schedule"].get(f"{weekday}_min", "25-35")
        return _decision(
            "scheduled_zone2",
            "zone2",
            f"Zone 2 cardio, {zone2} min, RPE 3-4/10.",
            tier,
        )

    if "rest" in schedule_default:
        return _decision(
            "scheduled_rest",
            "rest_or_mobility",
            "Rest, walk, or short home mobility/stability.",
            tier,
        )

    if "recovery_focused" in schedule_default:
        return _decision(
            "scheduled_recovery",
            "recovery_default",
            RECOVERY_CARDIO["wednesday_default"],
            tier,
        )

    if "soccer" in schedule_default:
        return _decision(
            "scheduled_soccer",
            "soccer",
            "Competitive soccer 60-90 min.",
            tier,
        )

    return _decision(
        "no_rule_matched",
        "zone2_conservative",
        "No specific rule matched; defaulting to conservative Zone 2 + mobility.",
        tier,
    )


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
