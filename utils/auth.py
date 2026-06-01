"""
Authentication module for RealSEO AI.

Credentials are loaded from Streamlit secrets (secrets.toml).
Passwords are stored as plain text in secrets — streamlit-authenticator
hashes them automatically at runtime (auto_hash=True).

secrets.toml structure:
------------------------
GEMINI_API_KEY = "your_key"

[auth]
cookie_name = "realseo_auth"
cookie_key  = "any_long_random_secret_string"

[auth.credentials.usernames.client1]
email    = "client1@example.com"
name     = "Client One"
password = "their_password"

[auth.credentials.usernames.client2]
email    = "client2@example.com"
name     = "Client Two"
password = "their_password"
"""

from __future__ import annotations

from typing import Optional, Tuple

import streamlit as st
import streamlit_authenticator as stauth


# ── Cookie defaults (overridden by secrets) ─────────────────────────────────
_DEFAULT_COOKIE_NAME = "realseo_auth_cookie"
_DEFAULT_COOKIE_KEY  = "realseo_default_secret_change_me"
_DEFAULT_EXPIRY_DAYS = 30


def _load_credentials() -> Tuple[dict, str, str, float]:
    """
    Pull credentials and cookie config from st.secrets.
    Returns (credentials_dict, cookie_name, cookie_key, expiry_days).
    """
    try:
        auth_cfg = st.secrets["auth"]
    except (KeyError, AttributeError):
        st.error(
            "Authentication config missing in Streamlit secrets.\n\n"
            "Add an [auth] section to your secrets. See the README for the format."
        )
        st.stop()

    # Build credentials dict from secrets
    try:
        raw_users = dict(auth_cfg["credentials"]["usernames"])
    except (KeyError, TypeError):
        st.error("No users found under [auth.credentials.usernames] in secrets.")
        st.stop()

    # Convert AttrDict / toml objects to plain Python dicts
    usernames: dict = {}
    for username, info in raw_users.items():
        usernames[username] = {
            "email":    str(info.get("email", "")),
            "name":     str(info.get("name", username)),
            "password": str(info.get("password", "")),
        }

    credentials = {"usernames": usernames}

    cookie_name   = str(auth_cfg.get("cookie_name",   _DEFAULT_COOKIE_NAME))
    cookie_key    = str(auth_cfg.get("cookie_key",    _DEFAULT_COOKIE_KEY))
    expiry_days   = float(auth_cfg.get("cookie_expiry_days", _DEFAULT_EXPIRY_DAYS))

    return credentials, cookie_name, cookie_key, expiry_days


def build_authenticator() -> stauth.Authenticate:
    """Build and cache the Authenticate object for this session."""
    if "authenticator" not in st.session_state:
        credentials, cookie_name, cookie_key, expiry_days = _load_credentials()
        st.session_state["authenticator"] = stauth.Authenticate(
            credentials=credentials,
            cookie_name=cookie_name,
            cookie_key=cookie_key,
            cookie_expiry_days=expiry_days,
            auto_hash=True,
        )
    return st.session_state["authenticator"]


def render_login() -> Tuple[Optional[str], bool, Optional[str]]:
    """
    Render the login form.
    Returns (name, authentication_status, username).
      authentication_status=True  → logged in
      authentication_status=False → wrong credentials
      authentication_status=None  → not attempted yet
    """
    authenticator = build_authenticator()
    result = authenticator.login(
        location="main",
        max_login_attempts=5,
        fields={
            "Form name": "RealSEO AI — Login",
            "Username":  "Username",
            "Password":  "Password",
            "Login":     "Login",
        },
        clear_on_submit=False,
        key="main_login_form",
    )

    # v0.4.x returns a tuple (name, auth_status, username)
    if result is None:
        return None, False, None

    name, auth_status, username = result
    return name, bool(auth_status) if auth_status is not None else False, username


def render_logout(username: Optional[str] = None) -> None:
    """Render logout button in sidebar with user greeting."""
    authenticator = build_authenticator()
    display_name = ""
    if username:
        try:
            creds, _, _, _ = _load_credentials()
            display_name = creds["usernames"].get(username, {}).get("name", username)
        except Exception:
            display_name = username

    if display_name:
        st.sidebar.markdown(f"👤 **{display_name}**")
    authenticator.logout(
        button_name="Logout",
        location="sidebar",
        key="sidebar_logout",
    )


def is_authenticated() -> bool:
    """Return True if current session has a valid authenticated user."""
    return st.session_state.get("authentication_status") is True
