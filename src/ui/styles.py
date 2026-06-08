import streamlit as st

def apply_custom_styles():
    """Apply professional malware analyzer theme matching system configuration dashboard."""
    st.markdown("""
    <style>
    /* ====================================================================
       GLOBAL RESET & TYPOGRAPHY
       ==================================================================== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500;600&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

    :root {
        --color-primary: #00e5ff;
        --color-primary-dark: #00b8cc;
        --color-bg-dark: #0a0c0f;
        --color-bg-medium: #1a1d24;
        --color-bg-light: #20242e;
        --color-border: rgba(255,255,255,0.06);
        --color-text: #e8eaf0;
        --color-text-secondary: #8b909e;
        --color-success: #00e5a0;
        --color-warning: #ffaa00;
        --color-error: #ff4060;
        --color-danger: #ef4444;
        --transition-fast: 0.15s ease-out;
        --transition-smooth: 0.3s ease-out;
    }

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'DM Sans', sans-serif;
        background-color: var(--color-bg-dark);
        color: var(--color-text);
        scroll-behavior: smooth;
    }

    /* ====================================================================
       HIDE STANDARD STREAMLIT CLUTTER & REMOVE TOP SPACING
       ==================================================================== */
    [data-testid="stHeader"], 
    .stAppHeader,
    [data-testid="stFooter"],
    [data-testid="stDecoration"] {
        display: none !important;
    }

    /* Tighten up the top spacing */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 1200px;
        margin: 0 auto;
    }

    /* ====================================================================
       PROFESSIONAL SIDEBAR
       ==================================================================== */
    [data-testid="stSidebar"] {
        background-color: var(--color-bg-medium) !important;
        border-right: 1px solid var(--color-border) !important;
        min-width: 300px !important;
        max-width: 300px !important;
        transition: all var(--transition-smooth) !important;
    }

    /* Sidebar toggle button styling */
    [data-testid="stSidebarCollapsedControl"] {
        background-color: var(--color-bg-light) !important;
        border-radius: 8px !important;
        color: var(--color-primary) !important;
        top: 10px !important;
        left: 10px !important;
        z-index: 10000 !important;
        border: 1px solid var(--color-border) !important;
    }

    /* ====================================================================
       TOPBAR & NAVIGATION
       ==================================================================== */
    .topbar {
        background: var(--color-bg-medium);
        border: 1px solid var(--color-border);
        border-radius: 12px;
        padding: 0.5rem 1rem;
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
        color: var(--color-text);
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        color: var(--color-text-secondary);
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
    .status-dot.ready { background: var(--color-success); }
    .status-dot.error { background: var(--color-error); }

    /* ====================================================================
       BUTTONS
       ==================================================================== */
    button {
        border-radius: 6px !important;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.5px;
        transition: all var(--transition-fast) !important;
    }

    /* Primary buttons */
    [data-testid="stButton"] button[kind="primary"] {
        background-color: var(--color-primary) !important;
        color: #000 !important;
        border: none !important;
        box-shadow: 0 0 10px rgba(0, 229, 255, 0.3);
    }

    [data-testid="stButton"] button[kind="primary"]:hover {
        background-color: #00ffff !important;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.6);
        transform: translateY(-1px);
    }

    /* Secondary buttons */
    [data-testid="stButton"] button[kind="secondary"] {
        background-color: transparent !important;
        border: 1px solid var(--color-border) !important;
        color: var(--color-text) !important;
    }

    [data-testid="stButton"] button[kind="secondary"]:hover {
        border-color: var(--color-primary) !important;
        color: var(--color-primary) !important;
    }

    /* ====================================================================
       CARDS & METRICS
       ==================================================================== */
    .stMetric {
        background-color: var(--color-bg-medium) !important;
        padding: 1rem !important;
        border-radius: 8px !important;
        border: 1px solid var(--color-border) !important;
    }

    .model-chip {
        margin-top: 1rem;
        padding: 0.75rem;
        background: var(--color-bg-light);
        border: 1px solid var(--color-border);
        border-radius: 8px;
    }

    /* ====================================================================
       TABS
       ==================================================================== */
    [data-testid="stTabs"] [role="tablist"] {
        border-bottom: 1px solid var(--color-border);
        gap: 1.5rem;
    }

    [data-testid="stTabs"] [role="tab"] {
        color: var(--color-text-secondary);
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.8rem;
    }

    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        color: var(--color-primary);
        border-bottom: 2px solid var(--color-primary);
    }
    </style>
    """, unsafe_allow_html=True)
