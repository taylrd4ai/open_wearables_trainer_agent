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

# Map Telegram chat_id -> internal client/user id.
# In production this should be a DB lookup (users.telegram_chat_id),
# not a hardcoded dict.
CHAT_ID_TO_CLIENT = {
    settings.ERIC_TELEGRAM_CHAT_ID: "Eric Taylor",
}


def _resolve_client(chat_id: int) -> Optional[str]:
    return CHAT_ID_TO_CLIENT.get(chat_id)


async def cmd_today(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/today -> pulls the existing recommendation + narration and sends it."""
    chat_id = update.effective_chat.id
    client = _resolve_client(chat_id)
    if not client:
        await update.message.reply_text("This chat isn't linked to a coaching profile yet.")
        return

    try:
        rec = await get_todays_recommendation(client)
    except Exception:
        logger.exception("Failed to fetch today's recommendation for %s", client)
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
    client = _resolve_client(chat_id)
    if not client:
        await update.message.reply_text("This chat isn't linked to a coaching profile yet.")
        return

    text = update.message.text.strip()
    state = await get_or_create_conversation_state(client)

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
        await log_set(client, parsed, workout_context=state.current_exercise)
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
                client=client, reason=text
            )
        except Exception:
            logger.exception("Failed to generate adjusted prescription for %s", client)
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
