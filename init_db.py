from src.db.connection import init_db
import os

if __name__ == "__main__":
    os.environ["DATABASE_URL"] = "sqlite:///./verifai_llm.db"
    init_db()
    print("Database initialized successfully.")
