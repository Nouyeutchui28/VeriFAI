import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple, Optional


def validate_github_url(url: str) -> bool:
    """Validate GitHub URL format."""
    pattern = r'^(?:https?://github\.com/|git@github\.com:)[\w\-]+/[\w\-\.]+/?$'
    return bool(re.match(pattern, url))


def extract_repo_info(url: str) -> Tuple[str, str]:
    """Extract owner and repo name from GitHub URL."""
    url = url.rstrip('/')
    match = re.search(r'github\.com/([^/]+)/([^/]+?)(?:\.git)?$', url)
    if match:
        return match.group(1), match.group(2)
    raise ValueError(f"Invalid GitHub URL format: {url}")


def clone_repository(url: str, target_dir: str, timeout: int = 300) -> str:
    """
    Clone GitHub repository to target directory.
    Supports GITHUB_TOKEN for private repositories.
    """
    os.makedirs(target_dir, exist_ok=True)
    
    # Authenticate URL if token is available
    token = os.getenv("GITHUB_TOKEN")
    clone_url = url
    if token and "github.com" in url and "@" not in url:
        clone_url = url.replace("https://", f"https://x-access-token:{token}@")

    try:
        result = subprocess.run(
            ['git', 'clone', '--depth', '1', clone_url, '.'],
            cwd=target_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True
        )

        # For the '.' clone, the repo_path is target_dir itself
        return target_dir

    except subprocess.TimeoutExpired:
        raise TimeoutError(f"Git clone timed out after {timeout} seconds")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        raise RuntimeError(f"Failed to clone repository: {error_msg}")
    except FileNotFoundError:
        raise RuntimeError("Git command not found. Please install git.")


def get_repo_size_mb(path: str) -> float:
    """Calculate repository size in MB."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
    return total_size / (1024 * 1024)


def get_file_count(path: str) -> int:
    """Count total files in repository."""
    count = 0
    for dirpath, dirnames, filenames in os.walk(path):
        count += len(filenames)
    return count


def cleanup_repo(path: str) -> bool:
    """
    Remove cloned repository directory.
    Returns True if successful, False otherwise.
    """
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
            return True
        return False
    except Exception as e:
        return False


def get_repo_language_stats(path: str) -> dict:
    """
    Get simple language breakdown of repository files.
    Returns dict mapping language to file count.
    """
    language_map = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.jsx': 'JSX',
        '.tsx': 'TSX',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.cs': 'C#',
        '.php': 'PHP',
        '.rb': 'Ruby',
        '.go': 'Go',
        '.rs': 'Rust',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.sh': 'Shell',
        '.bash': 'Bash',
        '.html': 'HTML',
        '.css': 'CSS',
        '.json': 'JSON',
        '.yaml': 'YAML',
        '.yml': 'YAML',
        '.xml': 'XML',
        '.sql': 'SQL',
    }

    stats = {}
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            language = language_map.get(ext, 'Other')
            stats[language] = stats.get(language, 0) + 1

    return stats
