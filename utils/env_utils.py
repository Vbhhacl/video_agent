"""Helpers for resolving configuration across local and cloud environments."""

import os


def load_secrets():
    """Merge Streamlit secrets into ``os.environ`` (used on Streamlit Cloud).

    On Streamlit Community Cloud, secrets configured in the dashboard are exposed
    through ``st.secrets``. The rest of the codebase reads API keys with
    ``os.getenv``, so we mirror secrets into the process environment as a fallback
    (existing environment variables always take priority).
    """
    try:
        import streamlit as st

        secrets = st.secrets
    except Exception:
        return  # not running inside a Streamlit runtime

    try:
        items = secrets.items()
    except Exception:
        # No secrets.toml configured (e.g. local dev). Nothing to merge.
        return

    for key, value in items:
        if isinstance(value, dict):
            # Support sectioned secrets, e.g. [MISTRAL] api_key = "..."
            # -> env var MISTRAL_API_KEY.
            for sub_key, sub_value in value.items():
                env_name = f"{key}_{sub_key}".upper()
                os.environ.setdefault(env_name, str(sub_value))
        else:
            os.environ.setdefault(str(key), str(value))

