import re
import json
import logging

logger = logging.getLogger(__name__)

# Common patterns for secrets and PII
SECRET_PATTERNS = [
    (r'api[_-]?key\s*[:=]\s*["\']([^"\']+)["\']', "secret"),
    (r'secret[_-]?key\s*[:=]\s*["\']([^"\']+)["\']', "secret"),
    (r'password\s*[:=]\s*["\']([^"\']+)["\']', "password"),
    (r'sk-[a-zA-Z0-9]{32,}', "openai_key"),
    (r'gsk_[a-zA-Z0-9]{32,}', "groq_key"),
    (r'hf_[a-zA-Z0-9]{32,}', "hf_token")
]

PII_PATTERNS = [
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', "[REDACTED_EMAIL]"),
    (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', "[REDACTED_IP]")
]

def scrub_sensitive_data(text: str) -> str:
    """
    Remove PII and secrets from text before sending to LLM.
    """
    if not text or not isinstance(text, str):
        return text

    scrubbed = text

    # Scrub Secrets using direct substitution for the captured group
    for pattern, label in SECRET_PATTERNS:
        # Use a more precise replacement that only touches the secret value
        def _replace_secret(match):
            full_match = match.group(0)
            try:
                secret_val = match.group(1)
                return full_match.replace(secret_val, f"[REDACTED_{label.upper()}]")
            except IndexError:
                return f"[REDACTED_{label.upper()}]"
        
        scrubbed = re.sub(pattern, _replace_secret, scrubbed, flags=re.IGNORECASE)

    # Scrub PII
    for pattern, replacement in PII_PATTERNS:
        scrubbed = re.sub(pattern, replacement, scrubbed)

    return scrubbed

def sanitize_semgrep_for_llm(results: dict) -> dict:
    """
    Scrub sensitive data from semgrep results JSON by traversing the dict.
    This is much safer than string-based replacement.
    """
    if not results or not isinstance(results, dict):
        return results
    
    try:
        # Deep copy-like processing for specific fields
        new_results = json.loads(json.dumps(results)) # Fast way to get a clean copy
        
        if "results" in new_results:
            for finding in new_results["results"]:
                # Scrub high-risk fields
                if "extra" in finding:
                    extra = finding["extra"]
                    if "lines" in extra:
                        extra["lines"] = scrub_sensitive_data(extra["lines"])
                    if "message" in extra:
                        extra["message"] = scrub_sensitive_data(extra["message"])
                
                # Fingerprints can contain PII sometimes, but they are IDs, so let's be careful
                if "fingerprint" in finding:
                    finding["fingerprint"] = "[REDACTED_ID]"
        
        return new_results
    except Exception as e:
        logger.error(f"Structured scrubbing failed: {e}. Falling back to string scrubbing.")
        # Fallback to string-based if structure is weird
        try:
            json_str = json.dumps(results)
            scrubbed_str = scrub_sensitive_data(json_str)
            return json.loads(scrubbed_str)
        except:
            return results # Return unscrubbed if all else fails (safety last, but don't crash)
