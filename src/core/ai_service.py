import os
import json
import logging
from huggingface_hub import InferenceClient

logger = logging.getLogger(__name__)

HF_MODEL_ID = "Qwen/Qwen2.5-Coder-32B-Instruct"

def get_ai_response(prompt: str, system_message: str = "", temperature: float = 0.2, max_tokens: int = 2048):
    """
    Directly call Hugging Face Inference API using the InferenceClient.
    """
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise ValueError("HF_TOKEN is missing. Please add it to your .env file.")

    try:
        client = InferenceClient(api_key=hf_token)
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        response = ""
        # Serverless API check for ChatCompletion
        comp = client.chat_completion(
            model=HF_MODEL_ID,
            messages=messages,
            max_tokens=max_tokens,
            temperature=max(0.01, temperature),
            stream=False
        )
        response = comp.choices[0].message.content
        return response
    except Exception as e:
        logger.error(f"Hugging Face API Error: {e}")
        raise e

def _parse_json_from_response(response: str) -> dict:
    """Extract JSON from AI response, handling markdown blocks and trailing text."""
    try:
        # 1. Try to find content between ```json and ```
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
        # 2. Try to find content between ``` and ```
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0].strip()
        else:
            # 3. Look for the first { and last }
            start = response.find("{")
            end = response.rfind("}")
            if start != -1 and end != -1:
                json_str = response[start:end+1]
            else:
                json_str = response.strip()
        
        # Clean up any potential control characters
        json_str = json_str.strip().replace('\r', '')
        # Simple string to dict
        return json.loads(json_str)
    except Exception as e:
        logger.error(f"Failed to parse JSON from AI: {e}. Raw: {response}")
        # Final fallback: if it looks like JSON but load failed, try a less aggressive clean
        try:
             import ast
             # This is risky but can work for malformed JSON that is valid Python dict
             return ast.literal_eval(json_str)
        except:
             return {"error": "Invalid JSON response from AI", "raw": response}

def generate_vulnerability_analysis(semgrep_results: dict, code_snippet: str, temperature: float = 0.2) -> dict:
    """Generate vulnerability analysis using Qwen2.5."""
    system_msg = """You are an expert security analyst. Provide analysis based on Semgrep findings and your expert review.
    OUTPUT ONLY VALID JSON:
    {
      "vulnerabilities": [
        {
          "name": "...",
          "classification": "...",
          "severity": "...",
          "description": "...",
          "remediation": "..."
        }
      ]
    }"""
    
    findings_str = json.dumps(semgrep_results.get("results", [])[:20])
    prompt = f"Semgrep Findings: {findings_str}\n\nCode:\n{code_snippet}"
    
    try:
        response = get_ai_response(prompt, system_msg, temperature)
        return _parse_json_from_response(response)
    except Exception as e:
        return {"error": str(e)}

def generate_remediation_patch(semgrep_results: dict, code_snippet: str, file_path: str = "main.py", temperature: float = 0.0) -> dict:
    """Generate a secure, vulnerability-free code patch."""
    system_msg = """You are a Senior Security Engineer. Your goal is to rewrite the provided code to be 100% VULNERABILITY-FREE.
    
    STRICT SECURITY REQUIREMENTS:
    1. SQL Injection: Use parameterized queries/prepared statements ONLY. NEVER use string concatenation or f-strings for queries.
    2. XSS: Implement strict input encoding and output escaping.
    3. Secrets: Replace any hardcoded secrets with environment variable lookups (e.g., os.getenv).
    4. Cryptography: Use only modern, secure algorithms (e.g., Argon2, AES-GCM). Replace MD5/SHA1.
    5. Completeness: Return the ENTIRE functional code block so it can replace the original.
    
    OUTPUT ONLY VALID JSON:
    {
      "file_path": "...",
      "patched_code": "The complete, SECURED code."
    }"""
    
    findings_str = json.dumps(semgrep_results.get("results", [])[:10])
    prompt = f"File: {file_path}\nTarget Vulnerabilities to Fix: {findings_str}\n\nOriginal Code:\n{code_snippet}"
    
    try:
        response = get_ai_response(prompt, system_msg, temperature)
        return _parse_json_from_response(response)
    except Exception as e:
        return {"error": str(e)}

def unified_scan_and_patch(semgrep_results: dict, code_snippet: str, file_path: str = "main.py", context_files: dict = None, temperature: float = 0.2) -> dict:
    """Perform analysis and patch generation in a single pass."""
    context_str = ""
    if context_files:
        for name, content in context_files.items():
            context_str += f"\n--- FILE: {name} ---\n{content[:2000]}\n"

    system_msg = f"""You are a Senior Security Auditor and Remediation Expert.
    {context_str}
    
    STRICT REMEDIATION RULES:
    - Eliminate ALL vulnerabilities identified by Semgrep.
    - Use secure-by-default libraries (e.g., sqlalchemy for DB, argon2 for hashing).
    - Ensure the 'fixed_code' is functional, complete, and VULNERABILITY-FREE.
    
    OUTPUT ONLY VALID JSON:
    {{
      "analysis": "A detailed security report.",
      "fixed_code": "The complete, SECURED code block."
    }}"""
    
    findings_str = json.dumps(semgrep_results.get("results", [])[:5])
    prompt = f"File: {file_path}\nFindings: {findings_str}\n\nCode:\n{code_snippet}"
    
    try:
        response = get_ai_response(prompt, system_msg, temperature)
        return _parse_json_from_response(response)
    except Exception as e:
        return {"error": str(e)}

def generate_chat_response(messages: list, temperature: float = 0.2) -> dict:
    """Handle chat responses using the Qwen model."""
    try:
        hf_token = os.getenv("HF_TOKEN")
        client = InferenceClient(api_key=hf_token)
        
        formatted_messages = []
        for msg in messages:
            role = "user" if msg.type == "human" else "assistant"
            formatted_messages.append({"role": role, "content": msg.content})

        comp = client.chat_completion(
            model=HF_MODEL_ID,
            messages=formatted_messages,
            temperature=max(0.01, temperature),
            max_tokens=2048,
            stream=False
        )
        response = comp.choices[0].message.content
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}

def generate_semgrep_rules(code_snippet: str, llm_analysis: str, temperature: float = 0.2) -> dict:
    """Generate custom Semgrep rules."""
    system_msg = """You are a Semgrep rule expert. Create custom YAML rules for detected vulnerabilities.
    OUTPUT ONLY VALID JSON:
    {
      "rules": "the raw YAML string"
    }"""
    
    prompt = f"Code:\n{code_snippet}\n\nAnalysis:\n{llm_analysis}"
    
    try:
        response = get_ai_response(prompt, system_msg, temperature)
        return _parse_json_from_response(response)
    except Exception as e:
        return {"error": str(e)}
