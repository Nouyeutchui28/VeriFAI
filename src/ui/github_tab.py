import os
import streamlit as st
from datetime import datetime
import tempfile

from ..core.github_handler import (
    validate_github_url,
    extract_repo_info,
    clone_repository,
    get_repo_size_mb,
    get_file_count,
    get_repo_language_stats,
    cleanup_repo,
)
from ..core.security import analyze_security, generate_patch_suggestions, run_semgrep_scan, run_llm_analysis
from ..core.file_utils import generate_report, apply_patch


def get_code_samples_from_repo(repo_path, max_files=5, max_size=5000):
    """Extract code samples from repository for analysis."""
    code_samples = []
    file_count = 0

    code_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go', '.kt', '.rs']

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', '.git']]

        for file in files:
            if file_count >= max_files:
                break

            file_path = os.path.join(root, file)
            _, ext = os.path.splitext(file)

            if ext.lower() in code_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if content.strip():
                            rel_path = os.path.relpath(file_path, repo_path)
                            code_samples.append({
                                'path': rel_path,
                                'content': content[:max_size],
                                'size': len(content)
                            })
                            file_count += 1
                except:
                    pass

        if file_count >= max_files:
            break

    return code_samples


def render_github_tab(metrics_enabled=False, custom_config=None,
                     llm_temperature=0, model_selection="deepseek-r1-distill-llama-70b"):
    """Render the dedicated repository analysis tab."""

    st.header(":material/folder: Project Repository Explorer")
    st.markdown("Load and explore remote code repositories directly within the platform.")

    # Repository URL input
    col1, col2 = st.columns([3, 1])
    with col1:
        github_url = st.text_input(
            "Remote Git Repository URL",
            placeholder="https://github.com/user/repository",
            help="Enter a public Git repository URL (e.g., GitHub, GitLab)"
        )

    with col2:
        clone_button = st.button(":material/download: Load Repository", key="github_clone")

    # Initialize session state for GitHub
    if "github_repo_path" not in st.session_state:
        st.session_state.github_repo_path = None
    if "github_repo_url" not in st.session_state:
        st.session_state.github_repo_url = None

    # Handle cloning
    if clone_button:
        if not github_url.strip():
            st.error(":material/error: Please enter a repository URL")
        elif not validate_github_url(github_url):
            st.error(":material/error: Please enter a valid Git repository URL.")
        else:
            with st.spinner(":material/sync: Loading repository..."):
                try:
                    temp_dir = os.path.join("temp_github", f"repo_{datetime.now().strftime('%Y%m%d%H%M%S')}")
                    os.makedirs(temp_dir, exist_ok=True)

                    repo_path = clone_repository(github_url, temp_dir)
                    st.session_state.github_repo_path = repo_path
                    st.session_state.github_repo_url = github_url

                    st.success(":material/check_circle: Repository cloned successfully!")
                    st.rerun()
                except TimeoutError:
                    st.error(":material/error: Clone operation timed out. Repository might be too large.")
                except RuntimeError as e:
                    st.error(f":material/error: Clone failed: {str(e)}")
                except Exception as e:
                    st.error(f":material/error: Unexpected error: {str(e)}")

    # Display repository info and analysis interface
    if st.session_state.github_repo_path:
        repo_path = st.session_state.github_repo_path

        st.markdown("---")

        # Repository information
        col_info1, col_info2, col_info3 = st.columns(3)

        try:
            repo_size_mb = get_repo_size_mb(repo_path)
            file_count = get_file_count(repo_path)
            language_stats = get_repo_language_stats(repo_path)

            with col_info1:
                st.metric("Repository Size", f"{repo_size_mb:.2f} MB")

            with col_info2:
                st.metric("Total Files", file_count)

            with col_info3:
                if language_stats:
                    top_lang = max(language_stats, key=language_stats.get)
                    st.metric("Primary Language", top_lang)

            # Language breakdown
            if language_stats:
                st.subheader(":material/analytics: Language Distribution")
                sorted_stats = dict(sorted(language_stats.items(), key=lambda x: x[1], reverse=True)[:10])
                st.bar_chart(sorted_stats)

        except Exception as e:
            st.warning(f"Could not retrieve repository statistics: {str(e)}")

        st.markdown("---")

        # Analysis section
        st.subheader(":material/search: Security Analysis")

        col_left, col_right = st.columns([2, 3])

        with col_left:
            st.info(":material/info: Repository is ready for analysis. Click the button to run security scan.")

            if st.button(":material/security: Run Security Scan", key="github_scan"):
                try:
                    from concurrent.futures import ThreadPoolExecutor, as_completed
                    from ..core.security import unified_security_scan, resolve_local_dependencies
                    from .api_client import get_api_client
                    import uuid

                    progress_placeholder = st.empty()
                    status_placeholder = st.empty()

                    with status_placeholder.status(":material/search: Initializing Repository Scan...", expanded=True) as status:
                        # Step 1: Semgrep Static Analysis
                        status.update(label=":material/rocket_launch: Running Semgrep Static Analysis... (Step 1/4)", state="running")
                        progress_placeholder.progress(0.1, text="Analyzing repository patterns with Semgrep...")
                        semgrep_results = run_semgrep_scan(repo_path, metrics_enabled)
                        findings = semgrep_results.get("results", [])

                        # Step 2: Parallel AI Analysis & Patching
                        status.update(label=":material/smart_toy: Running AI Security Analysis... (Step 2/4)", state="running")
                        progress_placeholder.progress(0.3, text="Initializing AI engine for deep repository review...")
                        
                        # Identify all unique flagged files
                        flagged_files = list(set([f.get("path") for f in findings if f.get("path")]))
                        
                        # HEURISTIC: If no findings, at least analyze the first primary file
                        if not flagged_files:
                            from ..core.file_utils import extract_primary_code_sample
                            _, primary_rel = extract_primary_code_sample(repo_path)
                            if primary_rel:
                                flagged_files = [primary_rel]
                        
                        # Limit to top 15 files for performance
                        flagged_files = flagged_files[:15]
                        
                        all_llm_analyses = []
                        all_patches = []
                        primary_code_content = ""

                        def process_repo_file(file_rel_path):
                            full_path = os.path.join(repo_path, file_rel_path)
                            if not os.path.exists(full_path):
                                return None, None, None
                            
                            try:
                                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                                    file_code = f.read(8000)
                                
                                # Resolve dependencies
                                context_files = {}
                                deps = resolve_local_dependencies(file_code, repo_path)
                                for d_rel, d_full in deps:
                                    try:
                                        with open(d_full, "r", encoding="utf-8", errors="ignore") as df:
                                            context_files[d_rel] = df.read(2000)
                                    except: pass
                                
                                analysis, patch = unified_security_scan(semgrep_results, file_code, None, file_path=file_rel_path, context_files=context_files)
                                return analysis, patch, file_code
                            except Exception as e:
                                return None, None, None

                        with ThreadPoolExecutor(max_workers=3) as executor:
                            future_to_file = {executor.submit(process_repo_file, f): f for f in flagged_files}
                            completed_count = 0
                            for future in as_completed(future_to_file):
                                fname = future_to_file[future]
                                try:
                                    analysis, patch, fcode = future.result()
                                    if analysis:
                                        all_llm_analyses.append(f"### :material/description: File: {fname}\n{analysis}")
                                    if patch and patch != "No patch suggestions.":
                                        all_patches.append(patch)
                                    if not primary_code_content and fcode:
                                        primary_code_content = fcode
                                except: pass
                                
                                completed_count += 1
                                progress_placeholder.progress(0.3 + (0.4 * (completed_count / len(flagged_files))), 
                                                           text=f"Analyzing: {completed_count}/{len(flagged_files)} vulnerable files...")

                        combined_analysis = "\n\n---\n\n".join(all_llm_analyses) or ":material/warning: No vulnerabilities found in AI deep-scan. Review Semgrep results."
                        combined_patch = "\n\n".join(all_patches) or "No patch suggestions."

                        # Step 3: Build & Save
                        status.update(label=":material/description: Building Security Report... (Step 3/4)", state="running")
                        progress_placeholder.progress(0.8, text="Finalizing report and persisting results...")
                        
                        report = generate_report(f"GitHub: {st.session_state.github_repo_url}", combined_analysis)
                        
                        # Persist to Backend
                        api_client = get_api_client()
                        
                        proj_name = f"GitHub: {extract_repo_info(st.session_state.github_repo_url)[1]}"
                        save_scan_resp = api_client.submit_scan(project_name=proj_name, repo_url=st.session_state.github_repo_url)
                        
                        if isinstance(save_scan_resp, dict) and "error" in save_scan_resp:
                            logger.warning(f"Scan save failed: {save_scan_resp['error']}")
                            sc_id = str(uuid.uuid4())
                        else:
                            sc_id = save_scan_resp.get("id", str(uuid.uuid4()))
                            api_client.update_scan_status(
                                sc_id, 
                                status="complete", 
                                file_count=len(flagged_files),
                                primary_language="python"
                            )
                        
                        sev_c = {}
                        for r in findings:
                            s = r.get("severity", "unknown").lower()
                            sev_c[s] = sev_c.get(s, 0) + 1
                        
                        save_res_resp = api_client.save_results(
                            scan_id=sc_id,
                            code_snippet=primary_code_content[:2000],
                            semgrep_json=semgrep_results,
                            llm_analysis=combined_analysis,
                            patches=combined_patch,
                            severity_count=sev_c,
                        )
                        
                        if isinstance(save_res_resp, dict) and "error" in save_res_resp:
                            logger.warning(f"Result save failed: {save_res_resp['error']}")
                            
                        result_id = save_res_resp.get("id", str(uuid.uuid4())) if isinstance(save_res_resp, dict) else str(uuid.uuid4())

                        # Step 4: Finalize
                        st.session_state.analysis_results = {
                            "result_id": result_id,
                            "code_content": primary_code_content,
                            "llm_analysis": combined_analysis,
                            "semgrep_results": semgrep_results,
                            "report": report,
                            "patch_suggestions": combined_patch,
                            "target_path": repo_path,
                            "patch_file_path": flagged_files[0] if flagged_files else "",
                            "severity_count": sev_c
                        }
                        
                        progress_placeholder.progress(1.0, text="Scan complete!")
                        status.update(label=":material/check_circle: Repository Analysis Complete!", state="complete", expanded=False)

                    st.success(":material/check_circle: Analysis complete! Results are ready.")
                    st.balloons()
                    st.rerun()

                except Exception as e:
                    st.error(f":material/error: Analysis error: {str(e)}")
                    import traceback
                    st.error(traceback.format_exc())

            if st.button(":material/delete: Clean Up Repository", key="github_cleanup"):
                try:
                    if cleanup_repo(repo_path):
                        st.session_state.github_repo_path = None
                        st.session_state.github_repo_url = None
                        st.success(":material/check_circle: Repository cleaned up successfully!")
                        st.rerun()
                    else:
                        st.warning(":material/warning: Could not fully clean up repository")
                except Exception as e:
                    st.error(f":material/error: Cleanup error: {str(e)}")

        # Display analysis results
        with col_right:
            prev = st.session_state.get('analysis_results', {}) or {}

            if prev:
                st.subheader("Results")
                result_tabs = st.tabs(["LLM Analysis", "Semgrep Results", "Patch Suggestions"])

                with result_tabs[0]:
                    if prev.get('llm_analysis'):
                        st.markdown(prev['llm_analysis'])
                    else:
                        st.info("No LLM analysis yet. Run security scan to generate.")

                with result_tabs[1]:
                    if prev.get('semgrep_results'):
                        st.json(prev['semgrep_results'])
                    else:
                        st.info("No Semgrep results yet. Run security scan to generate.")

                with result_tabs[2]:
                    if prev.get('patch_suggestions'):
                        st.code(prev['patch_suggestions'], language="diff")
                        st.download_button(
                            ":material/download: Download Patch",
                            prev['patch_suggestions'],
                            file_name="github_repo.patch"
                        )
                    else:
                        st.info("No patches generated yet. Patches are created when Semgrep finds vulnerabilities.")
            else:
                st.info(":material/lightbulb: Run security scan to view analysis results here")
