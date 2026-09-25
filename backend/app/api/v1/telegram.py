"""
FastAPI route that receives Telegram webhook updates and feeds them
into the python-telegram-bot Application.

Location: app/api/v1/telegram.py

Registered in app/main.py:
    - router included via app.include_router(telegram_router, prefix="/api/v1")
    - start_telegram() / stop_telegram() called from main.py's lifespan,
      since APIRouter has no on_event/startup hooks of its own.

Required settings (app/config.py / .env):
    TELEGRAM_BOT_TOKEN      - from @BotFather
    TELEGRAM_WEBHOOK_SECRET - random string you generate, verified via
                              the X-Telegram-Bot-Api-Secret-Token header
    PUBLIC_BASE_URL         - public HTTPS URL Telegram can reach
                              (e.g. an ngrok URL during development)
"""

import logging

from fastapi import APIRouter, HTTPException, Request
from telegram import Update

from app.config import settings
from app.services.telegram_bot import build_telegram_app

logger = logging.getLogger("telegram_webhook")

router = APIRouter(prefix="/telegram", tags=["telegram"])

telegram_app = build_telegram_app()


async def start_telegram() -> None:
    await telegram_app.initialize()

    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN is not set — skipping webhook registration.")
        return

    if not settings.PUBLIC_BASE_URL:
        logger.warning(
            "PUBLIC_BASE_URL is not set — skipping webhook registration. "
            "Set it to a public HTTPS URL (e.g. an ngrok tunnel) to enable Telegram."
        )
        return

    webhook_url = f"{settings.PUBLIC_BASE_URL.rstrip('/')}/api/v1/telegram/webhook"
    await telegram_app.bot.set_webhook(
        url=webhook_url,
        secret_token=settings.TELEGRAM_WEBHOOK_SECRET or None,
    )
    logger.info("Telegram webhook registered at %s", webhook_url)


async def stop_telegram() -> None:
    await telegram_app.shutdown()


@router.post("/webhook")
async def telegram_webhook(request: Request) -> dict:
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if settings.TELEGRAM_WEBHOOK_SECRET and secret != settings.TELEGRAM_WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid webhook secret")

    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)

    try:
        await telegram_app.process_update(update)
    except Exception:
        logger.exception("Error processing Telegram update: %s", data)
        return {"ok": True}

    return {"ok": True}


@router.get("/health")
async def telegram_health() -> dict:
    info = await telegram_app.bot.get_webhook_info()
    return {
        "configured": bool(settings.TELEGRAM_BOT_TOKEN and settings.PUBLIC_BASE_URL),
        "webhook_url": info.url,
        "pending_update_count": info.pending_update_count,
        "last_error_message": info.last_error_message,
    }