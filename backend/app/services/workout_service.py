"""
Workout service — shared logic used by both the Telegram bot and the
existing REST API. Wraps DB access for logging sets against the real
User -> WorkoutSession -> ExerciseEntry chain, delegates validation and
volume/RPE math to workout_logging_service.py, and tracks lightweight
per-conversation state for the Telegram bot.

Location: app/services/workout_service.py
"""

import re
import logging
import uuid
from datetime import datetime, date
from typing import Any, Dict, List, Optional

from pydantic import ValidationError
from sqlalchemy import select

from app.database import get_session
from app.models.exercise import Exercise
from app.models.exercise_entry import ExerciseEntry
from app.models.workout_session import WorkoutSession
from app.services.workout_logging_service import (
    ExerciseEntrySchema,
    calculate_average_rpe,
    calculate_total_volume,
)

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
        self.exercise_queue: List[str] = []
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


def start_workout_queue(state: ConversationState, exercises: List[str]) -> None:
    state.exercise_queue = list(exercises)
    advance_to_next_exercise(state)


# --------------------------------------------------------------------------
# Today's recommendation — reuses the existing recommendations engine.
# Uses the client's display name (e.g. "Eric Taylor"), NOT the user_id UUID,
# since that's how the recommendations engine is keyed per the coaching
# handoff doc.
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
# Set logging: text parsing.
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
    Note: this only extracts raw values -- real bounds validation
    (reps 1-100, weight 0-2000, etc.) happens via ExerciseEntrySchema
    in workout_logging_service.py, not here.
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
    }


# --------------------------------------------------------------------------
# Exercise catalog resolution.
# --------------------------------------------------------------------------

async def resolve_exercise_id(name: str) -> Optional[int]:
    """
    Matches a free-text exercise name (e.g. "bench press") against
    Exercise.name or Exercise.aliases, case-insensitively.
    Returns None if nothing matches -- caller decides how to handle that
    (ask the user to clarify, rather than silently failing).
    """
    normalized = name.strip().lower()

    async with get_session() as session:
        result = await session.execute(select(Exercise))
        all_exercises = result.scalars().all()

        for ex in all_exercises:
            if ex.name.lower() == normalized:
                return ex.id
            if ex.aliases and normalized in [a.lower() for a in ex.aliases]:
                return ex.id

        for ex in all_exercises:
            candidates = [ex.name.lower()] + [a.lower() for a in (ex.aliases or [])]
            if any(normalized in c or c in normalized for c in candidates):
                return ex.id

    return None


# --------------------------------------------------------------------------
# Set logging: DB writes against the real User -> WorkoutSession ->
# ExerciseEntry chain, with validation + volume/RPE math delegated to
# workout_logging_service.py.
# --------------------------------------------------------------------------

async def _get_or_create_todays_session(user_id: uuid.UUID) -> WorkoutSession:
    async with get_session() as session:
        stmt = select(WorkoutSession).where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.date == date.today(),
        )
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing is not None:
            return existing

        new_session = WorkoutSession(
            user_id=user_id,
            date=date.today(),
            location="unspecified",
        )
        session.add(new_session)
        await session.flush()
        await session.refresh(new_session)
        return new_session


async def _recalculate_session_totals(workout_session_id: uuid.UUID) -> None:
    """
    Recomputes total_volume/rpe_avg across ALL entries in a session using
    the same math as workout_logging_service.calculate_total_volume /
    calculate_average_rpe, so a session built up from multiple Telegram
    messages stays consistent with a session logged in one REST call.
    """
    async with get_session() as session:
        result = await session.execute(
            select(ExerciseEntry).where(ExerciseEntry.session_id == workout_session_id)
        )
        entries = result.scalars().all()

        schema_entries = [
            ExerciseEntrySchema(
                exercise_id=e.exercise_id,
                set_number=e.set_number,
                reps=e.reps,
                weight=e.weight,
                rpe=e.rpe,
            )
            for e in entries
        ]

        total_volume = calculate_total_volume(schema_entries)
        avg_rpe = calculate_average_rpe(schema_entries)

        workout_session = await session.get(WorkoutSession, workout_session_id)
        if workout_session is not None:
            workout_session.total_volume = total_volume
            workout_session.rpe_avg = avg_rpe


