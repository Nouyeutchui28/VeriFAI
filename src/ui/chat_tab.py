import streamlit as st
from ..core.security import security_chat
from ..utils.state import AppState


def render_chat_tab():
    st.markdown(
        """
        <style>
        .chat-card {
            background: #111827;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 1.25rem;
            margin-bottom: 1.25rem;
        }
        .context-label {
            font-family: 'Syne', sans-serif;
            color: #8b909e;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 1rem;
            display: block;
        }
        .context-chip {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.85rem 1rem;
            background: #0f172a;
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 14px;
            margin-bottom: 0.75rem;
            color: #e8eaf0;
        }
        .chip-badge {
            font-family: 'DM Mono', monospace;
            font-size: 0.75rem;
            color: #8b909e;
            background: rgba(255,255,255,0.05);
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "prefill_prompt" not in st.session_state:
        st.session_state.prefill_prompt = ""
    if "quick_ask_prompt" not in st.session_state:
        st.session_state.quick_ask_prompt = None
    if "last_scan_results" not in st.session_state:
        st.session_state.last_scan_results = None
    if "last_scan_code" not in st.session_state:
        st.session_state.last_scan_code = ""
    if "last_scan_file" not in st.session_state:
        st.session_state.last_scan_file = ""

    code_context = st.session_state.get("last_scan_code", "")
    analysis_context = st.session_state.get("last_scan_results", {}) or {}
    security_analysis = analysis_context.get("llm_analysis", "")
    severity_count = analysis_context.get("severity_count", {})

    if st.session_state.get("patch_generated_from_chat"):
        st.success(":material/celebration: A new security patch was generated from your chat request and loaded into the **Patch Review** section!")
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Go to Patch Review", key="go_to_patch_review_from_notif", type="primary"):
                st.session_state.patch_generated_from_chat = False
                AppState.set_page(":material/build: Patch Review")
                st.rerun()
        with col2:
            if st.button("Dismiss", key="dismiss_patch_notif"):
                st.session_state.patch_generated_from_chat = False
                st.rerun()
        st.markdown("---")

    left, right = st.columns([3, 1])

    with left:
        if st.session_state.chat_history:
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        else:
            st.info("No chat history yet. Start by asking a security question.")

        quick_query = st.session_state.get("quick_ask_prompt")
        if quick_query:
            user_query = quick_query
            st.session_state.quick_ask_prompt = None
        else:
            user_query = st.chat_input("Ask a security-specific question...", key="security_chat_input")

        if user_query:
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            with st.spinner("Analyzing vulnerabilities..."):
                llm = None
                response = security_chat(
                    code_context,
                    security_analysis,
                    st.session_state.chat_history[:-1],
                    user_query,
                    llm,
                )
                
                # Check if the response contains code remediation to extract
                import re
                from src.core.security import _build_unified_diff
                
                # 1. Try extracting ```diff block
                extracted_patch = None
                diff_pattern = r"```diff\s*(.*?)\s*```"
                diff_matches = re.findall(diff_pattern, response, re.DOTALL)
                if diff_matches:
                    for dm in diff_matches:
                        if dm.strip():
                            extracted_patch = dm.strip()
                            break
                            
                # 2. Try extracting ```python block and compute diff against original code
                if not extracted_patch and code_context:
                    py_pattern = r"```(?:python)?\s*(.*?)\s*```"
                    py_matches = re.findall(py_pattern, response, re.DOTALL)
                    if py_matches:
                        for pm in py_matches:
                            pm_stripped = pm.strip()
                            if len(pm_stripped) > 50 and pm_stripped != code_context:
                                diff = _build_unified_diff(code_context, pm_stripped, st.session_state.get("last_scan_file") or "main.py")
                                if diff:
                                    extracted_patch = diff
                                    break
                
                if extracted_patch:
                    # 1. Resolve target path and patch root
                    import os
                    from src.ui.scanner_tab import _resolve_patch_target
                    from src.core.file_utils import apply_patch
                    from src.ui.patch_review import extract_patched_code
                    
                    target_path = st.session_state.get("last_scan_file") or "main.py"
                    if st.session_state.get("analysis_results"):
                        target_path = st.session_state.analysis_results.get("target_path") or target_path
                    
                    patch_root = _resolve_patch_target(target_path)
                    
                    # 2. Automatically apply patch to make it the remediation code
                    apply_res = apply_patch(extracted_patch, patch_root, dry_run=False)
                    st.session_state.patch_applied = True
                    
                    # 3. Update analysis_results dict
                    if "analysis_results" not in st.session_state or not st.session_state.analysis_results:
                        st.session_state.analysis_results = {
                            "code_content": code_context,
                            "target_path": target_path,
                            "patch_file_path": target_path,
                            "result_id": "chat_generated",
                            "llm_analysis": security_analysis or "Generated from chat",
                            "semgrep_results": {"results": []}
                        }
                    else:
                        st.session_state.analysis_results["code_content"] = st.session_state.analysis_results.get("code_content") or code_context
                        st.session_state.analysis_results["target_path"] = st.session_state.analysis_results.get("target_path") or target_path
                        st.session_state.analysis_results["patch_file_path"] = st.session_state.analysis_results.get("patch_file_path") or target_path
                    
                    st.session_state.analysis_results["patch_suggestions"] = extracted_patch
                    
                    # 4. Configure scan target for verification scan
                    patched_preview = extract_patched_code(code_context, extracted_patch) if code_context else None
                    if target_path and os.path.exists(target_path):
                        if os.path.isdir(target_path):
                            st.session_state.pop("scanner_zip_file", None)
                            st.session_state.pop("scanner_uploaded_file", None)
                            st.session_state.scanner_github_repo_path = target_path
                        else:
                            st.session_state.pop("scanner_zip_file", None)
                            st.session_state.pop("scanner_uploaded_file", None)
                            try:
                                with open(target_path, "r") as f:
                                    st.session_state.scanner_paste_code = f.read()
                            except:
                                st.session_state.scanner_paste_code = patched_preview
                    else:
                        st.session_state.pop("scanner_zip_file", None)
                        st.session_state.pop("scanner_uploaded_file", None)
                        st.session_state.scanner_paste_code = patched_preview or code_context
                    
                    # 5. Trigger the automatic verification scan
                    st.session_state.run_scan_request = True
                    st.session_state.patch_verified = True
                    st.session_state.patch_generated_from_chat = True
                
                st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.session_state.prefill_prompt = ""
            if extracted_patch:
                AppState.set_page(":material/analytics: Security Scanner")
            st.rerun()

    with right:
        st.markdown('<div class="chat-card">', unsafe_allow_html=True)
        st.markdown('<span class="context-label">scan context</span>', unsafe_allow_html=True)

        if st.session_state.last_scan_file or security_analysis:
            st.markdown(
                f'<div class="context-chip"><span><strong>{st.session_state.last_scan_file or "No scan loaded"}</strong></span><span class="chip-badge">File</span></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="context-chip"><span><strong>High: {severity_count.get("high", 0)}</strong></span><span class="chip-badge">High</span></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="context-chip"><span><strong>Medium: {severity_count.get("medium", 0)}</strong></span><span class="chip-badge">Medium</span></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="context-chip"><span><strong>Fixed: {severity_count.get("fixed", 0)}</strong></span><span class="chip-badge">Fixed</span></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown("<div style='color: #8b909e; margin-bottom: 1rem;'>no scan loaded — run a scan first</div>", unsafe_allow_html=True)
            if st.button("Go to Scanner", key="chat_go_to_scanner"):
                AppState.set_page(":material/analytics: Security Scanner")

        st.markdown('<div style="margin-top: 1.5rem; margin-bottom: 0.75rem;"><strong>Quick ask</strong></div>', unsafe_allow_html=True)
        prompts = [
            "Explain all findings",
            "Generate full patch",
            "Estimate CVSS scores",
            "Write test cases",
        ]
        for idx, prompt in enumerate(prompts):
            if st.button(prompt, key=f"quick_ask_{idx}"):
                st.session_state.quick_ask_prompt = prompt
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
