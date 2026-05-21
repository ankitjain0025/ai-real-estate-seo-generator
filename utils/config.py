"""Runtime configuration helpers for local and Streamlit Cloud environments."""

from __future__ import annotations

import os


def _clean_key(value: object) -> str:
    """Normalize secret values and strip accidental wrapping quotes."""
    if value is None:
        return ""
    text = str(value).strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {'"', "'"}:
        text = text[1:-1].strip()
    return text


def get_gemini_api_key() -> str:
    """Resolve Gemini API key from Streamlit secrets or environment variable."""
    try:
        import streamlit as st
        for key_name in ("GEMINI_API_KEY", "gemini_api_key"):
            try:
                value = _clean_key(st.secrets[key_name])
                if value and value != "your_gemini_api_key_here":
                    return value
            except (KeyError, AttributeError):
                pass
        try:
            value = _clean_key(st.secrets["gemini"]["api_key"])
            if value and value != "your_gemini_api_key_here":
                return value
        except (KeyError, AttributeError, TypeError):
            pass
    except Exception:
        pass

    env_key = _clean_key(os.getenv("GEMINI_API_KEY", ""))
    if env_key and env_key != "your_gemini_api_key_here":
        return env_key

    return ""


def get_gemini_model() -> str:
    """Return the configured Gemini model name."""
    return "gemini-2.5-flash"


def configure_runtime_secrets() -> None:
    """Expose resolved secrets to process environment for shared modules."""
    key = get_gemini_api_key()
    if key:
        os.environ["GEMINI_API_KEY"] = key
