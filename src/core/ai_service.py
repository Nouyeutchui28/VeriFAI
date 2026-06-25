import os
import json
import logging
from openai import OpenAI, RateLimitError, AuthenticationError, APIConnectionError

logger = logging.getLogger(__name__)

def get_groq_model():
    return os.getenv("GROQ_MODEL", "qwen-2.5-coder-32b")

def get_ai_response(prompt: str, system_message: str = "", temperature: float = 0.2, max_tokens: int = 2048):
    """
    Directly call Groq API using the Groq SDK.
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("API_KEY is missing. Please add it to your .env file.")

    try:
        client = OpenAI(api_key=groq_api_key, base_url="https://openrouter.ai/api/v1")
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        comp = client.chat.completions.create(
            model=get_groq_model(),
            messages=messages,
            max_tokens=max_tokens,
            temperature=max(0.01, temperature),
            stream=False,
            response_format={"type": "json_object"} if "OUTPUT ONLY VALID JSON" in system_message else None
        )
        response = comp.choices[0].message.content
        return response
    except AuthenticationError as e:
        logger.error(f"API Authentication Error: {e}")
        raise ValueError(f"Invalid API Key. Please check your credentials.")
    except RateLimitError as e:
        logger.error(f"API Rate Limit Error: {e}")
        raise ValueError(f"API rate limit exceeded. Please try again later.")
    except APIConnectionError as e:
        logger.error(f"API Connection Error: {e}")
        raise ValueError(f"Failed to connect to API. Please check your network.")
    except Exception as e:
        logger.error(f"API Error: {e}")
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
    """Generate vulnerability analysis using Groq."""
    system_msg = """You are an expert security analyst. Provide analysis based on Semgrep findings and your expert review.
    OUTPUT ONLY VALID JSON matching this exact structure:
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
        return {"error": f"API unavailable. Unable to generate analysis. Details: {e}"}

def generate_remediation_patch(semgrep_results: dict, code_snippet: str, file_path: str = "main.py", temperature: float = 0.0) -> dict:
    """Generate a secure, vulnerability-free code patch."""
    system_msg = """You are a Senior Security Engineer. Your goal is to rewrite the provided code to be 100% VULNERABILITY-FREE.
    
    STRICT SECURITY REQUIREMENTS:
    1. SQL Injection: Use parameterized queries/prepared statements ONLY. NEVER use string concatenation or f-strings for queries.
    2. XSS: Implement strict input encoding and output escaping.
    3. Secrets: Replace any hardcoded secrets with environment variable lookups (e.g., os.getenv).
    4. Cryptography: Use only modern, secure algorithms (e.g., Argon2, AES-GCM). Replace MD5/SHA1.
    5. Completeness: Return the ENTIRE functional code block so it can replace the original.
    
    OUTPUT ONLY VALID JSON matching this exact structure:
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
        return {"error": f"API unavailable. Unable to generate AI patch at this time. Details: {e}"}

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
    
    OUTPUT ONLY VALID JSON matching this exact structure:
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
        return {"error": f"API unavailable. Unable to generate unified scan and patch. Details: {e}"}

def generate_chat_response(messages: list, temperature: float = 0.2) -> dict:
    """Handle chat responses using the Groq model."""
    try:
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            return {"error": "API Key is missing. Please add it to your .env file."}
            
        client = OpenAI(api_key=groq_api_key, base_url="https://openrouter.ai/api/v1")
        
        formatted_messages = []
        for msg in messages:
            role = "user" if msg.type == "human" else "assistant"
            formatted_messages.append({"role": role, "content": msg.content})

        comp = client.chat.completions.create(
            model=get_groq_model(),
            messages=formatted_messages,
            temperature=max(0.01, temperature),
            max_tokens=2048,
            stream=False
        )
        response = comp.choices[0].message.content
        return {"response": response}
    except AuthenticationError as e:
        return {"error": f"Invalid API Key. Please check your credentials."}
    except RateLimitError as e:
        return {"error": f"API rate limit exceeded. Please try again later."}
    except APIConnectionError as e:
        return {"error": f"Failed to connect to API. Please check your network."}
    except Exception as e:
        return {"error": str(e)}

def generate_semgrep_rules(code_snippet: str, llm_analysis: str, temperature: float = 0.2) -> dict:
    """Generate custom Semgrep rules."""
    system_msg = """You are a Semgrep rule expert. Create custom YAML rules for detected vulnerabilities.
    OUTPUT ONLY VALID JSON matching this exact structure:
    {
      "rules": "the raw YAML string"
    }"""
    
    prompt = f"Code:\n{code_snippet}\n\nAnalysis:\n{llm_analysis}"
    
    try:
        response = get_ai_response(prompt, system_msg, temperature)
        return _parse_json_from_response(response)
    except Exception as e:
        return {"error": f"API unavailable. Unable to generate Semgrep rules. Details: {e}"}
