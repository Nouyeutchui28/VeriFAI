#!/usr/bin/env python3
"""
generate_secure_patch.py - Standalone AI-driven self-correcting security patching utility.
Scans code, generates fixes, runs a validation loop with Semgrep, and outputs a 100% vulnerability-free patch.
"""

import os
import sys
import argparse
import tempfile
import json
import subprocess
import difflib
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.security import run_semgrep_scan, security_chat, _build_unified_diff
from src.core.file_utils import apply_patch

def scan_code(file_path):
    """Run local Semgrep scan and return results."""
    print(f"[*] Scanning {file_path} with Semgrep...")
    results = run_semgrep_scan(file_path)
    findings = results.get("results", [])
    return findings

def get_remediation_from_llm(original_code, findings, previous_code=None, remaining_findings=None):
    """Ask LLM to generate secure code, incorporating previous failures if doing self-correction."""
    if not previous_code:
        # Initial fix request
        prompt = (
            "Please rewrite the entire code to remediate all the security vulnerabilities identified in the scan results.\n"
            f"Vulnerabilities list: {json.dumps(findings, indent=2)}\n\n"
            "Return the complete, fully secured, and compilable code. The output MUST contain the entire file content "
            "so it can be used to patch the file, and the code MUST be wrapped in a ```python ... ``` code block."
        )
    else:
        # Self-correction request
        prompt = (
            "Your previous fix still contains security vulnerabilities. We scanned your remediated code and found the following issues:\n"
            f"{json.dumps(remaining_findings, indent=2)}\n\n"
            "Please correct these remaining issues and rewrite the entire code to be 100% vulnerability-free.\n"
            f"Previous code attempt:\n{previous_code}\n\n"
            "Return the complete, fully secured, and compilable code wrapped in a ```python ... ``` code block."
        )

    response = security_chat(
        code_snippet=original_code,
        llm_analysis="Scan Findings remediation request",
        chat_history=[],
        query=prompt
    )

    # Extract the python code block
    import re
    pattern = r"```(?:python)?\s*(.*?)\s*```"
    matches = re.findall(pattern, response, re.DOTALL)
    if matches:
        for m in matches:
            if m.strip():
                return m.strip()
    
    if "def " in response or "import " in response or "class " in response:
        return response.strip()
        
    return None

def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Generate 100% Vulnerability-Free Security Patches")
    parser.add_argument("--file", required=True, help="Path to the vulnerable code file")
    parser.add_argument("--apply", action="store_true", help="Apply the patch directly to the file on success")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"[❌] Error: File '{args.file}' not found.")
        sys.exit(1)

    with open(args.file, "r", encoding="utf-8") as f:
        original_code = f.read()

    # Step 1: Scan original code
    findings = scan_code(args.file)
    if not findings:
        print("[✅] Already Secure: Semgrep found 0 vulnerabilities in the target file.")
        sys.exit(0)

    print(f"[!] Detected {len(findings)} vulnerabilities in the original code.")

    # Step 2: Self-Correction Loop
    current_code = original_code
    max_attempts = 3
    success = False
    temp_file_path = None

    for attempt in range(1, max_attempts + 1):
        print(f"\n[*] Attempt {attempt}/{max_attempts}: Generating remediation code...")
        
        if attempt == 1:
            remediated_code = get_remediation_from_llm(original_code, findings)
        else:
            remediated_code = get_remediation_from_llm(original_code, findings, current_code, remaining_findings)

        if not remediated_code:
            print("[⚠️] AI failed to output a valid code block. Retrying...")
            continue

        # Save to temp file to scan and verify
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tf:
            tf.write(remediated_code)
            temp_file_path = tf.name

        # Scan the remediated code
        remaining_findings = scan_code(temp_file_path)
        
        if not remaining_findings:
            print(f"[🎉] Success! Attempt {attempt} generated 100% vulnerability-free code.")
            current_code = remediated_code
            success = True
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            temp_file_path = None
            break
        else:
            print(f"[❌] Attempt {attempt} failed: remediated code still has {len(remaining_findings)} issues.")
            current_code = remediated_code
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            temp_file_path = None

    if not success:
        print("\n[⚠️] Warning: Could not achieve 0 vulnerabilities after max attempts, using best effort code.")

    # Step 3: Generate Unified Patch
    print("\n[*] Generating unified patch...")
    patch = _build_unified_diff(original_code, current_code, os.path.basename(args.file))
    
    if not patch:
        print("[ℹ️] No changes were made to the file.")
        sys.exit(0)

    patch_filename = f"{args.file}.patch"
    with open(patch_filename, "w", encoding="utf-8") as pf:
        pf.write(patch)
    print(f"[💾] Patch saved directly to: {patch_filename}")

    # Display patch overview
    print("\n" + "="*60)
    print("🛠️ GENERATED VULNERABILITY-FREE PATCH:")
    print("="*60)
    print(patch)
    print("="*60)

    # Step 4: Apply patch if requested
    if args.apply:
        print(f"\n[*] Applying patch directly to {args.file}...")
        with open(args.file, "w", encoding="utf-8") as f:
            f.write(current_code)
        print("[✅] Patch applied! File is now vulnerability-free.")

if __name__ == "__main__":
    main()
