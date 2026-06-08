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

        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'DM Sans', sans-serif;
            background: var(--bg);
            color: var(--text);
        }

        /* RESPONSIVE LAYOUT SYSTEM */
        
        /* Default (Desktop) */
        [data-testid="stSidebar"] {
            background: var(--surface) !important;
            border-right: 1px solid var(--border) !important;
            min-width: 320px !important;
            max-width: 320px !important;
        }

        .main .block-container {
            max-width: 1200px !important;
            margin-left: auto !important;
            margin-right: auto !important;
            padding: 2rem !important;
        }

        /* Desktop: Allow Sidebar Toggle */
        @media (min-width: 1024px) {
            [data-testid="stSidebar"] {
                transition: transform 0.3s ease-in-out !important;
            }
            /* Make native collapse button invisible but clickable via JS */
            [data-testid="stSidebarCollapsedControl"] {
                opacity: 0 !important;
                pointer-events: none !important;
                position: absolute !important;
                z-index: -1 !important;
            }
        }

        /* Responsive Controls (Mobile/Tablet) */
        @media (max-width: 1023px) {
            /* Force the toggle to be UNMISSABLE */
            [data-testid="stSidebarCollapsedControl"], 
            .st-emotion-cache-zq5wih,
            button[kind="headerNoContext"] {
                display: flex !important;
                visibility: visible !important;
                opacity: 1 !important;
                background-color: var(--accent) !important;
                border-radius: 0 50% 50% 0 !important;
                left: 0 !important;
                top: 60px !important; /* Move it down slightly from the header */
                width: 56px !important;
                height: 56px !important;
                z-index: 9999999 !important;
                box-shadow: 0 0 20px rgba(0, 229, 160, 0.7) !important;
                animation: pulse-green 2s infinite !important;
                justify-content: center !important;
                align-items: center !important;
            }

            @keyframes pulse-green {
                0% { box-shadow: 0 0 0 0 rgba(0, 229, 160, 0.7); }
                70% { box-shadow: 0 0 0 15px rgba(0, 229, 160, 0); }
                100% { box-shadow: 0 0 0 0 rgba(0, 229, 160, 0); }
            }

            /* Darken the icon for contrast */
            [data-testid="stSidebarCollapsedControl"] svg,
            .st-emotion-cache-zq5wih svg {
                width: 32px !important;
                height: 32px !important;
                fill: #000 !important;
                color: #000 !important;
            }
            .main .block-container {
                max-width: 95% !important;
                padding: 1.5rem !important;
            }
            [data-testid="stSidebar"] {
                min-width: 280px !important;
                max-width: 280px !important;
            }
        }

        /* Mobile Devices */
        @media (max-width: 767px) {
            .main .block-container {
                padding: 1rem !important;
            }
            .page-header {
                font-size: 1.2rem !important;
            }
            .dashboard-title {
                font-size: 1.5rem !important;
            }
        }

        /* Sidebar Header and Branding */
        .sidebar-header {
            padding-bottom: 1.5rem;
            margin-bottom: 1.25rem;
            border-bottom: 1px solid var(--border);
            text-align: center;
        }

        .sidebar-title {
            font-family: 'Syne', sans-serif;
            font-size: 1.25rem;
            font-weight: 800;
            margin: 0;
            color: var(--text);
        }

        .sidebar-subtitle {
            color: var(--text2);
            font-size: 0.85rem;
            margin: 0.25rem 0 0;
            font-weight: 400;
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

        .sidebar-nav-item,
        .sidebar-nav-button {
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.85rem 1rem;
            margin-bottom: 0.35rem;
            border-radius: 10px;
            font-size: 0.95rem;
            color: var(--text);
            background: transparent;
            cursor: pointer;
            border: 1px solid transparent;
        }

        .sidebar-nav-item.active {
            border-left: 4px solid var(--accent);
            background: rgba(0, 229, 160, 0.08);
            color: var(--text);
        }

        .sidebar-nav-item:hover,
        .sidebar-nav-button:hover {
            background: rgba(255,255,255,0.03);
        }

        .sidebar-badge {
            background: rgba(255,255,255,0.08);
            color: var(--text2);
            padding: 0.1rem 0.45rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-family: 'DM Mono', monospace;
        }

        .live-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 0.35rem;
            background: var(--accent);
            box-shadow: 0 0 8px rgba(0, 229, 160, 0.45);
        }

        .model-chip {
            margin-top: 2rem;
            padding: 1rem;
            background: var(--surface2);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 10px;
            font-size: 0.9rem;
        }

        .model-chip .chip-title {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--text);
            font-weight: 700;
        }

        .model-chip .chip-subtitle {
            color: var(--text2);
            font-size: 0.85rem;
            margin-top: 0.35rem;
        }

        .topbar {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1rem 1.25rem;
            margin-bottom: 1.5rem;
            position: sticky;
            top: 0;
            z-index: 999;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .topbar-left {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .page-header {
            font-family: 'Syne', sans-serif;
            font-size: 1.55rem;
            font-weight: 800;
            margin: 0;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--text2);
            font-size: 0.9rem;
            padding: 0.45rem 0.8rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.06);
        }

        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            box-shadow: 0 0 8px rgba(0, 229, 160, 0.35);
        }

        .status-dot.error {
            background: var(--danger);
            box-shadow: 0 0 8px rgba(255, 64, 96, 0.35);
        }

        .status-dot.ready {
            background: var(--accent);
        }

        .button-primary {
            background: var(--accent) !important;
            color: #000 !important;
            font-weight: 700 !important;
        }

        .button-disabled {
            opacity: 0.45;
            pointer-events: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_navigation(current_page):
    """Render the left sidebar navigation and status panel."""
    rules_count = st.session_state.get("rules_loaded_count", 0)

    # 1. BRANDING
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align: center; margin-top: 1.5rem; margin-bottom: 1.5rem;">
                <div style="font-family: 'Syne', sans-serif; font-size: 1.25rem; font-weight: 800; color: var(--accent);">VeriFAI LLM</div>
                <div style="color: var(--text2); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;">Oxbiy Intelligence</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 2. SCAN SECTION
    st.sidebar.markdown('<div class="sidebar-section">SCAN</div>', unsafe_allow_html=True)
    for label, page_value in NAV_ITEMS[:3]:
        is_active = current_page == page_value
        if st.sidebar.button(
            label, 
            key=f"nav_{label}", 
            use_container_width=True, 
            type="primary" if is_active else "secondary"
        ):
            AppState.set_page(page_value)
            st.rerun()

    # 3. ANALYSIS SECTION
    st.sidebar.markdown('<div class="sidebar-section">ANALYSIS</div>', unsafe_allow_html=True)
    for label, page_value in NAV_ITEMS[3:6]:
        is_active = current_page == page_value
        display_label = label
        if label == "Intelligence Chat":
            display_label = f"💬 Chat [Live]"
            
        if st.sidebar.button(
            display_label, 
            key=f"nav_{label}", 
            use_container_width=True, 
            type="primary" if is_active else "secondary"
        ):
            AppState.set_page(page_value)
            st.rerun()

    # 4. MANAGE SECTION
    st.sidebar.markdown('<div class="sidebar-section">MANAGE</div>', unsafe_allow_html=True)
    for label, page_value in NAV_ITEMS[6:]:
        is_active = current_page == page_value
        display_label = label
        if label == "Custom Rules":
            display_label = f"📋 Rules ({rules_count})"
            
        if st.sidebar.button(
            display_label, 
            key=f"nav_{label}", 
            use_container_width=True, 
            type="primary" if is_active else "secondary"
        ):
            AppState.set_page(page_value)
            st.rerun()

    st.sidebar.markdown(
        f"""
        <div class="model-chip">
            <div style="font-weight: 700; color: var(--text); font-size: 0.85rem;">
                <span class="live-dot"></span> Qwen2.5-Coder-7B
            </div>
            <div style="color: var(--text3); font-size: 0.75rem; margin-top: 0.25rem;">
                Engine: Hugging Face AI
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.sidebar.button("Edit", key="sidebar_edit", use_container_width=True):
        AppState.set_page("⚙️ Settings")


def render_top_bar(current_page):
    """Render the top bar for every page with status and action buttons."""
    page_title = next((label for label, value in NAV_ITEMS if value == current_page), "VeriFAI LLM")
    semgrep_ready = not st.session_state.get("scan_error", False)
    status_class = "ready" if semgrep_ready else "error"

    st.markdown('<div class="topbar">', unsafe_allow_html=True)
    with st.container():
        # Layout: Menu Toggle (small), Title (large), padding, Status, Export, Run Scan
        cols = st.columns([0.3, 3, 0.5, 1, 1, 1])
        
        # Pure HTML/JS Menu Toggle
        with cols[0]:
            st.components.v1.html("""
                <button onclick="
                    var parentDoc = window.parent.document;
                    var clicked = false;
                    
                    // Helper to click if found
                    function tryClick(selector) {
                        if (clicked) return;
                        var btn = parentDoc.querySelector(selector);
                        if (btn) {
                            btn.click();
                            clicked = true;
                        }
                    }

                    // Try all known Streamlit sidebar toggle selectors
                    tryClick('button[data-testid=\\'stSidebarCollapsedControl\\']');
                    tryClick('button[data-testid=\\'stSidebarCollapseButton\\']');
                    tryClick('button[aria-label=\\'Collapse sidebar\\']');
                    tryClick('button[aria-label=\\'Expand sidebar\\']');
                    tryClick('[data-testid=\\'collapsedControl\\']');
                    
                    if (!clicked) {
                        // Fallback: search all buttons for the SVG icon characteristic
                        var buttons = Array.from(parentDoc.querySelectorAll('button'));
                        for (var i=0; i<buttons.length; i++) {
                            var b = buttons[i];
                            var svg = b.querySelector('svg');
                            if (svg && (svg.getAttribute('data-testid') === 'stSidebarCollapseButton' || 
                                        svg.getAttribute('data-testid') === 'stSidebarCollapsedControl')) {
                                b.click();
                                clicked = true;
                                break;
                            }
                        }
                    }
                " style="
                    background: transparent; border: 1px solid rgba(255,255,255,0.1); color: #00e5a0; 
                    cursor: pointer; font-size: 1.5rem; border-radius: 6px; width: 40px; height: 40px;
                    display: flex; align-items: center; justify-content: center; transition: all 0.2s;
                ">☰</button>
                <style>button:hover { background: rgba(0, 229, 160, 0.1) !important; color: #00e5a0 !important; border-color: #00e5a0 !important; }</style>
            """, height=45)

        cols[1].markdown(f'<div class="page-header" style="margin-top: 5px;">{page_title}</div>', unsafe_allow_html=True)
        cols[2].markdown("&nbsp;")
        
        with cols[3]:
            st.markdown(f'<div class="status-pill" style="margin-top: 5px;"><span class="status-dot {status_class}"></span> semgrep</div>', unsafe_allow_html=True)

        has_results = bool(st.session_state.get("analysis_results"))
        if current_page == "📊 Security Scanner":
            if has_results:
                try:
                    result = st.session_state.analysis_results
                    pdf_bytes = generate_pdf_report(
                        result.get("code_content", ""),
                        result.get("llm_analysis", ""),
                        result.get("semgrep_results", {}),
                    )
                    cols[3].download_button(
                        "Export Report",
                        pdf_bytes,
                        file_name="security_audit.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception:
                    cols[3].button("Export Report", disabled=True, use_container_width=True)
            else:
                cols[3].button("Export Report", disabled=True, use_container_width=True)
        else:
            cols[3].button("Export Report", disabled=True, use_container_width=True)

        if current_page == "📊 Security Scanner":
            if cols[4].button("Run Scan", key="top_run_scan", use_container_width=True, type="primary"):
                st.session_state.run_scan_request = True
                st.rerun()
        else:
            cols[4].button("Run Scan", disabled=True, use_container_width=True)
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
                AppState.set("legal_agreed", True)
                st.rerun()
        show_legal_warning()
        return

    current_page = AppState.get("current_page")
    render_sidebar_navigation(current_page)
    render_top_bar(current_page)

    if current_page == "🏠 Dashboard":
        st.markdown('<div class="dashboard-title">Security Command Center</div>', unsafe_allow_html=True)
        st.markdown('<div class="dashboard-subtitle">Real-time threat intelligence and infrastructure health</div>', unsafe_allow_html=True)

        api_client = get_api_client()
        with st.spinner("Synchronizing live data..."):
            try:
                stats = api_client.get_summary_stats_insforge()
            except Exception as e:
                st.warning(f"Unable to load dashboard metrics: {str(e)}")
                stats = {}

        # 1. METRICS GRID
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Analyses", stats.get("total_scans", 0), delta=None, help="Cumulative code scans performed")
        m2.metric("Threats Detected", stats.get("vulnerabilities", 0), delta=stats.get("vulnerabilities", 0) * -1 if stats.get("vulnerabilities") else 0, delta_color="inverse")
        m3.metric("Auto-Remediated", stats.get("fixed_issues", 0), delta=stats.get("fixed_issues", 0), delta_color="normal")
        m4.metric("Risk Index", f"{stats.get('security_score', 100)}/100", help="Lower index indicates higher security posture")

        st.markdown("---")
        
        # 2. VISUAL INTELLIGENCE
        v1, v2 = st.columns([2, 1])
        with v1:
            st.markdown("#### 📈 Analysis Velocity (Last 7 Days)")
            try:
                history = api_client.get_scan_history(limit=15)
                if isinstance(history, list) and history:
                    history_df = pd.DataFrame(history)
                    if 'start_time' in history_df.columns:
                        history_df['date'] = pd.to_datetime(history_df['start_time']).dt.date
                        trend_data = history_df.groupby('date').size().reset_index(name='Scans')
                        st.area_chart(trend_data.set_index('date'), color="#00e5a0")
                    else: st.info("Analysis velocity data pending.")
                else: st.info("Scan more projects to see your velocity trends.")
            except: st.info("Real-time data currently unavailable.")

        with v2:
            st.markdown("#### 🛡️ Threat Distribution")
            try:
                severity_data = api_client.get_severity_stats_insforge()
                if any(severity_data.values()):
                    # Use a pie chart for better distribution view if possible, else bar
                    st.bar_chart(severity_data, color="#ff4060")
                else: st.info("No threats detected in recent scans.")
            except: st.info("Distribution data unavailable.")

        st.markdown("---")
        
        # 3. LIVE ACTIVITY FEED
        st.markdown("#### 📡 Live Infrastructure Status")
        s1, s2, s3 = st.columns(3)
        with s1:
            st.markdown(f"""
                <div class="model-chip" style="margin-top:0;">
                    <div class="chip-title"><span class="status-dot ready"></span> Database</div>
                    <div class="chip-subtitle">Encrypted RDS Connected</div>
                </div>
            """, unsafe_allow_html=True)
        with s2:
            st.markdown(f"""
                <div class="model-chip" style="margin-top:0;">
                    <div class="chip-title"><span class="status-dot ready"></span> AI Engine</div>
                    <div class="chip-subtitle">Local Ollama Phi-3 (8-Core)</div>
                </div>
            """, unsafe_allow_html=True)
        with s3:
            st.markdown(f"""
                <div class="model-chip" style="margin-top:0;">
                    <div class="chip-title"><span class="status-dot ready"></span> API Layer</div>
                    <div class="chip-subtitle">FastAPI Production Node</div>
                </div>
            """, unsafe_allow_html=True)

    elif current_page == "📊 Security Scanner":
        render_scanner_tab()

    elif current_page == "🛠️ Patch Review":
        st.markdown('<div class="dashboard-title">Security Patch Review</div>', unsafe_allow_html=True)
        st.markdown('<div class="dashboard-subtitle">Review and apply AI-generated security fixes</div>', unsafe_allow_html=True)
        
        # Check if we have results to show
        results = st.session_state.get("analysis_results")
        if results and results.get("patch_suggestions"):
            from .patch_review import render_patch_review_panel, extract_patched_code
            from .scanner_tab import _resolve_patch_target
            
            patch_text = results.get("patch_suggestions", "")
            code_content = results.get("code_content", "")
            patch_target = _resolve_patch_target(results.get("target_path", ""))
            
            if patch_text and patch_text.strip() and patch_text != "No patch suggestions.":
                patched_code = extract_patched_code(code_content, patch_text) if code_content else None
                render_patch_review_panel(
                    patch_text=patch_text,
                    original_code=code_content,
                    patched_code=patched_code,
                    target_path=results.get("target_path", ""), # Original path for zipping
                    patch_root=patch_target,                  # Root dir for applying patches
                    patch_file_path=results.get("patch_file_path", ""),
                )
            else:
                st.info("No patch suggestions available for the last scan.")
        else:
            st.info("Run a scan first to see patch suggestions here.")

    elif current_page == "🕒 Scan History":
        st.markdown('<div class="dashboard-title">Scan History Explorer</div>', unsafe_allow_html=True)
        st.markdown('<div class="dashboard-subtitle">Review previous security analysis results</div>', unsafe_allow_html=True)
        render_history_tab()

    elif current_page == "📋 Custom Rules":
        st.markdown('<div class="dashboard-title">Custom Security Rules</div>', unsafe_allow_html=True)
        st.markdown('<div class="dashboard-subtitle">Create and manage custom detection rules</div>', unsafe_allow_html=True)
        render_rules_tab()

    elif current_page == "📦 Project Repositories":
        st.markdown('<div class="dashboard-title">Project Repositories</div>', unsafe_allow_html=True)
        st.markdown('<div class="dashboard-subtitle">Scan GitHub repositories for security vulnerabilities</div>', unsafe_allow_html=True)
        render_github_tab(metrics_enabled=True, llm_temperature=st.session_state.get('llm_temperature', 0.2), model_selection=st.session_state.get('model_selection', 'secure-patch-model'))

    elif current_page == "💬 Intelligence Chat":
        st.markdown('<div class="dashboard-title">Security Intelligence Chat</div>', unsafe_allow_html=True)
        st.markdown('<div class="dashboard-subtitle">Ask questions and get security insights</div>', unsafe_allow_html=True)
        render_chat_tab()

    elif current_page == "📚 Help":
        st.markdown('<div class="dashboard-title">Help & Documentation</div>', unsafe_allow_html=True)
        st.markdown('<div class="dashboard-subtitle">Learn how to use VeriFAI LLM</div>', unsafe_allow_html=True)
        render_help_tab()

    elif current_page == "⚙️ Settings":
        st.markdown('<div class="dashboard-title">Settings & Preferences</div>', unsafe_allow_html=True)
        st.markdown('<div class="dashboard-subtitle">Configure application behavior and preferences</div>', unsafe_allow_html=True)
        render_settings_tab()

    st.markdown('<div style="text-align: center; color: #8b9bb4; font-size: 0.75rem; padding: 2rem 0; border-top: 1px solid #1d2b3f; margin-top: 4rem; text-transform: uppercase; letter-spacing: 0.5px;">VeriFAI LLM Security Scanner | Pro Edition 2026</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    atexit.register(cleanup_temp_files)
    main()

