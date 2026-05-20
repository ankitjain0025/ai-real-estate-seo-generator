"""Content quality scoring."""

from __future__ import annotations

from typing import Dict, List


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
