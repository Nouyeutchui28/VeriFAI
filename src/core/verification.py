import os
import subprocess
import ast
import logging
from typing import Tuple, Dict, Any
from .security import run_semgrep_scan

logger = logging.getLogger("verifai_llm.verification")

def verify_python_syntax(code: str) -> Tuple[bool, str]:
    """Check if Python code is syntactically correct."""
    try:
        ast.parse(code)
        return True, "Syntax is valid."
    except SyntaxError as e:
        return False, f"Syntax Error: {e.msg} at line {e.lineno}"
    except Exception as e:
        return False, f"Validation Error: {str(e)}"

def verify_fix_with_scanner(file_path: str, original_findings_count: int) -> Tuple[bool, Dict[str, Any]]:
    """
    Re-scan a file to see if the findings count decreased.
    
    Returns:
        Tuple of (is_improved, details_dict)
    """
    if not os.path.exists(file_path):
        return False, {"error": f"File not found: {file_path}"}

    # Run a fresh scan
    try:
        new_results = run_semgrep_scan(file_path)
    except Exception as e:
        return False, {"error": f"Scanner execution failed: {str(e)}"}
        
    new_findings = new_results.get("results", [])
    new_count = len(new_findings)
    
    # If the original scan had 0 findings, and the new one also has 0, consider it fixed/verified
    if original_findings_count == 0 and new_count == 0:
        is_improved = True
    else:
        is_improved = new_count < original_findings_count
        
    is_fixed = new_count == 0
    
    return (is_improved or is_fixed), {
        "original_count": original_findings_count,
        "new_count": new_count,
        "is_improved": is_improved,
        "is_fixed": is_fixed,
        "new_findings": new_findings,
        "scan_error": new_results.get("error")
    }

def verify_patch_safety(file_path: str, patched_code: str) -> Tuple[bool, str]:
    """
    Perform multiple safety checks on patched code before final application.
    """
    # 1. Syntax Check
    if file_path.endswith(".py"):
        valid, msg = verify_python_syntax(patched_code)
        if not valid:
            return False, msg
            
    # 2. Basic Sanity (e.g., didn't delete everything)
    if len(patched_code.strip()) < 10 and len(patched_code.strip()) < (os.path.getsize(file_path) / 2):
        return False, "Patch results in suspiciously small file content."
        
    return True, "Patch passed safety checks."
