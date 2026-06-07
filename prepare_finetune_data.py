import os
import json
import glob

def prepare_data():
    base_dir = "/home/bruns/Pictures/VeriFAI LLM/security_datasets/external/advisory-database/advisories/github-reviewed"
    output_file = "/home/bruns/Pictures/VeriFAI LLM/security_datasets/finetune_advisories.jsonl"
    
    python_advisories = []
    
    # Walk through the directory structure
    pattern = os.path.join(base_dir, "**/*.json")
    files = glob.glob(pattern, recursive=True)
    
    print(f"Found {len(files)} total advisories. Filtering for Python...")
    
    count = 0
    with open(output_file, 'w') as f:
        for file_path in files:
            try:
                with open(file_path, 'r') as jf:
                    data = json.load(jf)
                
                # Check if it's a Python advisory
                is_python = False
                affected_packages = []
                if 'affected' in data:
                    for aff in data['affected']:
                        if aff.get('package', {}).get('ecosystem') == 'PyPI':
                            is_python = True
                            affected_packages.append(aff['package'].get('name'))
                
                if is_python:
                    summary = data.get('summary', '')
                    details = data.get('details', '')
                    ghsa_id = data.get('id', '')
                    cwe_ids = data.get('database_specific', {}).get('cwe_ids', [])
                    packages_str = ", ".join(affected_packages)
                    
                    # Construct the instruction pair
                    prompt = f"Analyze the following security advisory for the Python package(s) {packages_str} ({ghsa_id}) and summarize the vulnerability, CWEs, and remediation steps."
                    
                    response = f"Vulnerability: {summary}\n\nDetails: {details}\n\nCWE IDs: {', '.join(cwe_ids) if cwe_ids else 'N/A'}"
                    
                    # Optional: Add severity
                    severity = data.get('database_specific', {}).get('severity', 'UNKNOWN')
                    response += f"\nSeverity: {severity}"
                    
                    # Write to JSONL
                    json.dump({"prompt": prompt, "completion": response}, f)
                    f.write('\n')
                    count += 1
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                
    print(f"Successfully processed {count} Python advisories. Saved to {output_file}")

if __name__ == "__main__":
    prepare_data()
