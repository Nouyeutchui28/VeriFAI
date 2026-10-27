import os
import sys
import time
import json
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv(override=True)

from src.core.llm import initialize_llm
from src.core.ai_service import get_ai_response, generate_vulnerability_analysis, unified_scan_and_patch
from src.core.security import unified_security_scan

def test_llm_performance():
    print("=" * 60)
    print("⚡ TESTING VERIFAI LLM SPEED & ACCURACY")
    print("=" * 60)

    # 1. Initialize client
    start = time.time()
    client = initialize_llm()
    init_time = time.time() - start
    print(f"[*] Client Init Time: {init_time:.2f}s")
    print(f"[*] Active Model: {getattr(client, 'active_model', 'N/A')}")
    print(f"[*] Provider Type: {getattr(client, 'provider_type', 'N/A')}")

    # 2. Simple prompt latency
    start = time.time()
    resp = get_ai_response("Say hello in one word", max_tokens=10)
    prompt_time = time.time() - start
    print(f"[*] Simple Response Time: {prompt_time:.2f}s -> Response: '{resp.strip()}'")

    # 3. Vulnerable code test
    vulnerable_code = '''
import sqlite3
from flask import request

def search_user():
    username = request.args.get("username")
    conn = sqlite3.connect("db.sqlite")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    return cursor.fetchall()
'''

    semgrep_results = {
        "results": [
            {
                "check_id": "python.lang.security.audit.sqli.sqlite-string-format",
                "path": "app.py",
                "start": {"line": 8},
                "extra": {
                    "message": "User data formatted directly into SQL query string.",
                    "severity": "ERROR"
                }
            }
        ]
    }

    # 4. Unified Scan & Patch performance
    start = time.time()
    analysis, patch = unified_security_scan(semgrep_results, vulnerable_code, file_path="app.py")
    scan_time = time.time() - start

    print("\n" + "=" * 60)
    print(f"⚡ UNIFIED SCAN & PATCH COMPLETED IN {scan_time:.2f} SECONDS")
    print("=" * 60)
    print(f"Analysis Preview ({len(analysis)} chars):\n{analysis[:300]}...\n")
    print(f"Patch Suggestions Preview ({len(patch)} chars):\n{patch[:400]}...")

    print("=" * 60)
    if scan_time < 5.0 and ("SQL" in analysis or "Injection" in analysis or "SELECT" in patch or "query" in patch):
        print("✅ PASSED: AI model is ULTRA FAST and ACCURATE!")
    else:
        print(f"⚠️ RESULT: Speed: {scan_time:.2f}s")

if __name__ == "__main__":
    test_llm_performance()
