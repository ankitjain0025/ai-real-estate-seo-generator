"""AI generation module using Google Gemini API (google-genai SDK)."""

from __future__ import annotations

import time
from typing import Dict, List

from google import genai
from google.genai import types

from .config import get_gemini_api_key, get_gemini_model
from .parsing import parse_ai_response
from .prompts import build_system_prompt, build_user_prompt


class AIGenerationError(Exception):
    """Raised when SEO content generation fails."""


def get_client() -> genai.Client:
    """Initialize and return a configured Gemini client."""
    api_key = get_gemini_api_key()
    if not api_key:
        raise AIGenerationError(
            "Missing GEMINI_API_KEY. Please add it to your Streamlit secrets or .env file."
        )
    return genai.Client(api_key=api_key)


def _request_completion(client: genai.Client, payload: Dict[str, object]) -> str:
    """Call Gemini generate_content and return the response text."""
    response = client.models.generate_content(
        model=get_gemini_model(),
        contents=build_user_prompt(payload),
        config=types.GenerateContentConfig(
            system_instruction=build_system_prompt(),
            temperature=0.7,
            response_mime_type="application/json",
        ),
    )

    text = ""
    try:
        text = response.text
    except Exception:
        pass

    if not text or not text.strip():
        raise AIGenerationError(
            "Empty response from Gemini. The request may have been blocked by safety filters."
        )

    return text


def generate_seo_content(payload: Dict[str, object], retries: int = 3) -> Dict[str, object]:
    """Generate SEO content with retry logic and robust error handling."""
    try:
        client = get_client()
    except AIGenerationError:
        raise

    failures: List[str] = []
    model_name = get_gemini_model()

    for attempt in range(1, retries + 1):
        try:
            content_text = _request_completion(client, payload)
            parsed = parse_ai_response(content_text)

            if not parsed.get("seo_title") or not parsed.get("meta_description"):
                raise AIGenerationError("AI response is incomplete. Please retry.")

            return parsed

        except AIGenerationError:
            raise

        except Exception as exc:
            error_str = str(exc)

            if any(kw in error_str.lower() for kw in ("quota", "rate", "resource_exhausted", "429")):
                if attempt >= retries:
                    failures.append(f"{model_name}: rate limit / quota exceeded — {error_str}")
                    break
                time.sleep(min(2 * attempt, 6))
                continue

            if any(kw in error_str.lower() for kw in ("api_key", "invalid", "401", "403", "permission")):
                raise AIGenerationError(
                    f"Invalid or unauthorised GEMINI_API_KEY. "
                    f"Verify your key at https://aistudio.google.com/app/apikey.\n\nDetail: {error_str}"
                ) from exc

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
