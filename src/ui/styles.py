import streamlit as st

def apply_custom_styles():
    """Apply professional malware analyzer theme matching system configuration dashboard."""
    st.markdown("""
    <style>
    /* ====================================================================
       GLOBAL RESET & TYPOGRAPHY
       ==================================================================== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

    :root {
        --color-primary: #00e5ff;
        --color-primary-dark: #00b8cc;
        --color-bg-dark: #070b14;
        --color-bg-medium: #0a111c;
        --color-bg-light: #0f182b;
        --color-border: #1d2b3f;
        --color-text: #e2e8f0;
        --color-text-secondary: #8b9bb4;
        --color-success: #00e676;
        --color-warning: #f59e0b;
        --color-error: #ff3b3b;
        --color-danger: #ef4444;
        --transition-fast: 0.15s ease-out;
        --transition-smooth: 0.3s ease-out;
    }

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: var(--color-bg-dark);
        color: var(--color-text);
        scroll-behavior: smooth;
    }

    h1, h2, h3, h4, h5, h6 {
        font-weight: 600;
        letter-spacing: 0.5px;
        color: var(--color-text);
    }

    /* ====================================================================
       ACCESSIBILITY
       ==================================================================== */
    button:focus-visible,
    input:focus-visible,
    select:focus-visible,
    textarea:focus-visible {
        outline: 2px solid var(--color-primary);
        outline-offset: 2px;
    }

    @media (prefers-reduced-motion: reduce) {
        * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }

    /* ====================================================================
       HIDE STANDARD STREAMLIT CLUTTER
       ==================================================================== */
    [data-testid="stHeader"],
    [data-testid="stFooter"],
    [data-testid="stDecoration"] {
        display: none !important;
    }

    /* ====================================================================
       TOP BAR STYLING
       ==================================================================== */
    [data-testid="stAppViewContainer"] > .main {
        background: linear-gradient(180deg, #070b14 0%, #0a0f1a 50%, #070b14 100%);
    }

    /* ====================================================================
       PROFESSIONAL SIDEBAR
       ==================================================================== */
    [data-testid="stSidebar"] {
        background-color: var(--color-bg-medium) !important;
        border-right: 1px solid var(--color-border) !important;
    }

    .sidebar-header {
        padding: 1.5rem;
        text-align: center;
        background: linear-gradient(135deg, #0a111c 0%, #0f182b 100%);
        border-bottom: 2px solid var(--color-border);
        margin: -1rem -1rem 1.5rem -1rem;
    }

    .sidebar-header h1 {
        font-size: 1.1rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: var(--color-text);
        margin: 0;
    }

    /* ====================================================================
       UPLOAD SECTION STYLING
       ==================================================================== */
    .upload-section {
        background-color: var(--color-bg-light);
        border: 2px dashed var(--color-primary);
        border-radius: 8px;
        padding: 2rem 1.5rem;
        text-align: center;
        margin: 1.5rem 0;
        transition: all var(--transition-smooth);
    }

    .upload-section:hover {
        background-color: rgba(0, 229, 255, 0.05);
        border-color: #00ffff;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.15);
    }

    .upload-section-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--color-primary);
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .upload-section-icon {
        font-size: 2.5rem;
        margin: 0.5rem 0;
    }

    /* ====================================================================
       PROFESSIONAL NAVIGATION BAR
       ==================================================================== */
    .top-nav-bar {
        background-color: var(--color-bg-medium);
        border-bottom: 1px solid var(--color-border);
        padding: 1rem 2rem;
        margin: -2rem -2rem 2rem -2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .top-nav-title {
        font-size: 1.5rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: var(--color-text);
    }

    .top-nav-actions {
        display: flex;
        gap: 1rem;
    }

    .nav-container {
        background-color: transparent;
        padding: 0;
        border-bottom: none;
        display: flex;
        gap: 2rem;
        justify-content: flex-start;
        flex-wrap: wrap;
        margin-bottom: 1.5rem;
    }

    .nav-container [data-testid="stButton"] {
        flex: 0 1 auto;
    }

    [data-testid="stButton"] button {
        transition: all var(--transition-smooth) !important;
        font-weight: 500;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        font-size: 0.8rem;
    }

    .nav-container button {
        background: transparent !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        padding: 0.75rem 0 !important;
        color: var(--color-text-secondary) !important;
    }

    .nav-container button:hover {
        color: var(--color-primary) !important;
        border-bottom-color: var(--color-primary) !important;
    }

    /* ====================================================================
       STATUS CARDS (Configuration)
       ==================================================================== */
    .config-card {
        background-color: var(--color-bg-light);
        border: 1px solid var(--color-border);
        border-radius: 6px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all var(--transition-smooth);
    }

    .config-card:hover {
        border-color: var(--color-primary);
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.1);
    }

    .config-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--color-border);
    }

    .config-card-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--color-text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .config-card-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.3rem;
        font-weight: 600;
        color: var(--color-primary);
    }

    /* ====================================================================
       METRIC CARDS & BLOCK CONTAINERS
       ==================================================================== */
    .stMetric {
        background-color: var(--color-bg-light) !important;
        padding: 1.5rem !important;
        border-radius: 6px !important;
        border: 1px solid var(--color-border) !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }

    .stMetric:hover {
        border-color: var(--color-primary);
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.15);
    }

    .stMetric label {
        color: var(--color-text-secondary) !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }

    .stMetric [data-testid="stMetricValue"] {
        color: var(--color-primary) !important;
        font-family: 'JetBrains Mono', monospace;
        font-size: 2rem !important;
        font-weight: 700;
    }

    /* ====================================================================
       CONTAINER BLOCKS AS PANELS
       ==================================================================== */
    .stContainer {
        background-color: var(--color-bg-light);
        border: 1px solid var(--color-border);
        border-radius: 6px;
        padding: 1.5rem;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    }

    /* ====================================================================
       TABS & EXPANDERS
       ==================================================================== */
    [data-testid="stTabs"] [role="tablist"] {
        border-bottom: 1px solid var(--color-border);
        gap: 2rem;
        background-color: transparent;
    }

    [data-testid="stTabs"] [role="tab"] {
        padding: 1rem 0;
        border-bottom: 2px solid transparent;
        color: var(--color-text-secondary);
        font-weight: 500;
        text-transform: uppercase;
        font-size: 0.8rem;
        letter-spacing: 0.5px;
        background: transparent;
    }

    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        color: var(--color-primary);
        border-bottom-color: var(--color-primary);
    }

    .streamlit-expanderHeader {
        background-color: var(--color-bg-light);
        border: 1px solid var(--color-border);
        border-radius: 6px;
        color: var(--color-text);
        font-size: 0.9rem;
        text-transform: uppercase;
        font-weight: 600;
    }

    /* ====================================================================
       INPUT ELEMENTS
       ==================================================================== */
    input, select, textarea, [data-testid="stTextInput"] input, [data-testid="stSelectbox"] select {
        background-color: #070b14 !important;
        color: var(--color-text) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: 4px !important;
        padding: 0.75rem 1rem !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important;
        transition: all var(--transition-fast) !important;
    }

    input:focus, select:focus, textarea:focus,
    [data-testid="stTextInput"] input:focus,
    [data-testid="stSelectbox"] select:focus {
        border-color: var(--color-primary) !important;
        box-shadow: 0 0 8px rgba(0, 229, 255, 0.3) !important;
        background-color: rgba(0, 229, 255, 0.05) !important;
    }

    /* ====================================================================
       MAIN CONTENT AREA
       ==================================================================== */
    .main .block-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }

    /* ====================================================================
       CODE BLOCKS
       ==================================================================== */
    [data-testid="stCodeBlock"] {
        border-radius: 6px !important;
        border: 1px solid var(--color-border) !important;
        background-color: #05080f !important;
    }

    [data-testid="stCodeBlock"] pre {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
    }

    /* ====================================================================
       ALERTS & NOTIFICATIONS
       ==================================================================== */
    [data-testid="stAlert"] {
        border-radius: 6px !important;
        border: 1px solid !important;
        background-color: rgba(0, 0, 0, 0.3) !important;
        font-family: 'Inter', sans-serif;
        padding: 1rem !important;
    }

    [data-testid="stAlert"][data-alert-type="info"] {
        border-color: var(--color-primary) !important;
        color: var(--color-primary) !important;
        background-color: rgba(0, 229, 255, 0.08) !important;
    }

    [data-testid="stAlert"][data-alert-type="warning"] {
        border-color: var(--color-warning) !important;
        color: var(--color-warning) !important;
        background-color: rgba(245, 158, 11, 0.08) !important;
    }

    [data-testid="stAlert"][data-alert-type="error"] {
        border-color: var(--color-error) !important;
        color: var(--color-error) !important;
        background-color: rgba(255, 59, 59, 0.08) !important;
    }

    [data-testid="stAlert"][data-alert-type="success"] {
        border-color: var(--color-success) !important;
        color: var(--color-success) !important;
        background-color: rgba(0, 230, 118, 0.08) !important;
    }

    /* ====================================================================
       BUTTONS
       ==================================================================== */
    button {
        border-radius: 4px !important;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.8rem;
        letter-spacing: 0.5px;
        transition: all var(--transition-fast) !important;
    }

    /* Primary buttons */
    [data-testid="stButton"] button[kind="primary"] {
        background-color: var(--color-primary) !important;
        color: #000 !important;
        border: none !important;
        box-shadow: 0 0 10px rgba(0, 229, 255, 0.3);
        font-weight: 700;
    }

    [data-testid="stButton"] button[kind="primary"]:hover {
        background-color: #00ffff !important;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.6);
        transform: translateY(-2px);
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
        box-shadow: 0 0 10px rgba(0, 229, 255, 0.15);
    }

    /* ====================================================================
       DATAFRAMES / TABLES
       ==================================================================== */
    [data-testid="stDataFrame"] {
        background-color: var(--color-bg-light) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: 6px !important;
        overflow: hidden;
    }

    [data-testid="stDataFrame"] table {
        color: var(--color-text) !important;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        width: 100%;
    }

    [data-testid="stDataFrame"] th {
        background-color: var(--color-bg-dark) !important;
        color: var(--color-text-secondary) !important;
        text-transform: uppercase;
        border-bottom: 2px solid var(--color-border) !important;
        font-weight: 700;
        padding: 1rem !important;
        letter-spacing: 0.5px;
    }

    [data-testid="stDataFrame"] td {
        border-bottom: 1px solid var(--color-border) !important;
        padding: 0.75rem 1rem !important;
    }

    [data-testid="stDataFrame"] tr:hover td {
        background-color: rgba(0, 229, 255, 0.05) !important;
    }

    /* ====================================================================
       SCROLLBAR CUSTOMIZATION
       ==================================================================== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--color-bg-dark);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--color-border);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--color-primary);
    }

    /* ====================================================================
       CUSTOM DASHBOARD COMPONENTS
       ==================================================================== */
    .dashboard-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: var(--color-text);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .dashboard-subtitle {
        font-size: 0.9rem;
        color: var(--color-text-secondary);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 2rem;
    }

    .status-badge {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 3px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    .status-running {
        background-color: rgba(0, 230, 118, 0.15);
        color: var(--color-success);
        border: 1px solid rgba(0, 230, 118, 0.5);
    }

    .status-malicious {
        background-color: rgba(255, 59, 59, 0.15);
        color: var(--color-error);
        border: 1px solid rgba(255, 59, 59, 0.5);
    }

    .status-analyzing {
        background-color: rgba(0, 229, 255, 0.15);
        color: var(--color-primary);
        border: 1px solid rgba(0, 229, 255, 0.5);
    }

    .status-clean {
        background-color: rgba(0, 230, 118, 0.15);
        color: var(--color-success);
        border: 1px solid rgba(0, 230, 118, 0.5);
    }

    .status-warning {
        background-color: rgba(245, 158, 11, 0.15);
        color: var(--color-warning);
        border: 1px solid rgba(245, 158, 11, 0.5);
    }

    /* ====================================================================
       FILE UPLOAD DROPZONE
       ==================================================================== */
    [data-testid="stFileUploader"] {
        background-color: var(--color-bg-light) !important;
        border: 2px dashed var(--color-primary) !important;
        border-radius: 6px !important;
        padding: 2rem !important;
    }

    [data-testid="stFileUploader"] label {
        color: var(--color-text) !important;
        font-weight: 600;
        text-transform: uppercase;
    }

    /* ====================================================================
       RESPONSIVE DESIGN (Media Queries)
       ==================================================================== */
    @media (max-width: 1024px) {
        .main .block-container {
            padding: 1.5rem;
        }
        .top-nav-bar {
            padding: 1rem;
            margin: -1.5rem -1.5rem 1.5rem -1.5rem;
        }
    }

    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
        
        .top-nav-bar {
            flex-direction: column;
            align-items: flex-start;
            gap: 1rem;
            margin: -1rem -1rem 1rem -1rem;
            padding: 1rem;
        }
        
        .top-nav-actions {
            width: 100%;
            justify-content: flex-start;
            flex-wrap: wrap;
        }

        .dashboard-title {
            font-size: 1.5rem;
        }
        
        .dashboard-subtitle {
            font-size: 0.8rem;
        }

        .nav-container {
            gap: 1rem;
            justify-content: flex-start;
        }
        
        [data-testid="stTabs"] [role="tablist"] {
            gap: 1rem;
            flex-wrap: wrap;
        }
        
        .stMetric {
            padding: 1rem !important;
        }
        
        .stMetric [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
        }
        
        .upload-section {
            padding: 1.5rem 1rem;
        }
    }

    @media (max-width: 480px) {
        .main .block-container {
            padding: 0.5rem;
        }
        
        .top-nav-title {
            font-size: 1.2rem;
        }
        
        .top-nav-actions {
            flex-direction: column;
            width: 100%;
            gap: 0.5rem;
        }
        
        .nav-container {
            flex-direction: column;
            align-items: stretch;
        }
        
        .nav-container [data-testid="stButton"] button {
            width: 100%;
        }

        .stMetric [data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
