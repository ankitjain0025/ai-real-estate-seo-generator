"""Production-ready Streamlit app for AI-powered real estate SEO generation."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

_ROOT_DIR = Path(__file__).resolve().parent
if str(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR))

import streamlit as st
from dotenv import load_dotenv

from utils.ai_generator import AIGenerationError, generate_seo_content, get_client
from utils.config import configure_runtime_secrets, get_gemini_api_key
from utils.formatting import format_output_markdown, format_output_txt
from utils.scoring import compute_quality_score
from utils.styling import get_custom_css
from utils.validation import validate_inputs

load_dotenv()

CITY_OPTIONS = [
    "Mumbai", "Thane", "Navi Mumbai", "Pune", "Bangalore",
    "Hyderabad", "Chennai", "Delhi NCR", "Ahmedabad",
]
PROJECT_TYPE_OPTIONS = ["Residential", "Commercial", "Mixed Use", "Retail", "Township"]
CONFIG_OPTIONS = ["Studio", "1BHK", "2BHK", "3BHK", "4BHK", "Penthouse", "Office", "Retail Shop"]
BRAND_POSITION_OPTIONS = [
    "Luxury", "Ultra Luxury", "Affordable Premium", "Family-Centric",
    "Investor-Focused", "Smart Living", "Corporate Commercial",
]
TARGET_AUDIENCE_OPTIONS = ["Families", "Investors", "Working Professionals", "NRIs", "Millennials", "Businesses"]
PRICE_SEGMENT_OPTIONS = ["Affordable", "Mid Segment", "Premium", "Luxury", "Ultra Luxury"]
TONE_OPTIONS = ["Premium", "Luxury", "Modern", "Aspirational", "Corporate", "Investor-focused"]


def _init_state() -> None:
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
    configure_runtime_secrets()
    key = get_gemini_api_key()
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
    mapping = {
        "connected": "Connected",
        "missing": "Not Connected (missing GEMINI_API_KEY)",
        "invalid": "Configuration Error (check API key value)",
    }
    return mapping.get(status, "Unknown")


def _api_error_message(status: str) -> str:
    if status == "missing":
        return (
            "API is not connected. Add your key in Streamlit Cloud → App settings → Secrets:\n\n"
            'GEMINI_API_KEY = "your_actual_gemini_api_key"\n\n'
            "Then click Manage app → Reboot app."
        )
    if status == "invalid":
        return (
            "API key is present but invalid. "
            "Generate a new key at https://aistudio.google.com/app/apikey and update Streamlit secrets."
        )
    return "API is not connected. Please configure GEMINI_API_KEY and try again."


def _render_sidebar(status: str) -> None:
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
        "3. Review keyword scores and SEO strength.\n"
        "4. Download in TXT or Markdown."
    )
    st.sidebar.markdown("### Keyword Scoring Guide")
    st.sidebar.markdown(
        "**Score (1–100):** Relevance + search value.\n\n"
        "🟢 **Low difficulty:** Long-tail, easy to rank — target first.\n\n"
        "🟡 **Medium:** Competitive but winnable in 6–12 months.\n\n"
        "🔴 **High:** Portal-dominated — use sparingly.\n\n"
        "**Intent:**\n"
        "- 🔵 Informational: Research phase\n"
        "- 🟣 Commercial: Comparing options\n"
        "- 🟢 Transactional: Ready to buy/visit"
    )
    st.sidebar.markdown("### About")
    st.sidebar.markdown(
        "Built with Streamlit + Google Gemini for high-quality SEO and social launch communication at scale."
    )
    st.sidebar.markdown("### API Status")
    label = _api_status_message(status)
    if status == "connected":
        st.sidebar.success(label)
    elif status == "missing":
        st.sidebar.warning(label)
        with st.sidebar.expander("Fix on Streamlit Cloud"):
            st.code('GEMINI_API_KEY = "your_actual_gemini_api_key"', language="toml")
            st.caption("After saving secrets, reboot the app from Manage app.")
    else:
        st.sidebar.error(label)
    st.sidebar.markdown("---")
    st.sidebar.caption("Powered by Google Gemini 2.5 Flash | Built for Indian Real Estate")


def _get_payload() -> Dict[str, object]:
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

    return {
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


def _score_bar_html(score: int) -> str:
    """Render an inline score bar for the keyword table."""
    if score >= 75:
        color = "#16a34a"  # green
    elif score >= 50:
        color = "#d97706"  # amber
    else:
        color = "#dc2626"  # red

    return (
        f'<div class="score-bar-wrap">'
        f'<div class="score-bar-bg"><div class="score-bar-fill" style="width:{score}%;background:{color};"></div></div>'
        f'<span class="score-label">{score}</span>'
        f'</div>'
    )


def _difficulty_badge(difficulty: str) -> str:
    cls = {"Low": "badge-low", "Medium": "badge-medium", "High": "badge-high"}.get(difficulty, "badge-medium")
    return f'<span class="badge {cls}">{difficulty}</span>'


def _intent_badge(intent: str) -> str:
    cls = {
        "Informational": "badge intent-info",
        "Commercial": "badge intent-comm",
        "Transactional": "badge intent-trans",
    }.get(intent, "badge intent-comm")
    return f'<span class="{cls}">{intent}</span>'


def _render_keyword_table(keywords: List[Dict[str, object]]) -> None:
    """Render scored keyword table as HTML inside Streamlit."""
    if not keywords:
        st.write("No keywords generated.")
        return

    rows = ""
    for i, kw in enumerate(keywords):
        keyword = str(kw.get("keyword", ""))
        score = int(kw.get("score", 50))
        difficulty = str(kw.get("difficulty", "Medium"))
        intent = str(kw.get("intent", "Commercial"))
        suggestion = str(kw.get("suggestion", ""))

        rows += (
            f"<tr>"
            f"<td><strong>{i + 1}</strong></td>"
            f"<td>{keyword}</td>"
            f"<td>{_score_bar_html(score)}</td>"
            f"<td>{_difficulty_badge(difficulty)}</td>"
            f"<td>{_intent_badge(intent)}</td>"
            f"<td><span class='kw-suggestion'>💡 {suggestion}</span></td>"
            f"</tr>"
        )

    table_html = f"""
    <table class="kw-table">
      <thead>
        <tr>
          <th>#</th>
          <th>Keyword</th>
          <th>Score</th>
          <th>Difficulty</th>
          <th>Intent</th>
          <th>Suggestion</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
    """
    st.markdown(table_html, unsafe_allow_html=True)

    # Copy-friendly plain text block
    st.markdown("<br>", unsafe_allow_html=True)
    plain_lines = "\n".join(
        [f"{i+1}. {kw.get('keyword','')}  |  Score: {kw.get('score','')}/100  |  "
         f"{kw.get('difficulty','')}  |  {kw.get('intent','')}  |  {kw.get('suggestion','')}"
         for i, kw in enumerate(keywords)]
    )
    with st.expander("📋 Copy-friendly keyword list", expanded=False):
        st.code(plain_lines, language="text")
        st.caption("Copy from the code block above.")


def _render_content_card(title: str, value: str) -> None:
    with st.expander(f"📌 {title}", expanded=True):
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.write(value)
        st.markdown("</div>", unsafe_allow_html=True)
        st.code(value, language="text")
        st.caption("Copy from the code block above.")


def _render_list_card(title: str, items: List[str], ordered: bool = False) -> None:
    with st.expander(f"📌 {title}", expanded=True):
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        if not items:
            st.write("No content generated.")
        else:
            for i, item in enumerate(items):
                st.write(f"{i + 1}. {item}" if ordered else f"- {item}")
        st.markdown("</div>", unsafe_allow_html=True)
        joined = "\n".join([f"{i+1}. {v}" if ordered else v for i, v in enumerate(items)])
        st.code(joined, language="text")
        st.caption("Copy from the code block above.")


def _render_results(content: Dict[str, object]) -> None:
    meta_description = str(content.get("meta_description", ""))
    keywords: List[Dict[str, object]] = content.get("seo_keywords", [])  # type: ignore[assignment]
    quality = compute_quality_score(content)
    strength = str(quality["strength"])
    score = int(quality["score"])

    st.markdown("### Generated Content Pack")

    # ── Quality metrics row ──
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

    # ── Keyword summary metrics ──
    if keywords:
        top = keywords[0]
        avg_score = round(sum(int(k.get("score", 0)) for k in keywords) / len(keywords))
        low_count = sum(1 for k in keywords if k.get("difficulty") == "Low")
        trans_count = sum(1 for k in keywords if k.get("intent") == "Transactional")

        km1, km2, km3, km4 = st.columns(4)
        with km1:
            st.metric("Top Keyword Score", f"{top.get('score', 0)}/100")
        with km2:
            st.metric("Avg Keyword Score", f"{avg_score}/100")
        with km3:
            st.metric("Low Difficulty Keywords", f"{low_count} / {len(keywords)}")
        with km4:
            st.metric("Transactional Intent", f"{trans_count} / {len(keywords)}")

    # ── SEO Keywords table ──
    with st.expander("📌 SEO Keywords — Scored & Ranked", expanded=True):
        st.markdown(
            "<small>Sorted highest score first. "
            "🟢 Low difficulty = target first. "
            "🟢 Transactional intent = highest buyer readiness.</small>",
            unsafe_allow_html=True,
        )
        _render_keyword_table(keywords)

    # ── Remaining content ──
    _render_content_card("SEO Title", str(content.get("seo_title", "")))
    _render_content_card("Meta Description", meta_description)
    _render_content_card("Google Search Snippet", str(content.get("google_snippet", "")))
    _render_content_card("Instagram Caption", str(content.get("instagram_caption", "")))
    _render_content_card("LinkedIn Caption", str(content.get("linkedin_caption", "")))
    _render_list_card("25 SEO Hashtags", list(content.get("seo_hashtags", [])))
    _render_list_card("10 Blog Topic Ideas", list(content.get("blog_topics", [])), ordered=True)
    _render_content_card("Short Project Description", str(content.get("short_description", "")))
    _render_content_card("Long-form Project Overview", str(content.get("long_form_overview", "")))

    # ── Downloads ──
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
                with st.spinner("Crafting premium SEO content with Gemini AI..."):
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
                    except Exception as exc:
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
            "Tip: Add GEMINI_API_KEY to Streamlit secrets. "
            "Get a free key at https://aistudio.google.com/app/apikey"
        )
        st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.get("generated"):
            _render_results(st.session_state["generated"])


if __name__ == "__main__":
    main()
