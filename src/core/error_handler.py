"""
Error handling and custom exceptions for VeriFAI LLM
"""

from typing import Optional, Any
from src.core.logger import get_logger


logger = get_logger(__name__)


class VeriFAILLMException(Exception):
    """Base exception for VeriFAI LLM"""

    def __init__(self, message: str, error_code: str = "UNKNOWN", details: Optional[dict] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Convert exception to dictionary"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }


class ValidationError(VeriFAILLMException):
    """Raised when input validation fails"""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, "VALIDATION_ERROR", details)


class FileHandlingError(VeriFAILLMException):
    """Raised when file operations fail"""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, "FILE_ERROR", details)


class AnalysisError(VeriFAILLMException):
    """Raised when security analysis fails"""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, "ANALYSIS_ERROR", details)


class LLMError(VeriFAILLMException):
    """Raised when LLM operations fail"""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, "LLM_ERROR", details)


class SemgrepError(VeriFAILLMException):
    """Raised when Semgrep operations fail"""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, "SEMGREP_ERROR", details)


class ConfigurationError(VeriFAILLMException):
    """Raised when configuration is invalid"""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, "CONFIG_ERROR", details)


class TimeoutError(VeriFAILLMException):
    """Raised when operations timeout"""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, "TIMEOUT_ERROR", details)


class RateLimitError(VeriFAILLMException):
    """Raised when rate limit is exceeded"""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, "RATE_LIMIT_ERROR", details)


class ErrorHandler:
    """Centralized error handling"""

    # User-friendly error messages
    ERROR_MESSAGES = {
        "VALIDATION_ERROR": "The provided input is invalid. Please check your input and try again.",
        "FILE_ERROR": "An error occurred while processing files. Please ensure the file exists and is readable.",
        "ANALYSIS_ERROR": "An error occurred during security analysis. Please try again.",
        "LLM_ERROR": "An error occurred with the LLM service. Please check your API key and try again.",
        "SEMGREP_ERROR": "An error occurred with Semgrep. Please ensure Semgrep is properly installed.",
        "CONFIG_ERROR": "Configuration error. Please check your settings.",
        "TIMEOUT_ERROR": "The operation took too long and timed out. Please try with a smaller input.",
        "RATE_LIMIT_ERROR": "Rate limit exceeded. Please wait a moment before trying again.",
    }

    @staticmethod
    def format_error(exception: Exception) -> dict:
        """
        Format exception for display

        Args:
            exception: Exception to format

        Returns:
            Formatted error dictionary
        """
        if isinstance(exception, VeriFAILLMException):
            return {
                "error_code": exception.error_code,
                "message": exception.message,
                "user_message": ErrorHandler.ERROR_MESSAGES.get(
                    exception.error_code,
                    "An unexpected error occurred. Please try again."
                ),
                "details": exception.details
            }

        # Generic exception handling
        error_str = str(exception)
        logger.error(f"Unhandled exception: {error_str}", exc_info=exception)

        return {
            "error_code": "UNKNOWN",
            "message": error_str,
            "user_message": "An unexpected error occurred. Please try again.",
            "details": {}
        }

    @staticmethod
    def handle_error(exception: Exception, context: Optional[str] = None) -> str:
        """
        Handle error with logging

        Args:
            exception: Exception to handle
            context: Context information

        Returns:
            User-friendly error message
        """
        formatted_error = ErrorHandler.format_error(exception)

        # Log the error
        if context:
            logger.error(f"Error in {context}: {formatted_error['message']}")
        else:
            logger.error(f"Error occurred: {formatted_error['message']}")

        return formatted_error["user_message"]

    @staticmethod
    def safe_execute(func, *args, **kwargs) -> tuple[Any, Optional[str]]:
        """
        Safely execute a function with error handling

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Tuple of (result, error_message)
        """
        try:
            result = func(*args, **kwargs)
            return result, None
        except Exception as e:
            error_msg = ErrorHandler.handle_error(e, func.__name__)
            return None, error_msg
