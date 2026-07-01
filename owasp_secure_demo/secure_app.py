import sqlite3
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or request.form
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Invalid Input"}), 400

    try:
        conn = sqlite3.connect("test_users.db")
        cursor = conn.cursor()
        
        query = "SELECT password_hash FROM users WHERE username=?"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
    except sqlite3.Error:
        return jsonify({"error": "Internal server error"}), 500
    finally:
        if 'conn' in locals():
            conn.close()

    if result and check_password_hash(result[0], password):
        return jsonify({"message": "Login Successful"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

def setup_db():
    conn = sqlite3.connect("test_users.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password_hash TEXT)")
    cursor.execute("DELETE FROM users")
    
    hashed_pw = generate_password_hash("secret")
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ("admin", hashed_pw))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_db()
    print("Database initialized with user: 'admin', password: 'secret'")
    print("Starting Flask server on http://127.0.0.1:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=False)
