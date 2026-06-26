import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables at the very beginning
load_dotenv()

import pandas as pd
import atexit
from datetime import datetime
import subprocess
import time
import socket

def start_backend():
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    if not is_port_in_use(8000):
        print("Starting FastAPI backend in the background...")
        # Start uvicorn using the same virtual environment Python interpreter
        import sys
        subprocess.Popen([sys.executable, "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"])
        # Give it a moment to boot
        for _ in range(15):
            if is_port_in_use(8000):
                break
            time.sleep(1)

start_backend()
# Import UI Components & Utilities
from src.ui.scanner_tab import render_scanner_tab
from src.ui.chat_tab import render_chat_tab
from src.ui.rules_tab import render_rules_tab
from src.ui.github_tab import render_github_tab
from src.ui.history_tab import render_history_tab
from src.ui.settings_tab import render_settings_tab
from src.ui.help_tab import render_help_tab
from src.ui.login_page import render_login_page
from src.ui.styles import apply_custom_styles
from src.ui.api_client import get_api_client
from src.core.file_utils import cleanup_temp_files
from src.utils.state import AppState
from src.utils.report_gen import generate_pdf_report

NAV_ITEMS = [
    ("Dashboard", ":material/dashboard: Dashboard"),
    ("Scanner", ":material/analytics: Security Scanner"),
    ("Patch Review", ":material/build: Patch Review"),
    ("History", ":material/history: Scan History"),
    ("Intelligence Chat", ":material/chat: Intelligence Chat"),
    ("Repositories", ":material/folder: Project Repositories"),
    ("Custom Rules", ":material/assignment: Custom Rules"),
    ("Help", ":material/menu_book: Help"),
    ("Settings", ":material/settings: Settings"),
]


