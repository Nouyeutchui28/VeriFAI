import os
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, "/home/bruns/Pictures/VeriFAI LLM")

from src.core.llm import initialize_llm
from src.core.security import generate_patch_suggestions

def test_patch_generation():
    print("🚀 Testing patch generation with local secure-patch-model...")
    
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

        print("📡 Sending patch request to Ollama (this may take up to 2 minutes)...")
        patch = generate_patch_suggestions(semgrep_results, vulnerable_code, llm, file_path="app.py")
        
        print(f"\n✅ Patch Received ({len(patch)} characters):")
        print("-" * 40)
        print(patch)
        print("-" * 40)
        
        if "--- a/app.py" in patch and "+++ b/app.py" in patch:
            print("💎 Patch format looks correct (Unified Diff)")
        else:
            print("⚠️ Patch format might be non-standard")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    test_patch_generation()
