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

import logging
import re

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


def _extract_content(response) -> str:
    message = response.choices[0].message
    content = getattr(message, "content", None)

    if content and content.strip():
        cleaned = _strip_leaked_reasoning(content.strip())
        if cleaned and not _looks_like_echoed_template(cleaned):
            return cleaned

    reasoning = getattr(message, "reasoning", None) or getattr(message, "reasoning_content", None)
    if reasoning and reasoning.strip():
        cleaned = _strip_leaked_reasoning(reasoning.strip())
        if cleaned and not _looks_like_echoed_template(cleaned):
            return cleaned

    raise ValueError("Model returned an empty, leaked-reasoning, or echoed-template completion")


async def _call_openrouter(prompt: str) -> str:
    fallback_chain = settings.openrouter_models
    primary, *rest = fallback_chain
    rest = rest[:MAX_FALLBACK_MODELS]

    response = await _openrouter_client.chat.completions.create(
        model=primary,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        max_tokens=150,
        timeout=settings.LLM_TIMEOUT_SECONDS,
        extra_body={"models": rest} if rest else {},
    )
    return _extract_content(response)


async def _call_ollama(prompt: str) -> str:
    response = await _ollama_client.chat.completions.create(
        model=settings.OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        max_tokens=150,
        timeout=settings.LLM_TIMEOUT_SECONDS,
    )
    return _extract_content(response)


async def generate_coaching_narration(prompt: str) -> str:
    try:
        return await _call_openrouter(prompt)
    except Exception as exc:
        logger.warning("OpenRouter (all models in chain) failed (%s), falling back to local Ollama", exc)

    try:
        return await _call_ollama(prompt)
    except Exception as exc:
        logger.error("Ollama fallback also failed: %s", exc)
        raise
