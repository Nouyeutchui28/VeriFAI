# VeriFAI LLM Development Guide

## Quick Start for Developers

### Prerequisites
- Python 3.9+
- Git
- Virtual environment tool (venv/conda)

### Setup

```bash
# Clone the repository
git clone https://github.com/codebytemirza/VeriFAI-LLM.git
cd VeriFAI LLM

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov pylint flake8 black bandit

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_security.py -v

# Run specific test
pytest tests/test_security.py::TestInputSanitization::test_null_byte_injection -v

# Run with markers
pytest -m "security" -v
```

---

## Code Quality

```bash
# Format code with Black
black src/ tests/ --line-length=100

# Check formatting
black --check src/ tests/

# Lint with Flake8
flake8 src/ tests/ --max-line-length=100

# Lint with Pylint
pylint src/ --fail-under=7.0

# Security scan with Bandit
bandit -r src/ -v
```

---

## Running the Application

```bash
# Streamlit UI
streamlit run app.py

# CLI Interface
python cli.py

# With logging
LOGLEVEL=DEBUG streamlit run app.py
```

---

## Project Structure

```
VeriFAI LLM/
├── src/
│   ├── core/              # Core analysis modules
│   │   ├── llm.py        # LLM initialization
│   │   ├── security.py   # Security analysis
│   │   ├── file_utils.py # File handling
│   │   ├── input_validator.py  # Validation
│   │   ├── error_handler.py    # Error handling
│   │   ├── logger.py     # Logging setup
│   │   └── metrics.py    # Metrics collection
│   ├── ui/                # Streamlit UI
│   │   ├── main.py       # App entry point
│   │   ├── scanner_tab.py
│   │   ├── chat_tab.py
│   │   └── rules_tab.py
│   └── utils/             # Utilities
│       └── text_chunk.py
├── tests/                 # Test suite
│   ├── test_core.py
│   ├── test_security.py
│   └── conftest.py
├── .github/
│   └── workflows/         # CI/CD pipelines
├── API_DOCUMENTATION.md
├── SECURITY_AUDIT.md
└── requirements.txt
```

---

## Key Modules

### `src.core.security`
Security analysis combining Semgrep + LLM

**Main Functions:**
- `analyze_security()` - Primary analysis function
- `generate_patch_suggestions()` - Generate fixes
- `security_chat()` - Interactive Q&A
- `suggest_rules()` - Generate Semgrep rules

### `src.core.input_validator`
Input validation and sanitization

**Key Class:** `InputValidator`
- `validate_code_input()`
- `validate_filename()`
- `validate_file_extension()`
- `check_dangerous_patterns()`

### `src.core.error_handler`
Centralized error handling

**Exception Classes:**
- `ValidationError`
- `AnalysisError`
- `LLMError`
- `SemgrepError`
- etc.

### `src.core.logger`
Logging system

**Functions:**
- `setup_logging()` - Initialize logging
- `get_logger()` - Get logger instance

### `src.core.metrics`
Performance monitoring

**Main Class:** `MetricsCollector`
- `start_scan()` - Begin tracking
- `end_scan()` - Finish tracking
- `get_summary()` - Get statistics

---

## Adding New Features

### 1. Add Validation
```python
from src.core.input_validator import InputValidator

# Validate user input
try:
    clean_input = InputValidator.validate_code_input(user_code)
except ValidationError as e:
    # Handle error
    pass
```

### 2. Add Error Handling
```python
from src.core.error_handler import ErrorHandler

# Safe execution
result, error = ErrorHandler.safe_execute(my_function, arg1, arg2)
if error:
    print(f"Error: {error}")
```

### 3. Add Logging
```python
from src.core.logger import get_logger

logger = get_logger(__name__)
logger.info("Starting process")
logger.error("Error occurred", exc_info=e)
```

### 4. Add Metrics
```python
from src.core.metrics import MetricsCollector

collector = MetricsCollector()
metrics = collector.start_scan("scan_001")

# ... perform work ...

collector.end_scan(status="completed")
```

---

## Git Workflow

### Creating a Feature Branch
```bash
git checkout -b feature/your-feature-name
git add src/
git commit -m "Add your feature"
git push origin feature/your-feature-name
```

### Commits Should
- Include specific changes only
- Have clear, descriptive messages
- Reference related issues: "Fixes #123"
- Pass all tests before pushing

---

## Common Tasks

### Running Full Test Suite with Coverage
```bash
pytest tests/ -v --cov=src --cov-report=html
# Open htmlcov/index.html to view coverage
```

### Checking for Security Issues
```bash
bandit -r src/ -v
safety check --requirements requirements.txt
```

### Building Docker Image
```bash
docker build -t verifai_llm:dev .
docker run -p 8501:8501 --env-file .env verifai_llm:dev
```

### Updating Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip list --outdated
```

---

## Debugging Tips

### Enable Debug Logging
```bash
LOGLEVEL=DEBUG streamlit run app.py
```

### Using Python Debugger
```python
import pdb; pdb.set_trace()
```

### Check Logs
```bash
tail -f logs/verifai_llm_*.log
```

### Test Individual Components
```python
# In Python shell
from src.core.input_validator import InputValidator
InputValidator.validate_code_input("test code")
```

---

## Performance Tips

1. **Code Chunking:** Automatically handles large files
2. **Lazy Loading:** LLM model loaded on first use
3. **Caching:** Consider implementing for repeated analyses

---

## Contributing Guidelines

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run full test suite: `pytest tests/ -v --cov=src`
6. Ensure code passes linting: `black src/ && flake8 src/`
7. Commit with clear messages
8. Push and create pull request

---

## Resources

- [Semgrep Documentation](https://semgrep.dev/)
- [Ollama Documentation](https://ollama.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Pytest Documentation](https://docs.pytest.org/)

---

## Support

For questions or issues:
1. Check existing issues on GitHub
2. Review logs in `logs/` directory
3. Check API_DOCUMENTATION.md
4. Open a new issue with details

.md
4. Open a new issue with details

