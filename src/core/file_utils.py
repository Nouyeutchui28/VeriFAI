import os
import tempfile
import re
from datetime import datetime

def is_valid_file_type(file_path, allowed_extensions):
    """
    Check if a file has an allowed extension.
    
    Args:
        file_path (str): Path to the file
        allowed_extensions (list): List of allowed extensions
        
    Returns:
        bool: True if allowed, False otherwise
    """
    if not file_path:
        return False
    
    # Handle both string and Path objects
    file_str = str(file_path)
    if '.' not in file_str:
        return False
        
    ext = file_str.split('.')[-1].lower()
    return ext in [e.lower() for e in allowed_extensions]

def save_uploaded_file(uploaded_file):
    """
    Save an uploaded file to a temporary directory.
    
    Args:
        uploaded_file: Streamlit uploaded file object
    
    Returns:
        str: Path to the saved file
    """
    # Create temp dir if it doesn't exist
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generate a unique file path
    file_path = os.path.join(temp_dir, uploaded_file.name)
    
    # Save the file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

def read_file_content(file_path):
    """
    Read content of a file.
    
    Args:
        file_path (str): Path to the file
    
    Returns:
        str: File content or error message
    """
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def get_files_from_folder(folder_path, max_files=5):
    """
    Collect code files from a folder.
    
    Args:
        folder_path (str): Path to the folder
        max_files (int): Maximum number of files to collect
    
    Returns:
        dict: Mapping of file paths to their contents
    """
    code_files = {}
    file_count = 0
    
    for file in os.listdir(folder_path):
        if file_count >= max_files:
            break
        
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path) and not file.startswith('.'):
            try:
                with open(file_path, 'r') as f:
                    code_files[file_path] = f.read()
                    file_count += 1
            except:
                pass
    
    return code_files

def save_code_to_temp_file(code_content, file_extension=".py"):
    """
    Save code content to a temporary file.
    
    Args:
        code_content (str): Code content to save
        file_extension (str): File extension to use (default: .py)
    
    Returns:
        str: Path to the saved temporary file
    """
    # Create temp dir if it doesn't exist
    temp_dir = "temp_code"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generate a unique filename using timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"code_{timestamp}{file_extension}"
    file_path = os.path.join(temp_dir, filename)
    
    # Save the code content
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code_content)
    
    return file_path


