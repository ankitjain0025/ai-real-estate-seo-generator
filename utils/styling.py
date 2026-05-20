"""Custom styling for premium Streamlit UI."""

from __future__ import annotations


def get_custom_css() -> str:
    """Return full CSS for premium visual styling."""
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: radial-gradient(circle at top left, #f7f9fc 0%, #eef2f7 45%, #e8edf5 100%);
    color: #10233f;
}

.main-title {
    font-size: 2rem;
    font-weight: 700;
    color: #10233f;
    letter-spacing: 0.2px;
    margin-bottom: 0.2rem;
}

.sub-title {
    color: #455a78;
    font-size: 1rem;
    margin-bottom: 1.2rem;
}

.premium-card {
    background: #ffffff;
    border: 1px solid #dbe4f0;
    border-radius: 16px;
    box-shadow: 0 12px 28px rgba(16, 35, 63, 0.08);
    padding: 1rem 1.1rem;
    margin-bottom: 0.9rem;
}

.metric-card {
    background: linear-gradient(135deg, #0f355f 0%, #1f4f85 100%);
    color: #f8fbff;
    border-radius: 14px;
    padding: 0.9rem 1rem;
    border: 1px solid rgba(255,255,255,0.2);
    margin-bottom: 0.8rem;
}

.small-label {
    font-size: 0.85rem;
    opacity: 0.85;
}

.big-value {
    font-size: 1.35rem;
    font-weight: 700;
}

.copy-tip {
    color: #607a9c;
    font-size: 0.84rem;
}

.stButton > button {
    border-radius: 12px !important;
    border: 1px solid #214e84 !important;
    background: linear-gradient(135deg, #17477a 0%, #2f6aaa 100%) !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 0.62rem 1rem !important;
}

.stDownloadButton > button {
    border-radius: 10px !important;
    border: 1px solid #c6d4e7 !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2f55 0%, #173d69 55%, #1f4a7b 100%);
    color: #f7fbff;
}

[data-testid="stSidebar"] * {
    color: #f7fbff !important;
}

.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #143761;
    margin-bottom: 0.4rem;
}

.seo-indicator-good {
    color: #0a7f3f;
    font-weight: 700;
}

.seo-indicator-mid {
    color: #b56b0a;
    font-weight: 700;
}

.seo-indicator-low {
    color: #b01d1d;
    font-weight: 700;
}
</style>
"""
