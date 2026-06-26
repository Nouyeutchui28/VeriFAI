#!/usr/bin/env python3
"""
Comprehensive verification script for VeriFAI LLM Application
Tests all major components and functionalities
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

sys.path.insert(0, str(Path(__file__).parent))

def print_header(title):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_environment_configuration():
    """Test environment configuration"""
    print_header("1. Environment Configuration")

    checks = {
        "DATABASE_URL": os.environ.get("DATABASE_URL", "").strip(),
        "SECRET_KEY": os.environ.get("SECRET_KEY", "").strip(),
    }

    for key, value in checks.items():
        if value:
            if len(value) > 20:
                value_display = value[:10] + "..." + value[-10:]
            else:
                value_display = value
            print(f"  ✓ {key}: {value_display}")
        else:
            print(f"  ✗ {key}: NOT SET")

    return bool(checks["DATABASE_URL"])

def test_core_imports():
    """Test core module imports"""
    print_header("2. Core Module Imports")

    imports = {
        "file_utils": "src.core.file_utils",
        "llm": "src.core.llm",
        "security": "src.core.security",
        "github_handler": "src.core.github_handler",
    }

    success_count = 0
    for name, module in imports.items():
        try:
            __import__(module)
            print(f"  ✓ {name} imported successfully")
            success_count += 1
        except Exception as e:
            print(f"  ✗ {name} failed: {str(e)[:50]}")

    return success_count == len(imports)

def test_file_utilities():
    """Test file utility functions"""
    print_header("3. File Utilities")

    from src.core.file_utils import is_valid_file_type, cleanup_temp_files

    test_cases = [
        ("test.py", ["py"], True),
        ("script.js", ["js"], True),
        ("test.py", ["js"], False),
        ("document.pdf", ["py", "js"], False),
    ]

    success_count = 0
    for filename, allowed, expected in test_cases:
        result = is_valid_file_type(filename, allowed)
        status = "✓" if result == expected else "✗"
        print(f"  {status} is_valid_file_type('{filename}', {allowed}) = {result}")
        if result == expected:
            success_count += 1

    return success_count == len(test_cases)

def test_text_chunking():
    """Test text chunking utilities"""
    print_header("4. Text Chunking Utilities")

    from src.utils.text_chunk import chunk_text

    # Test small text
    small_text = "def hello():\n    print('hello')"
    result = chunk_text(small_text, chunk_size=1000)
    print(f"  ✓ Small text chunking: {type(result).__name__}")

    # Test large text
    large_text = "code line\n" * 1000
    result = chunk_text(large_text, chunk_size=500)
    is_list_or_str = isinstance(result, (list, str))
    print(f"  {'✓' if is_list_or_str else '✗'} Large text chunking: {type(result).__name__}")

    # Test empty text
    result = chunk_text("", chunk_size=1000)
    is_valid = result == "" or result == []
    print(f"  {'✓' if is_valid else '✗'} Empty text handling")

    return is_list_or_str and is_valid

def test_semgrep_availability():
    """Test Semgrep availability"""
    print_header("5. Semgrep Tool Availability")

    import subprocess

    try:
        result = subprocess.run(
            ["semgrep", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            print(f"  ✓ Semgrep installed: {version}")
            return True
        else:
            print(f"  ✗ Semgrep available but returned error: {result.stderr[:100]}")
            return False
    except FileNotFoundError:
        print(f"  ✗ Semgrep not found in PATH")
        return False
    except Exception as e:
        print(f"  ✗ Error checking Semgrep: {str(e)[:100]}")
        return False

def test_llm_initialization():
    """Test LLM initialization"""
    print_header("6. LLM Initialization")

    from src.core.llm import initialize_llm

    try:
        llm = initialize_llm(model="mixtral-8x7b-32768", temperature=0.1)
        if llm is not None:
            print(f"  ✓ LLM initialized successfully")
            print(f"    Model: mixtral-8x7b-32768")
            print(f"    Temperature: 0.1")
            return True
        else:
            print(f"  ✗ LLM initialization returned None (API key issue)")
            return False
    except Exception as e:
        print(f"  ✗ LLM initialization failed: {str(e)[:100]}")
        return False

def test_security_functions():
    """Test security analysis functions"""
    print_header("7. Security Analysis Functions")

    from src.core.security import run_semgrep_scan, analyze_security

    # Test Semgrep scan
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("import os\npassword = input('enter')\n")

            results = run_semgrep_scan(tmpdir, metrics_enabled=False)
            print(f"  ✓ Semgrep scan completed")
            print(f"    Results type: {type(results).__name__}")
            if "results" in results:
                print(f"    Findings: {len(results.get('results', []))}")
            return True
    except Exception as e:
        print(f"  ⚠ Semgrep scan test: {str(e)[:100]}")
        return False

def test_github_handler():
    """Test GitHub handler utilities"""
    print_header("8. GitHub Handler")

    try:
        from src.core.github_handler import validate_github_url

        test_urls = [
            ("https://github.com/user/repo", True),
            ("https://github.com/user/repo.git", True),
            ("invalid-url", False),
        ]

        success_count = 0
        for url, expected in test_urls:
            try:
                result = validate_github_url(url)
                status = "✓" if result == expected else "✗"
                print(f"  {status} validate_github_url('{url[:30]}...') = {result}")
                if result == expected:
                    success_count += 1
            except Exception as e:
                print(f"  ✗ Error validating {url[:30]}: {str(e)[:50]}")

        return success_count > 0
    except Exception as e:
        print(f"  ✗ GitHub handler import failed: {str(e)[:100]}")
        return False

def test_database_connection():
    """Test database connection"""
    print_header("9. Database Connection")

    try:
        from src.db.connection import get_session

        with get_session() as session:
            if session is not None:
                print(f"  ✓ Database connection established")
                return True
            else:
                print(f"  ⚠ Database connection returned None")
                return False
    except ImportError:
        print(f"  ⚠ Database module not fully implemented")
        return False
    except Exception as e:
        print(f"  ⚠ Database connection error: {str(e)[:100]}")
        return False

def test_ui_components():
    """Test UI component imports"""
    print_header("10. UI Components")

    ui_modules = [
        ("main", "src.ui.main"),
        ("scanner_tab", "src.ui.scanner_tab"),
        ("chat_tab", "src.ui.chat_tab"),
        ("settings_tab", "src.ui.settings_tab"),
    ]

    success_count = 0
    for name, module in ui_modules:
        try:
            __import__(module)
            print(f"  ✓ {name} module imported")
            success_count += 1
        except Exception as e:
            print(f"  ✗ {name} failed: {str(e)[:50]}")

    return success_count == len(ui_modules)

def test_requirements():
    """Test if all requirements are installed"""
    print_header("11. Python Dependencies")

    requirements = [
        "streamlit",
        "langchain",
        "python_dotenv",
        "pyyaml",
        "requests",
        "pytest",
        "semgrep",
        "fpdf2",
        "PyGithub",
    ]

    success_count = 0
    import_map = {
        "python_dotenv": "dotenv",
        "pyyaml": "yaml",
        "PyGithub": "github",
        "fpdf2": "fpdf",
    }
    for pkg in requirements:
        import_name = import_map.get(pkg, pkg)
        try:
            __import__(import_name)
            print(f"  ✓ {pkg}")
            success_count += 1
        except ImportError:
            print(f"  ✗ {pkg} NOT installed")

    print(f"\nInstalled: {success_count}/{len(requirements)}")
    return success_count == len(requirements)

def generate_summary(results):
    """Generate and display verification summary"""
    print_header("Verification Summary")

    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed

    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✓")
    print(f"Failed: {failed} ✗")
    print(f"Success Rate: {(passed/total*100):.1f}%")

    print("\nDetailed Results:")
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")

    return passed == total

def main():
    """Run all verification tests"""
    print("\n" + "="*60)
    print("  VeriFAI LLM - Application Verification Suite")
    print("="*60)

    results = {
        "Environment Configuration": test_environment_configuration(),
        "Core Module Imports": test_core_imports(),
        "File Utilities": test_file_utilities(),
        "Text Chunking": test_text_chunking(),
        "Semgrep Availability": test_semgrep_availability(),
        "LLM Initialization": test_llm_initialization(),
        "Security Functions": test_security_functions(),
        "GitHub Handler": test_github_handler(),
        "Database Connection": test_database_connection(),
        "UI Components": test_ui_components(),
        "Python Dependencies": test_requirements(),
    }

    all_passed = generate_summary(results)

    print("\n" + "="*60)
    if all_passed:
        print("  ✓ ALL TESTS PASSED - Application is ready!")
    else:
        print("  ⚠ SOME TESTS FAILED - Check details above")
    print("="*60 + "\n")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
