import os
import json
import glob

def create_index():
    base_dir = "/home/bruns/Pictures/VeriFAI LLM/security_datasets/external/advisory-database/advisories/github-reviewed"
    output_file = "/home/bruns/Pictures/VeriFAI LLM/security_datasets/python_advisory_index.json"
    
    index = {}
    
    pattern = os.path.join(base_dir, "**/*.json")
    files = glob.glob(pattern, recursive=True)
    
    for file_path in files:
        try:
            with open(file_path, 'r') as jf:
                data = json.load(jf)
            
            is_python = False
            package_names = []
            if 'affected' in data:
                for aff in data['affected']:
                    if aff.get('package', {}).get('ecosystem') == 'PyPI':
                        is_python = True
                        package_names.append(aff['package'].get('name'))
            
            if is_python:
                ghsa_id = data.get('id', '')
                cwe_ids = data.get('database_specific', {}).get('cwe_ids', [])
                summary = data.get('summary', '')
                
                for pkg in package_names:
                    if pkg not in index:
                        index[pkg] = []
                    index[pkg].append({
                        "id": ghsa_id,
                        "cwe": cwe_ids,
                        "summary": summary
                    })
        except:
            continue
            
    with open(output_file, 'w') as f:
        json.dump(index, f, indent=2)
    
    print(f"Created index for {len(index)} Python packages. Saved to {output_file}")

if __name__ == "__main__":
    create_index()
