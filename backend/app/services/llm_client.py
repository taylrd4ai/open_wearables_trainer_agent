"""LLM wrapper using OpenRouter's native model-fallback routing, with local
Ollama as the final fallback if OpenRouter is unreachable entirely.

OpenRouter caps the `models` fallback array at 3 entries, so the full chain
(primary + fallbacks) supports at most 4 models total.

Free/random-router models selected via `openrouter/free` have shown two
distinct failure modes so far:
1. Leaked reasoning/meta-commentary in the content field
   (e.g. "We need to respond as a supportive coach...").
2. Verbatim echo of the input prompt template instead of a real answer
   (e.g. "Prescription: ... Detail: ... Recovery tier: ...").
Both are detected and rejected below; if nothing usable survives, we move to
the next model in the fallback chain (and ultimately to local Ollama).

Docs: https://openrouter.ai/docs/guides/routing/model-fallbacks
      https://openrouter.ai/docs/guides/routing/routers/free-router
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a supportive strength and conditioning coach speaking directly "
    "to your client. You are given a fixed workout prescription and readiness "
    "data as background context only -- do not repeat, quote, or restate any "
    "of the input labels or values (e.g. 'Prescription:', 'Detail:', "
    "'Recovery tier:', 'Recovery score:'). Reply with ONLY your own original "
    "2-3 sentence coaching message in plain conversational language -- no "
    "meta-commentary, no restating these instructions, no explaining your "
    "reasoning process, no phrases like 'we need to' or 'I should respond'. "
    "Never change the prescribed exercises, sets, reps, or loads."
)

INTENT_SYSTEM_PROMPT = (
    "You classify short messages from a fitness client to their AI coach "
    "into exactly one intent. Respond with ONLY a JSON object, no other "
    "text, no markdown, no reasoning, no meta-commentary.\n\n"
    "Valid intents:\n"
    '- "log_set": client is reporting a completed exercise set '
    '(e.g. "bench press 3x8 @ 100lbs", "did 3 sets of squats at 135").\n'
    '- "safety_escalation": client mentions pain, swelling, locking, '
    "giving-way, instability, or any injury-related symptom.\n"
    '- "modification_request": client wants today\'s plan adjusted due to '
    "fatigue, soreness, time constraints, or low motivation, WITHOUT "
    "mentioning pain/injury.\n"
    '- "general_question": anything else (questions, greetings, unclear '
    "input).\n\n"
    "JSON shape:\n"
    '{"intent": "<one of the four above>", "parsed_set": '
    '{"exercise": str, "sets": int, "reps": int, "weight": float or null} '
    "or null}\n\n"
    'Only populate "parsed_set" when intent is "log_set" AND you can '
    'confidently extract exercise/sets/reps. Otherwise set it to null.'
)

ADJUSTMENT_SYSTEM_PROMPT = (
    "You are a concise, safety-conscious strength and conditioning coach. "
    "The client has reported a reason today's workout should be modified "
    "(fatigue, soreness, time constraint, low motivation -- NOT pain or "
    "injury, that is handled separately). Given their reason, produce a "
    "short, encouraging, SPECIFIC adjusted prescription: reduced volume, "
    "lower intensity, or a swap to an easier template. Keep it under 80 "
    "words, plain text, no headers, no markdown, no meta-commentary, ready "
    "to send directly as a chat message."
)

MAX_FALLBACK_MODELS = 3  # OpenRouter hard limit on the `models` array

_META_LINE_PATTERN = re.compile(
    r"^\s*(we need to|i need to|i should|let me|the (user|system|task) (wants|asks)|"
    r"as an ai|okay,? (so|let)|first,? i|so,? i (need|should|will))",
    re.IGNORECASE,
)

# Catches verbatim echo of our own prompt template labels -- a real coaching
# message would never use these exact structured field names.
_ECHOED_TEMPLATE_PATTERN = re.compile(
    r"(prescription:|detail:|recovery tier:|recovery score:|sleep score:|"
    r"played soccer yesterday:|high strain yesterday:)",
    re.IGNORECASE,
)


def _strip_leaked_reasoning(text: str) -> str:
    if not _META_LINE_PATTERN.match(text):
        return text
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    for para in paragraphs:
        if not _META_LINE_PATTERN.match(para):
            return para
    sentences = re.split(r"(?<=[.!?])\s+", text)
    kept = [s for s in sentences if not _META_LINE_PATTERN.match(s)]
    return " ".join(kept).strip()


def _looks_like_echoed_template(text: str) -> bool:
    return bool(_ECHOED_TEMPLATE_PATTERN.search(text))


_openrouter_client = AsyncOpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url=settings.OPENROUTER_BASE_URL,
    default_headers={
        "HTTP-Referer": settings.OPENROUTER_SITE_URL,
        "X-Title": settings.OPENROUTER_APP_NAME,
    },
)

_ollama_client = AsyncOpenAI(
    api_key="ollama",
    base_url=settings.OLLAMA_BASE_URL,
)


def _extract_content(response, validate: bool = True) -> str:
    """
    Pulls the usable text out of a chat completion response.
    When validate=True (narration use cases), applies leaked-reasoning
    and echoed-template rejection. When validate=False (structured JSON
    use cases), just returns raw content/reasoning -- JSON validity is
    checked separately by the caller.
    """
    message = response.choices[0].message
    content = getattr(message, "content", None)

    if content and content.strip():
        if not validate:
            return content.strip()
        cleaned = _strip_leaked_reasoning(content.strip())
        if cleaned and not _looks_like_echoed_template(cleaned):
            return cleaned

    reasoning = getattr(message, "reasoning", None) or getattr(message, "reasoning_content", None)
    if reasoning and reasoning.strip():
        if not validate:
            return reasoning.strip()
        cleaned = _strip_leaked_reasoning(reasoning.strip())
        if cleaned and not _looks_like_echoed_template(cleaned):
            return cleaned

    raise ValueError("Model returned an empty, leaked-reasoning, or echoed-template completion")


# --------------------------------------------------------------------------
# Low-level provider calls
# --------------------------------------------------------------------------

async def _call_openrouter(
    messages: List[Dict[str, str]],
    response_format: Optional[Dict[str, Any]] = None,
    validate: bool = True,
) -> str:
    fallback_chain = settings.openrouter_models
    primary, *rest = fallback_chain
    rest = rest[:MAX_FALLBACK_MODELS]

    extra_body: Dict[str, Any] = {}
    if rest:
        extra_body["models"] = rest

    kwargs: Dict[str, Any] = dict(
        model=primary,
        messages=messages,
        temperature=0.4,
        max_tokens=150,
        timeout=settings.LLM_TIMEOUT_SECONDS,
        extra_body=extra_body,
    )
    if response_format:
        kwargs["response_format"] = response_format

    response = await _openrouter_client.chat.completions.create(**kwargs)
    return _extract_content(response, validate=validate)


async def _call_ollama(
    messages: List[Dict[str, str]],
    response_format: Optional[Dict[str, Any]] = None,
    validate: bool = True,
) -> str:
    kwargs: Dict[str, Any] = dict(
        model=settings.OLLAMA_MODEL,
        messages=messages,
        temperature=0.4,
        max_tokens=150,
        timeout=settings.LLM_TIMEOUT_SECONDS,
    )
    if response_format:
        kwargs["response_format"] = response_format

    response = await _ollama_client.chat.completions.create(**kwargs)
    return _extract_content(response, validate=validate)


async def _generate(
    messages: List[Dict[str, str]],
    response_format: Optional[Dict[str, Any]] = None,
    validate: bool = True,
) -> str:
    """Shared OpenRouter -> Ollama fallback dance, used by all public functions."""
    try:
        return await _call_openrouter(messages, response_format=response_format, validate=validate)
    except Exception as exc:
        logger.warning("OpenRouter (all models in chain) failed (%s), falling back to local Ollama", exc)

    try:
        return await _call_ollama(messages, response_format=response_format, validate=validate)
    except Exception as exc:
        logger.error("Ollama fallback also failed: %s", exc)
        raise


# --------------------------------------------------------------------------
# Public: coaching narration (unchanged from existing behavior)
# --------------------------------------------------------------------------

async def generate_coaching_narration(prompt: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    return await _generate(messages, validate=True)


# --------------------------------------------------------------------------
# Public: Telegram bot support
# --------------------------------------------------------------------------

async def classify_message_intent(text: str) -> Dict[str, Any]:
    """
    Classifies a free-text Telegram message into one of four intents.
    Used by telegram_bot.py's handle_free_text() before any DB write
    or safety response happens. Uses JSON mode where the provider
    supports it, since structured output is far more reliable than
    hoping the model formats plain text correctly.
    """
    messages = [
        {"role": "system", "content": INTENT_SYSTEM_PROMPT},
        {"role": "user", "content": text},
    ]
    response_format = {"type": "json_object"}

    try:
        raw = await _generate(messages, response_format=response_format, validate=False)
    except Exception as exc:
        logger.error("classify_message_intent: all providers failed (%s)", exc)
        return {"intent": "general_question", "parsed_set": None}

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("classify_message_intent got non-JSON response: %s", raw[:200])
        return {"intent": "general_question", "parsed_set": None}

    if parsed.get("intent") not in {
        "log_set",
        "safety_escalation",
        "modification_request",
        "general_question",
    }:
        parsed["intent"] = "general_question"

    return parsed


async def generate_adjusted_prescription(client: str, reason: str) -> Dict[str, Any]:
    """
    Generates a modified/easier version of today's plan based on a
    free-text reason (e.g. "I'm exhausted"). Used by telegram_bot.py's
    "modification_request" branch. Reuses the same leaked-reasoning /
    echoed-template validation as coaching narration, since this is
    also a free-text conversational response.
    """
    messages = [
        {"role": "system", "content": ADJUSTMENT_SYSTEM_PROMPT},
        {"role": "user", "content": f"Client: {client}\nReason for modification: {reason}"},
    ]
    narration = await _generate(messages, validate=True)
    return {"narration": narration.strip()}
