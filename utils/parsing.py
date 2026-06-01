"""AI response parsing helpers."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from .schema import (
    VALID_DIFFICULTIES,
    VALID_INTENTS,
    default_keyword,
    default_output,
    required_keys,
)


def _strip_markdown_fences(text: str) -> str:
    """Remove ```json ... ``` or ``` ... ``` wrappers that Gemini adds."""
    text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text.strip())
    return text.strip()


def _extract_first_json_blob(text: str) -> str:
    """Attempt to extract the first JSON object from plain text."""
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    return match.group(0) if match else text


def _normalize_string_list(value: Any, target_count: int, prefix: str = "") -> List[str]:
    """Convert a list of plain strings into a cleaned capped list."""
    items: List[str] = []
    if isinstance(value, list):
        for v in value:
            if isinstance(v, str) and v.strip():
                items.append(v.strip())
            elif isinstance(v, dict) and v.get("keyword"):
                # Fallback: Gemini returned keyword objects here instead of strings
                items.append(str(v["keyword"]).strip())
    elif isinstance(value, str) and value.strip():
        parts = re.split(r"[\n,;]+", value)
        items = [p.strip() for p in parts if p.strip()]

    cleaned: List[str] = []
    seen: set = set()
    for item in items:
        candidate = item
        if prefix and not candidate.startswith(prefix):
            candidate = f"{prefix}{candidate.lstrip('#')}"
        key = candidate.lower()
        if key not in seen:
            seen.add(key)
            cleaned.append(candidate)

    return cleaned[:target_count]


def _normalize_keyword_object(raw: Any, fallback_keyword: str = "") -> Dict[str, object]:
    """Normalize a single keyword entry into a validated keyword object."""
    if isinstance(raw, str):
        # Plain string — wrap into object with defaults
        return default_keyword(keyword=raw.strip())

    if not isinstance(raw, dict):
        return default_keyword(keyword=fallback_keyword)

    keyword = str(raw.get("keyword", fallback_keyword)).strip()
    if not keyword:
        keyword = fallback_keyword

    # Score: clamp to 1-100 integer
    try:
        score = max(1, min(100, int(float(str(raw.get("score", 50))))))
    except (ValueError, TypeError):
        score = 50

    # Difficulty: validate against allowed values
    difficulty = str(raw.get("difficulty", "Medium")).strip().capitalize()
    if difficulty not in VALID_DIFFICULTIES:
        difficulty = "Medium"

    # Intent: validate against allowed values
    intent = str(raw.get("intent", "Commercial")).strip().capitalize()
    # Handle partial matches e.g. "transactional" -> "Transactional"
    intent_map = {v.lower(): v for v in VALID_INTENTS}
    intent = intent_map.get(intent.lower(), "Commercial")

    suggestion = str(raw.get("suggestion", "Use in page content naturally")).strip()
    if not suggestion:
        suggestion = "Use in page content naturally"
    # Truncate very long suggestions
    if len(suggestion) > 80:
        suggestion = suggestion[:77] + "..."

    return {
        "keyword": keyword,
        "score": score,
        "difficulty": difficulty,
        "intent": intent,
        "suggestion": suggestion,
    }


def _normalize_keyword_list(value: Any, target_count: int = 15) -> List[Dict[str, object]]:
    """Parse and normalize a list of keyword objects, sorted by score descending."""
    raw_list: List[Any] = []

    if isinstance(value, list):
        raw_list = value
    elif isinstance(value, str) and value.strip():
        # Plain comma/newline separated keywords — convert to objects
        parts = re.split(r"[\n,;]+", value)
        raw_list = [p.strip() for p in parts if p.strip()]

    normalized: List[Dict[str, object]] = []
    seen: set = set()

    for i, item in enumerate(raw_list):
        obj = _normalize_keyword_object(item, fallback_keyword=f"keyword_{i+1}")
        kw_lower = obj["keyword"].lower()
        if kw_lower not in seen and obj["keyword"]:
            seen.add(kw_lower)
            normalized.append(obj)

    # Sort by score descending — highest value keywords first
    normalized.sort(key=lambda x: int(x["score"]), reverse=True)

    return normalized[:target_count]


def parse_ai_response(raw_text: str) -> Dict[str, object]:
    """Parse AI JSON response robustly and normalize schema."""
    parsed: Dict[str, object] = default_output()

    if not raw_text or not raw_text.strip():
        raise ValueError("Empty response from AI service.")

    # Step 1: strip markdown code fences
    cleaned = _strip_markdown_fences(raw_text)

    # Step 2: try direct JSON parse
    data = None
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Step 3: fallback — extract first {...} blob
    if data is None:
        blob = _extract_first_json_blob(cleaned)
        try:
            data = json.loads(blob)
        except json.JSONDecodeError as exc:
            raise ValueError("AI returned malformed JSON content.") from exc

    if not isinstance(data, dict):
        raise ValueError("AI response format is invalid.")

    # Populate base keys
    for key in required_keys():
        parsed[key] = data.get(key, parsed[key])

    # Normalize keyword objects (scored + sorted)
    parsed["seo_keywords"] = _normalize_keyword_list(parsed.get("seo_keywords"), 15)

    # Normalize plain string lists
    parsed["seo_hashtags"] = _normalize_string_list(parsed.get("seo_hashtags"), 25, prefix="#")
    parsed["blog_topics"] = _normalize_string_list(parsed.get("blog_topics"), 10)

    # Normalize string fields
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
