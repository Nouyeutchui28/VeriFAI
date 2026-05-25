import json
import random
import os

def generate_500_security_dataset():
    dataset = []
    
    languages = ["Python", "JavaScript", "PHP", "Java", "Go", "Ruby", "C#"]
    vuln_types = [
        "SQL Injection", "Cross-Site Scripting (XSS)", "Command Injection", 
        "Path Traversal", "Hardcoded Secret", "Insecure Hashing", 
        "JWT Weakness", "CORS Misconfiguration", "LDAP Injection",
        "SSRF", "Insecure Deserialization", "Broken Access Control"
    ]
    
    # Templates for generation
    templates = {
        "SQL Injection": {
            "Python": [
                "query = 'SELECT * FROM {table} WHERE {col} = \"' + {var} + '\"'",
                "db.execute('UPDATE {table} SET {col} = \"' + {var} + '\" WHERE id = ' + {id})",
                "cursor.execute(f'DELETE FROM {table} WHERE {col} = \"{{user_data}}\"')"
            ],
            "JavaScript": [
                "const sql = `SELECT * FROM ${table} WHERE ${col} = '${var}'`;",
                "db.query('SELECT * FROM ' + table + ' WHERE ' + col + ' = \"' + input + '\"');",
                "const query = \"UPDATE \" + {table} + \" SET \" + {col} + \" = '\" + {var} + \"'\";"
            ],
            "PHP": [
                "$sql = \"SELECT * FROM $table WHERE $col = '\" . $_GET['$var'] . \"'\";",
                "$query = \"DELETE FROM $table WHERE id = $id\";",
                "$db->query(\"UPDATE users SET name = '\" . $name . \"' WHERE id = \" . $id);"
            ]
        },
        "Cross-Site Scripting (XSS)": {
            "JavaScript": [
                "document.getElementById('{id}').innerHTML = {var};",
                "$('#{id}').html(urlParams.get('{var}'));",
                "document.write('<div>' + {var} + '</div>');"
            ],
            "Python": [
                "return render_template_string('<h1>Hello ' + {var} + '</h1>')",
                "return f'<div>Results for: {{{var}}}</div>'",
                "template = Template('Hello $name'); return template.render(name={var})"
            ]
        },
        "Command Injection": {
            "Python": [
                "os.system('ping ' + {var})",
                "subprocess.call('ls ' + {var}, shell=True)",
                "os.popen('cat ' + {var}).read()"
            ],
            "JavaScript": [
                "exec('nslookup ' + {var}, (err, out) => {{ ... }});",
                "spawn('grep ' + {var} + ' file.txt', {{ shell: true }});",
                "require('child_process').execSync('rm -rf ' + {var});"
            ]
        },
        "Hardcoded Secret": {
            "Any": [
                "API_KEY = \"{secret}\"",
                "password: \"{secret}\"",
                "const TOKEN = '{secret}';",
                "String secret = \"{secret}\";"
            ]
        }
    }

    tables = ["users", "accounts", "orders", "products", "settings", "logs", "profiles"]
    cols = ["username", "email", "password", "id", "status", "role", "key"]
    vars = ["user_input", "data", "payload", "input_str", "request_param", "query_val"]
    secrets = ["sk_live_51M...", "ghp_...", "AIzaSy...", "xoxb-...", "secret123", "admin_pass"]

    for i in range(500):
        v_type = random.choice(list(templates.keys()))
        lang = random.choice(list(templates[v_type].keys()))
        
        # Select a template
        template = random.choice(templates[v_type][lang])
        
        # Fill template
        table = random.choice(tables)
        col = random.choice(cols)
        var = random.choice(vars)
        secret = random.choice(secrets)
        element_id = f"content_{random.randint(1,100)}"
        
        vulnerable_code = template.format(
            table=table, col=col, var=var, id=element_id, secret=secret
        )
        
        # Generate generic fix based on type
        if v_type == "SQL Injection":
            secure_code = f"# Use parameterized queries: cursor.execute('SELECT * FROM {table} WHERE {col} = %s', ({var},))"
        elif v_type == "Cross-Site Scripting (XSS)":
            secure_code = f"# Use proper escaping or templating: html.escape({var})"
        elif v_type == "Command Injection":
            secure_code = f"# Avoid shell=True: subprocess.run(['ping', '-c', '4', {var}])"
        elif v_type == "Hardcoded Secret":
            secure_code = f"# Load from environment: os.environ.get('API_KEY')"
        else:
            secure_code = "// Implementation of secure pattern here"

        dataset.append({
            "id": i + 1,
            "vulnerability_type": v_type,
            "language": lang,
            "vulnerable_code": vulnerable_code,
            "secure_code": secure_code,
            "severity": random.choice(["Critical", "High", "Medium"]),
            "description": f"A {v_type} vulnerability in {lang} code."
        })

    os.makedirs("security_datasets", exist_ok=True)
    with open("security_datasets/security_500_dataset.json", "w") as f:
        json.dump(dataset, f, indent=2)
    
    print(f"✅ Successfully generated 500 security parameters at: security_datasets/security_500_dataset.json")

if __name__ == "__main__":
    generate_500_security_dataset()
