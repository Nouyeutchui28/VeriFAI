# VeriFAI LLM API Documentation

## Overview

VeriFAI LLM combines Semgrep's static analysis with a local Ollama AI engine (Phi-3) for intelligent security scanning. This document describes the core API for developers.

---

## Table of Contents

1. [Security Analysis](#security-analysis)
2. [File Utilities](#file-utilities)
3. [Input Validation](#input-validation)
4. [Error Handling](#error-handling)
5. [Logging](#logging)
6. [Metrics](#metrics)
7. [Examples](#examples)

---

## Security Analysis

### `analyze_security(semgrep_results, code_snippet, llm)`

Performs comprehensive security analysis combining Semgrep results with LLM insights.

**Parameters:**
- `semgrep_results` (dict): Results from Semgrep scan
- `code_snippet` (str): Source code to analyze
- `llm`: Initialized LLM instance

**Returns:**
- `str`: Comprehensive security analysis report

**Raises:**
- `AnalysisError`: If analysis fails
- `ValidationError`: If input is invalid

**Example:**
```python
from src.core.security import analyze_security
from src.core.llm import initialize_llm

llm = initialize_llm(model="llama-3.1-8b-instant", temperature=0.1)
analysis = analyze_security(
    semgrep_results={"results": []},
    code_snippet="def login(user, pwd): ...",
    llm=llm
)
print(analysis)
```

---

### `generate_patch_suggestions(semgrep_results, code_snippet, llm)`

Generates unified diff format patches for identified vulnerabilities.

**Parameters:**
- `semgrep_results` (dict): Semgrep scan results
- `code_snippet` (str): Source code
- `llm`: Initialized LLM instance

**Returns:**
- `str`: Patch suggestions in unified diff format

**Example:**
```python
patches = generate_patch_suggestions(
    semgrep_results=analysis_results,
    code_snippet=source_code,
    llm=llm
)
print(patches)
```

---

### `security_chat(code_snippet, llm_analysis, chat_history, query, llm)`

Provides interactive security consultation based on analysis.

**Parameters:**
- `code_snippet` (str): Original code
- `llm_analysis` (str): Previous LLM security analysis
- `chat_history` (list): Conversation history
- `query` (str): User's question
- `llm`: Initialized LLM instance

**Returns:**
- `str`: Response to the query

**Example:**
```python
response = security_chat(
    code_snippet=code,
    llm_analysis=analysis,
    chat_history=[],
    query="How do I fix the SQL injection?",
    llm=llm
)
```

---

### `suggest_rules(code_snippet, llm_analysis, llm)`

Generates custom Semgrep rules based on identified vulnerabilities.

**Parameters:**
- `code_snippet` (str): Source code
- `llm_analysis` (str): Identified vulnerabilities
- `llm`: Initialized LLM instance

**Returns:**
- `str`: YAML-formatted Semgrep rules

---

## File Utilities

### `generate_report(code, semgrep_results, llm_analysis)`

Generates a comprehensive security report.

**Parameters:**
- `code` (str): Source code
- `semgrep_results` (dict): Semgrep results
- `llm_analysis` (str): LLM analysis

**Returns:**
- `str`: Formatted report

---

### `extract_zip(zip_path, extract_to=None)`

Extracts ZIP files for analysis.

**Parameters:**
- `zip_path` (str): Path to ZIP file
- `extract_to` (str, optional): Extraction directory

**Returns:**
- `str`: Path to extracted directory

---

## Input Validation

### `InputValidator` Class

Provides comprehensive input validation and sanitization.

#### `validate_code_input(code: str) -> str`

Validates and cleans code input.

**Parameters:**
- `code` (str): Code to validate

**Returns:**
- `str`: Cleaned code

**Raises:**
- `ValidationError`: If validation fails

**Example:**
```python
from src.core.input_validator import InputValidator

try:
    clean_code = InputValidator.validate_code_input(user_code)
except ValidationError as e:
    print(f"Validation error: {e.message}")
```

---

#### `validate_filename(filename: str) -> str`

Validates and sanitizes filenames.

**Parameters:**
- `filename` (str): Filename to validate

**Returns:**
- `str`: Sanitized filename

---

#### `validate_file_extension(filename: str, allowed_extensions=None) -> bool`

Validates file extension.

**Parameters:**
- `filename` (str): File to check
- `allowed_extensions` (list, optional): Allowed extensions

**Returns:**
- `bool`: True if valid

---

#### `check_dangerous_patterns(code: str) -> List[str]`

Detects dangerous code patterns.

**Parameters:**
- `code` (str): Code to scan

**Returns:**
- `List[str]`: List of dangerous patterns found

---

## Error Handling

### Exception Classes

```python
from src.core.error_handler import (
    VeriFAI LLMException,
    ValidationError,
    FileHandlingError,
    AnalysisError,
    LLMError,
    SemgrepError,
    ConfigurationError,
    TimeoutError,
    RateLimitError
)
```

### `ErrorHandler` Class

Centralized error handling and formatting.

#### `format_error(exception: Exception) -> dict`

Formats exception for display.

**Returns:**
```python
{
    "error_code": "VALIDATION_ERROR",
    "message": "Detailed error message",
    "user_message": "User-friendly message",
    "details": {}
}
```

#### `safe_execute(func, *args, **kwargs) -> tuple[Any, Optional[str]]`

Safely executes a function with error handling.

**Returns:**
- `Tuple[result, error_message]`

**Example:**
```python
from src.core.error_handler import ErrorHandler

result, error = ErrorHandler.safe_execute(risky_function, arg1, arg2)
if error:
    print(f"Error: {error}")
else:
    print(f"Result: {result}")
```

---

## Logging

### `setup_logging(log_level=logging.INFO, log_dir="logs")`

Initializes logging system.

**Example:**
```python
from src.core.logger import setup_logging

logger = setup_logging(log_level="INFO", log_dir="logs")
logger.info("Starting analysis")
```

### `get_logger(name=None)`

Gets logger instance.

**Example:**
```python
from src.core.logger import get_logger

logger = get_logger("module_name")
logger.info("Message")
```

---

## Metrics

### `MetricsCollector` Class

Collects scan metrics and performance data.

#### `start_scan(scan_id: str) -> ScanMetrics`

Starts tracking a scan.

#### `end_scan(status: str = "completed", error_message=None)`

Ends scan tracking and saves metrics.

#### `get_summary() -> Dict[str, Any]`

Returns metrics summary.

**Example:**
```python
from src.core.metrics import MetricsCollector

collector = MetricsCollector()
metrics = collector.start_scan("scan_001")

# ... perform analysis ...

collector.update_scan(
    files_scanned=5,
    vulnerabilities_found=2
)
collector.end_scan(status="completed")

summary = collector.get_summary()
print(summary)
```

---

## Examples

### Basic Security Analysis

```python
from src.core.security import analyze_security
from src.core.llm import initialize_llm
from src.core.input_validator import InputValidator

# Validate input
code = InputValidator.validate_code_input(user_code)

# Initialize LLM
llm = initialize_llm(model="llama-3.1-8b-instant")

# Run Semgrep
import subprocess
result = subprocess.run(
    ["semgrep", "--json", "-"],
    input=code,
    capture_output=True,
    text=True
)
semgrep_results = json.loads(result.stdout)

# Analyze with LLM
analysis = analyze_security(semgrep_results, code, llm)
print(analysis)
```

### Error Handling

```python
from src.core.error_handler import ErrorHandler

try:
    result = analyze_security(results, code, llm)
except Exception as e:
    formatted = ErrorHandler.format_error(e)
    print(f"Error: {formatted['user_message']}")
    log_error(formatted)
```

---

## Configuration

VeriFAI LLM uses environment variables for configuration:

```
LOG_LEVEL=INFO
MAX_CODE_SIZE=10485760
METRICS_ENABLED=true
```

---

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review error messages and error codes
3. Consult the Contributing Guidelines

