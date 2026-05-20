"""Production-ready Streamlit app for AI-powered real estate SEO generation."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import streamlit as st
from dotenv import load_dotenv

from utils.ai_generator import AIGenerationError, generate_seo_content, get_client
from utils.config import configure_runtime_secrets, get_xai_api_key
from utils.helpers import (
    compute_quality_score,
    format_output_markdown,
    format_output_txt,
    validate_inputs,
)
from utils.styling import get_custom_css

load_dotenv()


CITY_OPTIONS = [
    "Mumbai",
    "Thane",
    "Navi Mumbai",
    "Pune",
    "Bangalore",
    "Hyderabad",
    "Chennai",
    "Delhi NCR",
    "Ahmedabad",
]

PROJECT_TYPE_OPTIONS = ["Residential", "Commercial", "Mixed Use", "Retail", "Township"]

CONFIG_OPTIONS = ["Studio", "1BHK", "2BHK", "3BHK", "4BHK", "Penthouse", "Office", "Retail Shop"]

BRAND_POSITION_OPTIONS = [
    "Luxury",
    "Ultra Luxury",
    "Affordable Premium",
    "Family-Centric",
    "Investor-Focused",
    "Smart Living",
    "Corporate Commercial",
]

TARGET_AUDIENCE_OPTIONS = [
    "Families",
    "Investors",
    "Working Professionals",
    "NRIs",
    "Millennials",
    "Businesses",
]

PRICE_SEGMENT_OPTIONS = ["Affordable", "Mid Segment", "Premium", "Luxury", "Ultra Luxury"]

TONE_OPTIONS = ["Premium", "Luxury", "Modern", "Aspirational", "Corporate", "Investor-focused"]


def _init_state() -> None:
    """Initialize Streamlit session state defaults."""
    defaults = {
        "generated": None,
        "last_payload": None,
        "last_error": "",
        "last_generated_at": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _api_status() -> str:
    """Return API connection readiness status."""
    configure_runtime_secrets()
    key = get_xai_api_key()
    if not key:
        return "missing"
    try:
        _ = get_client()
        return "connected"
    except AIGenerationError:
        return "invalid"
    except Exception:
        return "invalid"


def _api_status_message(status: str) -> str:
    """Human-readable API status for sidebar."""
    mapping = {
        "connected": "Connected",
        "missing": "Not Connected (missing XAI_API_KEY)",
        "invalid": "Configuration Error (check API key value)",
    }
    return mapping.get(status, "Unknown")


def _api_error_message(status: str) -> str:
    """Actionable error when generation is blocked."""
    if status == "missing":
        return (
            "API is not connected. Add your key in Streamlit Cloud → App settings → Secrets:\n\n"
            "XAI_API_KEY = \"your_actual_xai_api_key\"\n\n"
            "Then click Manage app → Reboot app."
        )
    if status == "invalid":
        return "API key is present but invalid. Regenerate your xAI key and update Streamlit secrets."
    return "API is not connected. Please configure XAI_API_KEY and try again."


def _render_sidebar(status: str) -> None:
    """Render branded sidebar content."""
    logo_path = Path("assets/logo.png")
    if logo_path.exists():
        try:
            st.sidebar.image(str(logo_path), use_container_width=True)
        except Exception:
            st.sidebar.markdown("## 🏙️")
    else:
        st.sidebar.markdown("## 🏙️")

    st.sidebar.markdown("## Real Estate AI SEO Generator")
    st.sidebar.markdown(
        "Premium launch content engine for Indian real estate developers, channel partners, and marketing teams."
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("### How to use")
    st.sidebar.markdown(
        "1. Fill complete project details.\n"
        "2. Click **Generate SEO Content**.\n"
        "3. Review SEO score and refine if needed.\n"
        "4. Download in TXT or Markdown."
    )
    st.sidebar.markdown("### About")
    st.sidebar.markdown(
        "Built with Streamlit + Grok API for high-quality SEO and social launch communication at scale."
    )
    st.sidebar.markdown("### API Status")
    label = _api_status_message(status)
    if status == "connected":
        st.sidebar.success(label)
    elif status == "missing":
        st.sidebar.warning(label)
        with st.sidebar.expander("Fix on Streamlit Cloud"):
            st.code(
                'XAI_API_KEY = "your_actual_xai_api_key"\nXAI_MODEL = "grok-3-beta"',
                language="toml",
            )
            st.caption("After saving secrets, reboot the app from Manage app.")
    else:
        st.sidebar.error(label)
    st.sidebar.markdown("---")
    st.sidebar.caption("Powered by xAI Grok | Built for Indian Real Estate")


def _get_payload() -> Dict[str, object]:
    """Render form and collect user payload."""
    with st.form("project_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            project_name = st.text_input("Project Name", placeholder="e.g., The Crest at Powai")
            city = st.selectbox("City", CITY_OPTIONS)
            micro_market = st.text_input("Micro Market", placeholder="e.g., Powai, Whitefield, Hinjewadi")
            project_type = st.selectbox("Project Type", PROJECT_TYPE_OPTIONS)
            configuration = st.multiselect("Configuration", CONFIG_OPTIONS)
            nearby_landmarks = st.text_area(
                "Nearby Landmarks",
                placeholder="e.g., 5 mins from Metro Station, near IT Park, close to top schools and hospitals",
                height=110,
            )
        with c2:
            brand_positioning = st.selectbox("Brand Positioning", BRAND_POSITION_OPTIONS)
            usp = st.text_area(
                "USP (Unique Selling Proposition)",
                placeholder="e.g., Largest rooftop lifestyle deck in the micro-market with panoramic lake views",
                height=110,
            )
            target_audience = st.multiselect("Target Audience", TARGET_AUDIENCE_OPTIONS)
            price_segment = st.selectbox("Price Segment", PRICE_SEGMENT_OPTIONS)
            tone = st.selectbox("Tone of Content", TONE_OPTIONS)

        submitted = st.form_submit_button("Generate SEO Content", use_container_width=True)

    payload = {
        "project_name": project_name,
        "city": city,
        "micro_market": micro_market,
        "project_type": project_type,
        "configuration": configuration,
        "nearby_landmarks": nearby_landmarks,
        "brand_positioning": brand_positioning,
        "usp": usp,
        "target_audience": target_audience,
        "price_segment": price_segment,
        "tone": tone,
        "submitted": submitted,
    }
    return payload


def _render_content_card(title: str, value: str) -> None:
    """Render one output card with expander and copy helper."""
    with st.expander(f"📌 {title}", expanded=True):
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.write(value)
        st.markdown("</div>", unsafe_allow_html=True)
        st.code(value, language="text")
        st.caption("Copy from the code block above.")


def _render_list_card(title: str, items: List[str], ordered: bool = False) -> None:
    """Render list output in premium card."""
    with st.expander(f"📌 {title}", expanded=True):
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        if not items:
            st.write("No content generated.")
        else:
            for i, item in enumerate(items):
                if ordered:
                    st.write(f"{i + 1}. {item}")
                else:
                    st.write(f"- {item}")
        st.markdown("</div>", unsafe_allow_html=True)
        joined = "\n".join([f"{i+1}. {v}" if ordered else v for i, v in enumerate(items)])
        st.code(joined, language="text")
        st.caption("Copy from the code block above.")


def _render_results(content: Dict[str, object]) -> None:
    """Render full generated output section."""
    meta_description = str(content.get("meta_description", ""))
    quality = compute_quality_score(content)
    strength = str(quality["strength"])
    score = int(quality["score"])

    st.markdown("### Generated Content Pack")
    m1, m2, m3 = st.columns([1, 1, 2])
    with m1:
        st.markdown(
            f'<div class="metric-card"><div class="small-label">Content Quality Score</div>'
            f'<div class="big-value">{score}/100</div></div>',
            unsafe_allow_html=True,
        )
    with m2:
        css_class = (
            "seo-indicator-good" if score >= 70 else "seo-indicator-mid" if score >= 50 else "seo-indicator-low"
        )
        st.markdown(
            f'<div class="metric-card"><div class="small-label">SEO Strength</div>'
            f'<div class="big-value {css_class}">{strength}</div></div>',
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.write(f"Meta Description Length: **{len(meta_description)}** characters")
        st.progress(min(score, 100))
        for check in quality["checks"]:
            st.write(f"✅ {check}")
        st.markdown("</div>", unsafe_allow_html=True)

    _render_content_card("SEO Title", str(content.get("seo_title", "")))
    _render_content_card("Meta Description", meta_description)
    _render_list_card("SEO Keywords", list(content.get("seo_keywords", [])))
    _render_content_card("Google Search Snippet", str(content.get("google_snippet", "")))
    _render_content_card("Instagram Caption", str(content.get("instagram_caption", "")))
    _render_content_card("LinkedIn Caption", str(content.get("linkedin_caption", "")))
    _render_list_card("25 SEO Hashtags", list(content.get("seo_hashtags", [])))
    _render_list_card("10 Blog Topic Ideas", list(content.get("blog_topics", [])), ordered=True)
    _render_content_card("Short Project Description", str(content.get("short_description", "")))
    _render_content_card("Long-form Project Overview", str(content.get("long_form_overview", "")))

    markdown_data = format_output_markdown(content)
    txt_data = format_output_txt(content)
    d1, d2 = st.columns(2)
    with d1:
        st.download_button(
            "Download as TXT",
            data=txt_data,
            file_name="real_estate_seo_content.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with d2:
        st.download_button(
            "Download as Markdown",
            data=markdown_data,
            file_name="real_estate_seo_content.md",
            mime="text/markdown",
            use_container_width=True,
        )


def main() -> None:
    """Run Streamlit app."""
    configure_runtime_secrets()
    st.set_page_config(
        page_title="AI Real Estate SEO Generator",
        page_icon="🏙️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    _init_state()

    st.markdown('<div class="main-title">AI-Powered Real Estate SEO Generator</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Generate premium launch content for Indian real estate projects in seconds.</div>',
        unsafe_allow_html=True,
    )

    api_status = _api_status()
    _render_sidebar(api_status)

    left_col, right_col = st.columns([1.25, 1], gap="large")

    with left_col:
        st.markdown('<div class="section-title">Project Input Form</div>', unsafe_allow_html=True)
        payload = _get_payload()

        if payload.get("submitted"):
            valid, errors = validate_inputs(payload)
            if not valid:
                for err in errors:
                    st.error(err)
            elif api_status != "connected":
                st.error(_api_error_message(api_status))
            else:
                with st.spinner("Crafting premium SEO content with Grok AI..."):
                    try:
                        generated = generate_seo_content(payload)
                        st.session_state["generated"] = generated
                        st.session_state["last_payload"] = payload
                        st.session_state["last_error"] = ""
                        st.session_state["last_generated_at"] = datetime.now().strftime("%d %b %Y, %I:%M %p")
                        st.success("SEO content generated successfully.")
                    except AIGenerationError as exc:
                        st.session_state["last_error"] = str(exc)
                        st.error(str(exc))
                    except Exception as exc:  # pragma: no cover
                        st.session_state["last_error"] = f"Unexpected app error: {exc}"
                        st.error(st.session_state["last_error"])

    with right_col:
        st.markdown('<div class="section-title">Generation Insights</div>', unsafe_allow_html=True)
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        if st.session_state.get("last_generated_at"):
            st.write(f"Last generated: **{st.session_state['last_generated_at']}**")
        else:
            st.write("No content generated yet.")
        if st.session_state.get("last_error"):
            st.warning(st.session_state["last_error"])
        st.info(
            "Tip: Use `XAI_MODEL = grok-3-beta` in secrets. xAI API requires account credits even for beta aliases."
        )
        st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.get("generated"):
            _render_results(st.session_state["generated"])


if __name__ == "__main__":
    main()
