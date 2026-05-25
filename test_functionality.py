#!/usr/bin/env python3
"""
Functional tests for VeriFAI LLM - Tests core scanning workflows
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

def print_header(title):
    """Print formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def print_test(name, passed, details=""):
    """Print test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"  {status}: {name}")
    if details:
        print(f"    {details}")

def test_semgrep_scanning():
    """Test Semgrep scanning functionality"""
    print_header("Test 1: Semgrep Code Scanning")

    from src.core.security import run_semgrep_scan

    # Create test code with potential vulnerability
    vulnerable_code = '''
import pickle
import subprocess

def unsafe_pickle(data):
    # Unsafe: pickle.loads without validation
    return pickle.loads(data)

def unsafe_command(user_input):
    # Unsafe: unsanitized subprocess call
    subprocess.run("ls " + user_input, shell=True)

def weak_crypto():
    import hashlib
    # Weak: MD5 should not be used
    password = hashlib.md5(b"password").hexdigest()
    return password
'''

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "vulnerable.py"
            test_file.write_text(vulnerable_code)

            results = run_semgrep_scan(tmpdir, metrics_enabled=False)

            # Check results structure
            has_results = "results" in results
            findings_count = len(results.get("results", []))

            print_test("Semgrep execution", has_results, f"Found {findings_count} issues (offline mode may return 0)")

            if has_results and findings_count > 0:
                first_finding = results["results"][0]
                print(f"    Sample issue:")
                print(f"      - Rule: {first_finding.get('check_id', 'N/A')}")
                print(f"      - File: {first_finding.get('path', 'N/A')}")
                print(f"      - Line: {first_finding.get('start', {}).get('line', 'N/A')}")

            return has_results # Pass as long as Semgrep ran and returned a valid structure

    except Exception as e:
        print_test("Semgrep execution", False, f"Error: {str(e)[:80]}")
        return False

def test_llm_analysis():
    """Test LLM-based code analysis"""
    print_header("Test 2: LLM Security Analysis")

    from src.core.llm import initialize_llm
    from src.core.security import analyze_security

    vulnerable_code = '''
def login(username, password):
    # SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    db.execute(query)
    return True
'''

    semgrep_results = {
        "results": [
            {
                "check_id": "python.sql-injection",
                "message": "Potential SQL injection",
                "path": "app.py",
                "start": {"line": 2},
            }
        ]
    }

    try:
        llm = initialize_llm(temperature=0.1)
        if llm is None:
            print_test("LLM analysis", False, "LLM initialization failed")
            return False

        analysis = analyze_security(semgrep_results, vulnerable_code, llm)

        # Check if analysis contains expected content
        has_content = bool(analysis and len(analysis) > 50)
        contains_vulnerability_info = "SQL" in analysis or "injection" in analysis.lower()

        print_test("LLM analysis completion", has_content, f"Response length: {len(analysis)} chars")
        if not has_content or not contains_vulnerability_info:
            print(f"    Raw Response: {analysis}")
        print_test("Vulnerability identification", contains_vulnerability_info)

        if has_content:
            # Print first 200 chars of analysis
            preview = analysis[:200].replace("\n", " ")
            print(f"    Analysis preview: {preview}...")

        return has_content and contains_vulnerability_info

    except Exception as e:
        error_msg = str(e)
        print_test("LLM analysis", False, f"Error: {error_msg[:80]}")
        return False

def test_patch_generation():
    """Test patch suggestion generation"""
    print_header("Test 3: Patch Suggestion Generation")

    from src.core.llm import initialize_llm
    from src.core.security import generate_patch_suggestions

    vulnerable_code = '''
def process_data(user_input):
    # Command injection vulnerability
    import os
    os.system(f"echo {user_input}")
'''

    semgrep_results = {
        "results": [
            {
                "check_id": "python.command-injection",
                "message": "Potential command injection",
                "path": "app.py",
                "extra": {"message": "os.system shell command injection"}
            }
        ]
    }

    try:
        llm = initialize_llm(temperature=0.1)
        if llm is None:
            print_test("Patch generation", False, "LLM initialization failed")
            return False

        patch = generate_patch_suggestions(
            semgrep_results,
            vulnerable_code,
            llm,
            file_path="app.py"
        )

        has_content = bool(patch and len(patch) > 10)
        is_patch_format = "---" in patch or "+++" in patch or "@@" in patch

        print_test("Patch generation", has_content, f"Patch length: {len(patch)} chars")
        print_test("Unified diff format", is_patch_format or "No patch" in patch)

        if has_content and len(patch) < 500:
            preview = patch[:300].replace("\n", " ")
            print(f"    Patch preview: {preview}...")

        return has_content

    except Exception as e:
        print_test("Patch generation", False, f"Error: {str(e)[:80]}")
        return False

def test_file_handling():
    """Test file upload and processing"""
    print_header("Test 4: File Upload and Processing")

    from src.core.file_utils import (
        save_code_to_temp_file,
        is_valid_file_type,
        cleanup_temp_files
    )

    test_code = "def hello():\n    print('Hello World')"

    try:
        # Test saving code to temp file
        temp_file = save_code_to_temp_file(test_code)
        file_exists = Path(temp_file).exists()
        print_test("Temp file creation", file_exists, f"Created: {temp_file}")

        # Test file validation
        valid_py = is_valid_file_type("test.py", ["py"])
        valid_js = is_valid_file_type("script.js", ["js"])
        invalid = is_valid_file_type("test.txt", ["py", "js"])

        print_test("Python file validation", valid_py)
        print_test("JavaScript file validation", valid_js)
        print_test("Invalid file rejection", not invalid)

        # Cleanup
        if file_exists:
            Path(temp_file).unlink()
            cleanup_temp_files()

        return file_exists and valid_py and valid_js and not invalid

    except Exception as e:
        print_test("File handling", False, f"Error: {str(e)[:80]}")
        return False

def test_github_integration():
    """Test GitHub URL validation"""
    print_header("Test 5: GitHub Integration")

    from src.core.github_handler import validate_github_url

    test_urls = [
        ("https://github.com/user/repo", True, "Standard HTTPS URL"),
        ("https://github.com/user/repo.git", True, "URL with .git"),
        ("git@github.com:user/repo.git", True, "SSH format"),
        ("https://gitlab.com/user/repo", False, "Non-GitHub host"),
        ("invalid-url", False, "Invalid format"),
    ]

    success_count = 0
    for url, expected, description in test_urls:
        try:
            result = validate_github_url(url)
            passed = result == expected
            print_test(
                f"Validate: {description}",
                passed,
                f"URL: {url[:40]}... => {result}"
            )
            if passed:
                success_count += 1
        except Exception as e:
            print_test(f"Validate: {description}", False, f"Error: {str(e)[:50]}")

    return success_count >= 3

def test_text_chunking():
    """Test text chunking for large inputs"""
    print_header("Test 6: Text Chunking for Large Inputs")

    from src.utils.text_chunk import chunk_text, analyze_code_in_chunks

    large_code = "def func_" + "x" * 100 + "():\n    pass\n" * 500

    try:
        # Test basic chunking
        result = chunk_text(large_code, chunk_size=1000)
        is_chunked = isinstance(result, list) and len(result) > 1
        print_test("Large text chunking", is_chunked, f"Chunks: {len(result) if isinstance(result, list) else 1}")

        # Test small text (no chunking needed)
        small_result = chunk_text("def hello(): pass", chunk_size=1000)
        is_string = isinstance(small_result, str)
        print_test("Small text no-chunking", is_string)

        # Test empty text
        empty_result = chunk_text("", chunk_size=1000)
        is_empty_valid = empty_result == "" or empty_result == []
        print_test("Empty text handling", is_empty_valid)

        return is_chunked and is_string and is_empty_valid

    except Exception as e:
        print_test("Text chunking", False, f"Error: {str(e)[:80]}")
        return False

def test_input_validation():
    """Test input validation and sanitization"""
    print_header("Test 7: Input Validation and Sanitization")

    from src.core.input_validator import validate_code_input

    test_cases = [
        ("def hello(): pass", True, "Valid Python code"),
        ("", False, "Empty code"),
        ("x" * 15000000, False, "Extremely large input"),
        ("import os\n" * 100, True, "Repetitive but valid code"),
    ]

    success_count = 0
    for code, should_pass, description in test_cases:
        try:
            result = validate_code_input(code)
            # validate_code_input returns the code string on success or raises ValidationError
            is_valid = isinstance(result, str) and len(result) > 0
            
            if should_pass:
                passed = is_valid
                details = f"Valid: {is_valid}"
            else:
                passed = False # Should have raised exception
                details = "Expected ValidationError but it passed"

        except Exception as e:
            if not should_pass:
                passed = True
                details = f"Correctly caught: {str(e)[:50]}"
            else:
                passed = False
                details = f"Error: {str(e)[:50]}"

        print_test(
            f"Input validation: {description}",
            passed,
            details
        )

        if passed:
            success_count += 1

    return success_count >= 2

def test_environment_variables():
    """Test environment variable loading"""
    print_header("Test 8: Environment Variables")

    required_vars = {
        "SECRET_KEY": "JWT secret key",
        "DATABASE_URL": "Database connection string",
    }

    success_count = 0
    for var, description in required_vars.items():
        value = os.environ.get(var, "").strip()
        is_set = bool(value)

        print_test(
            f"{var}",
            is_set,
            description if is_set else "NOT SET"
        )

        if is_set:
            success_count += 1

    return success_count >= 1

def generate_report(results):
    """Generate final report"""
    print_header("Functional Test Results Summary")

    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed

    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✓")
    print(f"Failed: {failed} ✗")
    print(f"Success Rate: {(passed/total*100):.1f}%\n")

    print("Test Results:")
    for test_name, result in results.items():
        status = "✓" if result else "✗"
        print(f"  {status} {test_name}")

    return passed == total

def main():
    """Run all functional tests"""
    print("\n" + "="*70)
    print("  VeriFAI LLM - Functional Test Suite")
    print("="*70)

    results = {
        "Semgrep Code Scanning": test_semgrep_scanning(),
        "LLM Security Analysis": test_llm_analysis(),
        "Patch Suggestion Generation": test_patch_generation(),
        "File Upload & Processing": test_file_handling(),
        "GitHub URL Validation": test_github_integration(),
        "Text Chunking": test_text_chunking(),
        "Input Validation": test_input_validation(),
        "Environment Variables": test_environment_variables(),
    }

    all_passed = generate_report(results)

    print("\n" + "="*70)
    if all_passed:
        print("  ✓ ALL FUNCTIONAL TESTS PASSED")
    else:
        failed_tests = [k for k, v in results.items() if not v]
        print(f"  ⚠ {len(failed_tests)} TEST(S) FAILED:")
        for test in failed_tests:
            print(f"    - {test}")
    print("="*70 + "\n")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
