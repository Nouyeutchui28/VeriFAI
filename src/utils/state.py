import streamlit as st
from typing import Any, Optional

class AppState:
    """Centralized management for Streamlit session state."""

    # Default state values
    DEFAULTS = {
        "authenticated": False,
        "user_info": None,
        "user_id": None,
        "access_token": None,
        "current_page": "🏠 Dashboard",
        "prev_page": None,
        "chat_history": [],
        "analysis_results": None,
        "code_content": "",
        "llm_analysis": "",
        "show_chat": False,
        "legal_agreed": False,
        "otp_verification_email": None,
        "github_repo_path": None,
        "github_repo_url": None,
        "model_selection": "Qwen2.5-Coder-7B-Instruct",
        "llm_temperature": 0.2,
        "theme": "dark",
        "notifications_enabled": True,
        "first_time_user": True,
        "last_scan_id": None,
        "favorites": [],
        "patch_verified": False,
        "patch_applied": False,
    }

    @staticmethod
    def initialize() -> None:
        """Initialize all required session state variables."""
        for key, default_value in AppState.DEFAULTS.items():
            if key not in st.session_state:
                st.session_state[key] = default_value

    @staticmethod
    def logout() -> None:
        """Handle user logout."""
        st.session_state.authenticated = False
        st.session_state.user_info = None
        st.session_state.access_token = None
        st.session_state.user_id = None
        st.rerun()

    @staticmethod
    def set_page(page_name: str) -> None:
        """Set the current page."""
        st.session_state.prev_page = st.session_state.get("current_page")
        st.session_state.current_page = page_name
        st.rerun()

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """Safely get a value from session state."""
        return st.session_state.get(key, default)

    @staticmethod
    def set(key: str, value: Any) -> None:
        """Set a value in session state."""
        st.session_state[key] = value

    @staticmethod
    def reset(key: str) -> None:
        """Reset a key to its default value."""
        if key in AppState.DEFAULTS:
            st.session_state[key] = AppState.DEFAULTS[key]

    @staticmethod
    def clear_analysis() -> None:
        """Clear analysis-related state."""
        st.session_state.analysis_results = None
        st.session_state.code_content = ""
        st.session_state.llm_analysis = ""
        st.session_state.chat_history = []

    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated."""
        return st.session_state.get("authenticated", False)

    @staticmethod
    def get_user_info() -> Optional[dict]:
        """Get current user info."""
        return st.session_state.get("user_info")

    @staticmethod
    def set_auth(user_info: dict, access_token: str, user_id: str) -> None:
        """Set authentication data."""
        st.session_state.authenticated = True
        st.session_state.user_info = user_info
        st.session_state.access_token = access_token
        st.session_state.user_id = user_id
