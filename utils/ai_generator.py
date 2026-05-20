"""AI generation module using xAI Grok API (OpenAI-compatible)."""

from __future__ import annotations

import time
from typing import Dict

from openai import APIConnectionError, APIStatusError, OpenAI, RateLimitError

from utils.config import get_xai_api_key
from utils.helpers import parse_ai_response
from utils.prompts import build_system_prompt, build_user_prompt


class AIGenerationError(Exception):
    """Raised when SEO content generation fails."""


def get_client() -> OpenAI:
    """Initialize and return the xAI client."""
    api_key = get_xai_api_key()
    if not api_key:
        raise AIGenerationError("Missing XAI_API_KEY. Please configure it in your environment.")
    return OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")


def generate_seo_content(payload: Dict[str, object], retries: int = 3, timeout: int = 90) -> Dict[str, object]:
    """Generate SEO content with retry logic and robust error handling."""
    client = get_client()

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            response = client.chat.completions.create(
                model="grok-3-beta",
                messages=[
                    {"role": "system", "content": build_system_prompt()},
                    {"role": "user", "content": build_user_prompt(payload)},
                ],
                temperature=0.7,
                timeout=timeout,
            )

            if not response.choices or not response.choices[0].message:
                raise AIGenerationError("Empty response from AI service.")

            content = response.choices[0].message.content or ""
            parsed = parse_ai_response(content)

            if not parsed.get("seo_title") or not parsed.get("meta_description"):
                raise AIGenerationError("AI response is incomplete. Please retry.")

            return parsed

        except RateLimitError as exc:
            last_error = AIGenerationError("Rate limit reached. Please wait and try again.")
        except APIConnectionError as exc:
            last_error = AIGenerationError("Network error while connecting to xAI API.")
        except APIStatusError as exc:
            if exc.status_code == 401:
                last_error = AIGenerationError("Invalid API key. Please verify XAI_API_KEY.")
            elif exc.status_code == 408:
                last_error = AIGenerationError("Request timeout from xAI API.")
            else:
                last_error = AIGenerationError(f"xAI API error: HTTP {exc.status_code}.")
        except Exception as exc:  # pragma: no cover - defensive fallback
            last_error = AIGenerationError(f"Unexpected generation error: {exc}")

        if attempt < retries:
            time.sleep(min(2 * attempt, 5))

    raise last_error or AIGenerationError("Generation failed after retries.")
