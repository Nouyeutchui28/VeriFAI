import os
import uuid
import streamlit as st
from datetime import datetime
import logging
import re

from ..core.security import generate_patch_suggestions, run_semgrep_scan, run_llm_analysis
from ..core.github_handler import validate_github_url, clone_repository
from ..core.file_utils import save_uploaded_file, generate_report, save_code_to_temp_file, extract_zip, apply_patch, extract_primary_code_sample
from ..utils.report_gen import generate_pdf_report
from ..utils.state import AppState
from .patch_review import render_patch_review_panel, extract_patched_code

logger = logging.getLogger(__name__)

def _get_scanner_input_state():
    return (
        st.session_state.get("scanner_paste_code", ""),
        st.session_state.get("scanner_uploaded_file"),
        st.session_state.get("scanner_zip_file"),
        st.session_state.get("scanner_github_url", ""),
        st.session_state.get("scanner_github_repo_path")
    )


def _active_input_mode(paste_code, uploaded_file, zip_file, github_repo_path):
    if github_repo_path:
        return "GitHub"
    if zip_file:
        return "ZIP"
    if uploaded_file:
        if uploaded_file.name.lower().endswith(".zip"):
            return "ZIP"
        return "Upload"
    return "Paste"


def _format_file_label(mode, uploaded_file, zip_file, github_url, github_repo_path):
    if mode == "Upload" and uploaded_file:
        size = getattr(uploaded_file, 'size', len(uploaded_file.getvalue()))
        return f"{uploaded_file.name} · {size} bytes"
    if mode == "ZIP":
        if zip_file:
            return f"{zip_file.name} · ZIP archive"
        if uploaded_file and uploaded_file.name.lower().endswith(".zip"):
            return f"{uploaded_file.name} · ZIP archive"
    if mode == "GitHub" and github_repo_path:
        return f"{os.path.basename(github_repo_path)} · repo"
    return "Paste input"


def _resolve_patch_target(target_path):
    """Return the directory that patch application should use."""
    if not target_path:
        return None
    if os.path.isdir(target_path):
        return target_path
    return os.path.dirname(target_path) or "."


def _resolve_target_path(mode, paste_code, uploaded_file, zip_file, github_repo_path):
    if mode == "Paste" and paste_code.strip():
        target_path = save_code_to_temp_file(paste_code)
        return target_path, "pasted_code.py", paste_code, os.path.basename(target_path)
    if mode == "Upload" and uploaded_file:
        file_path = save_uploaded_file(uploaded_file)
        code_content = ""
        if uploaded_file.name.lower().endswith(".zip"):
            target_path = extract_zip(uploaded_file)
            code_content, patch_file_path = extract_primary_code_sample(target_path)
            return target_path, uploaded_file.name, code_content, patch_file_path
        try:
            code_content = uploaded_file.getvalue().decode("utf-8")
        except UnicodeDecodeError:
            try:
                code_content = uploaded_file.getvalue().decode("utf-8", errors="replace")
            except Exception:
                code_content = ""
        return file_path, uploaded_file.name, code_content, os.path.basename(file_path)
    if mode == "ZIP" and zip_file:
        target_path = extract_zip(zip_file)
        code_content, patch_file_path = extract_primary_code_sample(target_path)
        return target_path, zip_file.name, code_content, patch_file_path
    if mode == "ZIP" and uploaded_file and uploaded_file.name.lower().endswith(".zip"):
        target_path = extract_zip(uploaded_file)
        code_content, patch_file_path = extract_primary_code_sample(target_path)
        return target_path, uploaded_file.name, code_content, patch_file_path
    if mode == "GitHub" and github_repo_path:
        code_content, patch_file_path = extract_primary_code_sample(github_repo_path)
        return github_repo_path, os.path.basename(github_repo_path), code_content, patch_file_path
    return None, None, "", ""


