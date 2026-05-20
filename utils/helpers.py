"""Utility helpers for validation, parsing, formatting, and scoring."""

from __future__ import annotations

import json
import re
from typing import Dict, List, Tuple

from utils.prompts import default_output, required_keys


def validate_inputs(payload: Dict[str, object]) -> Tuple[bool, List[str]]:
    """Validate required fields and return errors."""
    errors: List[str] = []
    required_text_fields = [
        "project_name",
        "city",
        "micro_market",
        "project_type",
        "nearby_landmarks",
        "brand_positioning",
        "usp",
        "price_segment",
        "tone",
    ]
    for field in required_text_fields:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"Please provide a valid value for {field.replace('_', ' ').title()}.")

    configuration = payload.get("configuration", [])
    target_audience = payload.get("target_audience", [])

    if not isinstance(configuration, list) or len(configuration) == 0:
        errors.append("Please select at least one Configuration.")
    if not isinstance(target_audience, list) or len(target_audience) == 0:
        errors.append("Please select at least one Target Audience.")

    return len(errors) == 0, errors


def _extract_first_json_blob(text: str) -> str:
    """Attempt to extract the first JSON object from plain text."""
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    return match.group(0) if match else text


def parse_ai_response(raw_text: str) -> Dict[str, object]:
    """Parse AI JSON response robustly and normalize schema."""
    parsed: Dict[str, object] = default_output()
    if not raw_text or not raw_text.strip():
        raise ValueError("Empty response from AI service.")

    blob = _extract_first_json_blob(raw_text)
    try:
        data = json.loads(blob)
    except json.JSONDecodeError as exc:
        raise ValueError("AI returned malformed JSON content.") from exc

    if not isinstance(data, dict):
        raise ValueError("AI response format is invalid.")

    for key in required_keys():
        parsed[key] = data.get(key, parsed[key])

    # Normalize list fields.
    parsed["seo_keywords"] = _normalize_list(parsed.get("seo_keywords"), 15)
    parsed["seo_hashtags"] = _normalize_list(parsed.get("seo_hashtags"), 25, prefix="#")
    parsed["blog_topics"] = _normalize_list(parsed.get("blog_topics"), 10)

    # Normalize strings.
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


def compute_quality_score(content: Dict[str, object]) -> Dict[str, object]:
    """Compute content quality score and SEO strength indicator."""
    score = 0
    checks: List[str] = []

    title = str(content.get("seo_title", ""))
    meta = str(content.get("meta_description", ""))
    keywords = content.get("seo_keywords", [])
    hashtags = content.get("seo_hashtags", [])
    blogs = content.get("blog_topics", [])
    long_overview = str(content.get("long_form_overview", ""))

    if 45 <= len(title) <= 65:
        score += 15
        checks.append("SEO title length is optimal")
    if 140 <= len(meta) <= 160:
        score += 20
        checks.append("Meta description length is optimal")
    if isinstance(keywords, list) and len(keywords) >= 10:
        score += 15
        checks.append("Keyword coverage is strong")
    if isinstance(hashtags, list) and len(hashtags) == 25:
        score += 15
        checks.append("Hashtag set is complete")
    if isinstance(blogs, list) and len(blogs) == 10:
        score += 15
        checks.append("Blog topic pipeline is complete")
    if len(long_overview.split()) >= 120:
        score += 20
        checks.append("Long-form overview depth is strong")

    if score >= 85:
        strength = "Excellent"
    elif score >= 70:
        strength = "Strong"
    elif score >= 50:
        strength = "Moderate"
    else:
        strength = "Needs Improvement"

    return {"score": score, "strength": strength, "checks": checks}


def format_output_markdown(content: Dict[str, object]) -> str:
    """Prepare markdown download format."""
    return (
        f"# SEO Content Pack - {content.get('seo_title', 'Project')}\n\n"
        f"## SEO Title\n{content.get('seo_title', '')}\n\n"
        f"## Meta Description\n{content.get('meta_description', '')}\n\n"
        f"## SEO Keywords\n{', '.join(content.get('seo_keywords', []))}\n\n"
        f"## Google Search Snippet\n{content.get('google_snippet', '')}\n\n"
        f"## Instagram Caption\n{content.get('instagram_caption', '')}\n\n"
        f"## LinkedIn Caption\n{content.get('linkedin_caption', '')}\n\n"
        f"## 25 SEO Hashtags\n{' '.join(content.get('seo_hashtags', []))}\n\n"
        f"## 10 Blog Topic Ideas\n"
        + "\n".join([f"- {t}" for t in content.get("blog_topics", [])])
        + "\n\n"
        + f"## Short Project Description\n{content.get('short_description', '')}\n\n"
        + f"## Long-form Project Overview\n{content.get('long_form_overview', '')}\n"
    )


def format_output_txt(content: Dict[str, object]) -> str:
    """Prepare plain-text download format."""
    blog_lines = "\n".join([f"{idx + 1}. {topic}" for idx, topic in enumerate(content.get("blog_topics", []))])
    return (
        f"SEO TITLE:\n{content.get('seo_title', '')}\n\n"
        f"META DESCRIPTION ({len(content.get('meta_description', ''))} chars):\n{content.get('meta_description', '')}\n\n"
        f"SEO KEYWORDS:\n{', '.join(content.get('seo_keywords', []))}\n\n"
        f"GOOGLE SNIPPET:\n{content.get('google_snippet', '')}\n\n"
        f"INSTAGRAM CAPTION:\n{content.get('instagram_caption', '')}\n\n"
        f"LINKEDIN CAPTION:\n{content.get('linkedin_caption', '')}\n\n"
        f"SEO HASHTAGS:\n{' '.join(content.get('seo_hashtags', []))}\n\n"
        f"BLOG TOPIC IDEAS:\n{blog_lines}\n\n"
        f"SHORT DESCRIPTION:\n{content.get('short_description', '')}\n\n"
        f"LONG-FORM PROJECT OVERVIEW:\n{content.get('long_form_overview', '')}\n"
    )
