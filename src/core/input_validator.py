"""
Input validation and sanitization utilities for VeriFAI LLM
"""

import re
import os
from pathlib import Path
from typing import Optional, List


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class InputValidator:
    """Validates and sanitizes user inputs"""

    # Constants
    MAX_CODE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    MAX_FILENAME_LENGTH = 255
    ALLOWED_EXTENSIONS = {
        'py', 'js', 'ts', 'java', 'cpp', 'c', 'cs', 'php', 'rb', 'go',
        'html', 'css', 'sql', 'json', 'yaml', 'yml', 'xml', 'sh', 'bash',
        'tsx', 'jsx', 'kt', 'rs', 'swift'
    }

    # Dangerous patterns
    DANGEROUS_PATTERNS = [
        r'\.\.[\\/]',  # Path traversal
        r'exec\s*\(',  # exec() calls
        r'eval\s*\(',  # eval() calls
        r'__import__',  # Dynamic imports
        r'subprocess\.call',  # Subprocess execution
        r'os\.system',  # OS system calls
    ]

    @staticmethod
    def validate_code_input(code: str) -> str:
        """
        Validate and clean code input

        Args:
            code: Code string to validate

        Returns:
            Cleaned code string

        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(code, str):
            raise ValidationError("Code must be a string")

        if not code.strip():
            raise ValidationError("Code cannot be empty")

        if len(code) > InputValidator.MAX_CODE_SIZE:
            raise ValidationError(
                f"Code exceeds maximum size of {InputValidator.MAX_CODE_SIZE / 1024 / 1024:.1f}MB"
            )

        # Check for null bytes
        if '\x00' in code:
            code = code.replace('\x00', '')

        # Check for excessive special characters
        special_chars = sum(1 for c in code if ord(c) < 32 and c not in '\n\r\t')
        if special_chars / len(code) > 0.1:  # More than 10% control chars
            raise ValidationError("Code contains excessive control characters")

        return code

    @staticmethod
    def validate_filename(filename: str) -> str:
        """
        Validate filename for security

        Args:
            filename: Filename to validate

        Returns:
            Cleaned filename

        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(filename, str):
            raise ValidationError("Filename must be a string")

        if not filename.strip():
            raise ValidationError("Filename cannot be empty")

        if len(filename) > InputValidator.MAX_FILENAME_LENGTH:
            raise ValidationError(
                f"Filename exceeds maximum length of {InputValidator.MAX_FILENAME_LENGTH}"
            )

        # Remove path components
        filename = os.path.basename(filename)

        # Check for path traversal
        if '..' in filename:
            raise ValidationError("Filename contains invalid path traversal")

        # Remove special characters except . and -
        clean_filename = re.sub(r'[^\w\-.]', '', filename)

        if not clean_filename:
            raise ValidationError("Filename contains only invalid characters")

        return clean_filename

    @staticmethod
    def validate_file_path(filepath: str) -> str:
        """
        Validate file path for security

        Args:
            filepath: File path to validate

        Returns:
            Normalized file path

        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(filepath, str):
            raise ValidationError("File path must be a string")

        if not filepath.strip():
            raise ValidationError("File path cannot be empty")

        # Normalize path
        filepath = os.path.normpath(filepath)

        # Check for path traversal
        if '..' in filepath:
            raise ValidationError("File path contains invalid path traversal")

        # Resolve to absolute path to prevent escaping
        try:
            filepath = str(Path(filepath).resolve())
        except (OSError, RuntimeError) as e:
            raise ValidationError(f"Invalid file path: {str(e)}")

        return filepath

    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: Optional[List[str]] = None) -> bool:
        """
        Validate file extension

        Args:
            filename: Filename to check
            allowed_extensions: List of allowed extensions (without dots)

        Returns:
            True if extension is allowed

        Raises:
            ValidationError: If extension is not allowed
        """
        if allowed_extensions is None:
            allowed_extensions = InputValidator.ALLOWED_EXTENSIONS

        filename = InputValidator.validate_filename(filename)
        ext = filename.split('.')[-1].lower() if '.' in filename else ''

        if not ext:
            raise ValidationError("File has no extension")

        if ext not in allowed_extensions:
            raise ValidationError(f"File type .{ext} is not allowed")

        return True

    @staticmethod
    def validate_file_size(file_size: int, max_size: Optional[int] = None) -> bool:
        """
        Validate file size

        Args:
            file_size: Size of file in bytes
            max_size: Maximum allowed size (defaults to MAX_FILE_SIZE)

        Returns:
            True if size is valid

        Raises:
            ValidationError: If size exceeds limit
        """
        if max_size is None:
            max_size = InputValidator.MAX_FILE_SIZE

        if file_size > max_size:
            raise ValidationError(
                f"File size {file_size / 1024 / 1024:.1f}MB exceeds maximum "
                f"of {max_size / 1024 / 1024:.1f}MB"
            )

        return True

    @staticmethod
    def check_dangerous_patterns(code: str) -> List[str]:
        """
        Check for dangerous patterns in code

        Args:
            code: Code to check

        Returns:
            List of found dangerous patterns
        """
        found_patterns = []

        for pattern in InputValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                found_patterns.append(pattern)

        return found_patterns

    @staticmethod
    def sanitize_for_display(text: str) -> str:
        """
        Sanitize text for safe display in UI

        Args:
            text: Text to sanitize

        Returns:
            Sanitized text
        """
        # Remove HTML/script tags
        text = re.sub(r'<[^>]+>', '', text)

        # Escape special characters for Streamlit
        text = text.replace('<', '&lt;').replace('>', '&gt;')

        return text

# Top-level helper functions for easier access
def validate_code_input(code: str) -> str:
    return InputValidator.validate_code_input(code)
