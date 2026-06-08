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
        --color-bg-dark: #0a0c0f;
        --color-bg-medium: #1a1d24;
        --color-bg-light: #20242e;
        --color-border: rgba(255,255,255,0.06);
        --color-text: #e8eaf0;
        --color-text-secondary: #8b909e;
        --color-success: #00e5a0;
        --color-error: #ff4060;
        --transition-smooth: 0.3s ease-out;
    }

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'DM Sans', sans-serif;
        background-color: var(--color-bg-dark);
        color: var(--color-text);
        margin: 0 !important;
        padding: 0 !important;
    }

    /* ====================================================================
       OVERLAY SIDEBAR SYSTEM
       ==================================================================== */
    
    /* 1. Main Content: Full width, zero offset */
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewBlockContainer"],
    [data-testid="stMain"] {
        margin-left: 0 !important;
        width: 100vw !important;
        max-width: 100vw !important;
    }

    .main .block-container {
        padding-top: 1rem !important;
        max-width: 1200px !important;
        margin: 0 auto !important;
    }

    /* 2. Sidebar: High-Z Overlay Drawer */
    section[data-testid="stSidebar"] {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        height: 100vh !important;
        width: 300px !important;
        min-width: 300px !important;
        z-index: 9999999 !important;
        background-color: var(--color-bg-medium) !important;
        border-right: 1px solid var(--color-border) !important;
        box-shadow: 20px 0 60px rgba(0,0,0,0.8) !important;
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    /* Streamlit's native collapsed state styling */
    [data-testid="stSidebar"][aria-expanded="false"] {
        transform: translateX(-100%) !important;
        visibility: hidden !important;
    }
    
    [data-testid="stSidebar"][aria-expanded="true"] {
        transform: translateX(0) !important;
        visibility: visible !important;
    }

    /* Ensure sidebar internal content fits */
    [data-testid="stSidebarUserContent"] {
        padding: 2rem 1rem !important;
    }

    /* Hide standard clutter but keep toggle button clickable in DOM */
    [data-testid="stHeader"], 
    .stAppHeader,
    [data-testid="stFooter"],
    [data-testid="stDecoration"] {
        display: none !important;
    }

    /* Keep the native toggle hidden but in the flow for JS interaction */
    [data-testid="stSidebarCollapsedControl"] {
        opacity: 0 !important;
        pointer-events: none !important;
    }

    /* ====================================================================
       TOPBAR & NAVIGATION
       ==================================================================== */
    .topbar {
        background: var(--color-bg-medium);
        border: 1px solid var(--color-border);
        border-radius: 12px;
        padding: 0.6rem 1rem;
        margin-bottom: 1.5rem;
        position: sticky;
        top: 0;
        z-index: 9999;
        display: flex;
        align-items: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }

    .page-header {
        font-family: 'Syne', sans-serif;
        font-size: 1.3rem;
        font-weight: 800;
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
        transition: all 0.2s ease-out !important;
    }

    [data-testid="stButton"] button[kind="primary"] {
        background-color: var(--color-primary) !important;
        color: #000 !important;
        border: none !important;
    }

    [data-testid="stButton"] button[kind="primary"]:hover {
        background-color: #00ffff !important;
        transform: translateY(-1px);
    }

    [data-testid="stButton"] button[kind="secondary"] {
        background-color: transparent !important;
        border: 1px solid var(--color-border) !important;
        color: var(--color-text) !important;
    }

    /* TABS */
    [data-testid="stTabs"] [role="tablist"] {
        border-bottom: 1px solid var(--color-border);
    }

    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        color: var(--color-primary);
        border-bottom: 2px solid var(--color-primary);
    }
    </style>
    """, unsafe_allow_html=True)
