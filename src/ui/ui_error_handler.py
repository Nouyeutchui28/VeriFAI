import streamlit as st
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class UIError:
    """User-friendly error categories and messages."""

    MESSAGES = {
        "file_read": "Failed to read file. Please ensure the file is valid and try again.",
        "file_write": "Failed to save file. Check permissions and available storage.",
        "zip_extract": "Failed to extract ZIP file. The file may be corrupted.",
        "upload_size": "File too large. Maximum size is 100MB.",
        "github_url": "Invalid GitHub URL. Please use format: https://github.com/user/repo",
        "network": "Network error. Please check your connection and try again.",
        "api": "Service unavailable. Please try again in a moment.",
        "validation": "Invalid input. Please check your entries and try again.",
        "auth": "Authentication failed. Please log in again.",
        "timeout": "Operation timed out. The target may be unavailable.",
        "unknown": "Something went wrong. Please try again.",
    }

    @staticmethod
    def get_friendly_message(error_type: str, context: str = "") -> str:
        """Get a user-friendly error message."""
        base_msg = UIError.MESSAGES.get(error_type, UIError.MESSAGES["unknown"])
        if context:
            return f"{base_msg}\n\n**Details:** {context}"
        return base_msg


def categorize_error(exception: Exception) -> str:
    """Categorize exception to determine user-friendly message."""
    error_str = str(exception).lower()

    if any(x in error_str for x in ["no such file", "file not found", "cannot find"]):
        return "file_read"
    elif any(x in error_str for x in ["permission denied", "access denied"]):
        return "file_write"
    elif any(x in error_str for x in ["zip", "extract", "corrupt"]):
        return "zip_extract"
    elif any(x in error_str for x in ["size", "too large", "100mb"]):
        return "upload_size"
    elif any(x in error_str for x in ["github", "url", "invalid"]):
        return "github_url"
    elif any(x in error_str for x in ["connection", "timeout", "refused"]):
        return "network"
    elif any(x in error_str for x in ["401", "403", "unauthorized"]):
        return "auth"
    elif any(x in error_str for x in ["timeout", "time out"]):
        return "timeout"
    elif any(x in error_str for x in ["validation", "invalid", "required"]):
        return "validation"

    return "unknown"


def handle_ui_error(
    exception: Exception,
    context: str = "",
    show_retry: bool = True,
    log_full: bool = True
) -> None:
    """
    Handle an error in the UI with user-friendly message and logging.

    Args:
        exception: The exception that occurred
        context: Additional context about what was being done
        show_retry: Whether to show retry suggestion
        log_full: Whether to log full exception details
    """
    error_type = categorize_error(exception)
    friendly_msg = UIError.get_friendly_message(error_type, str(exception)[:100])

    # Log full exception for debugging
    if log_full:
        logger.exception(f"UI Error ({error_type}): {context}", exc_info=exception)

    # Show user-friendly error in Streamlit
    with st.container():
        st.error(f"❌ {friendly_msg}")

        if show_retry:
            st.info("💡 Try again or contact support if the problem persists.")


def handle_ui_warning(message: str, context: str = "") -> None:
    """Show a warning message to user."""
    full_msg = f"{message}\n\n**Context:** {context}" if context else message
    st.warning(full_msg)


def handle_ui_success(message: str) -> None:
    """Show a success message to user."""
    st.success(message)


def handle_ui_info(message: str) -> None:
    """Show an info message to user."""
    st.info(message)


def with_error_handling(context: str = ""):
    """
    Decorator to wrap a function with error handling.

    Usage:
        @with_error_handling("scanning code")
        def scan_code():
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handle_ui_error(e, context or func.__name__)
                return None
        return wrapper
    return decorator
