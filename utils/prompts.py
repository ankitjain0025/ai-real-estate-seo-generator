"""Prompt builders for the AI-powered SEO generator."""

from __future__ import annotations

import json
from typing import Dict


def build_system_prompt() -> str:
    """Return the system prompt that governs response quality and format."""
    return (
        "You are an elite Indian real estate SEO strategist, luxury real estate "
        "marketing consultant, and organic growth specialist. "
        "Generate premium, high-conversion, human-sounding content for project launches. "
        "Avoid cliches, avoid generic filler, avoid repetitive wording, and avoid clickbait. "
        "Use local Indian real estate search intent naturally (city, micro-market, project type). "
        "Maintain premium developer branding tone and practical SEO relevance. "
        "Your output must be valid JSON with exactly these keys:\n"
        "{\n"
        '  "seo_title": string,\n'
        '  "meta_description": string,\n'
        '  "seo_keywords": [string, ...],\n'
        '  "google_snippet": string,\n'
        '  "instagram_caption": string,\n'
        '  "linkedin_caption": string,\n'
        '  "seo_hashtags": [string, ...],\n'
        '  "blog_topics": [string, ...],\n'
        '  "short_description": string,\n'
        '  "long_form_overview": string\n'
        "}\n"
        "Rules:\n"
        "- seo_hashtags must contain exactly 25 entries.\n"
        "- blog_topics must contain exactly 10 entries.\n"
        "- meta_description should target 140-160 characters.\n"
        "- Keep language premium, concise, and conversion-focused.\n"
        "- Never include markdown in JSON values.\n"
        "- Never wrap your response in markdown code fences (no ```json or ```).\n"
        "- Return raw JSON only — no preamble, no explanation, no formatting.\n"
        "- Never include keys outside the required schema."
    )


def build_user_prompt(payload: Dict[str, object]) -> str:
    """Build a structured user prompt from normalized form data."""
    context = {
        "project_name": payload["project_name"],
        "city": payload["city"],
        "micro_market": payload["micro_market"],
        "project_type": payload["project_type"],
        "configuration": payload["configuration"],
        "nearby_landmarks": payload["nearby_landmarks"],
        "brand_positioning": payload["brand_positioning"],
        "usp": payload["usp"],
        "target_audience": payload["target_audience"],
        "price_segment": payload["price_segment"],
        "tone": payload["tone"],
    }

    return (
        "Generate a complete SEO and social content pack for this Indian real estate launch.\n\n"
        f"Project context:\n{json.dumps(context, indent=2, ensure_ascii=True)}\n\n"
        "Ensure the content is market-ready for developers and marketing teams. "
        "Use premium Indian real estate terminology naturally. "
        "Return raw JSON only — no markdown fences, no extra text before or after the JSON object."
    )
