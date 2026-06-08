import streamlit as st

def apply_custom_styles():
    """Apply professional malware analyzer theme with Overlay Sidebar functionality."""
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
       OVERLAY SIDEBAR SYSTEM
       ==================================================================== */
    
    /* 1. Main Content: Force it to take full width and NEVER shift */
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewBlockContainer"] {
        margin-left: 0 !important;
        width: 100% !important;
        max-width: 100% !important;
    }
    
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 1200px !important;
        margin: 0 auto !important;
        transition: none !important;
    }

    /* 2. Sidebar: Force it to OVERLAP (Position Fixed) */
    [data-testid="stSidebar"] {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        height: 100vh !important;
        z-index: 1000001 !important; /* Above everything */
        background-color: var(--color-bg-medium) !important;
        border-right: 1px solid var(--color-border) !important;
        box-shadow: 20px 0 50px rgba(0,0,0,0.8) !important;
        min-width: 320px !important;
        max-width: 320px !important;
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    /* Handle Streamlit's native collapsed state classes if they exist */
    [data-testid="stSidebar"][aria-expanded="false"] {
        transform: translateX(-105%) !important;
    }
    
    [data-testid="stSidebar"][aria-expanded="true"] {
        transform: translateX(0) !important;
    }

    /* Ensure the sidebar's internal content scrolls correctly */
    [data-testid="stSidebarUserContent"] {
        padding-top: 2rem !important;
    }

    /* ====================================================================
       HIDE STANDARD STREAMLIT CLUTTER
       ==================================================================== */
    [data-testid="stHeader"], 
    .stAppHeader,
    [data-testid="stFooter"],
    [data-testid="stDecoration"],
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
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
