"""
Workout service — shared logic used by both the Telegram bot and the
existing REST API. Wraps DB access for logging sets, pulling today's
recommendation, and tracking lightweight per-conversation state
(e.g. "which exercise are we on right now in this Telegram session").

Location: app/services/workout_service.py

NOTE: adjust the two TODOs below once you confirm the exact function/
model names in your recommendations.py and database.py.
"""

import re
import logging
from datetime import datetime, date
from typing import Any, Dict, Optional

from app.config import settings
from app.database import get_session  # TODO: confirm this is your session dependency/context manager
from app.services.ow_client import ow_client

logger = logging.getLogger("workout_service")

# --------------------------------------------------------------------------
# In-memory conversation state (per client). Fine for a single-user /
# single-process deployment; move to a DB table or Redis if you ever
# run multiple workers or add more clients.
# --------------------------------------------------------------------------

class ConversationState:
    def __init__(self, client: str):
        self.client = client
        self.current_exercise: Optional[str] = None
        self.exercise_queue: list[str] = []
        self.last_interaction: datetime = datetime.utcnow()


_STATE: Dict[str, ConversationState] = {}


async def get_or_create_conversation_state(client: str) -> ConversationState:
    state = _STATE.get(client)
    if state is None:
        state = ConversationState(client)
        _STATE[client] = state
    state.last_interaction = datetime.utcnow()
    return state


def advance_to_next_exercise(state: ConversationState) -> Optional[str]:
    if state.exercise_queue:
        state.current_exercise = state.exercise_queue.pop(0)
    else:
        state.current_exercise = None
    return state.current_exercise


def start_workout_queue(state: ConversationState, exercises: list[str]) -> None:
    state.exercise_queue = list(exercises)
    advance_to_next_exercise(state)


# --------------------------------------------------------------------------
# Today's recommendation — reuses the existing recommendations engine.
# --------------------------------------------------------------------------

async def get_todays_recommendation(client: str) -> Dict[str, Any]:
    """
    Wraps the same logic behind GET /api/v1/recommendations/workout.
    TODO: replace this local import + call with whatever function your
    app/api/v1/recommendations.py actually calls internally.
    """
    from app.api.v1.recommendations import get_workout_recommendation

    rec = await get_workout_recommendation(client=client, target_date=date.today())
    if hasattr(rec, "dict"):
        rec = rec.dict()
    return rec


# --------------------------------------------------------------------------
# Set logging.
# --------------------------------------------------------------------------

SET_PATTERN = re.compile(
    r"""
    (?P<exercise>[a-zA-Z][a-zA-Z\s\-]*?)\s*[,:]?\s*
    (?P<sets>\d+)\s*x\s*(?P<reps>\d+)
    (?:\s*@?\s*(?P<weight>\d+(?:\.\d+)?)\s*(?:lb|lbs|kg)?)?
    """,
    re.IGNORECASE | re.VERBOSE,
)


def parse_set_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Regex fallback parser for the common "Bench press 3x8 @ 100lbs" shape.
    Runs BEFORE trusting any LLM-parsed set, since a deterministic regex
    match is more reliable than LLM extraction for this narrow format.
    """
    match = SET_PATTERN.search(text)
    if not match:
        return None
    exercise = match.group("exercise").strip().title()
    sets = int(match.group("sets"))
    reps = int(match.group("reps"))
    weight_raw = match.group("weight")
    weight = float(weight_raw) if weight_raw else None
    if not exercise or sets <= 0 or reps <= 0:
        return None
    return {
        "exercise": exercise,
        "sets": sets,
        "reps": reps,
        "weight": weight,
        "logged_at": datetime.utcnow().isoformat(),
    }


async def log_set(
    client: str,
    parsed_set: Dict[str, Any],
    workout_context: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Persists a single logged set.
    TODO: swap the raw-dict insert below for your actual ORM model, e.g.:

        from app.models.workout import WorkoutSet
        async with get_session() as session:
            row = WorkoutSet(
                client=client,
                exercise=parsed_set["exercise"],
                sets=parsed_set["sets"],
                reps=parsed_set["reps"],
                weight=parsed_set.get("weight"),
                context=workout_context,
                logged_at=datetime.utcnow(),
            )
            session.add(row)
            await session.commit()
            return {"id": row.id, **parsed_set}
    """
    logger.info("Logging set for %s: %s (context=%s)", client, parsed_set, workout_context)
    record = {"client": client, "context": workout_context, **parsed_set}
    # async with get_session() as session:
    #     ... insert `record` using your actual model ...
    return record


async def get_recent_sets(client: str, since: Optional[date] = None) -> list[Dict[str, Any]]:
    """
    TODO: replace with a real query once the ORM model is wired in.
    """
    return []


async def has_logged_today(client: str) -> bool:
    today_sets = await get_recent_sets(client, since=date.today())
    return len(today_sets) > 0
