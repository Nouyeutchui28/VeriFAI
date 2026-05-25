import os
import json
import subprocess
import streamlit as st
from datetime import datetime
import asyncio
import threading

from ..core.llm import initialize_llm
from ..core.security import analyze_security, generate_patch_suggestions, run_semgrep_scan, run_llm_analysis
from ..core.file_utils import save_uploaded_file, generate_report, save_code_to_temp_file, extract_zip, apply_patch, extract_primary_code_sample
from .api_client import get_api_client

def render_scanner_tab_with_api(scan_target_type, uploaded_file=None, uploaded_files=None,
                               code_input=None, metrics_enabled=True, custom_config=None,
                               llm_temperature=0, model_selection="deepseek-r1-distill-llama-70b"):
    """Render scanner tab with backend API integration."""

    if not st.session_state.get("user_id"):
        st.warning("⚠️ Please log in first to submit scans")
        return {}

    col1, col2 = st.columns([2, 3])

    code_content = ""
    target_path = None

    with col1:
        st.subheader("Code Preview")

        if scan_target_type == "📝 Direct Code Input":
            code_content = code_input or ""
            st.code(code_content if code_content else "# Paste code here")
            if code_content:
                target_path = save_code_to_temp_file(code_content)

        elif scan_target_type == "📤 Upload File" and uploaded_file:
            try:
                code_content = uploaded_file.getvalue().decode("utf-8")
                st.code(code_content)
                target_path = save_uploaded_file(uploaded_file)
            except Exception as e:
                st.error(f"Error reading file: {e}")

        elif scan_target_type == "📤 Upload Multiple Files" and uploaded_files:
            st.info(f"Selected {len(uploaded_files)} files")
            if uploaded_files:
                selected_file = st.selectbox("Select file to preview:", [file.name for file in uploaded_files])
                for file in uploaded_files:
                    if file.name == selected_file:
                        try:
                            code_content = file.getvalue().decode("utf-8")
                            st.code(code_content)
                            break
                        except Exception as e:
                            st.error(f"Error reading file {file.name}: {str(e)}")

            folder_path = os.path.join("temp_uploads", f"upload_folder_{datetime.now().strftime('%Y%m%d%H%M%S')}")
            os.makedirs(folder_path, exist_ok=True)
            for file in uploaded_files:
                file_path = os.path.join(folder_path, file.name)
                with open(file_path, "wb") as f:
                    f.write(file.getvalue())
            target_path = folder_path

        elif scan_target_type == "📦 Upload ZIP" and uploaded_file:
            st.info("Uploaded ZIP file will be extracted and scanned")
            try:
                target_path = extract_zip(uploaded_file)
                sample_files = []
                for root, dirs, files in os.walk(target_path):
                    for fn in files[:5]:
                        sample_files.append(os.path.relpath(os.path.join(root, fn), target_path))
                    if len(sample_files) >= 5:
                        break
                if sample_files:
                    st.markdown("**Files inside ZIP (sample):**")
                    for fn in sample_files:
                        st.write(fn)
                    if sample_files:
                        try:
                            with open(os.path.join(target_path, sample_files[0]), 'r', encoding='utf-8', errors='ignore') as f:
                                code_content = f.read()
                                st.code(code_content)
                        except Exception as e:
                            pass
            except Exception as e:
                st.error(f"Failed to process ZIP: {str(e)}")

    prev = st.session_state.get('analysis_results', {}) or {}
    existing_patch = prev.get('patch_suggestions', '')
    existing_target = prev.get('target_path', None)

    with col2:
        st.subheader("Analysis Results")
        result_tabs = st.tabs(["LLM Analysis", "Semgrep Results", "Patch Suggestions"])

        # Run analysis button
        if st.button("🔍 Run Security Scan"):
            if not target_path:
                st.error("❌ No code to scan")
                return {}

            try:
                api_client = get_api_client()

                # Submit scan to backend
                st.info("📤 Submitting scan to backend...")
                scan_response = api_client.submit_scan(
                    project_name="Direct Upload",
                    repo_url=None
                )

                if "error" in scan_response:
                    st.error(f"❌ Failed to submit scan: {scan_response['error']}")
                    return {}

                scan_id = scan_response.get("id")
                st.success(f"✅ Scan submitted: {scan_id}")

                # Run local analysis
                st.info("📋 Running Semgrep...")
                semgrep_results = run_semgrep_scan(target_path, metrics_enabled)

                patch_file_path = ""
                if target_path:
                    _, patch_file_path = extract_primary_code_sample(target_path)
                    patch_file_path = patch_file_path or os.path.basename(target_path)

                st.info("📋 Running LLM analysis...")
                llm_analysis = run_llm_analysis(code_content, semgrep_results, llm_temperature, model_selection)

                st.info("📋 Generating patches...")
                try:
                    patch_suggestions = generate_patch_suggestions(semgrep_results, code_content[:3000],
                                                                 initialize_llm(model=model_selection, temperature=llm_temperature),
                                                                 file_path=patch_file_path or os.path.basename(target_path))
                except:
                    patch_suggestions = ""

                report = generate_report(code_content, llm_analysis)

                # Save results to backend
                st.info("💾 Saving results to backend...")
                results_response = api_client.save_results(
                    scan_id=scan_id,
                    code_snippet=code_content[:3000],
                    semgrep_json=semgrep_results,
                    llm_analysis=llm_analysis,
                    patches=patch_suggestions
                )

                # Update scan status
                api_client.update_scan_status(scan_id, "complete")

                results = {
                    'code_content': code_content,
                    'llm_analysis': llm_analysis,
                    'semgrep_results': semgrep_results,
                    'report': report,
                    'patch_suggestions': patch_suggestions,
                    'target_path': target_path,
                    'scan_id': scan_id
                }
                st.session_state.analysis_results = results
                st.success("✅ Analysis complete!")
                return results

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

        # Display existing results
        if existing_patch:
            with result_tabs[2]:
                st.subheader("🔧 Patch Suggestions")
                st.code(existing_patch)
                st.download_button("Download patch file", existing_patch, file_name="patch.diff")
                if existing_target and st.button("✅ Apply patch", key="apply_patch"):
                    result = apply_patch(existing_patch, existing_target, dry_run=False, create_backup=True)
                    if isinstance(result, dict) and result.get("applied"):
                        st.success(f"Patch applied: {result.get('message', 'Success')}")
                    else:
                        msg = result.get("message", "Failed to apply patch") if isinstance(result, dict) else str(result)
                        st.error(f"Patch application failed: {msg}")

    return {
        'code_content': code_content,
        'llm_analysis': "",
        'report': "",
        'patch_suggestions': existing_patch,
        'target_path': existing_target
    }
