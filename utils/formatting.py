"""Output formatting for downloads."""

from __future__ import annotations

from typing import Dict


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
