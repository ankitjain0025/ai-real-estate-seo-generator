"""Runtime configuration helpers for local and Streamlit Cloud environments."""

from __future__ import annotations

import os
from typing import Iterable, Tuple


def _clean_key(value: object) -> str:
    """Normalize secret values and strip accidental wrapping quotes."""
    if value is None:
        return ""
    text = str(value).strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {'"', "'"}:
        text = text[1:-1].strip()
    return text


def _secret_candidates() -> Iterable[Tuple[str, ...]]:
    """Supported secret lookup paths (root and nested)."""
    return (
        ("XAI_API_KEY",),
        ("xai_api_key",),
        ("xai", "api_key"),
        ("xai", "API_KEY"),
        ("xai", "XAI_API_KEY"),
        ("secrets", "XAI_API_KEY"),
    )


def _read_nested_secret(secrets: object, path: Tuple[str, ...]) -> str:
    """Read a nested Streamlit secret path safely."""
    node = secrets
    for part in path:
        if node is None or part not in node:
            return ""
        node = node[part]
    return _clean_key(node)


def get_xai_api_key() -> str:
    """Resolve xAI API key from environment or Streamlit secrets."""
    env_key = _clean_key(os.getenv("XAI_API_KEY", ""))
    if env_key and env_key != "your_xai_api_key_here":
        return env_key

    try:
        import streamlit as st

        secrets = st.secrets
        for path in _secret_candidates():
            value = _read_nested_secret(secrets, path)
            if value and value != "your_xai_api_key_here":
                return value
    except Exception:
        pass

    return ""


def get_xai_model() -> str:
    """Return configured xAI model with a safe default."""
    model = _clean_key(os.getenv("XAI_MODEL", "grok-4.3"))
    return model or "grok-4.3"


def configure_runtime_secrets() -> None:
    """Expose resolved secrets to process environment for shared modules."""
    key = get_xai_api_key()
    if key:
        os.environ["XAI_API_KEY"] = key

    try:
        import streamlit as st

        if hasattr(st, "secrets") and "XAI_MODEL" in st.secrets:
            model = _clean_key(st.secrets["XAI_MODEL"])
            if model:
                os.environ["XAI_MODEL"] = model
    except Exception:
        pass
