"""Shared output schema constants (no internal utils dependencies)."""

from __future__ import annotations

from typing import Dict, List

OUTPUT_KEYS: List[str] = [
    "seo_title",
    "meta_description",
    "seo_keywords",
    "google_snippet",
    "instagram_caption",
    "linkedin_caption",
    "seo_hashtags",
    "blog_topics",
    "short_description",
    "long_form_overview",
]

# Expected fields for each keyword object
KEYWORD_FIELDS = ("keyword", "score", "difficulty", "intent", "suggestion")
VALID_DIFFICULTIES = {"Low", "Medium", "High"}
VALID_INTENTS = {"Informational", "Commercial", "Transactional"}


def default_keyword(keyword: str = "", score: int = 50) -> Dict[str, object]:
    """Return a safe default keyword object."""
    return {
        "keyword": keyword,
        "score": score,
        "difficulty": "Medium",
        "intent": "Commercial",
        "suggestion": "Use in page content naturally",
    }


def default_output() -> Dict[str, object]:
    """Return a safe default output shape."""
    return {
        "seo_title": "",
        "meta_description": "",
        "seo_keywords": [],
        "google_snippet": "",
        "instagram_caption": "",
        "linkedin_caption": "",
        "seo_hashtags": [],
        "blog_topics": [],
        "short_description": "",
        "long_form_overview": "",
    }


def required_keys() -> List[str]:
    """Return required output keys."""
    return list(OUTPUT_KEYS)
