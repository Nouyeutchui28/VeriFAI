import os
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, "/home/bruns/Pictures/VeriFAI LLM")

from src.core.llm import initialize_llm
from src.core.security import analyze_security

def test_local_connection():
    print("🚀 Testing connection to local secure-patch-model...")
    
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
            print("❌ FAIL: LLM initialization failed")
            return

        print("📡 Sending analysis request to Ollama (this may take up to 2 minutes)...")
        analysis = analyze_security(semgrep_results, vulnerable_code, llm)
        
        print(f"\n✅ Analysis Received ({len(analysis)} characters):")
        print("-" * 40)
        print(analysis)
        print("-" * 40)
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    test_local_connection()
