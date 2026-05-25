import os
import shutil
from src.core.security import generate_patch_suggestions
from src.core.file_utils import extract_primary_code_sample, apply_patch


def setup_sample_repo(tmpdir):
    repo_path = os.path.join(str(tmpdir), "sample_repo")
    os.makedirs(repo_path, exist_ok=True)
    vuln_code = '''import sqlite3
import os


def search_user(user_id):
    db = sqlite3.connect("users.db")
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query).fetchall()


def run_echo(user_input):
    os.system(f"echo {user_input}")
'''
    file_path = os.path.join(repo_path, "vuln.py")
    with open(file_path, "w") as f:
        f.write(vuln_code)
    return repo_path, file_path


def test_end_to_end_scan_patch_apply(tmp_path):
    # Prepare sample repo
    repo_path, file_path = setup_sample_repo(tmp_path)

    # Extract primary sample
    code, rel = extract_primary_code_sample(repo_path)
    assert code

    # Simulate semgrep results identifying SQL and command injection
    semgrep_results = {"results": [
        {"check_id": "sql-injection", "extra": {"message": "Possible SQL injection"}},
        {"check_id": "command-injection", "extra": {"message": "Possible command injection"}}
    ]}

    # Generate patch via fallback (llm=None)
    patch = generate_patch_suggestions(semgrep_results, code, llm=None, file_path=rel)
    assert patch and "+++ b/" in patch

    # Dry-run apply should validate
    dry = apply_patch(patch, repo_path, dry_run=True)
    assert isinstance(dry, dict) and dry.get("applied")

    # Apply for real (create backups)
    res = apply_patch(patch, repo_path, dry_run=False, create_backup=True)
    assert isinstance(res, dict) and res.get("applied")

    # Ensure backup exists and file updated
    backup = os.path.join(repo_path, rel + ".bak")
    assert os.path.exists(backup)
    with open(os.path.join(repo_path, rel), "r") as f:
        updated = f.read()
    assert "subprocess.run" in updated or "db.execute(query, (user_id,))" in updated

    # cleanup
    shutil.rmtree(repo_path)