def _clear_scanner_state():
    AppState.clear_analysis()
    # Use a set of keys to clear safely
    for key in ["analysis_results", "last_scan_results", "last_scan_code", "last_scan_file", "scan_step", "scan_error", "scan_running", "run_scan_request"]:
        if key in st.session_state:
            st.session_state[key] = None if "results" in key else ""
            if key == "scan_step": st.session_state[key] = 0
            if "running" in key or "request" in key or "error" in key: st.session_state[key] = False

    # For widget keys, we just delete them so they reset to default on next render
    widget_keys = ["scanner_paste_code", "scanner_uploaded_file", "scanner_zip_file", "scanner_github_url", "scanner_github_repo_path", "quick_ask_prompt"]
    for key in widget_keys:
        if key in st.session_state:
            del st.session_state[key]


def _build_step_status(step_index, current_step, running, error):
    if error and current_step == step_index:
        return "error"
    if running and current_step == step_index:
        return "running"
    if current_step > step_index:
        return "done"
    return "idle"


def _render_status_badge(status):
    colors = {
        "done": "#00e5a0",
        "running": "#0066ff",
        "error": "#ff4060",
        "idle": "#8b909e",
    }
    icons = {
        "done": "✔",
        "running": "●",
        "error": "✖",
        "idle": "○",
    }
    return f"<span style='color: {colors[status]}; font-family: DM Mono, monospace;'>{icons[status]}</span>"


