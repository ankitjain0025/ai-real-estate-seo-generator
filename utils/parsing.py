"""AI response parsing helpers."""

from __future__ import annotations

import json
import re
from typing import Dict, List

from .schema import default_output, required_keys


def _strip_markdown_fences(text: str) -> str:
    """Remove ```json ... ``` or ``` ... ``` wrappers that Gemini adds."""
    # Remove opening fence with optional language tag
    text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
    # Remove closing fence
    text = re.sub(r"\s*```$", "", text.strip())
    return text.strip()


def _extract_first_json_blob(text: str) -> str:
    """Attempt to extract the first JSON object from plain text."""
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    return match.group(0) if match else text


def _normalize_list(value: object, target_count: int, prefix: str = "") -> List[str]:
    """Convert list-like values into cleaned list with target max count."""
    items: List[str] = []
    if isinstance(value, list):
        items = [str(v).strip() for v in value if str(v).strip()]
    elif isinstance(value, str) and value.strip():
        parts = re.split(r"[\n,;]+", value)
        items = [p.strip() for p in parts if p.strip()]

    cleaned: List[str] = []
    seen = set()
    for item in items:
        candidate = item
        if prefix and not candidate.startswith(prefix):
            candidate = f"{prefix}{candidate.lstrip('#')}"
        key = candidate.lower()
        if key not in seen:
            seen.add(key)
            cleaned.append(candidate)

    return cleaned[:target_count]


def parse_ai_response(raw_text: str) -> Dict[str, object]:
    """Parse AI JSON response robustly and normalize schema."""
    parsed: Dict[str, object] = default_output()
    if not raw_text or not raw_text.strip():
        raise ValueError("Empty response from AI service.")

    # Step 1: strip markdown code fences (Gemini often wraps in ```json)
    cleaned = _strip_markdown_fences(raw_text)

    # Step 2: try parsing directly
    data = None
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Step 3: fallback — extract first {...} blob from the text
    if data is None:
        blob = _extract_first_json_blob(cleaned)
        try:
            data = json.loads(blob)
        except json.JSONDecodeError as exc:
            raise ValueError("AI returned malformed JSON content.") from exc

    if not isinstance(data, dict):
        raise ValueError("AI response format is invalid.")

    for key in required_keys():
        parsed[key] = data.get(key, parsed[key])

    parsed["seo_keywords"] = _normalize_list(parsed.get("seo_keywords"), 15)
    parsed["seo_hashtags"] = _normalize_list(parsed.get("seo_hashtags"), 25, prefix="#")
    parsed["blog_topics"] = _normalize_list(parsed.get("blog_topics"), 10)

    for key in [
        "seo_title",
        "meta_description",
        "google_snippet",
        "instagram_caption",
        "linkedin_caption",
        "short_description",
        "long_form_overview",
    ]:
        value = parsed.get(key, "")
        parsed[key] = str(value).strip() if value is not None else ""

    return parsed
