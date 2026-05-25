import sqlite3
import os

def search_user(user_id):
    db = sqlite3.connect("users.db")
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query).fetchall()

def run_echo(user_input):
    os.system(f"echo {user_input}")
