"""
Logging configuration for VeriFAI LLM
Includes log sanitization to prevent sensitive data leakage.
"""

import logging
import logging.handlers
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Any, str


# ============================================================================
# Log Sanitization
# ============================================================================

# Patterns to detect and redact sensitive information in logs
SENSITIVE_PATTERNS = [
    # API Keys and tokens
    (r'(?i)(api[_-]?key|apikey|token|secret[_-]?key|access[_-]?token)\s*[=:]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?', r'\1=***REDACTED***'),
    
    # Passwords in connection strings
    (r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']?([^\s"\']{4,})["\']?', r'\1=***REDACTED***'),
    
    # AWS/GCP/Azure credentials
    (r'(?i)(AKIA[0-9A-Z]{16})', '***AWS_KEY_REDACTED***'),
    (r'(?i)(AIza[0-9A-Za-z\-_]{35})', '***GOOGLE_KEY_REDACTED***'),
    
    # JWT tokens
    (r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+', '***JWT_REDACTED***'),
    
    # Private keys
    (r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----[\s\S]*?-----END\s+(RSA\s+)?PRIVATE\s+KEY-----', '***PRIVATE_KEY_REDACTED***'),
    
    # Email addresses (optional - comment out if emails are needed)
    # (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '***EMAIL_REDACTED***'),
    
    # IP addresses (optional - comment out if IPs are needed for debugging)
    # (r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '***IP_REDACTED***'),
    
    # Database connection strings with credentials
    (r'(postgresql|mysql|mongodb)://([^:]+):([^@]+)@', r'\1://\2:***PASSWORD***@'),
]

# Code snippet markers to redact large code blocks
CODE_BLOCK_PATTERN = r'```[\s\S]*?```'


class SanitizingFilter(logging.Filter):
    """
    Logging filter that sanitizes log messages to remove sensitive information.
    """
    
    def __init__(self, patterns: list = None, max_code_length: int = 500):
        """
        Initialize the sanitizing filter.
        
        Args:
            patterns: List of (pattern, replacement) tuples for sanitization
            max_code_length: Maximum length for code snippets in logs
        """
        super().__init__()
        self.patterns = patterns or SENSITIVE_PATTERNS
        self.max_code_length = max_code_length
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Sanitize the log record message before logging.
        
        Args:
            record: The log record to sanitize
            
        Returns:
            True if the record should be logged
        """
        if hasattr(record, 'msg'):
            record.msg = self.sanitize(str(record.msg))
        
        if record.args:
            sanitized_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    sanitized_args.append(self.sanitize(arg))
                else:
                    sanitized_args.append(arg)
            record.args = tuple(sanitized_args)
        
        return True
    
    def sanitize(self, text: str) -> str:
        """
        Sanitize text by removing or redacting sensitive information.
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        if not text or not isinstance(text, str):
            return text
        
        sanitized = text
        
        # Apply all sensitive patterns
        for pattern, replacement in self.patterns:
            sanitized = re.sub(pattern, replacement, sanitized)
        
        # Truncate overly long code snippets
        code_blocks = re.findall(CODE_BLOCK_PATTERN, sanitized)
        for block in code_blocks:
            if len(block) > self.max_code_length:
                truncated = block[:self.max_code_length] + f"\n... [truncated, {len(block) - self.max_code_length} chars redacted]"
                sanitized = sanitized.replace(block, truncated)
        
        # Truncate very long single lines
        lines = sanitized.split('\n')
        truncated_lines = []
        for line in lines:
            if len(line) > 1000:
                truncated_lines.append(line[:1000] + f"... [line truncated, {len(line) - 1000} chars redacted]")
            else:
                truncated_lines.append(line)
        
        return '\n'.join(truncated_lines)


def sanitize_log_message(message: str) -> str:
    """
    Utility function to sanitize a log message.
    Can be used for manual sanitization when needed.
    
    Args:
        message: The message to sanitize
        
    Returns:
        Sanitized message
    """
    sanitizer = SanitizingFilter()
    return sanitizer.sanitize(message)


def setup_logging(log_level=logging.INFO, log_dir="logs", enable_sanitization: bool = True):
    """
    Setup logging configuration for the application

    Args:
        log_level: Logging level (default: INFO)
        log_dir: Directory to store log files (default: 'logs')
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # Create logger
    logger = logging.getLogger("verifai_llm")
    logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Log format
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler - rotating
    log_file = log_path / f"verifai_llm_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(log_format)
    
    # Add sanitizing filter to prevent sensitive data in logs
    if enable_sanitization:
        file_handler.addFilter(SanitizingFilter())
    
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    
    # Add sanitizing filter to console output as well
    if enable_sanitization:
        console_handler.addFilter(SanitizingFilter())
    
    logger.addHandler(console_handler)

    return logger


def get_logger(name=None):
    """
    Get logger instance

    Args:
        name: Logger name (default: 'verifai_llm')

    Returns:
        Logger instance
    """
    if name is None:
        name = "verifai_llm"
    return logging.getLogger(name)


# Initialize default logger
logger = setup_logging()


class LoggerMixin:
    """Mixin class to add logging to classes"""

    @property
    def logger(self):
        """Get logger for the class"""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger
