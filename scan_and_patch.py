import os
import sys
import json
from dotenv import load_dotenv

# Ensure the src directory is in the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.security import run_semgrep_scan, unified_security_scan

def main():
    # Load environment variables (e.g., GROQ_API_KEY / OpenRouter key)
    load_dotenv()

    # Create a dummy vulnerable file to test
    test_file = "vulnerable_test.py"
    vulnerable_code = """
import sqlite3

def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # ⚠️ VULNERABLE TO SQL INJECTION ⚠️
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    return cursor.fetchall()
"""
    
    with open(test_file, "w") as f:
        f.write(vulnerable_code)

    print(f"[*] Created vulnerable file: {test_file}")
    print("[*] Running Semgrep OWASP Security Scan...")

    # Step 1: Run the Semgrep Scan
    semgrep_results = run_semgrep_scan(test_file)
    
    findings_count = len(semgrep_results.get("results", []))
    if findings_count == 0:
        print("[!] No vulnerabilities detected by Semgrep.")
        os.remove(test_file)
        return
        
    print(f"[!] Detected {findings_count} vulnerabilities!")

    # Step 2: Use the AI Engine to Generate a Patch
    print("\n[*] Sending findings to AI Engine for patching (Security Chat logic)...")
    
    # Notice we pass llm=None so it uses the native Groq/OpenRouter generate_chat_response internally
    analysis, patch = unified_security_scan(
        semgrep_results=semgrep_results,
        code_snippet=vulnerable_code,
        llm=None,
        file_path=test_file
    )

    print("\n" + "="*50)
    print("🧠 AI SECURITY ANALYSIS:")
    print("="*50)
    print(analysis)
    
    print("\n" + "="*50)
    print("🛠️ GENERATED SECURE PATCH:")
    print("="*50)
    print(patch)

    # Clean up
    os.remove(test_file)

if __name__ == "__main__":
    main()
