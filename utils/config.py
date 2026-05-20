"""Runtime configuration helpers for local and Streamlit Cloud environments."""

from __future__ import annotations

import os


def get_xai_api_key() -> str:
    """Resolve xAI API key from environment or Streamlit secrets."""
    key = os.getenv("XAI_API_KEY", "").strip()
    if key:
        return key

    try:
        import streamlit as st

        if hasattr(st, "secrets") and "XAI_API_KEY" in st.secrets:
            return str(st.secrets["XAI_API_KEY"]).strip()
    except Exception:
        pass

    return ""


def configure_runtime_secrets() -> None:
    """Expose Streamlit Cloud secrets to process environment for shared modules."""
    key = get_xai_api_key()
    if key:
        os.environ["XAI_API_KEY"] = key