def _execute_scan(target_path, code_content, actual_filename, patch_file_path=""):
    """Execute a comprehensive security scan with parallel AI analysis."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from ..core.security import unified_security_scan
    
    if not target_path or not os.path.exists(target_path):
        st.error("❌ Error: Target path does not exist.")
        return
    
    st.session_state.analysis_results = None
    st.session_state.scan_running = True
    st.session_state.scan_error = False
    st.session_state.scan_step = 1
    st.session_state.run_scan_request = False

    progress_placeholder = st.empty()
    status_placeholder = st.empty()

    with status_placeholder.status("🔍 Initializing Security Scan...", expanded=True) as status:
        try:
            # Step 1: Semgrep Static Analysis
            status.update(label="🚀 Running Semgrep Static Analysis... (Step 1/3)", state="running")
            progress_placeholder.progress(0.1, text="Analyzing code patterns with Semgrep...")
            sem_res = run_semgrep_scan(target_path, True)
            findings = sem_res.get("results", [])
            
            # Step 2: Parallel AI Analysis & Patching
            status.update(label="🤖 Running Parallel AI Analysis... (Step 2/3)", state="running")
            progress_placeholder.progress(0.4, text="Initializing Hugging Face engine for concurrent analysis...")
            
            llm = None

            # Identify all unique flagged files
            flagged_files = list(set([f.get("path") for f in findings if f.get("path")]))
            
            # HEURISTIC FALLBACK: Always ensure at least the primary file is analyzed by AI
            from ..core.file_utils import extract_primary_code_sample
            _, primary_rel = extract_primary_code_sample(target_path)
            
            if primary_rel and primary_rel not in flagged_files:
                # Insert at the beginning so it's prioritized
                flagged_files.insert(0, primary_rel)
            
            # If still no files found (shouldn't happen with valid code), fallback to target path itself
            if not flagged_files:
                flagged_files = [patch_file_path or os.path.basename(target_path)]
            
            # Limit parallel scans to top 10 vulnerable/critical files for speed + resource safety
            flagged_files = flagged_files[:10]
            
            all_llm_analyses = []
            all_patches = []
            
            def process_file_task(file_rel_path):
                # Resolve absolute path
                if os.path.isdir(target_path):
                    full_path = os.path.join(target_path, file_rel_path)
                else:
                    full_path = target_path
                
                if not os.path.exists(full_path):
                    return None, None
                
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        file_code = f.read(8000)
                    
                    # Agentic Feature: Resolve local context dependencies
                    from ..core.security import resolve_local_dependencies
                    context_files = {}
                    if os.path.isdir(target_path):
                        deps = resolve_local_dependencies(file_code, target_path)
                        for d_rel, d_full in deps:
                            try:
                                with open(d_full, "r", encoding="utf-8", errors="ignore") as df:
                                    context_files[d_rel] = df.read(2000)
                            except: pass
                    
                    return unified_security_scan(sem_res, file_code, llm, file_path=file_rel_path, context_files=context_files)
                except Exception as e:
                    logger.error(f"Error in parallel task for {file_rel_path}: {e}")
                    return None, None

            # Run analysis in parallel (Max 3 concurrent to be safer for local CPU/Ollama stability)
            with ThreadPoolExecutor(max_workers=3) as executor:
                future_to_file = {executor.submit(process_file_task, f): f for f in flagged_files}
                completed_count = 0
                for future in as_completed(future_to_file):
                    fname = future_to_file[future]
                    try:
                        analysis, patch = future.result()
                        if analysis: 
                            all_llm_analyses.append(f"### 📄 File: {fname}\n{analysis}")
                        if patch and patch != "No patch suggestions.": 
                            all_patches.append(patch)
                    except Exception as e:
                        logger.error(f"Task failed for {fname}: {e}")
                    
                    completed_count += 1
                    progress_placeholder.progress(
                        0.4 + (0.4 * (completed_count / len(flagged_files))), 
                        text=f"AI Expert Analysis: {completed_count}/{len(flagged_files)} files..."
                    )
            
            combined_analysis = "\n\n---\n\n".join(all_llm_analyses) or "⚠️ No vulnerabilities found in AI deep-scan. Review Semgrep results."
            combined_patch = "\n\n".join(all_patches) or "No patch suggestions."
            
            # Ensure code_content is populated for single files if it was empty
            if not code_content and not os.path.isdir(target_path):
                try:
                    with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
                        code_content = f.read(5000)
                except: pass
            
            # Step 3: Build & Save
            status.update(label="📄 Building Security Report... (Step 3/3)", state="running")
            progress_placeholder.progress(0.9, text="Finalizing report and saving results...")
            
            report = generate_report(code_content, sem_res, combined_analysis)
            
            # Backend Persistence (Simplified for speed)
            result_id = str(uuid.uuid4())
            try:
                from .api_client import get_api_client
                api_client = get_api_client()
                sc_id = str(uuid.uuid4())
                u_id = st.session_state.get("user_info", {}).get("id", "anonymous_user")

                api_client.save_scan_insforge({
                    "id": sc_id, "user_id": u_id, "status": "complete",
                    "project_name": actual_filename, "start_time": datetime.now().isoformat(),
                    "end_time": datetime.now().isoformat(),
                })

                sev_c = {}
                for r in findings:
                    s = r.get("severity", "unknown").lower()
                    sev_c[s] = sev_c.get(s, 0) + 1

                api_client.save_result_insforge({
                    "id": result_id, "scan_id": sc_id, "code_snippet": code_content[:2000],
                    "semgrep_json": sem_res, "llm_analysis": combined_analysis,
                    "patches": combined_patch, "severity_count": sev_c,
                })
            except Exception as e:
                logger.error(f"Backend persistence failed: {e}")
                sev_c = {r.get("severity", "low").lower(): 1 for r in findings} # Fallback

            st.session_state.analysis_results = {
                "result_id": result_id,
                "code_content": code_content,
                "llm_analysis": combined_analysis,
                "semgrep_results": sem_res,
                "report": report,
                "patch_suggestions": combined_patch,
                "target_path": target_path,
                "patch_file_path": patch_file_path or actual_filename,
                "severity_count": sev_c,
            }
            st.session_state.last_scan_code = code_content
            st.session_state.last_scan_results = st.session_state.analysis_results
            st.session_state.last_scan_file = actual_filename

            progress_placeholder.progress(1.0, text="Scan complete!")
            status.update(label="✅ Security Scan Complete!", state="complete", expanded=False)
            
            # Verification Success Message
            if st.session_state.get("patch_verified") and not findings:
                st.success("🎉 VERIFICATION PASSED: All vulnerabilities have been successfully resolved in the new version!")
                st.session_state.patch_verified = False # Reset flag after successful pass

        except Exception as e:
            st.session_state.scan_error = True
            status.update(label="❌ Analysis Failed", state="error")
            st.error(f"❌ Analysis failed: {str(e)}")
        finally:
            st.session_state.scan_running = False
            st.session_state.run_scan_request = False
            if not st.session_state.scan_error: st.balloons()
            st.rerun()


def render_scanner_tab():
    st.markdown(
        """
        <style>
        .scanner-panel {
            padding: 1.25rem;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 14px;
            background: #151a26;
            margin-bottom: 1.5rem;
        }
        .scanner-panel-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
        }
        .scanner-panel-title {
            font-family: 'Syne', sans-serif;
            font-size: 1rem;
            font-weight: 700;
            color: #e8eaf0;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }
        .scanner-file-label {
            color: #8b909e;
            font-size: 0.85rem;
        }
        .finding-card {
            background: #121824;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 14px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        .finding-header {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            align-items: center;
            margin-bottom: 0.75rem;
        }
        .finding-title {
            font-family: 'Syne', sans-serif;
            color: #e8eaf0;
            font-size: 1rem;
            margin: 0;
        }
        .severity-badge {
            font-family: 'DM Mono', monospace;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            padding: 0.25rem 0.6rem;
            border-radius: 999px;
        }
        .severity-high { background: rgba(255,64,96,0.15); color: #ff4060; }
        .severity-med { background: rgba(255,170,0,0.15); color: #ffaa00; }
        .severity-low { background: rgba(0,102,255,0.15); color: #0066ff; }
        .workflow-step {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            padding: 0.85rem 1rem;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.06);
            margin-bottom: 0.75rem;
            background: #101424;
        }
        .step-indicator {
            min-width: 32px;
            height: 32px;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 0.85rem;
            font-weight: 700;
            color: #000;
        }
        .step-idle { background: #2f3549; }
        .step-running { background: #0066ff; }
        .step-done { background: #00e5a0; }
        .step-error { background: #ff4060; }
        .step-label {
            color: #e8eaf0;
            margin: 0;
            font-weight: 600;
        }
        .step-description {
            color: #8b909e;
            margin: 0.25rem 0 0;
            font-size: 0.9rem;
        }
        .step-tag {
            color: #8b909e;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .analysis-container {
            background: #0f172a;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 14px;
            padding: 1.5rem;
            margin-top: 1.5rem;
            color: #e2e8f0;
        }
        .analysis-title {
            font-family: 'Syne', sans-serif;
            font-size: 1.25rem;
            font-weight: 700;
            color: #00e5a0;
            margin-bottom: 1rem;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 0.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if "scanner_github_url" not in st.session_state:
        st.session_state.scanner_github_url = ""
    if "scanner_github_repo_path" not in st.session_state:
        st.session_state.scanner_github_repo_path = None

    paste_code, uploaded_file, zip_file, github_url, github_repo_path = _get_scanner_input_state()
    mode = _active_input_mode(paste_code, uploaded_file, zip_file, github_repo_path)
    file_label = _format_file_label(mode, uploaded_file, zip_file, github_url, github_repo_path)

    # Trigger scan if requested
    if st.session_state.run_scan_request and not st.session_state.scan_running:
        target_path, actual_filename, code_content, patch_file_path = _resolve_target_path(mode, paste_code, uploaded_file, zip_file, github_repo_path)
        if target_path is None:
            st.error("Please provide code input, upload a file, upload a ZIP, or clone a GitHub repository before scanning.")
            st.session_state.run_scan_request = False
        else:
            _execute_scan(target_path, code_content, actual_filename, patch_file_path)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<div class="scanner-panel">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="scanner-panel-header"><div class="scanner-panel-title">code input</div><div class="scanner-file-label">{file_label}</div></div>',
            unsafe_allow_html=True,
        )

        tabs = st.tabs(["Paste", "Upload", "ZIP", "GitHub"])

        with tabs[0]:
            st.text_area(
                "Paste code here",
                height=200,
                key="scanner_paste_code",
                placeholder="Paste code here...",
                label_visibility="collapsed"
            )
            st.markdown("**Sample vulnerable code to test:**")
            sample_code = '''import sqlite3

def search_user(user_id):
    """VULNERABLE: SQL Injection"""
    db = sqlite3.connect("users.db")
    query = f"SELECT * FROM users WHERE id = {user_id}"  # Direct string concat
    return db.execute(query).fetchall()

def process_data(user_input):
    """VULNERABLE: Command Injection"""
    import os
    os.system(f"echo {user_input}")  # Command injection risk

def unsafe_pickle():
    """VULNERABLE: Insecure Deserialization"""
    import pickle
    data = pickle.loads(user_data)  # Unsafe deserialize
    return data
'''
            if st.button("📋 Load Sample Vulnerable Code", key="sample_code_btn"):
                st.session_state.scanner_paste_code = sample_code
                st.success("Sample code loaded! Click 'Run Scan' to analyze.")
                st.rerun()

        with tabs[1]:
            uploaded_file = st.file_uploader("Upload a file", key="scanner_uploaded_file")

        with tabs[2]:
            zip_file = st.file_uploader("Upload ZIP archive", type=["zip"], key="scanner_zip_file")

        with tabs[3]:
            github_url = st.text_input(
                "GitHub repository URL",
                value=github_url,
                key="scanner_github_url",
                placeholder="https://github.com/user/repo"
            )
            if st.button("Clone", key="scanner_clone_repo"):
                if not github_url.strip():
                    st.error("Please enter a repository URL.")
                elif not validate_github_url(github_url):
                    st.error("Please enter a valid GitHub repository URL.")
                else:
                    temp_dir = os.path.join("temp_github", f"scan_{datetime.now().strftime('%Y%m%d%H%M%S')}")
                    os.makedirs(temp_dir, exist_ok=True)
                    try:
                        repo_path = clone_repository(github_url, temp_dir)
                        st.session_state.scanner_github_repo_path = repo_path
                        st.success("Repository cloned successfully.")
                    except Exception as e:
                        st.error(f"Clone failed: {str(e)}")

        st.markdown('</div>', unsafe_allow_html=True)

        status_count = 0
        results = st.session_state.get("analysis_results") or {}
        if results.get("semgrep_results", {}).get("results"):
            status_count = len(results["semgrep_results"]["results"])

        status_line = f"ready · {status_count} findings"
        st.markdown(f"<div style='display:flex; justify-content: space-between; align-items:center; margin-top: 1rem;'><div></div><span style='color: #8b909e;'>{status_line}</span></div>", unsafe_allow_html=True)

        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("Run Scan", type="primary", use_container_width=True, key="scanner_run"):
                st.session_state.run_scan_request = True
                st.rerun()
        
        with btn_col2:
            if st.button("Clear Results", type="secondary", use_container_width=True, key="scanner_clear"):
                _clear_scanner_state()
                st.rerun()

    with col2:
        st.markdown('<div class="scanner-panel">', unsafe_allow_html=True)
        st.markdown('<div class="scanner-panel-header"><div class="scanner-panel-title">workflow</div></div>', unsafe_allow_html=True)

        scan_step = st.session_state.get("scan_step", 0)
        scan_running = st.session_state.get("scan_running", False)
        scan_error = st.session_state.get("scan_error", False)

        steps = [
            ("Semgrep Scan", "Static rule-based analysis"),
            ("LLM Analysis", "Local AI vulnerability review"),
            ("Patch Generation", "AI-suggested remediation"),
            ("Report Build", "PDF audit report generation"),
            ("Save to Backend", "Persist via InsForge API"),
        ]

        for idx, (title, description) in enumerate(steps, start=1):
            status = _build_step_status(idx, scan_step, scan_running, scan_error)
            st.markdown(
                f'<div class="workflow-step"><span class="step-indicator step-{status}">{idx}</span><div style="flex:1;"><p class="step-label">{title}</p><p class="step-description">{description}</p></div><span class="step-tag">{status}</span></div>',
                unsafe_allow_html=True,
            )

        if st.session_state.analysis_results and not scan_running:
            st.markdown('<div class="scanner-panel" style="margin-top: 1rem;">', unsafe_allow_html=True)
            st.markdown('<div class="scanner-panel-header"><div class="scanner-panel-title">actions</div></div>', unsafe_allow_html=True)

            result = st.session_state.analysis_results
            code_content = result.get("code_content", "")
            llm_analysis = result.get("llm_analysis", "")
            semgrep_results = result.get("semgrep_results", {})
            patch_text = result.get("patch_suggestions", "")
            patch_target = _resolve_patch_target(result.get("target_path", ""))

            col_open_chat, col_copy = st.columns(2)
            with col_open_chat:
                if st.button("Ask AI about findings ↗", use_container_width=True, key="scanner_ask_ai"):
                    AppState.set("current_page", "💬 Intelligence Chat")
                    st.session_state.quick_ask_prompt = "Explain all findings"
                    st.session_state.last_scan_code = code_content
                    st.session_state.last_scan_results = result
                    st.session_state.last_scan_file = st.session_state.get('last_scan_file', '') or result.get('target_path', '')
                    st.session_state.llm_analysis = llm_analysis
                    st.rerun()

            with col_copy:
                if st.button("Use in Chat", use_container_width=True, key="scanner_use_in_chat"):
                    st.session_state.last_scan_code = code_content
                    st.session_state.last_scan_results = result
                    st.session_state.last_scan_file = st.session_state.get('last_scan_file', '') or result.get('target_path', '')
                    st.session_state.llm_analysis = llm_analysis
                    st.session_state.quick_ask_prompt = "Explain all findings"
                    AppState.set_page("💬 Intelligence Chat")

            pdf_bytes = None
            try:
                pdf_bytes = generate_pdf_report(code_content, llm_analysis, semgrep_results)
            except Exception:
                pdf_bytes = None

            if pdf_bytes:
                st.download_button("Download PDF Report", pdf_bytes, file_name="security_audit.pdf", mime="application/pdf", use_container_width=True)

            if st.button("🛠️ Review Security Patches", type="primary", use_container_width=True, key="goto_patches_btn"):
                AppState.set_page("🛠️ Patch Review")
                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    # Analysis Results in Main Column
    if results := st.session_state.get("analysis_results"):
        llm_analysis = results.get("llm_analysis", "")
        semgrep_results = results.get("semgrep_results", {})
        findings = semgrep_results.get("results", [])

        if llm_analysis:
            st.markdown('<div class="analysis-container">', unsafe_allow_html=True)
            st.markdown('<div class="analysis-title">🛡️ AI Security Analysis</div>', unsafe_allow_html=True)
            st.markdown(llm_analysis)
            st.markdown('</div>', unsafe_allow_html=True)

        if findings:
            st.markdown(f'<div class="scanner-panel" style="margin-top: 1.5rem;"><div class="scanner-panel-header"><div class="scanner-panel-title">findings</div><div class="scanner-file-label" style="color: #ff4060;">{len(findings)} vulnerabilities identified</div></div></div>', unsafe_allow_html=True)
            for finding in findings:
                severity = (finding.get("severity", "low") or "low").lower()
                label = finding.get("check_id", "Unknown Issue")
                message = finding.get("extra", {}).get("message", "No description available.")
                location = f"{finding.get('path', 'unknown')} · line {finding.get('start', {}).get('line', 'N/A')} · CWE {finding.get('extra', {}).get('cwe', 'N/A')}"
                title = label
                description = message
                badge_style = {
                    'high': 'severity-high',
                    'medium': 'severity-med',
                    'low': 'severity-low',
                }.get(severity, 'severity-low')

                with st.expander(f"{title} — {location}"):
                    st.markdown(
                        f'<div class="finding-card"><div class="finding-header"><div><p class="finding-title">{title}</p><p style="margin:0; color:#8b909e;">{location}</p></div><span class="severity-badge {badge_style}">{severity.upper()}</span></div><p style="color:#cbd5e1; margin-bottom:0.85rem;">{description}</p><pre style="color:#e8eaf0; background: #0f172a; border-radius: 10px; padding: 0.85rem; overflow:auto;">{finding.get('extra', {}).get('lines', '')}</pre></div>',
                        unsafe_allow_html=True,
                    )
    return None

    return None