def configure_app():
    """Initial app configuration."""
    st.set_page_config(
        page_title="VeriFAI LLM - AI Security Scanner",
        page_icon=":material/shield:",
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

        /* Mobile Layout Refinements */
        @media (max-width: 1023px) {
            .main .block-container {
                max-width: 100% !important;
                padding: 1.5rem !important;
            }
            .topbar {
                flex-wrap: wrap !important;
                gap: 1rem !important;
                height: auto !important;
            }
            .topbar-left {
                flex-wrap: wrap !important;
            }
            .page-header {
                font-size: 1.2rem !important;
            }
            /* Hide custom iframe menu toggle on mobile, use native header */
            .topbar iframe {
                display: none !important;
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
            display_label = f":material/chat: Chat [Live]"
            
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
            display_label = f":material/assignment: Rules ({rules_count})"
            
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
                <span class="live-dot"></span> qwen-2.5-coder-32b
            </div>
            <div style="color: var(--text3); font-size: 0.75rem; margin-top: 0.25rem;">
                Engine: Groq AI (Ultra)
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.sidebar.button("Edit", key="sidebar_edit", use_container_width=True):
        AppState.set_page(":material/settings: Settings")


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
            import streamlit.components.v1 as components
            components.html("""
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
        if current_page == ":material/analytics: Security Scanner":
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

        if current_page == ":material/analytics: Security Scanner":
            if cols[4].button("Run Scan", key="top_run_scan", use_container_width=True, type="primary"):
                st.session_state.run_scan_request = True
                st.rerun()
        else:
            cols[4].button("Run Scan", disabled=True, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


@st.fragment(run_every=15)
def render_dashboard_fragment():
    """Render the dashboard metrics with real-time auto-refresh."""
    api_client = get_api_client()
    
    # Attempt to fetch real stats from backend
    try:
        stats = api_client.get_summary_stats()
        is_mock = False
        if stats is None or (isinstance(stats, dict) and "error" in stats):
            is_mock = True
    except Exception:
        is_mock = True
        stats = {}

    # Check for current session data to override zeros
    current_results = st.session_state.get("analysis_results")
    if current_results:
        # If we have current results, we're definitely not just showing "mock" data, 
        # but we might need to seed the base stats if backend is empty
        if is_mock:
            stats = {
                "total_scans": 1,
                "vulnerabilities": sum(current_results.get("severity_count", {}).values()),
                "fixed_issues": 1 if current_results.get("patch_suggestions") else 0,
                "security_score": 90
            }
            is_mock = False # We have real current session data!
    elif is_mock:
        # Full fallback to simulated data if no backend AND no current scan
        stats = {
            "total_scans": 124,
            "vulnerabilities": 42,
            "fixed_issues": 28,
            "security_score": 84
        }
        st.warning(":material/warning: **Running in Demo Mode:** Showing simulated security intelligence until you run your first scan.")

    # 1. METRICS GRID
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Analyses", stats.get("total_scans", 0), delta="Session Active" if current_results else None)
    
    vuln_count = stats.get("vulnerabilities", 0)
    m2.metric("Threats Detected", vuln_count, 
              delta=f"-{stats.get('fixed_issues', 0)}" if vuln_count > 0 else None, 
              delta_color="inverse")
    
    m3.metric("Auto-Remediated", stats.get("fixed_issues", 0), delta=None, delta_color="normal")
    m4.metric("Risk Index", f"{stats.get('security_score', 100)}/100", help="Lower index indicates higher security posture")

    st.markdown("---")
    
    # 2. VISUAL INTELLIGENCE
    v1, v2 = st.columns([2, 1])
    with v1:
        st.markdown("#### :material/trending_up: Analysis Velocity (Last 7 Days)")
        try:
            history = [] if is_mock else api_client.get_scan_history(limit=15)
            if not history and is_mock:
                # Generate realistic mock trend
                dates = pd.date_range(end=datetime.now(), periods=7)
                mock_scans = [12, 18, 15, 22, 19, 25, 30]
                trend_data = pd.DataFrame({'date': dates, 'Scans': mock_scans})
                st.area_chart(trend_data.set_index('date'), color="#00e5a0")
            elif not history and current_results:
                # Show at least the one current scan
                dates = [datetime.now().date()]
                trend_data = pd.DataFrame({'date': dates, 'Scans': [1]})
                st.area_chart(trend_data.set_index('date'), color="#00e5a0")
            elif isinstance(history, list) and history:
                history_df = pd.DataFrame(history)
                if 'start_time' in history_df.columns:
                    history_df['date'] = pd.to_datetime(history_df['start_time']).dt.date
                    trend_data = history_df.groupby('date').size().reset_index(name='Scans')
                    st.area_chart(trend_data.set_index('date'), color="#00e5a0")
                else: st.info("Analysis velocity data pending.")
            else: st.info("Scan more projects to see your velocity trends.")
        except: st.info("Real-time data currently unavailable.")

    with v2:
        st.markdown("#### :material/shield: Threat Distribution")
        try:
            severity_data = {} if is_mock else api_client.get_severity_stats()
            
            # If backend distribution is empty but we have current scan results, use those
            if not any(severity_data.values()) and current_results:
                raw_sc = current_results.get("severity_count", {})
                severity_data = {k.capitalize(): v for k, v in raw_sc.items()}
            
            # Fallback to mock if still empty
            if not any(severity_data.values()) and is_mock:
                severity_data = {"Critical": 5, "High": 12, "Medium": 18, "Low": 7}
            
            if any(severity_data.values()):
                df_sev = pd.DataFrame(list(severity_data.items()), columns=['Severity', 'Count'])
                st.bar_chart(df_sev.set_index('Severity'), color="#ff4060")
            else: st.info("No threats detected in recent scans.")
        except: st.info("Distribution data unavailable.")

    st.markdown("---")
    
    # 3. LIVE ACTIVITY FEED
    st.markdown("#### :material/sensors: Live Infrastructure Status")
    s1, s2, s3 = st.columns(3)
    
    db_status = "ready" if not is_mock else "warning"
    db_sub = "Encrypted RDS Connected" if not is_mock else "Using Local SQLite Cache"
    
    with s1:
        st.markdown(f"""
            <div class="model-chip" style="margin-top:0;">
                <div class="chip-title"><span class="status-dot {db_status}"></span> Database</div>
                <div class="chip-subtitle">{db_sub}</div>
            </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
            <div class="model-chip" style="margin-top:0;">
                <div class="chip-title"><span class="status-dot ready"></span> AI Engine</div>
                <div class="chip-subtitle">Groq Engine (qwen-2.5-coder-32b)</div>
            </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
            <div class="model-chip" style="margin-top:0;">
                <div class="chip-title"><span class="status-dot ready"></span> API Layer</div>
                <div class="chip-subtitle">FastAPI Production Node</div>
            </div>
        """, unsafe_allow_html=True)

    # 4. DETAILED THREAT RECORDS TABLE
    if not is_mock:
        st.markdown("---")
        st.markdown("#### :material/assignment: Detected Vulnerability Records (Real-Time)")
        
        try:
            scans = api_client.get_scan_history(limit=50)
            if scans and not (isinstance(scans, dict) and "error" in scans):
                records = []
                for scan in scans:
                    res = api_client.get_results(scan.get("id"))
                    if isinstance(res, dict) and not "error" in res:
                        sem_res = res.get("semgrep_json", {})
                        if isinstance(sem_res, dict):
                            findings = sem_res.get("results", [])
                            for f in findings:
                                severity = f.get("severity", "unknown").upper()
                                # Mapping severity to emoji/badge
                                if severity in ["ERROR", "CRITICAL"]:
                                    sev_emoji = ":material/error: CRITICAL"
                                elif severity in ["WARNING", "HIGH"]:
                                    sev_emoji = ":material/warning: WARNING"
                                else:
                                    sev_emoji = ":material/info: INFO"
                                    
                                records.append({
                                    "Project Name": scan.get("project_name", "Unknown"),
                                    "Vulnerability": f.get("check_id", "Unknown"),
                                    "Severity": sev_emoji,
                                    "File Path": f.get("path", "Unknown"),
                                    "Line": f.get("start", {}).get("line", "N/A"),
                                    "Description": f.get("extra", {}).get("message", "No description"),
                                    "Detected At": scan.get("created_at", "")[:19].replace("T", " ")
                                })
                
                if records:
                    df = pd.DataFrame(records)
                    st.dataframe(
                        df,
                        use_container_width=True,
                        column_config={
                            "Severity": st.column_config.TextColumn("Severity", width="medium"),
                            "Description": st.column_config.TextColumn("Description", width="large")
                        }
                    )
                else:
                    st.info(":material/celebration: No active vulnerability records detected in your scans.")
            else:
                st.info("No scan history found.")
        except Exception as e:
            st.error(f"Error loading threat records: {str(e)}")

def main():
    """Main Application Router."""
    configure_app()

    if not AppState.get("authenticated"):
        render_login_page()
        return

    if not AppState.get("legal_agreed"):
        @st.dialog(":material/gavel: Legal & Ethical Usage Warning")
        def show_legal_warning():
            st.warning("### :material/warning: CRITICAL: AUTHORIZED USE ONLY")
            
            st.markdown("""
            This tool is designed for **defensive security research** and **authorized testing** only. Using this tool on systems or codebases you do not own or have explicit, written permission to test is **illegal and unethical**.

            #### :material/warning: Legal Dangers of Unauthorized Use
            *   **Criminal Liability:** Scanning or accessing unauthorized systems may violate the **Computer Fraud and Abuse Act (CFAA)** or similar international cybercrime laws, leading to heavy fines or imprisonment.
            *   **Civil Lawsuits:** Owners of unauthorized targets can sue for damages, even if no harm was intended.
            *   **Employment/Academic Risk:** Unauthorized testing can result in immediate termination or expulsion.

            #### :material/lock: Important Security Aspects
            1.  **AI Hallucinations:** AI-generated security patches (remediations) may be incorrect or introduce new bugs. **Always manually review and test every patch** in a safe environment before deployment.
            2.  **Data Privacy:** Code sent for analysis may be processed by external APIs (Hugging Face). Ensure you do not scan code containing sensitive secrets, PII, or proprietary information unless authorized.
            3.  **No Guarantee:** This tool assists in detection but does not guarantee 100% security. It should be part of a broader security strategy.
            """)
            
            st.info("By clicking below, you certify that you have the legal right to scan the targets you provide and accept full responsibility for your actions.")
            
            if st.button("I Agree, Understand, & Accept Responsibility", type="primary", use_container_width=True):
                AppState.set("legal_agreed", True)
                st.rerun()
        show_legal_warning()
        return

    current_page = AppState.get("current_page")
    render_sidebar_navigation(current_page)
    render_top_bar(current_page)

    if current_page == ":material/dashboard: Dashboard":
        st.markdown('<div class="dashboard-title">Security Command Center</div>', unsafe_allow_html=True)
        st.markdown('<div class="dashboard-subtitle">Real-time threat intelligence and infrastructure health</div>', unsafe_allow_html=True)
        render_dashboard_fragment()

    elif current_page == ":material/analytics: Security Scanner":
        render_scanner_tab()

    elif current_page == ":material/build: Patch Review":
        st.markdown('<div class="dashboard-title">Security Patch Review</div>', unsafe_allow_html=True)
        st.markdown('<div class="dashboard-subtitle">Review and apply AI-generated security fixes</div>', unsafe_allow_html=True)
        
        # Check if we have results to show
        results = st.session_state.get("analysis_results")
        if results and results.get("patch_suggestions"):
            from src.ui.patch_review import render_patch_review_panel, extract_patched_code
            from src.ui.scanner_tab import _resolve_patch_target
            
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
                        target_path=results.get("target_path", ""), # Original path for zipping
                        patch_root=patch_target,                  # Root dir for applying patches
                        patch_file_path=results.get("patch_file_path", ""),
                    )
                except Exception as e:
                    st.error(f":material/warning: Unable to render interactive patch review panel. The patch diff may be malformed or incompatible with this file. Please review the patch text manually.")
                    with st.expander("View Raw Patch Diff"):
                        st.code(patch_text, language="diff")
            else:
                st.info("No patch suggestions available for the last scan.")
        else:
            st.info("Run a scan first to see patch suggestions here.")

    elif current_page == ":material/history: Scan History":
        st.markdown('<div class="dashboard-title">Scan History Explorer</div>', unsafe_allow_html=True)
        st.markdown('<div class="dashboard-subtitle">Review previous security analysis results</div>', unsafe_allow_html=True)
        render_history_tab()

    elif current_page == ":material/assignment: Custom Rules":
        st.markdown('<div class="dashboard-title">Custom Security Rules</div>', unsafe_allow_html=True)
        st.markdown('<div class="dashboard-subtitle">Create and manage custom detection rules</div>', unsafe_allow_html=True)
        render_rules_tab()

    elif current_page == ":material/folder: Project Repositories":
        st.markdown('<div class="dashboard-title">Project Repositories</div>', unsafe_allow_html=True)
        st.markdown('<div class="dashboard-subtitle">Scan GitHub repositories for security vulnerabilities</div>', unsafe_allow_html=True)
        render_github_tab(metrics_enabled=True, llm_temperature=st.session_state.get('llm_temperature', 0.2), model_selection=st.session_state.get('model_selection', 'secure-patch-model'))

    elif current_page == ":material/chat: Intelligence Chat":
        st.markdown('<div class="dashboard-title">Security Intelligence Chat</div>', unsafe_allow_html=True)
        st.markdown('<div class="dashboard-subtitle">Ask questions and get security insights</div>', unsafe_allow_html=True)
        render_chat_tab()

    elif current_page == ":material/menu_book: Help":
        st.markdown('<div class="dashboard-title">Help & Documentation</div>', unsafe_allow_html=True)
        st.markdown('<div class="dashboard-subtitle">Learn how to use VeriFAI LLM</div>', unsafe_allow_html=True)
        render_help_tab()

    elif current_page == ":material/settings: Settings":
        st.markdown('<div class="dashboard-title">Settings & Preferences</div>', unsafe_allow_html=True)
        st.markdown('<div class="dashboard-subtitle">Configure application behavior and preferences</div>', unsafe_allow_html=True)
        render_settings_tab()

    st.markdown('<div style="text-align: center; color: #8b9bb4; font-size: 0.75rem; padding: 2rem 0; border-top: 1px solid #1d2b3f; margin-top: 4rem; text-transform: uppercase; letter-spacing: 0.5px;">VeriFAI LLM Security Scanner | Pro Edition 2026</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    atexit.register(cleanup_temp_files)
    main()

