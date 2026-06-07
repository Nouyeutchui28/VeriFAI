import json
import os
import re

ADVISORY_INDEX_PATH = "/home/bruns/Pictures/VeriFAI LLM/security_datasets/python_advisory_index.json"

def get_relevant_advisories(code: str) -> str:
    """
    Scans the provided code for package imports and returns relevant 
    security advisories from the GitHub Advisory Database.
    """
    if not os.path.exists(ADVISORY_INDEX_PATH):
        return ""

    try:
        with open(ADVISORY_INDEX_PATH, 'r') as f:
            index = json.load(f)
        
        # Simple regex to find common python imports
        imports = re.findall(r"(?:from|import)\s+([a-zA-Z0-9_]+)", code)
        unique_imports = set(imports)
        
        relevant_context = []
        for pkg in unique_imports:
            # Check for direct match or lowercase match
            pkg_name = pkg.lower()
            if pkg_name in index:
                for adv in index[pkg_name]:
                    relevant_context.append(f"- [{adv['id']}] {pkg_name}: {adv['summary']} (CWE: {', '.join(adv['cwe'])})")
        
        if relevant_context:
            header = "\n### RELEVANT SECURITY ADVISORIES (GitHub Advisory Database)\n"
            return header + "\n".join(relevant_context[:10]) # Limit to top 10 for context window
            
        return ""
    except Exception as e:
        print(f"Advisory Lookup Error: {e}")
        return ""
