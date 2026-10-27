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
    )


def _has_code_input(paste_code, uploaded_file, zip_file):
    if uploaded_file is not None:
        return True
    if zip_file is not None:
        return True
    if paste_code and paste_code.strip():
        return True
    return False


def _active_input_mode(paste_code, uploaded_file, zip_file):
    if zip_file is not None:
        return "ZIP"
    if uploaded_file is not None:
        if uploaded_file.name.lower().endswith(".zip"):
            return "ZIP"
        return "Upload"
    if paste_code and paste_code.strip():
        return "Paste"
    return "None"


def _format_file_label(mode, uploaded_file, zip_file, paste_code):
    if mode == "Upload" and uploaded_file:
        size = getattr(uploaded_file, 'size', len(uploaded_file.getvalue()))
        return f"{uploaded_file.name} · {size:,} bytes"
    if mode == "ZIP":
        if zip_file:
            size = getattr(zip_file, 'size', len(zip_file.getvalue()))
            return f"{zip_file.name} · {size:,} bytes (ZIP Archive)"
        if uploaded_file and uploaded_file.name.lower().endswith(".zip"):
            size = getattr(uploaded_file, 'size', len(uploaded_file.getvalue()))
            return f"{uploaded_file.name} · {size:,} bytes (ZIP Archive)"
    if mode == "Paste" and paste_code.strip():
        lines = len(paste_code.splitlines())
        return f"Code Snippet · {lines} lines · {len(paste_code):,} chars"
    return "No code loaded"


def _resolve_patch_target(target_path):
    """Return the directory that patch application should use."""
    if not target_path:
        return None
    if os.path.isdir(target_path):
        return target_path
    return os.path.dirname(target_path) or "."


def _resolve_target_path(mode, paste_code, uploaded_file, zip_file):
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
        "done": "<svg width='10' height='10' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='4' stroke-linecap='round' stroke-linejoin='round' style='vertical-align: middle; display: inline-block;'><polyline points='20 6 9 17 4 12'></polyline></svg>",
        "running": "<span style='display: inline-block; width: 8px; height: 8px; border-radius: 50%; background-color: currentColor; vertical-align: middle;'></span>",
        "error": "<svg width='10' height='10' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='4' stroke-linecap='round' stroke-linejoin='round' style='vertical-align: middle; display: inline-block;'><line x1='18' y1='6' x2='6' y2='18'></line><line x1='6' y1='6' x2='18' y2='18'></line></svg>",
        "idle": "<span style='display: inline-block; width: 6px; height: 6px; border-radius: 50%; border: 1.5px solid currentColor; vertical-align: middle;'></span>",
    }
    return f"<span style='color: {colors[status]};'>{icons[status]}</span>"


