"""AI generation module using xAI Grok API (OpenAI-compatible)."""

from __future__ import annotations

import time
from typing import Dict, List

from openai import APIConnectionError, APIStatusError, OpenAI, RateLimitError

from .config import get_xai_api_key, get_xai_model
from .parsing import parse_ai_response
from .prompts import build_system_prompt, build_user_prompt


class AIGenerationError(Exception):
    """Raised when SEO content generation fails."""


# Valid xAI aliases (see https://docs.x.ai/developers/models/grok-4.3)
DEFAULT_MODEL_FALLBACKS: List[str] = [
    "grok-3-beta",
    "grok-3-mini-beta",
    "grok-3-mini",
    "grok-3",
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
            if isinstance(error_obj, str):
                return error_obj
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


def _build_failure_message(failures: List[str]) -> str:
    """Create a single actionable error from model attempts."""
    lines = "\n".join([f"- {item}" for item in failures])
    return (
        "No xAI model worked for your API key.\n"
        f"{lines}\n\n"
        "What to do:\n"
        "1. In Streamlit secrets set: XAI_MODEL = \"grok-3-beta\"\n"
        "2. Reboot app after saving secrets.\n"
        "3. Check https://console.x.ai → Billing (API credits are required).\n"
        "4. Check https://console.x.ai → Models for enabled models on your team."
    )


def generate_seo_content(payload: Dict[str, object], retries: int = 3) -> Dict[str, object]:
    """Generate SEO content with retry logic and robust error handling."""
    client = get_client()
    models = _model_candidates()
    failures: List[str] = []

    for model in models:
        for attempt in range(1, retries + 1):
            try:
                content = _request_completion(client, model, payload)
                parsed = parse_ai_response(content)

                if not parsed.get("seo_title") or not parsed.get("meta_description"):
                    raise AIGenerationError("AI response is incomplete. Please retry.")

                return parsed

            except RateLimitError:
                if attempt >= retries:
                    failures.append(f"{model}: rate limit reached")
                    break
                time.sleep(min(2 * attempt, 5))
                continue

            except APIConnectionError:
                if attempt >= retries:
                    failures.append(f"{model}: network error")
                    break
                time.sleep(min(2 * attempt, 5))
                continue

            except APIStatusError as exc:
                detail = _format_api_error(exc)
                if exc.status_code == 401:
                    raise AIGenerationError("Invalid API key. Please verify XAI_API_KEY.") from exc

                if exc.status_code in {400, 404}:
                    failures.append(f"{model}: {detail}")
                    break

                if exc.status_code in {402, 403} or "credit" in detail.lower() or "balance" in detail.lower():
                    failures.append(f"{model}: insufficient credits")
                    break

                if exc.status_code == 408:
                    if attempt >= retries:
                        failures.append(f"{model}: request timeout")
                        break
                    time.sleep(min(2 * attempt, 5))
                    continue

                failures.append(f"{model}: HTTP {exc.status_code} - {detail}")
                break

            except AIGenerationError:
                raise
            except Exception as exc:
                failures.append(f"{model}: {exc}")
                break

    raise AIGenerationError(_build_failure_message(failures))
