import os
import json
import logging
from openai import OpenAI, RateLimitError, AuthenticationError, APIConnectionError
from src.core.llm import initialize_llm

logger = logging.getLogger(__name__)

def get_groq_model():
    return os.getenv("GROQ_MODEL", "qwen/qwen-2.5-coder-32b-instruct")

def get_ai_response(prompt: str, system_message: str = "", temperature: float = 0.2, max_tokens: int = 2048):
    """
    Call AI model using either Local AI (Ollama) or Cloud API.
    """
    client = initialize_llm(temperature=temperature)
    if not client:
        raise ValueError("No AI backend available. Start Ollama at http://localhost:11434 or explicitly configure a cloud provider.")

    provider_type = getattr(client, "provider_type", "cloud")
    if provider_type == "cloud":
        active_model = getattr(client, "active_model", None) or get_groq_model()
    else:
        active_model = getattr(client, "active_model", None) or os.getenv("OLLAMA_MODEL", "llama3.2:latest")


    try:
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        from src.core.retry_utils import retry_callable
        class NonRetryableError(Exception):
            pass

        def make_call():
            try:
                # Optimize for 8GB RAM / Low capacity: cap max_tokens and set num_ctx context window
                effective_tokens = min(max_tokens, 1024) if provider_type == "ollama" else max_tokens
                kwargs = {
                    "model": active_model,
                    "messages": messages,
                    "max_tokens": effective_tokens,
                    "temperature": max(0.01, temperature),
                    "stream": False
                }
                # Only include json_object format if requesting JSON and using supported cloud model
                if "OUTPUT ONLY VALID JSON" in system_message and provider_type != "ollama":
                    kwargs["response_format"] = {"type": "json_object"}

                if provider_type == "ollama":
                    num_ctx = int(os.getenv("OLLAMA_NUM_CTX", "1024"))
                    kwargs["extra_body"] = {"num_ctx": num_ctx}
                    
                return client.chat.completions.create(**kwargs)
            except AuthenticationError as ae:
                raise NonRetryableError(ae)

        try:
            comp = retry_callable(
                make_call,
                retries=3 if provider_type != "ollama" else 1,
                backoff_factor=1.0,
                exceptions=(Exception,)
            )
        except NonRetryableError as nre:
            raise nre.args[0]

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
        raise ValueError(f"Failed to connect to AI API. Check if Ollama service is active.")
    except Exception as e:
        logger.error(f"AI Service Error: {e}")
        raise e

def extract_vulnerabilities_fallback(text: str) -> dict:
    """Fallback parser to extract vulnerabilities from malformed/truncated JSON text using regex."""
    import re
    vulns = []
    
    # Split by opening brace '{' to locate potential JSON objects representing vulnerabilities
    parts = text.split('{')
    for part in parts[1:]:
        # Use regex to search for standard JSON string fields
        name_match = re.search(r'"name"\s*:\s*"([^"]*)"', part)
        class_match = re.search(r'"classification"\s*:\s*"([^"]*)"', part)
        sev_match = re.search(r'"severity"\s*:\s*"([^"]*)"', part)
        desc_match = re.search(r'"description"\s*:\s*"([^"]*)"', part)
        rem_match = re.search(r'"remediation"\s*:\s*"([^"]*)"', part)
        
        # If we found at least name or description, create a recovery entry
        if name_match or desc_match:
            vulns.append({
                "name": name_match.group(1) if name_match else "Unknown Vulnerability",
                "classification": class_match.group(1) if class_match else "N/A",
                "severity": sev_match.group(1) if sev_match else "N/A",
                "description": desc_match.group(1) if desc_match else "No description provided",
                "remediation": rem_match.group(1) if rem_match else "No remediation details provided"
            })
            
    if vulns:
        return {"vulnerabilities": vulns}
    return {}