def _execute_scan(target_path, code_content, actual_filename, patch_file_path=""):
    """Execute a comprehensive security scan with parallel AI analysis."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from ..core.security import unified_security_scan
    
    if not target_path or not os.path.exists(target_path):
        st.error(":material/error: Error: Target path does not exist.")
        return

    # Check for Python language
    is_python = False
    if os.path.isdir(target_path):
        for root, dirs, files in os.walk(target_path):
            if any(f.endswith('.py') for f in files):
                is_python = True
                break
    else:
        if (target_path.endswith('.py') or 
            (actual_filename and actual_filename.endswith('.py')) or 
            (patch_file_path and patch_file_path.endswith('.py'))):
            is_python = True

    if not is_python:
        st.error(":material/error: this is not a python code")
        return
    
    st.session_state.analysis_results = None
    st.session_state.scan_running = True
    st.session_state.scan_error = False
    st.session_state.scan_step = 1
    st.session_state.run_scan_request = False

    progress_placeholder = st.empty()
    status_placeholder = st.empty()

    with status_placeholder.status(":material/search: Initializing Security Scan...", expanded=True) as status:
        try:
            # Step 1: Semgrep Static Analysis
            status.update(label=":material/rocket_launch: Running Semgrep Static Analysis... (Step 1/3)", state="running")
            progress_placeholder.progress(0.1, text="Analyzing code patterns with Semgrep...")
            sem_res = run_semgrep_scan(target_path, True)
            findings = sem_res.get("results", [])
            
            # Step 2: Local AI Analysis & Patching
            status.update(label=":material/smart_toy: Running Local AI Analysis... (Step 2/3)", state="running")
            progress_placeholder.progress(0.4, text="Initializing Local AI engine for analysis...")
            
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
            
            # Limit parallel scans to top 3 vulnerable/critical files for speed + 8GB RAM safety
            flagged_files = flagged_files[:3]
            
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
                        file_code = f.read(4000)
                    
                    # Agentic Feature: Resolve local context dependencies
                    from ..core.security import resolve_local_dependencies
                    context_files = {}
                    if os.path.isdir(target_path):
                        deps = resolve_local_dependencies(file_code, target_path)
                        for d_rel, d_full in deps:
                            try:
                                with open(d_full, "r", encoding="utf-8", errors="ignore") as df:
                                    context_files[d_rel] = df.read(1500)
                            except: pass
                    
                    return unified_security_scan(sem_res, file_code, llm, file_path=file_rel_path, context_files=context_files)
                except Exception as e:
                    logger.error(f"Error in task for {file_rel_path}: {e}")
                    return None, None

            # Run sequentially (max_workers=1) to prevent Ollama GPU/CPU RAM thrashing on 8GB RAM
            with ThreadPoolExecutor(max_workers=1) as executor:
                future_to_file = {executor.submit(process_file_task, f): f for f in flagged_files}
                completed_count = 0
                for future in as_completed(future_to_file):
                    fname = future_to_file[future]
                    try:
                        analysis, patch = future.result()
                        if analysis: 
                            all_llm_analyses.append(f"### :material/description: File: {fname}\n{analysis}")
                        if patch and patch != "No patch suggestions.": 
                            all_patches.append(patch)
                    except Exception as e:
                        logger.error(f"Task failed for {fname}: {e}")
                    
                    completed_count += 1
                    progress_placeholder.progress(
                        0.4 + (0.4 * (completed_count / len(flagged_files))), 
                        text=f"AI Expert Analysis: {completed_count}/{len(flagged_files)} files..."
                    )
            
            # Engage MultiAgentOrchestrator (Zetaris Data Fabric + Meterless Nightshift + H-MEM) if patches needed
            if findings and not all_patches:
                try:
                    from ..core.multi_agent.orchestrator import MultiAgentOrchestrator
                    status.update(label=":material/smart_toy: Running 3-Agent Collaborative Remediation (Zetaris / Nightshift / H-MEM)...", state="running")
                    orchestrator = MultiAgentOrchestrator(max_critique_rounds=2)
                    target_to_remediate = target_path if os.path.isfile(target_path) else (os.path.join(target_path, flagged_files[0]) if flagged_files else target_path)
                    if os.path.exists(target_to_remediate):
                        for event in orchestrator.run_remediation_pipeline(target_to_remediate, findings):
                            if event.get("type") == "patch_generated" and event.get("diff"):
                                all_patches.append(event.get("diff"))
                except Exception as ex:
                    logger.warning(f"Multi-agent orchestrator fallback failed: {ex}")

            combined_analysis = "\n\n---\n\n".join(all_llm_analyses) or ":material/warning: No vulnerabilities found in AI deep-scan. Review Semgrep results."
            combined_patch = "\n\n".join(all_patches) or "No patch suggestions."
            
            # Ensure code_content is populated for single files if it was empty
            if not code_content and not os.path.isdir(target_path):
                try:
                    with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
                        code_content = f.read(5000)
                except: pass
            
            # Step 3: Build & Save
            status.update(label=":material/description: Building Security Report... (Step 3/3)", state="running")
            progress_placeholder.progress(0.9, text="Finalizing report and saving results...")
            
            report = generate_report(code_content, sem_res, combined_analysis)
            
            # Backend Persistence
            result_id = str(uuid.uuid4())
            try:
                from .api_client import get_api_client
                api_client = get_api_client()
                
                # Use FastAPI endpoint instead of InsForge
                save_scan_resp = api_client.submit_scan(project_name=actual_filename, repo_url=None)
                
                if isinstance(save_scan_resp, dict) and "error" in save_scan_resp:
                    logger.warning(f"Scan save failed: {save_scan_resp['error']}")
                    sc_id = str(uuid.uuid4()) # fallback
                else:
                    sc_id = save_scan_resp.get("id", str(uuid.uuid4()))
                    # Update status to complete
                    api_client.update_scan_status(
                        sc_id, 
                        status="complete", 
                        file_count=1,
                        primary_language="python"
                    )

                sev_c = {}
                for r in findings:
                    s = r.get("severity", "unknown").lower()
                    sev_c[s] = sev_c.get(s, 0) + 1

                save_res_resp = api_client.save_results(
                    scan_id=sc_id,
                    code_snippet=code_content[:2000],
                    semgrep_json=sem_res,
                    llm_analysis=combined_analysis,
                    patches=combined_patch,
                    severity_count=sev_c,
                )
                
                if isinstance(save_res_resp, dict) and "error" in save_res_resp:
                    logger.warning(f"Result save failed: {save_res_resp['error']}")
                    
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
            status.update(label=":material/check_circle: Security Scan Complete!", state="complete", expanded=False)
            
            # Verification Success Message
            if st.session_state.get("patch_verified") and not findings:
                st.success(":material/celebration: Verification successful: no owaps top 10 vulnerability detected.")
                st.session_state.patch_verified = False # Reset flag after successful pass

        except Exception as e:
            st.session_state.scan_error = True
            status.update(label=":material/error: Analysis Failed", state="error")
            st.error(f":material/error: Analysis failed: {str(e)}")
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

    paste_code, uploaded_file, zip_file = _get_scanner_input_state()
    mode = _active_input_mode(paste_code, uploaded_file, zip_file)
    has_code = _has_code_input(paste_code, uploaded_file, zip_file)
    file_label = _format_file_label(mode, uploaded_file, zip_file, paste_code)

    # Strictly enforce: when no code is uploaded, no scan action can be performed
    if st.session_state.get("run_scan_request", False) and not st.session_state.get("scan_running", False):
        if not has_code:
            st.session_state.run_scan_request = False
            st.warning("⚠️ No code provided. Please upload a file, upload a ZIP archive, or paste code before scanning.")
        else:
            target_path, actual_filename, code_content, patch_file_path = _resolve_target_path(mode, paste_code, uploaded_file, zip_file)
            if target_path is None:
                st.error("Unable to process uploaded code. Please re-upload your file.")
                st.session_state.run_scan_request = False
            else:
                _execute_scan(target_path, code_content, actual_filename, patch_file_path)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<div class="scanner-panel">', unsafe_allow_html=True)
        st.markdown(
            f'''<div class="scanner-panel-header">
                <div class="scanner-panel-title">Uploaded Code Input</div>
                <div class="scanner-file-label" style="color: {'#00e5a0' if has_code else '#8b909e'}; font-weight: {'600' if has_code else '400'};">
                    {'● ' if has_code else ''}{file_label}
                </div>
            </div>''',
            unsafe_allow_html=True,
        )

        tabs = st.tabs([":material/upload_file: Single File", ":material/folder_zip: ZIP Archive", ":material/edit_note: Paste Code"])

        with tabs[0]:
            st.file_uploader(
                "Upload a code file",
                type=["py", "txt", "js", "ts", "json", "sh"],
                key="scanner_uploaded_file",
                help="Upload a single Python script or source file to scan."
            )

        with tabs[1]:
            st.file_uploader(
                "Upload a ZIP archive",
                type=["zip"],
                key="scanner_zip_file",
                help="Upload a ZIP archive containing your project codebase."
            )

        with tabs[2]:
            st.text_area(
                "Paste Python code snippet here",
                height=210,
                key="scanner_paste_code",
                placeholder="# Paste your Python code snippet here to scan for vulnerabilities...\n",
                label_visibility="collapsed"
            )

        st.markdown('</div>', unsafe_allow_html=True)

        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if not has_code:
                st.button(
                    "Run Security Scan",
                    type="primary",
                    disabled=True,
                    use_container_width=True,
                    key="scanner_run_disabled",
                    help="Upload a file, ZIP archive, or paste code to enable scanning"
                )
            else:
                if st.button("🚀 Run Security Scan", type="primary", use_container_width=True, key="scanner_run"):
                    st.session_state.run_scan_request = True
                    st.rerun()

        with btn_col2:
            if st.button("Clear / Reset", type="secondary", use_container_width=True, key="scanner_clear"):
                _clear_scanner_state()
                st.rerun()

        if not has_code:
            st.info("ℹ️ **No code uploaded.** Please upload a Python file (.py), a ZIP archive, or paste a code snippet above to perform a security scan.")

    with col2:
        st.markdown('<div class="scanner-panel">', unsafe_allow_html=True)
        st.markdown('<div class="scanner-panel-header"><div class="scanner-panel-title">Workflow Progress</div></div>', unsafe_allow_html=True)

        scan_step = st.session_state.get("scan_step", 0)
        scan_running = st.session_state.get("scan_running", False)
        scan_error = st.session_state.get("scan_error", False)

        steps = [
            ("Semgrep Static Scan", "AST security rules & pattern match"),
            ("AI Vulnerability Review", "Deep risk evaluation & CWE mapping"),
            ("Security Patch Synthesis", "Remediation generation"),
            ("Audit Report Compilation", "PDF audit package creation"),
        ]

        for idx, (title, description) in enumerate(steps, start=1):
            status = _build_step_status(idx, scan_step, scan_running, scan_error)
            st.markdown(
                f'<div class="workflow-step"><span class="step-indicator step-{status}">{idx}</span><div style="flex:1;"><p class="step-label">{title}</p><p class="step-description">{description}</p></div><span class="step-tag">{status}</span></div>',
                unsafe_allow_html=True,
            )

        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.get("analysis_results") and not scan_running:
            st.markdown('<div class="scanner-panel">', unsafe_allow_html=True)
            st.markdown('<div class="scanner-panel-header"><div class="scanner-panel-title">Actions</div></div>', unsafe_allow_html=True)

            result = st.session_state.analysis_results
            code_content = result.get("code_content", "")
            llm_analysis = result.get("llm_analysis", "")
            semgrep_results = result.get("semgrep_results", {})

            pdf_bytes = None
            try:
                pdf_bytes = generate_pdf_report(code_content, llm_analysis, semgrep_results)
            except Exception:
                pdf_bytes = None

            if pdf_bytes:
                st.download_button(
                    "📄 Download PDF Audit Report",
                    pdf_bytes,
                    file_name="security_audit_report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            if st.button("🔧 Review & Apply Patches", type="primary", use_container_width=True, key="goto_patches_btn"):
                AppState.set_page(":material/build: Patch Review")
                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    # Analysis Results in Main Area
    if results := st.session_state.get("analysis_results"):
        llm_analysis = results.get("llm_analysis", "")
        semgrep_results = results.get("semgrep_results", {})
        findings = semgrep_results.get("results", [])

        # Calculate metrics
        high_count = sum(1 for f in findings if (f.get("extra", {}).get("severity") or "").upper() in ["ERROR", "HIGH"])
        med_count = sum(1 for f in findings if (f.get("extra", {}).get("severity") or "").upper() in ["WARNING", "MEDIUM"])
        low_count = sum(1 for f in findings if (f.get("extra", {}).get("severity") or "").upper() in ["INFO", "LOW"])
        score = max(0, 100 - (high_count * 15 + med_count * 5 + low_count * 1))

        score_color = "#00e5a0" if score >= 80 else "#ffaa00" if score >= 50 else "#ff4060"
        grade = "CLEAN / LOW RISK" if score >= 85 else "MODERATE RISK" if score >= 50 else "CRITICAL VULNERABILITIES"

        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #101626 0%, #151d30 100%); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; padding: 1.5rem; margin-top: 1.5rem; margin-bottom: 1.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                    <div>
                        <div style="color: var(--text2); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px;">Security Health Score</div>
                        <div style="font-family: 'Syne', sans-serif; font-size: 2.5rem; font-weight: 800; color: {score_color}; line-height: 1.1; margin-top: 0.25rem;">
                            {score} <span style="font-size: 1rem; color: var(--text2);">/ 100</span>
                        </div>
                        <div style="color: {score_color}; font-size: 0.85rem; font-weight: 600; margin-top: 0.25rem;">{grade}</div>
                    </div>
                    <div style="display: flex; gap: 1.5rem; text-align: center;">
                        <div style="background: rgba(255,64,96,0.1); border: 1px solid rgba(255,64,96,0.25); border-radius: 10px; padding: 0.75rem 1.25rem;">
                            <div style="color: #ff4060; font-size: 1.5rem; font-weight: 800;">{high_count}</div>
                            <div style="color: #8b909e; font-size: 0.75rem; text-transform: uppercase;">High</div>
                        </div>
                        <div style="background: rgba(255,170,0,0.1); border: 1px solid rgba(255,170,0,0.25); border-radius: 10px; padding: 0.75rem 1.25rem;">
                            <div style="color: #ffaa00; font-size: 1.5rem; font-weight: 800;">{med_count}</div>
                            <div style="color: #8b909e; font-size: 0.75rem; text-transform: uppercase;">Medium</div>
                        </div>
                        <div style="background: rgba(0,102,255,0.1); border: 1px solid rgba(0,102,255,0.25); border-radius: 10px; padding: 0.75rem 1.25rem;">
                            <div style="color: #0066ff; font-size: 1.5rem; font-weight: 800;">{low_count}</div>
                            <div style="color: #8b909e; font-size: 0.75rem; text-transform: uppercase;">Low</div>
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        tab_findings, tab_analysis, tab_patch = st.tabs([
            f"🛡️ Security Findings ({len(findings)})",
            "🤖 AI Security Assessment",
            "🔧 Patch & Remediation"
        ])

        with tab_findings:
            if not findings:
                st.success("✅ **Clean scan:** No known security vulnerabilities or policy violations were detected in the uploaded code.")
            else:
                for idx, f in enumerate(findings, start=1):
                    sev = (f.get("extra", {}).get("severity") or "low").upper()
                    sev_class = "severity-high" if sev in ["ERROR", "HIGH"] else "severity-med" if sev in ["WARNING", "MEDIUM"] else "severity-low"
                    sev_label = "HIGH" if sev in ["ERROR", "HIGH"] else "MEDIUM" if sev in ["WARNING", "MEDIUM"] else "LOW"
                    check_id = f.get("check_id", "General Vulnerability")
                    file_path = f.get("path", "source")
                    line_no = f.get("start", {}).get("line", "N/A")
                    msg = f.get("extra", {}).get("message", "No description provided.")
                    code_snippet = f.get("extra", {}).get("lines", "")
                    cwe = f.get("extra", {}).get("metadata", {}).get("cwe")
                    cwe_str = f" · {cwe}" if cwe else ""

                    with st.expander(f"[{sev_label}] #{idx}: {check_id} (Line {line_no})", expanded=(idx <= 3)):
                        st.markdown(f"""
                            <div style="display: flex; gap: 0.5rem; align-items: center; margin-bottom: 0.5rem;">
                                <span class="severity-badge {sev_class}">{sev_label}</span>
                                <span style="color: var(--text2); font-size: 0.85rem;">File: <code>{file_path}</code> · Line {line_no}{cwe_str}</span>
                            </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f"**Description:** {msg}")
                        if code_snippet:
                            st.code(code_snippet, language="python")

        with tab_analysis:
            if llm_analysis:
                st.markdown('<div class="analysis-container">', unsafe_allow_html=True)
                st.markdown('<div class="analysis-title">:material/shield: AI Security Assessment & Remediation</div>', unsafe_allow_html=True)
                st.markdown(llm_analysis)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No AI Security Assessment available for this scan.")

        with tab_patch:
            patch_text = results.get("patch_suggestions", "")
            code_content = results.get("code_content", "")
            patch_target = _resolve_patch_target(results.get("target_path", ""))

            if patch_text and patch_text.strip() and patch_text != "No patch suggestions.":
                patched_code = extract_patched_code(code_content, patch_text) if code_content else None
                try:
                    render_patch_review_panel(
                        patch_text=patch_text,
                        original_code=code_content,
                        patched_code=patched_code,
                        target_path=results.get("target_path", ""),
                        patch_root=patch_target,
                        patch_file_path=results.get("patch_file_path", ""),
                    )
                except Exception as e:
                    st.error(f":material/warning: Unable to render interactive patch review panel: {e}")
                    with st.expander("View Raw Patch Diff"):
                        st.code(patch_text, language="diff")
            else:
                st.info("No patch suggestions available for this scan.")

    return None