def extract_primary_code_sample(target_path, max_bytes=5000):
    """
    Return a representative code sample and patch-relative file path.

    For files, this returns the file contents and basename.
    For directories, it returns the first readable source file found and its
    path relative to the scan root.
    """
    code_extensions = (".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".cs", ".cpp", ".c", ".go", ".rb", ".php", ".rs", ".kt", ".swift")

    if not target_path or not os.path.exists(target_path):
        return "", ""

    if os.path.isfile(target_path):
        try:
            with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(max_bytes), os.path.basename(target_path)
        except Exception:
            return "", os.path.basename(target_path)

    for root, _, files in os.walk(target_path):
        for file_name in files:
            if not file_name.lower().endswith(code_extensions):
                continue
            file_path = os.path.join(root, file_name)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read(max_bytes), os.path.relpath(file_path, target_path)
            except Exception:
                continue

    return "", ""

def generate_report(code=None, semgrep_results=None, llm_analysis=""):
    """
    Generate a markdown report for security analysis.

    Args:
        code (str): Code that was analyzed (optional)
        semgrep_results (dict): Semgrep JSON results (optional)
        llm_analysis (str): LLM's security analysis

    Returns:
        str: Markdown-formatted report
    """
    code_preview = "" if not code else (code[:1000] + ("... [truncated]" if len(code) > 1000 else ""))
    semgrep_summary = "No semgrep results provided."
    try:
        if semgrep_results and isinstance(semgrep_results, dict):
            findings = semgrep_results.get("results", [])
            semgrep_summary = f"{len(findings)} findings from Semgrep."
    except Exception:
        semgrep_summary = "Semgrep results could not be parsed."

    return f"""# Security Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Code Analyzed
```
{code_preview}
```

## Semgrep Summary
{semgrep_summary}

## Security Analysis
{llm_analysis}
"""

# ZIP bomb protection constants
MAX_UNCOMPRESSED_SIZE = 500 * 1024 * 1024  # 500MB max uncompressed size
MAX_COMPRESSION_RATIO = 100  # Max 100:1 compression ratio
MAX_FILE_COUNT = 10000  # Max number of files in ZIP
MAX_SINGLE_FILE_SIZE = 100 * 1024 * 1024  # 100MB max single file


class ZIPBombError(Exception):
    """Raised when a potential ZIP bomb is detected."""
    pass


def _validate_zip_safety(zip_path: str) -> dict:
    """
    Validate a ZIP file for potential ZIP bomb attacks.
    
    Args:
        zip_path: Path to the ZIP file
        
    Returns:
        dict with validation results
        
    Raises:
        ZIPBombError: If the ZIP file appears to be malicious
    """
    import zipfile
    
    total_uncompressed_size = 0
    file_count = 0
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        # Check for nested ZIP files (common in ZIP bombs)
        nested_zips = [f for f in zf.namelist() if f.lower().endswith('.zip')]
        if nested_zips:
            raise ZIPBombError(
                f"ZIP contains {len(nested_zips)} nested ZIP file(s) - potential ZIP bomb"
            )
        
        for info in zf.infolist():
            file_count += 1
            
            # Check file count limit
            if file_count > MAX_FILE_COUNT:
                raise ZIPBombError(
                    f"ZIP contains too many files ({file_count}) - potential ZIP bomb"
                )
            
            # Check individual file size
            if info.file_size > MAX_SINGLE_FILE_SIZE:
                raise ZIPBombError(
                    f"File '{info.filename}' is too large ({info.file_size / 1024 / 1024:.1f}MB) - max {MAX_SINGLE_FILE_SIZE / 1024 / 1024:.0f}MB"
                )
            
            # Check for directory traversal in filenames
            if '..' in info.filename or info.filename.startswith('/'):
                raise ZIPBombError(
                    f"File '{info.filename}' contains invalid path - potential path traversal attack"
                )
            
            total_uncompressed_size += info.file_size
            
            # Check compression ratio for each file
            if info.compress_size > 0:
                ratio = info.file_size / info.compress_size
                if ratio > MAX_COMPRESSION_RATIO:
                    raise ZIPBombError(
                        f"File '{info.filename}' has suspicious compression ratio ({ratio:.0f}:1) - potential ZIP bomb"
                    )
            
            # Check total uncompressed size
            if total_uncompressed_size > MAX_UNCOMPRESSED_SIZE:
                raise ZIPBombError(
                    f"Total uncompressed size ({total_uncompressed_size / 1024 / 1024:.1f}MB) exceeds limit - potential ZIP bomb"
                )
    
    return {
        "file_count": file_count,
        "total_uncompressed_size": total_uncompressed_size,
        "is_safe": True
    }


def extract_zip(uploaded_zip_file, validate_safety: bool = True):
    """
    Extract an uploaded ZIP file to a temporary directory and return its path.
    
    Includes ZIP bomb protection by default.

    Args:
        uploaded_zip_file: Streamlit uploaded file object representing a ZIP archive
        validate_safety: If True, validate ZIP for potential bomb attacks (default: True)

    Returns:
        str: Path to the extracted folder
        
    Raises:
        ZIPBombError: If the ZIP file appears to be malicious
        Exception: If extraction fails
    """
    import zipfile

    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    folder_name = f"unzipped_{timestamp}"
    extract_path = os.path.join(temp_dir, folder_name)
    os.makedirs(extract_path, exist_ok=True)

    # Write the uploaded zip to disk first
    zip_path = os.path.join(temp_dir, uploaded_zip_file.name)
    with open(zip_path, "wb") as f:
        f.write(uploaded_zip_file.getbuffer())

    try:
        # Validate ZIP safety before extraction
        if validate_safety:
            validation = _validate_zip_safety(zip_path)
        
        # Extract with safety checks
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Check total extracted size during extraction
            extracted_size = 0
            for info in zip_ref.infolist():
                # Skip directories
                if info.filename.endswith('/'):
                    continue
                
                extracted_size += info.file_size
                if extracted_size > MAX_UNCOMPRESSED_SIZE:
                    raise ZIPBombError(
                        f"Extracted size exceeds limit during extraction - potential ZIP bomb"
                    )
                
                # Extract each file safely
                zip_ref.extract(info, extract_path)
                
    except ZIPBombError:
        # Clean up on ZIP bomb detection
        try:
            os.remove(zip_path)
            if os.path.exists(extract_path):
                import shutil
                shutil.rmtree(extract_path)
        except Exception:
            pass
        raise
    except Exception as e:
        raise Exception(f"Failed to extract ZIP: {str(e)}")

    return extract_path


def apply_patch(patch_text, target_dir, dry_run=False, create_backup=True):
    """
    Attempt to apply a unified diff patch string to files under target_dir.

    Args:
        patch_text (str): Unified-diff formatted patch
        target_dir (str): Directory where the patch should be applied
        dry_run (bool): If True, do not modify files — only validate the patch format and target files.
        create_backup (bool): If True, create .bak backups of files before applying changes.

    Returns:
        dict: {"applied": bool, "message": str}
    """
    import subprocess, tempfile, shutil
    import shutil
    import time

    # Basic validation
    if not patch_text or not patch_text.strip():
        return {"applied": False, "message": "Empty patch."}

    # If dry_run, validate hunks and file targets without writing
    if dry_run:
        try:
            # quick validation: ensure there is at least one file header and one hunk
            if "+++" not in patch_text or "@@" not in patch_text:
                return {"applied": False, "message": "Patch appears malformed."}
            # check referenced files exist under target_dir
            for line in patch_text.splitlines():
                if line.startswith('+++ '):
                    fp = line[4:].strip()
                    if fp.startswith('a/') or fp.startswith('b/'):
                        fp = fp[2:]
                    full = os.path.join(target_dir, fp)
                    if not os.path.exists(full):
                        return {"applied": False, "message": f"Target file not found: {fp}"}
            return {"applied": True, "message": "Patch validated (dry-run successful)."}
        except Exception as e:
            return {"applied": False, "message": f"Dry-run validation error: {str(e)}"}

    # Real apply: try system `patch` tool first
    patch_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.patch')
    patch_file.write(patch_text)
    patch_file.close()

    # Attempt git-backed safe apply if target is a git repo and git is available
    try:
        git_path = shutil.which("git")
        if git_path:
            # check if target_dir is inside a git worktree
            try:
                r = subprocess.run([git_path, "rev-parse", "--is-inside-work-tree"], cwd=target_dir, capture_output=True, text=True, timeout=10)
                if r.returncode == 0 and r.stdout.strip() == 'true':
                    # create a temporary branch
                    branch_name = f"verifai/patch-{int(time.time())}"
                    # get current branch to allow rollback
                    cur = subprocess.run([git_path, "rev-parse", "--abbrev-ref", "HEAD"], cwd=target_dir, capture_output=True, text=True, timeout=10)
                    current_branch = cur.stdout.strip() if cur.returncode == 0 else None

                    # create branch
                    subprocess.run([git_path, "checkout", "-b", branch_name], cwd=target_dir, capture_output=True, text=True, timeout=10)

                    # try to apply the patch with index to stage changes
                    apply_res = subprocess.run([git_path, "apply", "--index", patch_file.name], cwd=target_dir, capture_output=True, text=True, timeout=30)
                    if apply_res.returncode == 0:
                        # commit the changes
                        commit_res = subprocess.run([git_path, "commit", "-m", f"Apply VeriFAI patch {branch_name}"], cwd=target_dir, capture_output=True, text=True, timeout=20)
                        if commit_res.returncode == 0:
                            # success
                            commit_hash = subprocess.run([git_path, "rev-parse", "HEAD"], cwd=target_dir, capture_output=True, text=True, timeout=10).stdout.strip()
                            return {"applied": True, "message": f"Patch applied and committed on branch {branch_name} ({commit_hash})."}
                        else:
                            # commit failed, rollback
                            subprocess.run([git_path, "reset", "--hard"], cwd=target_dir)
                            if current_branch:
                                subprocess.run([git_path, "checkout", current_branch], cwd=target_dir)
                                subprocess.run([git_path, "branch", "-D", branch_name], cwd=target_dir)
                            # fallthrough to other apply methods
                    else:
                        # git apply failed; attempt to rollback branch creation
                        if current_branch:
                            subprocess.run([git_path, "checkout", current_branch], cwd=target_dir)
                        try:
                            subprocess.run([git_path, "branch", "-D", branch_name], cwd=target_dir)
                        except Exception:
                            pass
            except Exception:
                # not a git repo or git failed; continue to other methods
                pass
    except Exception:
        pass

    try:
        # create backups if requested by copying files before applying
        if create_backup:
            # parse patch to find target files
            targets = set()
            for line in patch_text.splitlines():
                if line.startswith('+++ '):
                    fp = line[4:].strip()
                    if fp.startswith('a/') or fp.startswith('b/'):
                        fp = fp[2:]
                    targets.add(fp)
            for t in targets:
                src = os.path.join(target_dir, t)
                if os.path.exists(src):
                    shutil.copy2(src, src + '.bak')

        for strip_level in (1, 0):
            result = subprocess.run([
                "patch", f"-p{strip_level}", "-i", patch_file.name
            ], cwd=target_dir, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return {"applied": True, "message": "Patch applied via system patch."}

        # fall back to manual patch parse if patch tool failed
        _apply_patch_manual(patch_text, target_dir)
        return {"applied": True, "message": "Patch applied via manual parser."}
    except FileNotFoundError:
        # patch program not available, do manual apply
        try:
            _apply_patch_manual(patch_text, target_dir)
            return {"applied": True, "message": "Patch applied via manual parser."}
        except Exception as e:
            return {"applied": False, "message": str(e)}
    except Exception as e:
        return {"applied": False, "message": str(e)}


def _apply_patch_manual(patch_text, target_dir):
    """
    Very simplistic manual patch application. Only handles additions and deletions
    and assumes file paths are correct and hunks are well-formed.
    This is not a full patch parser but should work for simple diffs produced by
    the LLM.
    """
    import re

    lines = patch_text.splitlines()
    file_path = None
    hunks = []

    for line in lines:
        if line.startswith('--- '):
            # old file path
            continue
        if line.startswith('+++ '):
            # new file path
            file_path = line[4:].strip()
            # remove a/ or b/ prefixes if present
            if file_path.startswith('a/') or file_path.startswith('b/'):
                file_path = file_path[2:]
            hunks = []
        elif line.startswith('@@'):
            hunks.append({'header': line, 'lines': []})
        elif hunks:
            hunks[-1]['lines'].append(line)
        elif line.startswith('diff '):
            # skip diff header
            continue

        # when we hit a new file header or end, apply previous hunks
        if file_path and line.startswith('diff ') or line == lines[-1]:
            if hunks:
                _apply_hunks_to_file(file_path, hunks, target_dir)
            file_path = None
            hunks = []

    return True


def _apply_hunks_to_file(relative_path, hunks, target_dir):
    """
    Apply parsed hunks to a single file.
    """
    full_path = os.path.join(target_dir, relative_path)
    if not os.path.exists(full_path):
        return
    try:
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            orig_lines = f.readlines()
    except Exception:
        return

    new_lines = []
    orig_index = 0

    for hunk in hunks:
        header = hunk['header']
        # parse the header for line numbers
        match = re.match(r"@@ -(\d+),(\d+) \+(\d+),(\d+) @@", header)
        if not match:
            continue
        old_start = int(match.group(1)) - 1

        # add unchanged lines before hunk
        while orig_index < old_start and orig_index < len(orig_lines):
            new_lines.append(orig_lines[orig_index])
            orig_index += 1

        # apply hunk lines
        for hl in hunk['lines']:
            if hl.startswith('+') and not hl.startswith('+++'):
                new_lines.append(hl[1:] + '\n')
            elif hl.startswith('-') and not hl.startswith('---'):
                orig_index += 1
            else:
                # context line
                if orig_index < len(orig_lines):
                    new_lines.append(orig_lines[orig_index])
                    orig_index += 1

    # append remaining original lines
    while orig_index < len(orig_lines):
        new_lines.append(orig_lines[orig_index])
        orig_index += 1

    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
    except Exception:
        pass


def create_zip_from_any(source_path):
    """
    Create a ZIP archive in memory from a file or folder.
    
    Args:
        source_path (str): Path to the file or directory to zip.
        
    Returns:
        bytes: ZIP file content as bytes.
    """
    import zipfile
    import io
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        if os.path.isfile(source_path):
            zf.write(source_path, os.path.basename(source_path))
        else:
            for root, _, files in os.walk(source_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, source_path)
                    zf.write(full_path, rel_path)
    
    return buf.getvalue()


def cleanup_temp_files():
    """
    Clean up temporary files and directories.
    """
    import shutil
    try:
        # List of directories to clean
        dirs_to_clean = ["temp_code", "temp_uploads", "temp_github", "results", "configs"]

        for dir_path in dirs_to_clean:
            if os.path.exists(dir_path):
                try:
                    shutil.rmtree(dir_path)
                except Exception as e:
                    print(f"Error cleaning {dir_path}: {str(e)}")

        # Recreate necessary directories
        os.makedirs("temp_code", exist_ok=True)
        os.makedirs("temp_uploads", exist_ok=True)
        os.makedirs("temp_github", exist_ok=True)
        os.makedirs("results", exist_ok=True)
        os.makedirs("configs", exist_ok=True)

    except Exception as e:
        raise Exception(f"Error during cleanup: {str(e)}")