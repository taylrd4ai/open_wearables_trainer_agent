"""
Telegram bot service for the AI Coach.
Runs inside the same FastAPI process/event loop as the main API,
sharing settings, DB session, and the llm_client used by the
recommendations engine.

Location: app/services/telegram_bot.py
"""

import logging
from typing import Optional

from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.config import settings
from app.services import llm_client
from app.services.workout_service import (
    get_todays_recommendation,
    log_set,
    get_or_create_conversation_state,
    parse_set_from_text,
)

logger = logging.getLogger("telegram_bot")

# Map Telegram chat_id -> client identity.
# "name" is used for the recommendations engine (keyed by display name,
# per fitness_coaching_handoff.docx). "user_id" is the real users.id UUID,
# used for all DB writes (WorkoutSession / ExerciseEntry).
# In production this should be a DB lookup (a telegram_chat_id column on
# User), not a hardcoded dict -- fine for a single-client deployment for now.
CHAT_ID_TO_CLIENT = {
    settings.ERIC_TELEGRAM_CHAT_ID: {
        "name": "Eric Taylor",
        "user_id": settings.ERIC_USER_ID,
    },
}


def _resolve_client(chat_id: int) -> Optional[dict]:
    return CHAT_ID_TO_CLIENT.get(chat_id)


async def cmd_today(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/today -> pulls the existing recommendation + narration and sends it."""
    chat_id = update.effective_chat.id
    identity = _resolve_client(chat_id)
    if not identity:
        await update.message.reply_text("This chat isn't linked to a coaching profile yet.")
        return

    try:
        rec = await get_todays_recommendation(identity["name"])
    except Exception:
        logger.exception("Failed to fetch today's recommendation for %s", identity["name"])
        await update.message.reply_text(
            "Couldn't pull today's plan right now — the recommendations service "
            "may be down. Try again in a few minutes."
        )
        return

    narration = rec.get("narration") or rec.get("prescription", "No prescription available.")
    await update.message.reply_text(narration)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Commands:\n"
        "/today - get today's workout/recovery plan\n"
        "Just tell me things like:\n"
        "  'my knee hurts' - flags safety/modification\n"
        "  'bench press 3x8 @ 100lbs' - logs a set\n"
        "  'I'm exhausted' - requests an easier version of today's plan"
    )


async def handle_free_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Catch-all handler for natural language: set logging, fatigue/pain
    reports, and modification requests all come through here and get
    classified by the LLM before any DB write happens.
    """
    chat_id = update.effective_chat.id
    identity = _resolve_client(chat_id)
    if not identity:
        await update.message.reply_text("This chat isn't linked to a coaching profile yet.")
        return

    if not identity["user_id"]:
        await update.message.reply_text(
            "This chat is linked to a coaching profile, but no user_id is "
            "configured (ERIC_USER_ID is empty in .env) — set logging won't "
            "work until that's set."
        )

    text = update.message.text.strip()
    state = await get_or_create_conversation_state(identity["name"])

    try:
        classification = await llm_client.classify_message_intent(text)
    except Exception:
        logger.exception("Intent classification failed for message: %s", text)
        await update.message.reply_text(
            "Had trouble understanding that — mind rephrasing? "
            "(e.g. 'bench press 3x8 @ 100lbs' or 'my knee hurts')"
        )
        return

    intent = classification.get("intent")

    if intent == "log_set":
        parsed = parse_set_from_text(text) or classification.get("parsed_set")
        if not parsed:
            await update.message.reply_text(
                "Couldn't parse that as a set. Try: 'Bench press 3x8 @ 100lbs'"
            )
            return
        result = await log_set(identity["user_id"], parsed, workout_context=state.current_exercise)
        if result.get("status") == "unresolved_exercise":
            await update.message.reply_text(result["message"])
        else:
            await update.message.reply_text(
                f"Logged: {parsed['exercise']} {parsed['sets']}x{parsed['reps']} "
                f"@ {parsed['weight']}lbs."
            )
        return

    if intent == "safety_escalation":
        await update.message.reply_text(
            "Got it — flagging that and pausing today's plan. "
            "Please don't push through pain. I'll note this and we'll "
            "reassess before your next session."
        )
        return

    if intent == "modification_request":
        try:
            adjusted = await llm_client.generate_adjusted_prescription(
                client=identity["name"], reason=text
            )
        except Exception:
            logger.exception("Failed to generate adjusted prescription for %s", identity["name"])
            await update.message.reply_text(
                "Noted, but couldn't regenerate the plan right now. "
                "Default to an easier version and take it slow today."
            )
            return
        await update.message.reply_text(adjusted["narration"])
        return

    await update.message.reply_text(
        "Not sure how to act on that yet. Use /help to see what I can do."
    )


def build_telegram_app() -> Application:
    """Constructs the python-telegram-bot Application used by the webhook route."""
    application = (
        ApplicationBuilder()
        .token(settings.TELEGRAM_BOT_TOKEN)
        .build()
    )
    application.add_handler(CommandHandler("today", cmd_today))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_free_text))
    return application
