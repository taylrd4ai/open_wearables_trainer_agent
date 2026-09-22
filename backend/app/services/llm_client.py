"""LLM wrapper with OpenRouter (free model) as primary and local Ollama as fallback.

Both OpenRouter and Ollama expose OpenAI-compatible chat completion APIs,
so the same AsyncOpenAI client class works for both -- only base_url and
api_key differ. If the OpenRouter call fails (rate limit, network, free-tier
model unavailable, etc.), we transparently retry against the local Ollama
instance before giving up.
"""

import logging

from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a supportive strength and conditioning coach. "
    "You are given a fixed workout prescription and readiness data. "
    "Explain the reasoning in 2-3 short sentences. "
    "Never change the prescribed exercises, sets, reps, or loads."
)

_openrouter_client = AsyncOpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url=settings.OPENROUTER_BASE_URL,
    default_headers={
        "HTTP-Referer": settings.OPENROUTER_SITE_URL,
        "X-Title": settings.OPENROUTER_APP_NAME,
    },
)

_ollama_client = AsyncOpenAI(
    api_key="ollama",  # Ollama ignores the key but the SDK requires a non-empty string
    base_url=settings.OLLAMA_BASE_URL,
)


async def _call(client: AsyncOpenAI, model: str, prompt: str) -> str:
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        max_tokens=150,
        timeout=settings.LLM_TIMEOUT_SECONDS,
    )
    return response.choices[0].message.content.strip()


async def generate_coaching_narration(prompt: str) -> str:
    """
    Try the OpenRouter free model first. On any failure (rate limit,
    network error, model overloaded), fall back to local Ollama.
    Callers should still wrap this in their own try/except for a final
    deterministic fallback if both LLM paths are unavailable.
    """
    try:
        return await _call(_openrouter_client, settings.OPENROUTER_MODEL, prompt)
    except Exception as exc:
        logger.warning("OpenRouter call failed (%s), falling back to local Ollama", exc)

    try:
        return await _call(_ollama_client, settings.OLLAMA_MODEL, prompt)
    except Exception as exc:
        logger.error("Ollama fallback also failed: %s", exc)
        raise
