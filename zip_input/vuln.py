import sqlite3
import os

def search_user(user_id):
    db = sqlite3.connect("users.db")
    query = 'SELECT * FROM users WHERE id = ?'; db.execute(query, (user_id,)).fetchall()

def run_echo(user_input):
    import subprocess; subprocess.run(['echo', user_input])
