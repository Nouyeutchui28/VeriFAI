import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables at the very beginning
load_dotenv()

import pandas as pd
import atexit
from datetime import datetime

# Import UI Components & Utilities
from .scanner_tab import render_scanner_tab
from .chat_tab import render_chat_tab
from .rules_tab import render_rules_tab
from .github_tab import render_github_tab
from .history_tab import render_history_tab
from .settings_tab import render_settings_tab
from .help_tab import render_help_tab
from .login_page import render_login_page
from .styles import apply_custom_styles
from .api_client import get_api_client
from ..core.file_utils import cleanup_temp_files
from ..utils.state import AppState
from ..utils.report_gen import generate_pdf_report

NAV_ITEMS = [
    ("Dashboard", "🏠 Dashboard"),
    ("Scanner", "📊 Security Scanner"),
    ("Patch Review", "🛠️ Patch Review"),
    ("History", "🕒 Scan History"),
    ("Intelligence Chat", "💬 Intelligence Chat"),
    ("Repositories", "📦 Project Repositories"),
    ("Custom Rules", "📋 Custom Rules"),
    ("Help", "📚 Help"),
    ("Settings", "⚙️ Settings"),
]


def configure_app():
    """Initial app configuration."""
    st.set_page_config(
        page_title="VeriFAI LLM - AI Security Scanner",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    AppState.initialize()
    initialize_session_state()
    apply_custom_styles()
    inject_layout_css()


def initialize_session_state():
    """Initialize session state keys required by the layout."""
    defaults = {
        "last_scan_code": "",
        "last_scan_results": None,
        "last_scan_file": "",
        "scan_step": 0,
        "scan_running": False,
        "scan_error": False,
        "prefill_prompt": "",
        "run_scan_request": False,
        "rules_loaded_count": 0,
    }
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def inject_layout_css():
    """Inject custom dark theme and sidebar layout styles."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
        :root {
            --bg: #0a0c0f;
            --surface: #1a1d24;
            --surface2: #20242e;
            --border: rgba(255,255,255,0.06);
            --accent: #00e5a0;
            --danger: #ff4060;
            --warn: #ffaa00;
            --info: #0066ff;
            --text: #e8eaf0;
            --text2: #8b909e;
            --text3: #555a68;
        }

        /* REMOVE TOP SPACING */
        [data-testid="stHeader"], .stAppHeader {
            display: none !important;
        }
        
        .main .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            max-width: 1200px !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }

        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'DM Sans', sans-serif;
            background: var(--bg);
            color: var(--text);
        }

        /* FORCE SIDEBAR VISIBILITY & STYLE */
        [data-testid="stSidebar"] {
            background: var(--surface) !important;
            border-right: 1px solid var(--border) !important;
            min-width: 300px !important;
            max-width: 300px !important;
            visibility: visible !important;
            display: block !important;
        }

        /* Hide the default collapse button but keep it clickable via our button */
        [data-testid="stSidebarCollapsedControl"] {
            display: none !important;
        }

        /* Sidebar Header and Branding */
        .sidebar-header {
            padding-bottom: 1.5rem;
            margin-bottom: 1.25rem;
            border-bottom: 1px solid var(--border);
            text-align: center;
        }

        .sidebar-section {
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
            color: var(--text2);
            font-size: 0.75rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            font-weight: 700;
        }

        .topbar {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 0.6rem 1rem;
            margin-bottom: 1.5rem;
            position: sticky;
            top: 0;
            z-index: 999;
            display: flex;
            align-items: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }

        .page-header {
            font-family: 'Syne', sans-serif;
            font-size: 1.3rem;
            font-weight: 800;
            margin: 0;
            margin-left: 1rem;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--text2);
            font-size: 0.8rem;
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.06);
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }

        .status-dot.ready { background: var(--accent); }
        .status-dot.error { background: var(--danger); }

        .menu-toggle-btn {
            background: var(--surface2) !important;
            color: var(--accent) !important;
            border: 1px solid var(--border) !important;
            padding: 0.4rem 0.7rem !important;
            border-radius: 8px !important;
            cursor: pointer !important;
            font-size: 1.1rem !important;
            transition: all 0.2s !important;
        }

        .menu-toggle-btn:hover {
            background: var(--accent) !important;
            color: #000 !important;
        }

        /* DASHBOARD CARDS */
        .model-chip {
            margin-top: 2rem;
            padding: 1rem;
            background: var(--surface2);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_navigation(current_page):
    """Render the left sidebar navigation and status panel."""
    rules_count = st.session_state.get("rules_loaded_count", 0)

    with st.sidebar:
        st.markdown(
            """
            <div style="text-align: center; margin-top: 1rem; margin-bottom: 1.5rem;">
                <div style="font-family: 'Syne', sans-serif; font-size: 1.25rem; font-weight: 800; color: var(--accent);">VeriFAI LLM</div>
                <div style="color: var(--text2); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;">Oxbiy Intelligence</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Sidebar Buttons
    st.sidebar.markdown('<div class="sidebar-section">SCAN</div>', unsafe_allow_html=True)
    for label, page_value in NAV_ITEMS[:3]:
        is_active = current_page == page_value
        if st.sidebar.button(label, key=f"nav_{label}", use_container_width=True, type="primary" if is_active else "secondary"):
            AppState.set_page(page_value); st.rerun()

    st.sidebar.markdown('<div class="sidebar-section">ANALYSIS</div>', unsafe_allow_html=True)
    for label, page_value in NAV_ITEMS[3:6]:
        is_active = current_page == page_value
        if st.sidebar.button(label, key=f"nav_{label}", use_container_width=True, type="primary" if is_active else "secondary"):
            AppState.set_page(page_value); st.rerun()

    st.sidebar.markdown('<div class="sidebar-section">MANAGE</div>', unsafe_allow_html=True)
    for label, page_value in NAV_ITEMS[6:]:
        is_active = current_page == page_value
        if st.sidebar.button(label, key=f"nav_{label}", use_container_width=True, type="primary" if is_active else "secondary"):
            AppState.set_page(page_value); st.rerun()

    st.sidebar.markdown(f"""<div class="model-chip"><div style="font-weight: 700; color: var(--text); font-size: 0.85rem;"><span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--accent); margin-right:5px;"></span> Qwen2.5-Coder-7B</div><div style="color:var(--text2); font-size:0.75rem; margin-top:5px;">Engine: Hugging Face AI</div></div>""", unsafe_allow_html=True)


def render_top_bar(current_page):
    """Render the top bar for every page with status and action buttons."""
    page_title = next((label for label, value in NAV_ITEMS if value == current_page), "VeriFAI LLM")
    semgrep_ready = not st.session_state.get("scan_error", False)
    status_class = "ready" if semgrep_ready else "error"

    st.markdown('<div class="topbar">', unsafe_allow_html=True)
    
    # Grid layout for topbar
    cols = st.columns([0.4, 3, 1, 1, 1.2, 1])
    
    # Toggle Sidebar Button
    if cols[0].button("☰", key="menu_toggle"):
        # Use component to trigger parent window sidebar collapse
        st.components.v1.html("""<script>window.parent.document.querySelector('button[aria-label="Collapse sidebar"]').click();</script>""", height=0)

    cols[1].markdown(f'<div class="page-header">{page_title}</div>', unsafe_allow_html=True)
    
    with cols[3]:
        st.markdown(f'<div class="status-pill"><span class="status-dot {status_class}"></span> semgrep</div>', unsafe_allow_html=True)

    # Action Buttons
    if current_page == "📊 Security Scanner":
        has_results = bool(st.session_state.get("analysis_results"))
        if has_results:
            try:
                result = st.session_state.analysis_results
                pdf_bytes = generate_pdf_report(result.get("code_content", ""), result.get("llm_analysis", ""), result.get("semgrep_results", {}))
                cols[4].download_button("Export Report", pdf_bytes, file_name="security_audit.pdf", mime="application/pdf", use_container_width=True)
            except: cols[4].button("Export Report", disabled=True, use_container_width=True)
        else: cols[4].button("Export Report", disabled=True, use_container_width=True)

        if cols[5].button("Run Scan", key="top_run_scan", use_container_width=True, type="primary"):
            st.session_state.run_scan_request = True; st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)


