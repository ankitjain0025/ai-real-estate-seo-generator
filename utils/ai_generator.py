"""AI generation module using xAI Grok API (OpenAI-compatible)."""

from __future__ import annotations

import time
from typing import Dict, List

from openai import APIConnectionError, APIStatusError, OpenAI, RateLimitError

from utils.config import get_xai_api_key, get_xai_model
from utils.helpers import parse_ai_response
from utils.prompts import build_system_prompt, build_user_prompt


class AIGenerationError(Exception):
    """Raised when SEO content generation fails."""


# Free / legacy-friendly models first (avoid paid flagship defaults).
DEFAULT_MODEL_FALLBACKS: List[str] = [
    "grok-3-beta",
    "grok-beta",
    "grok-3",
    "grok-2-1212",
]


def get_client() -> OpenAI:
    """Initialize and return the xAI client."""
    api_key = get_xai_api_key()
    if not api_key:
        raise AIGenerationError("Missing XAI_API_KEY. Please configure it in your environment.")
    return OpenAI(api_key=api_key, base_url="https://api.x.ai/v1", timeout=120.0)


def _model_candidates() -> List[str]:
    """Build ordered model list: configured model first, then known fallbacks."""
    preferred = get_xai_model()
    candidates = [preferred]
    for model in DEFAULT_MODEL_FALLBACKS:
        if model not in candidates:
            candidates.append(model)
    return candidates


def _format_api_error(exc: APIStatusError) -> str:
    """Extract readable API error details."""
    try:
        body = exc.body
        if isinstance(body, dict):
            error_obj = body.get("error")
            if isinstance(error_obj, dict) and error_obj.get("message"):
                return str(error_obj["message"])
            if body.get("message"):
                return str(body["message"])
    except Exception:
        pass
    return str(exc)


def _request_completion(client: OpenAI, model: str, payload: Dict[str, object]) -> str:
    """Call chat completions and return assistant text."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": build_user_prompt(payload)},
        ],
        temperature=0.7,
    )

    if not response.choices or not response.choices[0].message:
        raise AIGenerationError("Empty response from AI service.")

    content = response.choices[0].message.content or ""
    if not content.strip():
        raise AIGenerationError("Empty response from AI service.")
    return content


def generate_seo_content(payload: Dict[str, object], retries: int = 3) -> Dict[str, object]:
    """Generate SEO content with retry logic and robust error handling."""
    client = get_client()
    models = _model_candidates()
    last_error: Exception | None = None

    for model in models:
        for attempt in range(1, retries + 1):
            try:
                content = _request_completion(client, model, payload)
                parsed = parse_ai_response(content)

                if not parsed.get("seo_title") or not parsed.get("meta_description"):
                    raise AIGenerationError("AI response is incomplete. Please retry.")

                return parsed

            except RateLimitError:
                last_error = AIGenerationError("Rate limit reached. Please wait and try again.")
            except APIConnectionError:
                last_error = AIGenerationError("Network error while connecting to xAI API.")
            except APIStatusError as exc:
                detail = _format_api_error(exc)
                if exc.status_code == 401:
                    raise AIGenerationError("Invalid API key. Please verify XAI_API_KEY.") from exc
                if exc.status_code in {400, 404}:
                    last_error = AIGenerationError(
                        f"xAI model '{model}' rejected the request: {detail}. Trying fallback model..."
                    )
                    break
                if exc.status_code in {402, 403} or "credit" in detail.lower() or "balance" in detail.lower():
                    last_error = AIGenerationError(
                        f"Insufficient credits for model '{model}'. "
                        "Use free-tier models in secrets: XAI_MODEL = \"grok-3-beta\"."
                    )
                    break
                if exc.status_code == 408:
                    last_error = AIGenerationError("Request timeout from xAI API.")
                else:
                    last_error = AIGenerationError(f"xAI API error (HTTP {exc.status_code}): {detail}")
            except AIGenerationError:
                raise
            except Exception as exc:
                last_error = AIGenerationError(f"Unexpected generation error: {exc}")

            if attempt < retries:
                time.sleep(min(2 * attempt, 5))

    if last_error:
        raise last_error
    raise AIGenerationError("Generation failed after retries.")