def validate_and_sanitize_vulnerabilities(data: dict, semgrep_results: dict = None) -> dict:
    """
    Ensures that the output strictly follows the expected vulnerabilities schema:
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
    }
    """
    if not isinstance(data, dict):
        data = {}
    
    vulns = data.get("vulnerabilities")
    if not isinstance(vulns, list):
        vulns = []
        
    sanitized_vulns = []
    for item in vulns:
        if not isinstance(item, dict):
            continue
        sanitized_item = {
            "name": str(item.get("name") or item.get("title") or "Unknown Vulnerability").strip(),
            "classification": str(item.get("classification") or item.get("category") or "N/A").strip(),
            "severity": str(item.get("severity") or "N/A").strip().upper(),
            "description": str(item.get("description") or item.get("details") or "No description provided").strip(),
            "remediation": str(item.get("remediation") or item.get("fix") or "No remediation details provided").strip()
        }
        sanitized_vulns.append(sanitized_item)
        
    # If no vulnerabilities could be extracted, but we have semgrep findings, map those findings
    if not sanitized_vulns and semgrep_results and isinstance(semgrep_results, dict):
        findings = semgrep_results.get("results", [])
        for f in findings:
            if not isinstance(f, dict):
                continue
            extra = f.get("extra", {})
            metadata = extra.get("metadata", {})
            
            # Map severity
            severity_str = str(f.get("severity") or "LOW").upper()
            if severity_str in ["ERROR", "CRITICAL"]:
                sev = "CRITICAL"
            elif severity_str in ["WARNING", "HIGH"]:
                sev = "HIGH"
            else:
                sev = "MEDIUM" if severity_str == "MEDIUM" else "LOW"
                
            sanitized_vulns.append({
                "name": str(f.get("check_id") or "Static Analysis Finding").split(".")[-1],
                "classification": str(metadata.get("cwe") or extra.get("cwe") or "CWE-General"),
                "severity": sev,
                "description": str(extra.get("message") or "Pattern flagged by static analyzer."),
                "remediation": f"Review and remediate code in {f.get('path', 'file')} around line {f.get('start', {}).get('line', 'N/A')}."
            })
            
    # If still completely empty (no findings), provide a default safe response
    if not sanitized_vulns:
        sanitized_vulns.append({
            "name": "No Vulnerabilities",
            "classification": "N/A",
            "severity": "LOW",
            "description": "No security issues were found or identified.",
            "remediation": "No remediation required."
        })
        
    return {"vulnerabilities": sanitized_vulns}

def _parse_json_from_response(response: str) -> dict:
    """Extract JSON from AI response, handling markdown blocks, trailing commas, and unescaped text."""
    if not response or not isinstance(response, str):
        return {"error": "Empty response from AI"}

    import re
    json_str = ""
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

        # Clean control characters and trailing commas before closing braces/brackets
        json_str = json_str.strip().replace('\r', '')
        json_str = re.sub(r',\s*([\}\]])', r'\1', json_str)
        
        return json.loads(json_str)
    except Exception as e:
        logger.error(f"Failed to parse JSON from AI: {e}. Raw snippet: {response[:300]}")
        # Try AST evaluation as fallback
        try:
             import ast
             res = ast.literal_eval(json_str)
             if isinstance(res, dict):
                 return res
        except Exception:
             pass
        
        # Run regex fallback parser to extract whatever structure we can from the raw response
        fallback = extract_vulnerabilities_fallback(response)
        if fallback and fallback.get("vulnerabilities"):
             logger.info("Successfully recovered vulnerabilities using regex fallback parser.")
             return fallback
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
        parsed = _parse_json_from_response(response)
        return validate_and_sanitize_vulnerabilities(parsed, semgrep_results)
    except Exception as e:
        logger.error(f"API/Parsing error in generate_vulnerability_analysis: {e}")
        return validate_and_sanitize_vulnerabilities({}, semgrep_results)

