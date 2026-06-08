import streamlit as st

def apply_custom_styles():
    """Restore native sidebar visibility and apply professional theme."""
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
    }

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'DM Sans', sans-serif;
        background-color: var(--color-bg-dark);
        color: var(--color-text);
    }

    /* ====================================================================
       RESTORE NATIVE SIDEBAR
       ==================================================================== */
    
    /* Ensure the main container behaves normally with the sidebar */
    [data-testid="stAppViewContainer"] {
        display: flex;
        flex-direction: row;
    }

    [data-testid="stSidebar"] {
        background-color: var(--color-bg-medium) !important;
        border-right: 1px solid var(--color-border) !important;
        visibility: visible !important;
        display: block !important;
        min-width: 300px !important;
        max-width: 300px !important;
    }

    /* Ensure sidebar content is visible */
    [data-testid="stSidebarUserContent"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }

    /* ====================================================================
       HIDE STANDARD STREAMLIT CLUTTER
       ==================================================================== */
    [data-testid="stHeader"], 
    .stAppHeader,
    [data-testid="stFooter"],
    [data-testid="stDecoration"] {
        display: none !important;
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
        z-index: 999;
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
    </style>
    """, unsafe_allow_html=True)
