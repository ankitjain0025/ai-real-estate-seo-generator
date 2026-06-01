"""Output formatting for downloads."""

from __future__ import annotations

from typing import Dict, List


def _keyword_lines_txt(keywords: List[Dict[str, object]]) -> str:
    """Format keyword list for plain text download."""
    lines = []
    for i, kw in enumerate(keywords):
        keyword = kw.get("keyword", "")
        score = kw.get("score", "")
        difficulty = kw.get("difficulty", "")
        intent = kw.get("intent", "")
        suggestion = kw.get("suggestion", "")
        lines.append(
            f"{i+1:>2}. {keyword}\n"
            f"    Score: {score}/100 | Difficulty: {difficulty} | Intent: {intent}\n"
            f"    Tip: {suggestion}"
        )
    return "\n".join(lines)


def _keyword_lines_markdown(keywords: List[Dict[str, object]]) -> str:
    """Format keyword list for markdown download."""
    lines = ["| # | Keyword | Score | Difficulty | Intent | Suggestion |",
             "|---|---------|-------|------------|--------|------------|"]
    for i, kw in enumerate(keywords):
        lines.append(
            f"| {i+1} | {kw.get('keyword','')} | {kw.get('score','')}/100 "
            f"| {kw.get('difficulty','')} | {kw.get('intent','')} "
            f"| {kw.get('suggestion','')} |"
        )
    return "\n".join(lines)


def _plain_keywords(keywords: object) -> str:
    """Safe plain keyword string for simple contexts."""
    if isinstance(keywords, list):
        parts = []
        for kw in keywords:
            if isinstance(kw, dict):
                parts.append(str(kw.get("keyword", "")))
            elif isinstance(kw, str):
                parts.append(kw)
        return ", ".join(p for p in parts if p)
    return str(keywords)


def format_output_markdown(content: Dict[str, object]) -> str:
    """Prepare markdown download format."""
    keywords = content.get("seo_keywords", [])
    keyword_table = _keyword_lines_markdown(keywords) if keywords else "_No keywords generated._"

    return (
        f"# SEO Content Pack - {content.get('seo_title', 'Project')}\n\n"
        f"## SEO Title\n{content.get('seo_title', '')}\n\n"
        f"## Meta Description\n{content.get('meta_description', '')}\n\n"
        f"## SEO Keywords (Ranked by Score)\n{keyword_table}\n\n"
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
    keywords = content.get("seo_keywords", [])
    keyword_section = _keyword_lines_txt(keywords) if keywords else "No keywords generated."
    blog_lines = "\n".join(
        [f"{idx + 1}. {topic}" for idx, topic in enumerate(content.get("blog_topics", []))]
    )
    meta = content.get("meta_description", "")

    return (
        f"SEO TITLE:\n{content.get('seo_title', '')}\n\n"
        f"META DESCRIPTION ({len(str(meta))} chars):\n{meta}\n\n"
        f"SEO KEYWORDS (Ranked by Score — Highest First):\n{keyword_section}\n\n"
        f"GOOGLE SNIPPET:\n{content.get('google_snippet', '')}\n\n"
        f"INSTAGRAM CAPTION:\n{content.get('instagram_caption', '')}\n\n"
        f"LINKEDIN CAPTION:\n{content.get('linkedin_caption', '')}\n\n"
        f"SEO HASHTAGS:\n{' '.join(content.get('seo_hashtags', []))}\n\n"
        f"BLOG TOPIC IDEAS:\n{blog_lines}\n\n"
        f"SHORT DESCRIPTION:\n{content.get('short_description', '')}\n\n"
        f"LONG-FORM PROJECT OVERVIEW:\n{content.get('long_form_overview', '')}\n"
    )
