"""AI generation module using Google Gemini API."""

from __future__ import annotations

import time
from typing import Dict, List

import google.generativeai as genai

from .config import get_gemini_api_key, get_gemini_model
from .parsing import parse_ai_response
from .prompts import build_system_prompt, build_user_prompt


class AIGenerationError(Exception):
    """Raised when SEO content generation fails."""


def _configure_genai() -> None:
    """Configure the Gemini SDK with the resolved API key."""
    api_key = get_gemini_api_key()
    if not api_key:
        raise AIGenerationError(
            "Missing GEMINI_API_KEY. Please add it to your Streamlit secrets or .env file."
        )
    genai.configure(api_key=api_key)


def get_client() -> genai.GenerativeModel:
    """Initialize and return a configured Gemini GenerativeModel."""
    _configure_genai()
    return genai.GenerativeModel(get_gemini_model())


def _request_completion(model: genai.GenerativeModel, payload: Dict[str, object]) -> str:
    """Call Gemini generate_content and return the response text."""
    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(payload)

    # Combine system + user prompt as a single turn (Gemini 2.5 Flash supports
    # system_instruction natively; fall back to prefixing if unavailable).
    try:
        response = model.generate_content(
            user_prompt,
            generation_config=genai.GenerationConfig(temperature=0.7),
        )
    except Exception:
        # Re-raise so the retry loop can categorise the error.
        raise

    text = ""
    try:
        text = response.text
    except Exception:
        # response.text raises ValueError when the response is blocked.
        pass

    if not text or not text.strip():
        raise AIGenerationError("Empty response from Gemini. The request may have been blocked by safety filters.")

    return text


def generate_seo_content(payload: Dict[str, object], retries: int = 3) -> Dict[str, object]:
    """Generate SEO content with retry logic and robust error handling."""
    try:
        model = get_client()
    except AIGenerationError:
        raise

    failures: List[str] = []
    model_name = get_gemini_model()

    for attempt in range(1, retries + 1):
        try:
            content_text = _request_completion(model, payload)
            parsed = parse_ai_response(content_text)

            if not parsed.get("seo_title") or not parsed.get("meta_description"):
                raise AIGenerationError("AI response is incomplete. Please retry.")

            return parsed

        except AIGenerationError:
            raise

        except Exception as exc:
            error_str = str(exc)

            # Rate limit / quota errors — wait and retry
            if any(kw in error_str.lower() for kw in ("quota", "rate", "resource_exhausted", "429")):
                if attempt >= retries:
                    failures.append(f"{model_name}: rate limit / quota exceeded — {error_str}")
                    break
                time.sleep(min(2 * attempt, 6))
                continue

            # Auth errors — fail fast
            if any(kw in error_str.lower() for kw in ("api_key", "invalid", "401", "403", "permission")):
                raise AIGenerationError(
                    f"Invalid or unauthorised GEMINI_API_KEY. "
                    f"Verify your key at https://aistudio.google.com/app/apikey.\n\nDetail: {error_str}"
                ) from exc

            # Network errors — retry
            if any(kw in error_str.lower() for kw in ("connection", "timeout", "network", "unavailable")):
                if attempt >= retries:
                    failures.append(f"{model_name}: network error — {error_str}")
                    break
                time.sleep(min(2 * attempt, 6))
                continue

            failures.append(f"{model_name}: {error_str}")
            break

    failure_lines = "\n".join([f"- {item}" for item in failures])
    raise AIGenerationError(
        f"Gemini content generation failed after {retries} attempt(s).\n\n"
        f"{failure_lines}\n\n"
        "What to try:\n"
        "1. Check your GEMINI_API_KEY in Streamlit secrets.\n"
        "2. Verify quota at https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas\n"
        "3. Reboot the app (Manage app → Reboot app) after updating secrets."
    )