async def log_set(
    client: str,
    parsed_set: Dict[str, Any],
    workout_context: Optional[str] = None,
    rpe: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Persists a logged set as one or more ExerciseEntry rows under today's
    WorkoutSession for the given user, validating each entry through
    ExerciseEntrySchema (reps 1-100, weight 0-2000, RPE 1-10) before
    writing anything. `client` here is the resolved user_id string
    (settings.ERIC_USER_ID), NOT the display name -- telegram_bot.py is
    responsible for that resolution before calling this.
    """
    if not client:
        raise ValueError("log_set requires a resolved user_id, got empty client")

    try:
        user_id = uuid.UUID(client)
    except ValueError as exc:
        raise ValueError(f"log_set: '{client}' is not a valid user_id UUID") from exc

    exercise_name = parsed_set["exercise"]
    exercise_id = await resolve_exercise_id(exercise_name)
    if exercise_id is None:
        logger.warning("Could not resolve exercise '%s' to a catalog entry", exercise_name)
        return {
            "status": "unresolved_exercise",
            "exercise": exercise_name,
            "message": (
                f"Couldn't match '{exercise_name}' to a known exercise. "
                "Check spelling or add it to the exercise catalog."
            ),
        }

    workout_session = await _get_or_create_todays_session(user_id)

    async with get_session() as session:
        existing = await session.execute(
            select(ExerciseEntry).where(
                ExerciseEntry.session_id == workout_session.id,
                ExerciseEntry.exercise_id == exercise_id,
            )
        )
        next_set_number = len(existing.scalars().all()) + 1

        num_sets = parsed_set.get("sets", 1)
        reps = parsed_set["reps"]
        weight = parsed_set.get("weight") or 0.0

        validated_entries = []
        try:
            for i in range(num_sets):
                validated_entries.append(
                    ExerciseEntrySchema(
                        exercise_id=exercise_id,
                        set_number=next_set_number + i,
                        reps=reps,
                        weight=weight,
                        rpe=rpe,
                    )
                )
        except ValidationError as exc:
            logger.warning("Set validation failed for %s: %s", exercise_name, exc)
            return {
                "status": "validation_error",
                "exercise": exercise_name,
                "message": f"That set looks off ({exc.errors()[0]['msg']}). Try again?",
            }

        rows = [
            ExerciseEntry(
                session_id=workout_session.id,
                exercise_id=entry.exercise_id,
                set_number=entry.set_number,
                reps=entry.reps,
                weight=entry.weight,
                rpe=entry.rpe,
            )
            for entry in validated_entries
        ]
        session.add_all(rows)
        await session.flush()
        for row in rows:
            await session.refresh(row)

        logger.info(
            "Logged %d set(s) of exercise_id=%s for user=%s (session=%s)",
            num_sets, exercise_id, user_id, workout_session.id,
        )

    await _recalculate_session_totals(workout_session.id)

    return {
        "status": "logged",
        "exercise": exercise_name,
        "exercise_id": exercise_id,
        "sets_logged": num_sets,
        "reps": reps,
        "weight": weight,
        "session_id": str(workout_session.id),
    }


async def get_recent_sets(client: str, since: Optional[date] = None) -> List[Dict[str, Any]]:
    """Returns logged exercise entries for a user, across sessions on/after `since`."""
    try:
        user_id = uuid.UUID(client)
    except ValueError:
        return []

    async with get_session() as session:
        stmt = select(ExerciseEntry).join(
            WorkoutSession, ExerciseEntry.session_id == WorkoutSession.id
        ).where(WorkoutSession.user_id == user_id)
        if since is not None:
            stmt = stmt.where(WorkoutSession.date >= since)

        result = await session.execute(stmt)
        rows = result.scalars().all()
        return [row.to_dict() for row in rows]


async def has_logged_today(client: str) -> bool:
    today_sets = await get_recent_sets(client, since=date.today())
    return len(today_sets) > 0
