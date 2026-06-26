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
                    # Initialize analysis_results if not present
                    if "analysis_results" not in st.session_state or not st.session_state.analysis_results:
                        st.session_state.analysis_results = {
                            "code_content": code_context,
                            "target_path": st.session_state.get("last_scan_file") or "main.py",
                            "patch_file_path": st.session_state.get("last_scan_file") or "main.py",
                            "result_id": "chat_generated",
                            "llm_analysis": security_analysis or "Generated from chat",
                            "semgrep_results": {"results": []}
                        }
                    else:
                        st.session_state.analysis_results["code_content"] = st.session_state.analysis_results.get("code_content") or code_context
                        st.session_state.analysis_results["target_path"] = st.session_state.analysis_results.get("target_path") or (st.session_state.get("last_scan_file") or "main.py")
                        st.session_state.analysis_results["patch_file_path"] = st.session_state.analysis_results.get("patch_file_path") or (st.session_state.get("last_scan_file") or "main.py")
                    
                    st.session_state.analysis_results["patch_suggestions"] = extracted_patch
                    st.session_state.patch_generated_from_chat = True
                
                st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.session_state.prefill_prompt = ""
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
