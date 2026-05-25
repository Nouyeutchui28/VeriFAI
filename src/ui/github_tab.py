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
from ..core.llm import initialize_llm
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

    st.header("📦 Project Repository Explorer")
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
        clone_button = st.button("📥 Load Repository", key="github_clone")

    # Initialize session state for GitHub
    if "github_repo_path" not in st.session_state:
        st.session_state.github_repo_path = None
    if "github_repo_url" not in st.session_state:
        st.session_state.github_repo_url = None

    # Handle cloning
    if clone_button:
        if not github_url.strip():
            st.error("❌ Please enter a repository URL")
        elif not validate_github_url(github_url):
            st.error("❌ Please enter a valid Git repository URL.")
        else:
            with st.spinner("🔄 Loading repository..."):
                try:
                    temp_dir = os.path.join("temp_github", f"repo_{datetime.now().strftime('%Y%m%d%H%M%S')}")
                    os.makedirs(temp_dir, exist_ok=True)

                    repo_path = clone_repository(github_url, temp_dir)
                    st.session_state.github_repo_path = repo_path
                    st.session_state.github_repo_url = github_url

                    st.success("✅ Repository cloned successfully!")
                    st.rerun()
                except TimeoutError:
                    st.error("❌ Clone operation timed out. Repository might be too large.")
                except RuntimeError as e:
                    st.error(f"❌ Clone failed: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")

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
                st.subheader("📊 Language Distribution")
                sorted_stats = dict(sorted(language_stats.items(), key=lambda x: x[1], reverse=True)[:10])
                st.bar_chart(sorted_stats)

        except Exception as e:
            st.warning(f"Could not retrieve repository statistics: {str(e)}")

        st.markdown("---")

        # Analysis section
        st.subheader("🔍 Security Analysis")

        col_left, col_right = st.columns([2, 3])

        with col_left:
            st.info("ℹ️ Repository is ready for analysis. Click the button to run security scan.")

            if st.button("🔐 Run Security Scan", key="github_scan"):
                try:
                    progress_placeholder = st.empty()
                    status_placeholder = st.empty()

                    with status_placeholder.status("🔍 Initializing Repository Scan...", expanded=True) as status:
                        # Step 1: Semgrep
                        status.update(label="🚀 Running Semgrep Static Analysis... (Step 1/5)", state="running")
                        progress_placeholder.progress(0.1, text="Analyzing repository patterns with Semgrep...")
                        semgrep_results = run_semgrep_scan(repo_path, metrics_enabled)

                        # Step 2: Code Extraction
                        status.update(label="📂 Extracting Code Samples... (Step 2/5)", state="running")
                        progress_placeholder.progress(0.3, text="Gathering code for AI review...")
                        code_samples = get_code_samples_from_repo(repo_path)
                        code_content = "\n\n".join([
                            f"File: {sample['path']}\n```\n{sample['content']}\n```"
                            for sample in code_samples
                        ])
                        patch_file_path = code_samples[0]['path'] if code_samples else os.path.basename(repo_path)

                        if not code_content:
                            code_content = "Repository analyzed but no readable code files found."

                        # Step 3: LLM Analysis
                        status.update(label="🤖 Running AI Security Analysis (Local)... (Step 3/5)", state="running")
                        progress_placeholder.progress(0.5, text="Leveraging Local AI for deep vulnerability review...")
                        llm_analysis = run_llm_analysis(
                            code_content,
                            semgrep_results,
                            llm_temperature,
                            model_selection
                        )

                        # Step 4: Patch Generation
                        status.update(label="🛠️ Generating Patch Suggestions... (Step 4/5)", state="running")
                        progress_placeholder.progress(0.7, text="Creating remediation patches...")
                        try:
                            patch_suggestions = generate_patch_suggestions(
                                semgrep_results,
                                code_content[:3000],
                                initialize_llm(model=model_selection, temperature=llm_temperature),
                                file_path=patch_file_path
                            )
                        except:
                            patch_suggestions = ""

                        # Step 5: Report & Persist
                        status.update(label="💾 Finalizing & Saving Results... (Step 5/5)", state="running")
                        progress_placeholder.progress(0.9, text="Generating report and persisting results...")
                        report = generate_report(
                            f"GitHub Repository: {st.session_state.github_repo_url}",
                            llm_analysis
                        )
                        
                        # Persist to Backend
                        from .api_client import get_api_client
                        import uuid
                        api_client = get_api_client()
                        sc_id = str(uuid.uuid4())
                        api_client.save_scan_insforge({
                            "id": sc_id, 
                            "user_id": st.session_state.user_info.get("id"), 
                            "status": "complete", 
                            "project_name": f"GitHub: {extract_repo_info(st.session_state.github_repo_url)['name']}", 
                            "start_time": datetime.now().isoformat(), 
                            "end_time": datetime.now().isoformat()
                        })
                        
                        sev_c = {}
                        if "results" in semgrep_results:
                            for r in semgrep_results["results"]:
                                s = r.get("severity", "unknown").lower()
                                sev_c[s] = sev_c.get(s, 0) + 1
                        
                        result_id = str(uuid.uuid4())
                        api_client.save_result_insforge({
                            "id": result_id, 
                            "scan_id": sc_id, 
                            "code_snippet": code_content[:5000], 
                            "semgrep_json": semgrep_results, 
                            "llm_analysis": llm_analysis, 
                            "patches": patch_suggestions, 
                            "severity_count": sev_c
                        })

                        results = {
                            'result_id': result_id,
                            'code_content': code_content,
                            'llm_analysis': llm_analysis,
                            'semgrep_results': semgrep_results,
                            'report': report,
                            'patch_suggestions': patch_suggestions,
                            'target_path': repo_path,
                            'patch_file_path': patch_file_path,
                            'severity_count': sev_c
                        }
                        st.session_state.analysis_results = results
                        
                        progress_placeholder.progress(1.0, text="Scan complete!")
                        status.update(label="✅ Repository Analysis Complete!", state="complete", expanded=False)

                    st.success("✅ Analysis complete and saved to backend!")
                    st.balloons()
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Analysis error: {str(e)}")
                    import traceback
                    st.error(traceback.format_exc())

            if st.button("🗑️ Clean Up Repository", key="github_cleanup"):
                try:
                    if cleanup_repo(repo_path):
                        st.session_state.github_repo_path = None
                        st.session_state.github_repo_url = None
                        st.success("✅ Repository cleaned up successfully!")
                        st.rerun()
                    else:
                        st.warning("⚠️ Could not fully clean up repository")
                except Exception as e:
                    st.error(f"❌ Cleanup error: {str(e)}")

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
                            "📥 Download Patch",
                            prev['patch_suggestions'],
                            file_name="github_repo.patch"
                        )
                    else:
                        st.info("No patches generated yet. Patches are created when Semgrep finds vulnerabilities.")
            else:
                st.info("💡 Run security scan to view analysis results here")
