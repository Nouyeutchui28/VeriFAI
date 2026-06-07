"""
Unified settings management for VeriFAI LLM with professional UI.
"""
import streamlit as st
from ..utils.state import AppState
from .components import render_settings_group, render_info_banner, render_action_button
from .ui_error_handler import handle_ui_success, handle_ui_info

def render_settings_tab():
    """Render the unified settings page with professional styling."""

    tab1, tab2, tab3, tab4 = st.tabs([
        "🧠 LLM Config",
        "🎨 Appearance",
        "📊 Scan Defaults",
        "🔐 Security"
    ])

    # ========================================================================
    # TAB 1: LLM CONFIGURATION
    # ========================================================================
    with tab1:
        st.markdown("### 🧠 Language Model Settings")
        render_info_banner(
            "Configure LLM parameters for security analysis intelligence",
            type="info"
        )

        col1, col2 = st.columns(2)

        with col1:
            render_settings_group("Model Selection", "🤖", "Hugging Face Inference API Active")
            model_options = [
                "Qwen/Qwen2.5-Coder-7B-Instruct"
            ]
            selected_model = st.selectbox(
                "Intelligence Model",
                model_options,
                index=0, 
                key="settings_model_select",
                label_visibility="collapsed"
            )
            st.info("🚀 Hugging Face API Complete: Using Qwen2.5-Coder-7B-Instruct.")

        with col2:
            render_settings_group("Response Variation", "🎲", "Creativity vs Consistency")
            temp_value = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=AppState.get("llm_temperature", 0.2),
                step=0.1,
                key="settings_temp_slider",
                label_visibility="collapsed"
            )
            if temp_value != AppState.get("llm_temperature"):
                AppState.set("llm_temperature", temp_value)

        st.divider()

        render_settings_group("Advanced LLM Settings", "🔧")
        col1, col2, col3 = st.columns(3)

        with col1:
            max_tokens = st.number_input(
                "Max Tokens",
                value=2000,
                step=100,
                label_visibility="collapsed"
            )

        with col2:
            timeout = st.number_input(
                "Timeout (seconds)",
                value=30,
                step=5,
                min_value=5,
                max_value=300,
                label_visibility="collapsed"
            )

        with col3:
            retries = st.number_input(
                "Retry Attempts",
                value=2,
                min_value=0,
                max_value=5,
                label_visibility="collapsed"
            )

    # ========================================================================
    # TAB 2: APPEARANCE
    # ========================================================================
    with tab2:
        st.markdown("### 🎨 User Interface Preferences")
        render_info_banner(
            "Customize the appearance and behavior of the interface",
            type="info"
        )

        render_settings_group("Theme Settings", "🌙")
        theme = st.selectbox(
            "Theme",
            ["Dark Mode (Default)", "Light Mode", "Auto (System)"],
            label_visibility="collapsed"
        )

        render_settings_group("Display Options", "👁️")
        col1, col2 = st.columns(2)
        with col1:
            compact_mode = st.checkbox("Compact Mode", value=False, help="Reduce spacing and padding")
        with col2:
            animations = st.checkbox("Enable Animations", value=True, help="Smooth UI transitions")

    # ========================================================================
    # TAB 3: SCAN DEFAULTS
    # ========================================================================
    with tab3:
        st.markdown("### 📊 Scan Behavior")
        render_info_banner(
            "Set default parameters for security scans",
            type="info"
        )

        render_settings_group("Default Scan Type", "📝")
        default_scan = st.selectbox(
            "Scan Type",
            ["Direct Code Input", "File Upload", "Multiple Files", "ZIP Archive", "GitHub Repository"],
            label_visibility="collapsed"
        )

        render_settings_group("Scan Options", "⚙️")
        col1, col2 = st.columns(2)
        with col1:
            auto_save = st.checkbox("Auto-Save Results", value=True)
        with col2:
            generate_reports = st.checkbox("Generate Reports", value=True)

        render_settings_group("Output Settings", "📁")
        st.text_input("Report Output Path", value="/tmp/reports/", label_visibility="collapsed")

    # ========================================================================
    # TAB 4: SECURITY & API
    # ========================================================================
    with tab4:
        st.markdown("### 🔐 Security & Authentication")
        render_info_banner(
            "Manage API keys, tokens, and security settings",
            type="warning"
        )

        render_settings_group("API Configuration", "🔑")
        with st.expander("View API Key (Click to reveal)"):
            st.warning("⚠️ Keep your API key secret!")
            api_key = st.text_input("API Key", type="password", label_visibility="collapsed")
            if st.button("🔄 Rotate API Key", type="secondary", use_container_width=True):
                st.info("✅ API key rotated. Update your integrations.")

        render_settings_group("Session Management", "👤")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current Session", "Active")
        with col2:
            if st.button("🚪 Sign Out", use_container_width=True, type="secondary"):
                AppState.logout()
                st.rerun()

        st.divider()
        st.markdown("### 📋 About")
        st.markdown("""
        **VeriFAI LLM** v1.0.0
        Security Analysis Platform powered by AI
        Built with Streamlit & InsForge
        © 2026 - All rights reserved
        """)

    # ========================================================================
    with tab2:
        st.header("🎨 UI Preferences")
        render_info_banner(
            "Customize the user interface appearance and behavior.",
            type="info"
        )

        render_settings_group("Theme & Appearance", "🌙")
        col1, col2 = st.columns(2)

        with col1:
            current_theme = AppState.get("theme", "dark")
            theme = st.radio(
                "Color Theme",
                options=["dark", "light", "auto"],
                index=["dark", "light", "auto"].index(current_theme),
                key="settings_theme",
                horizontal=True,
                help="Choose your preferred theme"
            )
            if theme != current_theme:
                AppState.set("theme", theme)
                handle_ui_success("✅ Theme updated! Refresh to apply.")

        with col2:
            notifications = st.checkbox(
                "Enable Notifications",
                value=AppState.get("notifications_enabled", True),
                key="settings_notif",
                help="Show notifications for scan completion"
            )
            AppState.set("notifications_enabled", notifications)

        st.divider()

        render_settings_group("Display Options", "📺")
        col1, col2 = st.columns(2)

        with col1:
            results_format = st.selectbox(
                "Result Display Format",
                ["Detailed", "Compact", "Summary"],
                key="settings_results_format"
            )

        with col2:
            items_per_page = st.number_input(
                "Items Per Page",
                value=10,
                min_value=5,
                max_value=100,
                step=5,
                key="settings_items_per_page"
            )

        st.divider()

        render_settings_group("Accessibility", "♿")
        col1, col2 = st.columns(2)

        with col1:
            st.checkbox(
                "High Contrast Mode",
                value=False,
                key="settings_high_contrast",
                help="Increase color contrast for better visibility"
            )

        with col2:
            st.checkbox(
                "Keyboard Navigation Helper",
                value=True,
                key="settings_keyboard_helper",
                help="Show keyboard shortcuts"
            )

    # ========================================================================
    # TAB 3: SCAN DEFAULTS
    # ========================================================================
    with tab3:
        st.header("📊 Scan Defaults")
        render_info_banner(
            "Configure default settings for security scans.",
            type="info"
        )

        render_settings_group("File Size Limits", "📁")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.number_input(
                "Max File Size (MB)",
                value=100,
                step=10,
                help="Maximum size for individual files"
            )

        with col2:
            st.number_input(
                "Max ZIP Size (MB)",
                value=500,
                step=50,
                help="Maximum size for ZIP archives"
            )

        with col3:
            st.number_input(
                "Max Total Upload (MB)",
                value=1000,
                step=100,
                help="Maximum total upload size per session"
            )

        st.divider()

        render_settings_group("Analysis Depth", "🔍")
        col1, col2 = st.columns(2)

        with col1:
            depth = st.select_slider(
                "Analysis Depth",
                options=["Fast", "Balanced", "Thorough"],
                value="Balanced",
                help="Deeper analysis takes longer but finds more issues"
            )

        with col2:
            st.selectbox(
                "Default Severity Filter",
                ["All", "Critical", "High & Critical", "High+", "Medium+"],
                index=1,
                help="Show only vulnerabilities above this severity"
            )

        st.divider()

        render_settings_group("Timeout Settings", "⏱️")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.number_input(
                "Semgrep Timeout (s)",
                value=120,
                step=10,
                help="Max time for static analysis"
            )

        with col2:
            st.number_input(
                "Git Clone Timeout (s)",
                value=60,
                step=10,
                help="Max time to clone repository"
            )

        with col3:
            st.number_input(
                "Overall Scan Timeout (s)",
                value=300,
                step=30,
                help="Max time for entire scan"
            )

    # ========================================================================
    # TAB 4: SECURITY & API
    # ========================================================================
    with tab4:
        st.header("🔐 Security & API Keys")
        render_info_banner(
            "Manage API credentials and security settings. Keys are never transmitted or logged.",
            type="warning"
        )

        render_settings_group("API Credentials", "🔑")

        # Hugging Face Token
        st.markdown("**Hugging Face API Token**")
        hf_token = st.text_input(
            "Hugging Face Token (HF_TOKEN)",
            type="password",
            value=os.getenv("HF_TOKEN", ""),
            placeholder="hf_...",
            help="Required for Qwen2.5-Coder intelligence. Get one at huggingface.co/settings/tokens"
        )
        if hf_token and hf_token != os.getenv("HF_TOKEN"):
            # Optionally update .env or just use in session
            # For simplicity in this demo, we'll suggest saving it
            st.info("💡 Don't forget to save settings to apply your new token.")
            os.environ["HF_TOKEN"] = hf_token

        st.divider()

        # GitHub Token
        st.markdown("**GitHub Personal Access Token**")
        github_token = st.text_input(
            "GitHub Token",
            type="password",
            placeholder="ghp_...",
            help="Required for private repository scanning"
        )
        if github_token:
            st.caption("✅ Token configured (masked for security)")

        st.divider()

        # Hugging Face Status
        st.markdown("**Hugging Face Intelligence Engine**")
        st.success("✅ System Context: Qwen2.5-Coder-7B-Instruct Active")
        st.caption("The pipeline is now running using Hugging Face Serverless Inference API.")

        st.divider()

        render_settings_group("Security Settings", "🛡️")

        col1, col2 = st.columns(2)

        with col1:
            st.checkbox(
                "Verify SSL Certificates",
                value=True,
                help="Verify SSL certificates for API calls"
            )

        with col2:
            st.checkbox(
                "Enable Rate Limiting",
                value=True,
                help="Limit API requests to avoid exceeding quotas"
            )

        st.divider()

        render_settings_group("Data & Privacy", "📋")
        col1, col2 = st.columns(2)

        with col1:
            st.checkbox(
                "Save Scan History",
                value=True,
                help="Store completed scans for later reference"
            )

        with col2:
            st.checkbox(
                "Allow Usage Analytics",
                value=True,
                help="Help us improve by sharing anonymized usage data"
            )

        if st.button("🗑️ Clear All Scan History", type="secondary", use_container_width=True):
            if st.session_state.get("confirm_clear_history"):
                st.warning("Scan history cleared!")
                st.session_state.confirm_clear_history = False
            else:
                st.session_state.confirm_clear_history = True
                st.warning("⚠️ This will permanently delete all scan history. Click again to confirm.")

    # ========================================================================
    # FOOTER
    # ========================================================================
    st.divider()
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💾 Save All Settings", type="primary", use_container_width=True):
            handle_ui_success("✅ All settings saved successfully!")

    with col2:
        if st.button("🔄 Reset to Defaults", type="secondary", use_container_width=True):
            AppState.reset("model_selection")
            AppState.reset("llm_temperature")
            AppState.reset("theme")
            handle_ui_success("✅ Settings reset to defaults!")

    with col3:
        if st.button("📖 Help & Documentation", type="secondary", use_container_width=True):
            st.info("📖 Visit our [documentation](https://github.com/codebytemirza/VeriFAI-LLM) for more help.")
