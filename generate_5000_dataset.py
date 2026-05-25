import json
import random
import os

def generate_5000_security_dataset():
    dataset = []
    
    languages = ["Python", "JavaScript", "PHP", "Java", "Go", "Ruby", "C#", "C++", "TypeScript", "Rust"]
    vuln_types = [
        "SQL Injection", "Cross-Site Scripting (XSS)", "Command Injection", 
        "Path Traversal", "Hardcoded Secret", "Insecure Hashing", 
        "JWT Weakness", "CORS Misconfiguration", "LDAP Injection",
        "SSRF", "Insecure Deserialization", "Broken Access Control",
        "Open Redirect", "Insecure Direct Object Reference (IDOR)",
        "Missing Function Level Access Control", "Clickjacking",
        "Insecure Cookie Configuration", "Brute Force Protection Missing"
    ]
    
    # Expanded templates for generation
    templates = {
        "SQL Injection": {
            "Python": [
                "query = 'SELECT * FROM {table} WHERE {col} = \"' + {var} + '\"'",
                "db.execute('UPDATE {table} SET {col} = \"' + {var} + '\" WHERE id = ' + {id})",
                "cursor.execute(f'DELETE FROM {table} WHERE {col} = \"{{user_data}}\"')",
                "results = User.query.filter(\"name = '\" + {var} + \"'\").all()",
                "cmd = \"SELECT secret FROM keys WHERE owner = '%s'\" % {var}"
            ],
            "JavaScript": [
                "const sql = `SELECT * FROM ${table} WHERE ${col} = '${var}'`;",
                "db.query('SELECT * FROM ' + table + ' WHERE ' + col + ' = \"' + input + '\"');",
                "const query = \"UPDATE \" + {table} + \" SET \" + {col} + \" = '\" + {var} + \"'\";",
                "let q = \"SELECT * FROM profiles WHERE bio LIKE %\" + {var} + \"%\";",
                "mysql.query(\"DELETE FROM sessions WHERE token = '\" + {var} + \"'\");"
            ],
            "PHP": [
                "$sql = \"SELECT * FROM $table WHERE $col = '\" . $_GET['$var'] . \"'\";",
                "$query = \"DELETE FROM $table WHERE id = $id\";",
                "$db->query(\"UPDATE users SET name = '\" . $name . \"' WHERE id = \" . $id);",
                "$stmt = \"SELECT password FROM users WHERE email = '{$_POST['email']}'\";",
                "$results = $mysqli->query(\"SELECT * FROM inventory WHERE item_id = \" . $item_id);"
            ]
        },
        "Cross-Site Scripting (XSS)": {
            "JavaScript": [
                "document.getElementById('{id}').innerHTML = {var};",
                "$('#{id}').html(urlParams.get('{var}'));",
                "document.write('<div>' + {var} + '</div>');",
                "element.insertAdjacentHTML('beforeend', `<span>${{{var}}}</span>`);",
                "window.location.hash = `Search results for: ${{{var}}}`;",
                "document.querySelector('.output').outerHTML = userGeneratedContent;"
            ],
            "Python": [
                "return render_template_string('<h1>Hello ' + {var} + '</h1>')",
                "return f'<div>Results for: {{{var}}}</div>'",
                "template = Template('Hello $name'); return template.render(name={var})",
                "return Response(f'<p>User said: {{{var}}}</p>', mimetype='text/html')",
                "html = \"<li>\" + {var} + \"</li>\"; return make_response(html)"
            ],
            "PHP": [
                "echo \"<h1>Welcome, \" . $_GET['name'] . \"</h1>\";",
                "printf(\"<div class='alert'>%s</div>\", $errorMessage);",
                "print(\"Search query: \" . $query);",
                "?> <p>Hello <?php echo $username; ?></p> <?php",
                "die(\"Access denied for \" . $user);"
            ]
        },
        "Command Injection": {
            "Python": [
                "os.system('ping ' + {var})",
                "subprocess.call('ls ' + {var}, shell=True)",
                "os.popen('cat ' + {var}).read()",
                "subprocess.run(f\"nslookup {{{var}}}\", shell=True)",
                "eval(f\"__import__('os').system('{{{var}}}')\")"
            ],
            "JavaScript": [
                "exec('nslookup ' + {var}, (err, out) => {{ ... }});",
                "spawn('grep ' + {var} + ' file.txt', {{ shell: true }});",
                "require('child_process').execSync('rm -rf ' + {var});",
                "const {{ exec }} = require('child_process'); exec(`curl ${{{var}}}`);",
                "process.mainModule.require('child_process').execSync(input);"
            ],
            "PHP": [
                "system(\"host \" . $target);",
                "exec(\"convert \" . $image . \" output.png\");",
                "passthru(\"git checkout \" . $branch);",
                "shell_exec(\"tail -n 10 \" . $logfile);",
                "popen(\"/usr/sbin/sendmail -t \" . $email, \"w\");"
            ]
        },
        "Hardcoded Secret": {
            "Any": [
                "API_KEY = \"{secret}\"",
                "password: \"{secret}\"",
                "const TOKEN = '{secret}';",
                "String secret = \"{secret}\";",
                "aws_secret_key: \"{secret}\"",
                "var db_pass = \"{secret}\";",
                "define('DB_PASSWORD', '{secret}');",
                "export GITHUB_TOKEN=\"{secret}\"",
                "client_id: \"{secret}\", client_secret: \"{secret}\"",
                "const connectionString = \"mongodb+srv://user:{secret}@cluster.io\";"
            ]
        },
        "Insecure Deserialization": {
            "Python": [
                "import pickle; data = pickle.loads({var})",
                "import yaml; config = yaml.load({var})",
                "import marshal; obj = marshal.loads(raw_data)"
            ],
            "JavaScript": [
                "const data = JSON.parse(untrustedString); // Missing schema validation",
                "const obj = require('serialize-javascript').deserialize(userInput);",
                "const nodeSerialize = require('node-serialize'); nodeSerialize.unserialize(data);"
            ],
            "Java": [
                "ObjectInputStream in = new ObjectInputStream(new FileInputStream(file)); Object obj = in.readObject();",
                "XMLDecoder d = new XMLDecoder(new BufferedInputStream(new FileInputStream(xmlFile))); Object result = d.readObject();"
            ]
        }
    }

    tables = ["users", "accounts", "orders", "products", "settings", "logs", "profiles", "sessions", "transactions", "messages", "comments", "posts"]
    cols = ["username", "email", "password", "id", "status", "role", "key", "token", "amount", "content", "bio", "ip_address"]
    vars = ["user_input", "data", "payload", "input_str", "request_param", "query_val", "user_id", "token_str", "blob", "raw_req"]
    secrets = ["sk_live_51M...", "ghp_ABC123...", "AIzaSy...", "xoxb-99...", "secret123", "admin_password_2026", "AKIA...", "MIIB...", "root_pass", "0xdeadbeef"]

    v_types_list = list(templates.keys())

    for i in range(5000):
        v_type = random.choice(v_types_list)
        lang = random.choice(list(templates[v_type].keys()))
        
        # Select a template
        template = random.choice(templates[v_type][lang])
        
        # Fill template
        table = random.choice(tables)
        col = random.choice(cols)
        var = random.choice(vars)
        secret = random.choice(secrets)
        element_id = f"content_{random.randint(1,1000)}"
        
        try:
            vulnerable_code = template.format(
                table=table, col=col, var=var, id=element_id, secret=secret
            )
        except KeyError:
            # Handle cases where template might not use all variables
            vulnerable_code = template
        
        # Generate generic fix based on type
        if v_type == "SQL Injection":
            if lang == "Python":
                secure_code = f"# Use parameterized queries:\ncursor.execute('SELECT * FROM {table} WHERE {col} = %s', ({var},))"
            elif lang == "JavaScript":
                secure_code = f"// Use parameterized queries:\ndb.query('SELECT * FROM ?? WHERE ?? = ?', [{table}, '{col}', {var}]);"
            else:
                secure_code = f"// Use prepared statements with placeholders for {var}"
        elif v_type == "Cross-Site Scripting (XSS)":
            if lang == "JavaScript":
                secure_code = f"// Use textContent instead of innerHTML:\ndocument.getElementById('{element_id}').textContent = {var};"
            elif lang == "Python":
                secure_code = f"# Use Jinja2 autoescaping or html.escape:\nfrom markupsafe import escape\nreturn f'<div>Results for: {{escape({var})}}</div>'"
            else:
                secure_code = f"// Sanitize and escape {var} before outputting to HTML"
        elif v_type == "Command Injection":
            if lang == "Python":
                secure_code = f"# Avoid shell=True and use list of arguments:\nimport subprocess\nsubprocess.run(['ping', '-c', '4', {var}], check=True)"
            else:
                secure_code = f"// Use built-in APIs instead of shell commands for {var}"
        elif v_type == "Hardcoded Secret":
            secure_code = f"# Load from environment variables or a secure secret manager:\nimport os\nAPI_KEY = os.environ.get('SERVICE_API_KEY')"
        elif v_type == "Insecure Deserialization":
            if lang == "Python":
                secure_code = f"# Use safe loading methods:\nimport json\ndata = json.loads({var})"
            else:
                secure_code = f"// Use safe serialization formats like JSON with schema validation"
        else:
            secure_code = "// Implementation of secure pattern here"

        dataset.append({
            "id": i + 1,
            "vulnerability_type": v_type,
            "language": lang if lang != "Any" else random.choice(languages),
            "vulnerable_code": vulnerable_code,
            "secure_code": secure_code,
            "severity": random.choice(["Critical", "High", "Medium"]),
            "description": f"A {v_type} vulnerability instance detected in {lang} implementation."
        })

    os.makedirs("security_datasets", exist_ok=True)
    out_path = "security_datasets/security_5000_dataset.json"
    with open(out_path, "w") as f:
        json.dump(dataset, f, indent=2)
    
    print(f"✅ Successfully generated 5000 security parameters at: {out_path}")
    return out_path

if __name__ == "__main__":
    generate_5000_security_dataset()