def main():
    """Main Application Router."""
    configure_app()

    if not AppState.get("authenticated"):
        render_login_page()
        return

    if not AppState.get("legal_agreed"):
        @st.dialog("⚖️ Legal & Ethical Usage Warning")
        def show_legal_warning():
            st.warning("### IMPORTANT: AUTHORIZED USE ONLY")
            st.markdown("You must agree to use this tool only on authorized codebases for defensive research.")
            if st.button("I Agree & Understand", type="primary", use_container_width=True):
                AppState.set("legal_agreed", True); st.rerun()
        show_legal_warning(); return

    current_page = AppState.get("current_page")
    render_sidebar_navigation(current_page)
    render_top_bar(current_page)

    # Page Content Routing
    if current_page == "🏠 Dashboard":
        st.markdown('<div class="dashboard-title">Security Command Center</div>', unsafe_allow_html=True)
        st.markdown('<div class="dashboard-subtitle">Real-time threat intelligence and infrastructure health</div>', unsafe_allow_html=True)

        api_client = get_api_client()
        with st.spinner("Synchronizing live data..."):
            try: stats = api_client.get_summary_stats_insforge()
            except: stats = {}

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Analyses", stats.get("total_scans", 0))
        m2.metric("Threats Detected", stats.get("vulnerabilities", 0), delta_color="inverse")
        m3.metric("Auto-Remediated", stats.get("fixed_issues", 0))
        m4.metric("Risk Index", f"{stats.get('security_score', 100)}/100")

        st.markdown("---")
        
        v1, v2 = st.columns([2, 1])
        with v1:
            st.markdown("#### 📈 Analysis Velocity")
            try:
                history = api_client.get_scan_history(limit=15)
                if isinstance(history, list) and history:
                    df = pd.DataFrame(history)
                    df['date'] = pd.to_datetime(df['start_time']).dt.date
                    st.area_chart(df.groupby('date').size().reset_index(name='Scans').set_index('date'), color="#00e5a0")
                else: st.info("Analysis velocity data pending.")
            except: st.info("Real-time data currently unavailable.")

        with v2:
            st.markdown("#### 🛡️ Threat Distribution")
            try:
                severity_data = api_client.get_severity_stats_insforge()
                if any(severity_data.values()): st.bar_chart(severity_data, color="#ff4060")
                else: st.info("No threats detected.")
            except: st.info("Distribution data unavailable.")

        st.markdown("---")
        st.markdown("#### 📡 Live Infrastructure Status")
        s1, s2, s3 = st.columns(3)
        for col, title, sub in [(s1, "Database", "Encrypted RDS Connected"), (s2, "AI Engine", "Local Ollama Phi-3"), (s3, "API Layer", "FastAPI Production Node")]:
            with col: st.markdown(f"""<div class="model-chip" style="margin-top:0;"><div style="font-weight:700; color:var(--text);"><span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--accent); margin-right:5px;"></span> {title}</div><div style="color:var(--text2); font-size:0.8rem; margin-top:5px;">{sub}</div></div>""", unsafe_allow_html=True)

    elif current_page == "📊 Security Scanner": render_scanner_tab()
    elif current_page == "🛠️ Patch Review":
        st.markdown('<div class="dashboard-title">Security Patch Review</div>', unsafe_allow_html=True)
        results = st.session_state.get("analysis_results")
        if results and results.get("patch_suggestions"):
            from .patch_review import render_patch_review_panel, extract_patched_code
            from .scanner_tab import _resolve_patch_target
            patch_text = results.get("patch_suggestions", "")
            code_content = results.get("code_content", "")
            if patch_text and patch_text.strip() and patch_text != "No patch suggestions.":
                render_patch_review_panel(patch_text=patch_text, original_code=code_content, patched_code=extract_patched_code(code_content, patch_text) if code_content else None, target_path=results.get("target_path", ""), patch_root=_resolve_patch_target(results.get("target_path", "")), patch_file_path=results.get("patch_file_path", ""))
            else: st.info("No patch suggestions available.")
        else: st.info("Run a scan first.")

    elif current_page == "🕒 Scan History": render_history_tab()
    elif current_page == "📋 Custom Rules": render_rules_tab()
    elif current_page == "📦 Project Repositories": render_github_tab(metrics_enabled=True, llm_temperature=st.session_state.get('llm_temperature', 0.2), model_selection=st.session_state.get('model_selection', 'secure-patch-model'))
    elif current_page == "💬 Intelligence Chat": render_chat_tab()
    elif current_page == "📚 Help": render_help_tab()
    elif current_page == "⚙️ Settings": render_settings_tab()

    st.markdown('<div style="text-align: center; color: #8b9bb4; font-size: 0.75rem; padding: 2rem 0; border-top: 1px solid #1d2b3f; margin-top: 4rem; text-transform: uppercase; letter-spacing: 0.5px;">VeriFAI LLM Security Scanner | © 2026</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    atexit.register(cleanup_temp_files); main()