def generate_remediation_patch(semgrep_results: dict, code_snippet: str, file_path: str = "main.py", temperature: float = 0.0) -> dict:
    """Generate a secure, vulnerability-free code patch."""
    system_msg = """You are a Senior Security Engineer. Your goal is to rewrite the provided code to be 100% VULNERABILITY-FREE.
    
    STRICT SECURITY REQUIREMENTS:
    1. SQL Injection: Use parameterized queries/prepared statements ONLY. NEVER use string concatenation or f-strings for queries.
    2. XSS: Implement strict input encoding and output escaping.
    3. Secrets: Replace any hardcoded secrets with environment variable lookups (e.g., os.getenv).
    4. Cryptography: Use only modern, secure algorithms (e.g., Argon2, AES-GCM). Replace MD5/SHA1.
    5. Completeness: Return the ENTIRE functional code block so it can replace the original.
    
    OUTPUT FORMAT:
    Output the complete, SECURED code block wrapped in ```python ... ``` markdown."""
    
    findings_str = json.dumps(semgrep_results.get("results", [])[:10])
    prompt = f"File: {file_path}\nTarget Vulnerabilities to Fix: {findings_str}\n\nOriginal Code:\n{code_snippet}"
    
    try:
        from langchain_core.messages import SystemMessage, HumanMessage
        messages = [
            SystemMessage(content=system_msg),
            HumanMessage(content=prompt)
        ]
        chat_out = generate_chat_response(messages, temperature)
        if "error" in chat_out:
            return {"error": chat_out["error"]}
            
        raw_text = chat_out.get("response", "")
        patched_code = ""
        
        # Use robust regex extraction
        import re
        pattern = r"```(?:python)?\s*(.*?)\s*```"
        matches = re.findall(pattern, raw_text, re.DOTALL)
        if matches:
            for m in matches:
                if m.strip():
                    patched_code = m.strip()
                    break
        else:
            patched_code = raw_text.strip()
            
        return {
            "file_path": file_path,
            "patched_code": patched_code
        }
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
    - Eliminate ALL vulnerabilities identified in the scan findings.
    - Ensure the remediated code is functional, complete, and 100% VULNERABILITY-FREE.
    - Do NOT wrap your analysis in code blocks.
    
    REQUIRED OUTPUT FORMAT:
    1. Write your detailed security analysis first (in plain text/markdown).
    2. At the end, output the complete SECURED code block strictly enclosed in:
    ```python
    # complete secured code here
    ```"""
    
    findings_str = json.dumps(semgrep_results.get("results", [])[:5])
    prompt = f"File: {file_path}\nFindings: {findings_str}\n\nOriginal Code:\n{code_snippet}"
    
    try:
        from langchain_core.messages import SystemMessage, HumanMessage
        messages = [
            SystemMessage(content=system_msg),
            HumanMessage(content=prompt)
        ]
        chat_out = generate_chat_response(messages, temperature)
        if "error" in chat_out:
            return {"error": chat_out["error"]}
            
        raw_text = chat_out.get("response", "")
        
        fixed_code = ""
        analysis = raw_text
        
        import re
        # First look specifically for ```python ... ``` block
        py_matches = re.findall(r"```python\s*(.*?)\s*```", raw_text, re.DOTALL)
        if py_matches:
            fixed_code = py_matches[-1].strip() # Use the last python code block
            analysis = raw_text.split("```python")[0].strip()
        else:
            # Fallback to any ``` ... ``` code block containing python code keywords
            all_matches = re.findall(r"```\s*(.*?)\s*```", raw_text, re.DOTALL)
            if all_matches:
                for block in reversed(all_matches):
                    b_strip = block.strip()
                    if any(kw in b_strip for kw in ["import ", "def ", "class ", "from ", "="]):
                        fixed_code = b_strip
                        break
                analysis = raw_text.split("```")[0].strip()
            else:
                fixed_code = ""
                analysis = raw_text.strip()

        return {
            "analysis": analysis,
            "fixed_code": fixed_code
        }
    except Exception as e:
        return {"error": f"API unavailable. Unable to generate unified scan and patch. Details: {e}"}


def generate_chat_response(messages: list, temperature: float = 0.2) -> dict:
    """Handle chat responses using Local AI (Ollama) or Cloud models."""
    try:
        client = initialize_llm(temperature=temperature)
        if not client:
            return {"error": "No AI backend available. Please start Ollama at http://localhost:11434."}

        provider_type = getattr(client, "provider_type", "cloud")
        if provider_type == "cloud":
            active_model = getattr(client, "active_model", None) or get_groq_model()
        else:
            active_model = getattr(client, "active_model", None) or os.getenv("OLLAMA_MODEL", "llama3.2:latest")

        
        formatted_messages = []
        for msg in messages:
            if hasattr(msg, "type"):
                if msg.type == "human":
                    role = "user"
                elif msg.type == "system":
                    role = "system"
                else:
                    role = "assistant"
                content = msg.content
            elif isinstance(msg, dict):
                role = msg.get("role", "user")
                content = msg.get("content", "")
            else:
                role = "user"
                content = str(msg)
            formatted_messages.append({"role": role, "content": content})

        from src.core.retry_utils import retry_callable
        class NonRetryableError(Exception):
            pass

        def make_call():
            try:
                effective_tokens = 768 if provider_type == "ollama" else 2048
                kwargs = {
                    "model": active_model,
                    "messages": formatted_messages,
                    "temperature": max(0.01, temperature),
                    "max_tokens": effective_tokens,
                    "stream": False
                }
                if provider_type == "ollama":
                    num_ctx = int(os.getenv("OLLAMA_NUM_CTX", "1024"))
                    kwargs["extra_body"] = {"num_ctx": num_ctx}

                return client.chat.completions.create(**kwargs)
            except AuthenticationError as ae:
                raise NonRetryableError(ae)

        try:
            comp = retry_callable(
                make_call,
                retries=3 if provider_type != "ollama" else 1,
                backoff_factor=1.0,
                exceptions=(Exception,)
            )
        except NonRetryableError as nre:
            raise nre.args[0]

        response = comp.choices[0].message.content
        return {"response": response}
    except AuthenticationError as e:
        return {"error": f"Invalid API Key. Please check your credentials."}
    except RateLimitError as e:
        return {"error": f"API rate limit exceeded. Please try again later."}
    except APIConnectionError as e:
        return {"error": f"Failed to connect to AI API. Check if Ollama service is active."}
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
