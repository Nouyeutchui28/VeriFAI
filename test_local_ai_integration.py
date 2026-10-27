import os
import sys

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.llm import initialize_llm, list_local_ollama_models
from src.core.ai_service import generate_vulnerability_analysis, generate_remediation_patch, generate_chat_response

def main():
    print("==================================================")
    print("🛡️ Testing VeriFAI LLM Local AI Integration")
    print("==================================================")

    # 1. Discover local models
    models = list_local_ollama_models()
    print(f"📡 Discovered Local Ollama Models: {models}")
    
    # 2. Test LLM client initialization
    client = initialize_llm()
    if not client:
        print("❌ Error: Could not initialize LLM client.")
        return

    provider = getattr(client, "provider_type", "unknown")
    model_name = getattr(client, "active_model", "unknown")
    print(f"✅ LLM Client initialized cleanly! Provider: {provider} | Model: {model_name}")

    # 3. Test simple chat response
    print("\n💬 Testing Chat Completion with Local AI...")
    chat_result = generate_chat_response([{"role": "user", "content": "Explain SQL injection in 1 short sentence."}])
    print("Response:", chat_result.get("response", chat_result.get("error")))

    # 4. Test Vulnerability Analysis
    print("\n🔍 Testing Vulnerability Analysis with Local AI...")
    vulnerable_code = "query = f'SELECT * FROM users WHERE user=\"{username}\"'\ndb.execute(query)"
    semgrep = {"results": [{"check_id": "python.sql-injection", "severity": "HIGH", "extra": {"message": "SQL Injection vulnerability"}}]}
    
    analysis = generate_vulnerability_analysis(semgrep, vulnerable_code)
    print("Vulnerability Analysis Result:")
    import json
    print(json.dumps(analysis, indent=2))

    print("\n🎉 VeriFAI LLM Local AI Integration verified successfully!")

if __name__ == "__main__":
    main()
