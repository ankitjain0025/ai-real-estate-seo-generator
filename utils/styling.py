"""Custom styling for premium Streamlit UI including login screen."""

from __future__ import annotations


def get_custom_css() -> str:
    """Return full CSS for premium visual styling."""
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: radial-gradient(circle at top left, #f7f9fc 0%, #eef2f7 45%, #e8edf5 100%);
    color: #10233f;
}

/* ── Login page ── */
.login-wrapper {
    max-width: 420px;
    margin: 6vh auto 0 auto;
    background: #ffffff;
    border: 1px solid #dbe4f0;
    border-radius: 20px;
    box-shadow: 0 20px 48px rgba(16,35,63,0.12);
    padding: 2.5rem 2rem 2rem 2rem;
}

.login-logo {
    text-align: center;
    font-size: 2.4rem;
    margin-bottom: 0.3rem;
}

.login-title {
    text-align: center;
    font-size: 1.5rem;
    font-weight: 700;
    color: #10233f;
    margin-bottom: 0.15rem;
}

.login-sub {
    text-align: center;
    color: #607a9c;
    font-size: 0.9rem;
    margin-bottom: 1.6rem;
}

.login-footer {
    text-align: center;
    color: #8fa3bf;
    font-size: 0.78rem;
    margin-top: 1.4rem;
}

/* ── App chrome ── */
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
    box-shadow: 0 12px 28px rgba(16,35,63,0.08);
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

.small-label { font-size: 0.85rem; opacity: 0.85; }
.big-value   { font-size: 1.35rem; font-weight: 700; }
.copy-tip    { color: #607a9c; font-size: 0.84rem; }

/* ── Keyword table ── */
.kw-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.87rem;
    margin-top: 0.5rem;
}
.kw-table th {
    background: #0f355f;
    color: #f7fbff;
    padding: 0.5rem 0.7rem;
    text-align: left;
    font-weight: 600;
    border-bottom: 2px solid #1f4f85;
}
.kw-table td {
    padding: 0.45rem 0.7rem;
    border-bottom: 1px solid #e4ecf4;
    vertical-align: middle;
}
.kw-table tr:hover td          { background: #f0f5fb; }
.kw-table tr:nth-child(even) td { background: #f8fafe; }
.kw-table tr:nth-child(even):hover td { background: #eef4fb; }

.score-bar-wrap { display: flex; align-items: center; gap: 6px; min-width: 110px; }
.score-bar-bg   { flex: 1; height: 8px; background: #dbe4f0; border-radius: 99px; overflow: hidden; }
.score-bar-fill { height: 100%; border-radius: 99px; }
.score-label    { font-size: 0.8rem; font-weight: 700; min-width: 28px; color: #10233f; }

.badge         { display: inline-block; padding: 0.15rem 0.55rem; border-radius: 99px;
                 font-size: 0.75rem; font-weight: 600; letter-spacing: 0.3px; white-space: nowrap; }
.badge-low     { background: #d1fae5; color: #065f46; }
.badge-medium  { background: #fef3c7; color: #92400e; }
.badge-high    { background: #fee2e2; color: #991b1b; }
.intent-info   { background: #dbeafe; color: #1e40af; }
.intent-comm   { background: #ede9fe; color: #5b21b6; }
.intent-trans  { background: #dcfce7; color: #166534; }
.kw-suggestion { color: #4b6a8a; font-size: 0.8rem; font-style: italic; }

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
[data-testid="stSidebar"] * { color: #f7fbff !important; }

.section-title      { font-size: 1.1rem; font-weight: 700; color: #143761; margin-bottom: 0.4rem; }
.seo-indicator-good { color: #0a7f3f; font-weight: 700; }
.seo-indicator-mid  { color: #b56b0a; font-weight: 700; }
.seo-indicator-low  { color: #b01d1d; font-weight: 700; }
</style>
"""
