import sqlite3
import os
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

DB_PATH = os.environ.get("VERIFAI_OFFLINE_DB", "./data/verifai_offline.db")


def _get_conn():
    d = os.path.dirname(DB_PATH)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        name TEXT,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_name TEXT,
        repo_url TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id INTEGER,
        code_snippet TEXT,
        semgrep_json TEXT,
        llm_analysis TEXT,
        patches TEXT,
        severity_count TEXT,
        fixed_code TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id INTEGER,
        role TEXT,
        content TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    return conn


_CONN = _init_db()


def _now():
    return datetime.utcnow().isoformat() + "Z"


def create_user(email: str, name: Optional[str], password: str) -> Dict[str, Any]:
    cur = _CONN.cursor()
    try:
        cur.execute("INSERT INTO users (email, name, password) VALUES (?, ?, ?)", (email, name, password))
        _CONN.commit()
        return {"id": cur.lastrowid, "email": email, "name": name}
    except Exception as e:
        return {"error": str(e)}


def find_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    cur = _CONN.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    return dict(row) if row else None


def save_scan(project_name: Optional[str], repo_url: Optional[str]) -> Dict[str, Any]:
    cur = _CONN.cursor()
    cur.execute("INSERT INTO scans (project_name, repo_url, status, created_at) VALUES (?, ?, ?, ?)", (project_name, repo_url, "queued", _now()))
    _CONN.commit()
    return {"id": cur.lastrowid, "project_name": project_name, "repo_url": repo_url, "status": "queued"}


def get_scan(scan_id: int) -> Optional[Dict[str, Any]]:
    cur = _CONN.cursor()
    cur.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
    row = cur.fetchone()
    return dict(row) if row else None


def get_scan_history(limit: int = 50) -> List[Dict[str, Any]]:
    cur = _CONN.cursor()
    cur.execute("SELECT * FROM scans ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    return [dict(r) for r in rows]


def update_scan_status(scan_id: int, status: str, **kwargs) -> Dict[str, Any]:
    cur = _CONN.cursor()
    cur.execute("UPDATE scans SET status = ? WHERE id = ?", (status, scan_id))
    _CONN.commit()
    return get_scan(scan_id) or {"error": "not found"}


def save_result(scan_id: int, code_snippet: Optional[str] = None, semgrep_json: Optional[dict] = None,
                llm_analysis: Optional[str] = None, patches: Optional[str] = None, severity_count: Optional[dict] = None) -> Dict[str, Any]:
    cur = _CONN.cursor()
    cur.execute("INSERT INTO results (scan_id, code_snippet, semgrep_json, llm_analysis, patches, severity_count, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", (
        scan_id, code_snippet, json.dumps(semgrep_json) if semgrep_json is not None else None,
        llm_analysis, patches, json.dumps(severity_count) if severity_count is not None else None, _now()
    ))
    _CONN.commit()
    return {"id": cur.lastrowid}


def get_results(scan_id: int) -> List[Dict[str, Any]]:
    cur = _CONN.cursor()
    cur.execute("SELECT * FROM results WHERE scan_id = ? ORDER BY id DESC", (scan_id,))
    rows = cur.fetchall()
    out = []
    for r in rows:
        row = dict(r)
        if row.get("semgrep_json"):
            try:
                row["semgrep_json"] = json.loads(row["semgrep_json"])
            except Exception:
                pass
        if row.get("severity_count"):
            try:
                row["severity_count"] = json.loads(row["severity_count"])
            except Exception:
                pass
        out.append(row)
    return out


def save_chat_message(scan_id: int, role: str, content: str) -> Dict[str, Any]:
    cur = _CONN.cursor()
    cur.execute("INSERT INTO chat_messages (scan_id, role, content, created_at) VALUES (?, ?, ?, ?)", (scan_id, role, content, _now()))
    _CONN.commit()
    return {"id": cur.lastrowid}


def get_chat_history(scan_id: int) -> List[Dict[str, Any]]:
    cur = _CONN.cursor()
    cur.execute("SELECT * FROM chat_messages WHERE scan_id = ? ORDER BY id ASC", (scan_id,))
    rows = cur.fetchall()
    return [dict(r) for r in rows]


def get_summary_stats(user_id: Optional[int] = None) -> Dict[str, Any]:
    cur = _CONN.cursor()
    cur.execute("SELECT COUNT(*) as total FROM scans")
    total_scans = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) as total FROM results")
    total_results = cur.fetchone()[0]
    return {"total_scans": total_scans, "vulnerabilities": total_results, "fixed_issues": 0, "security_score": 100}
