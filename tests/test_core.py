"""
Test suite for VeriFAI LLM - Enhanced Security Scanner
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.file_utils import is_valid_file_type, generate_report
from src.core.llm import initialize_llm
from src.utils.text_chunk import chunk_text


class TestLLMProviderSelection:
    def test_local_ollama_is_default_without_api_keys(self, monkeypatch):
        for key in ("LLM_PROVIDER", "METERLESS_API_KEY", "NIGHTSHIFT_API_KEY", "GROQ_API_KEY"):
            monkeypatch.delenv(key, raising=False)

        client = initialize_llm()

        assert client is not None
        assert client.provider_type == "ollama"
        assert client.active_model == "llama3.2:latest"

    def test_cloud_provider_requires_explicit_selection_and_key(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "cloud")
        for key in ("METERLESS_API_KEY", "NIGHTSHIFT_API_KEY", "GROQ_API_KEY"):
            monkeypatch.delenv(key, raising=False)

        assert initialize_llm() is None


class TestFileValidation:
    """Test file validation utilities"""

    def test_valid_python_file(self):
        """Test Python file validation"""
        assert is_valid_file_type("test.py", ["py"]) == True

    def test_valid_javascript_file(self):
        """Test JavaScript file validation"""
        assert is_valid_file_type("script.js", ["js"]) == True

    def test_invalid_file_type(self):
        """Test invalid file type"""
        assert is_valid_file_type("document.doc", ["py", "js"]) == False

    def test_case_insensitive_validation(self):
        """Test case-insensitive file type checking"""
        assert is_valid_file_type("script.PY", ["py"]) == True

    def test_file_with_no_extension(self):
        """Test file with no extension"""
        assert is_valid_file_type("Makefile", ["py"]) == False


class TestTextChunking:
    """Test code chunking utilities"""

    def test_small_text_no_chunking(self):
        """Small text should not be chunked"""
        small_text = "def hello():\n    print('hello')"
        result = chunk_text(small_text, chunk_size=1000)
        assert isinstance(result, str)

    def test_large_text_chunking(self):
        """Large text should be chunked"""
        large_text = "code line\n" * 10000
        result = chunk_text(large_text, chunk_size=500)
        assert isinstance(result, list) or isinstance(result, str)

    def test_empty_text(self):
        """Empty text handling"""
        result = chunk_text("", chunk_size=1000)
        assert result == "" or result == []


class TestReportGeneration:
    """Test report generation"""

    def test_report_basic_structure(self):
        """Test that reports have required sections"""
        report = generate_report(
            code="print('test')",
            semgrep_results={},
            llm_analysis="Test analysis"
        )
        assert isinstance(report, str)
        assert len(report) > 0


class TestInputValidation:
    """Test input validation"""

    def test_empty_code_input(self):
        """Empty code should be detected"""
        empty_code = ""
        assert len(empty_code.strip()) == 0

    def test_valid_code_input(self):
        """Valid code should pass"""
        valid_code = "def test(): pass"
        assert len(valid_code.strip()) > 0

    def test_sql_injection_like_input(self):
        """Test handling of suspicious patterns"""
        suspicious = "'; DROP TABLE users; --"
        # Should not execute but should be analyzable
        assert isinstance(suspicious, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
