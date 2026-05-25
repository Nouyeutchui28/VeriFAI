"""
Pytest configuration and fixtures
"""

import pytest
import os
from pathlib import Path


@pytest.fixture
def sample_python_code():
    """Sample vulnerable Python code"""
    return """
def login(username, password):
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    result = db.execute(query)
    return result.fetchone()
"""


@pytest.fixture
def sample_js_code():
    """Sample vulnerable JavaScript code"""
    return """
function getUserData(userId) {
    const html = `<div>${userId}</div>`;
    document.innerHTML = html;
    return html;
}
"""


@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary test file"""
    test_file = tmp_path / "test.py"
    test_file.write_text("print('test')")
    return test_file


@pytest.fixture
def temp_zip(tmp_path):
    """Create a temporary ZIP file for testing"""
    import zipfile
    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr("test.py", "print('test')")
        zf.writestr("test.js", "console.log('test');")
    return zip_path


@pytest.fixture
def mock_semgrep_results():
    """Mock Semgrep scan results"""
    return {
        "results": [
            {
                "check_id": "python.lang.security.injection.sql.sql-injection",
                "message": "SQL Injection detected",
                "path": "test.py",
                "line": 2,
                "severity": "HIGH"
            }
        ]
    }


@pytest.fixture(autouse=True)
def cleanup_env():
    """Clean up test environment"""
    yield
    # Cleanup code here if needed
