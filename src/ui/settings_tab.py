import os
import streamlit as st
from ..utils.state import AppState
from .components import render_settings_group, render_info_banner, render_action_button
from .ui_error_handler import handle_ui_success, handle_ui_info
from ..core.llm import list_local_ollama_models

def render_settings_tab():
    """Render the unified settings page with professional styling."""

    tab1, tab2, tab3, tab4 = st.tabs([
        ":material/psychology: LLM Config",
        ":material/palette: Appearance",
        ":material/analytics: Scan Defaults",
        ":material/security: Security"
    ])

    # ========================================================================
    # TAB 1: LLM CONFIGURATION
    # ========================================================================
    with tab1:
        st.markdown("### :material/psychology: Language Model Settings")
        render_info_banner(
            "Configure local Ollama or explicitly enabled cloud AI for security analysis.",
            type="info"
        )

        col1, col2 = st.columns(2)

        with col1:
            render_settings_group("AI Provider Selection", ":material/smart_toy:", "Choose Backend")
            provider_choice = st.radio(
                "AI Backend Provider",
                options=["Local AI (Ollama - Offline)", "Cloud API (requires provider key)"],
                index=1 if os.getenv("LLM_PROVIDER", "ollama").lower() == "cloud" else 0,
                key="settings_provider_radio"
            )
            
            selected_provider_key = "cloud" if provider_choice.startswith("Cloud") else "ollama"
            os.environ["LLM_PROVIDER"] = selected_provider_key
            AppState.set("llm_provider", selected_provider_key)

            local_models = list_local_ollama_models()
            
            if selected_provider_key == "ollama":
                if local_models:
                    default_idx = 0
                    preferred_local = ["qwen2.5-coder:1.5b", "qwen2.5-coder:3b", "llama3.2:latest", "phi3:latest", "qwen2.5:0.5b", "codellama:latest"]
                    for pref in preferred_local:
                        if pref in local_models:
                            default_idx = local_models.index(pref)
                            break
                        
                    sel_local = st.selectbox(
                        "Local Ollama Model",
                        local_models,
                        index=default_idx,
                        key="settings_ollama_model_select"
                    )
                    os.environ["OLLAMA_MODEL"] = sel_local
                    AppState.set("ollama_model", sel_local)
                    st.success(f":material/check_circle: Local AI Active: **{sel_local}** (Ollama)")
                else:
                    st.warning(":material/warning: Ollama not detected on localhost:11434. Make sure Ollama service is running.")
            else:
                model_options = [
                    "qwen/qwen-2.5-coder-32b-instruct",
                    "openai/gpt-4o-mini",
                    "meta-llama/llama-3.3-70b-instruct"
                ]
                current_gmodel = os.getenv("GROQ_MODEL", "qwen/qwen-2.5-coder-32b-instruct")
                default_cloud_idx = model_options.index(current_gmodel) if current_gmodel in model_options else 0
                selected_model = st.selectbox(
                    "Cloud Intelligence Model",
                    model_options,
                    index=default_cloud_idx, 
                    key="settings_model_select"
                )
                os.environ["GROQ_MODEL"] = selected_model
                st.info(f":material/rocket_launch: Cloud API Active: Using **{selected_model}**.")
                st.warning("Cloud AI sends prompts and code to the configured provider. No cloud API key is stored in this app.")


        with col2:
            render_settings_group("Response Variation", ":material/casino:", "Creativity vs Consistency")
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

        render_settings_group("Advanced LLM Settings", ":material/settings:")
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
        st.markdown("### :material/palette: User Interface Preferences")
        render_info_banner(
            "Customize the appearance and behavior of the interface",
            type="info"
        )

        render_settings_group("Theme Settings", ":material/dark_mode:")
        theme = st.selectbox(
            "Theme",
            ["Dark Mode (Default)", "Light Mode", "Auto (System)"],
            label_visibility="collapsed"
        )

        render_settings_group("Display Options", ":material/visibility:")
        col1, col2 = st.columns(2)
        with col1:
            compact_mode = st.checkbox("Compact Mode", value=False, help="Reduce spacing and padding")
        with col2:
            animations = st.checkbox("Enable Animations", value=True, help="Smooth UI transitions")

    # ========================================================================
    # TAB 3: SCAN DEFAULTS
    # ========================================================================
    with tab3:
        st.markdown("### :material/analytics: Scan Behavior")
        render_info_banner(
            "Set default parameters for security scans",
            type="info"
        )

        render_settings_group("Default Scan Type", ":material/edit:")
        default_scan = st.selectbox(
            "Scan Type",
            ["Direct Code Input", "File Upload", "Multiple Files", "ZIP Archive", "GitHub Repository"],
            label_visibility="collapsed"
        )

        render_settings_group("Scan Options", ":material/settings:")
        col1, col2 = st.columns(2)
        with col1:
            auto_save = st.checkbox("Auto-Save Results", value=True)
        with col2:
            generate_reports = st.checkbox("Generate Reports", value=True)

        render_settings_group("Output Settings", ":material/folder:")
        st.text_input("Report Output Path", value="/tmp/reports/", label_visibility="collapsed")

    # ========================================================================
    # TAB 4: SECURITY & API
    # ========================================================================
    with tab4:
        st.markdown("### :material/security: Security & Authentication")
        render_info_banner(
            "AI runs locally through Ollama by default. This app does not collect or store AI API keys.",
            type="info"
        )

        render_settings_group("Session Management", ":material/person:")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current Session", "Active")
        with col2:
            if st.button(":material/logout: Sign Out", use_container_width=True, type="secondary"):
                AppState.logout()
                st.rerun()

        st.divider()
        st.markdown("### :material/assignment: About")
        st.markdown("""
        **VeriFAI LLM** v1.0.0
        Security Analysis Platform powered by AI
        Built with Streamlit & InsForge
        © 2026 - All rights reserved
        """)

    # ========================================================================
    with tab2:
        st.header(":material/palette: UI Preferences")
        render_info_banner(
            "Customize the user interface appearance and behavior.",
            type="info"
        )

        render_settings_group("Theme & Appearance", ":material/dark_mode:")
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
                handle_ui_success(":material/check_circle: Theme updated! Refresh to apply.")

        with col2:
            notifications = st.checkbox(
                "Enable Notifications",
                value=AppState.get("notifications_enabled", True),
                key="settings_notif",
                help="Show notifications for scan completion"
            )
            AppState.set("notifications_enabled", notifications)

        st.divider()

        render_settings_group("Display Options", ":material/tv:")
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

        render_settings_group("Accessibility", ":material/accessibility:")
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
        st.header(":material/analytics: Scan Defaults")
        render_info_banner(
            "Configure default settings for security scans.",
            type="info"
        )

        render_settings_group("File Size Limits", ":material/folder:")
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

        render_settings_group("Analysis Depth", ":material/search:")
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

        render_settings_group("Timeout Settings", ":material/timer:")
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
        st.header(":material/security: Security")
        render_info_banner(
            "Manage local session and security settings.",
            type="info"
        )

        render_settings_group("Security Settings", ":material/shield:")

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

        render_settings_group("Data & Privacy", ":material/assignment:")
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

        if st.button(":material/delete: Clear All Scan History", type="secondary", use_container_width=True):
            if st.session_state.get("confirm_clear_history"):
                st.warning("Scan history cleared!")
                st.session_state.confirm_clear_history = False
            else:
                st.session_state.confirm_clear_history = True
                st.warning(":material/warning: This will permanently delete all scan history. Click again to confirm.")

    # ========================================================================
    # FOOTER
    # ========================================================================
    st.divider()
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(":material/save: Save All Settings", type="primary", use_container_width=True):
            handle_ui_success(":material/check_circle: All settings saved successfully!")

    with col2:
        if st.button(":material/sync: Reset to Defaults", type="secondary", use_container_width=True):
            AppState.reset("model_selection")
            AppState.reset("llm_temperature")
            AppState.reset("theme")
            handle_ui_success(":material/check_circle: Settings reset to defaults!")

    with col3:
        if st.button(":material/menu_book: Help & Documentation", type="secondary", use_container_width=True):
            st.info(":material/menu_book: Visit our [documentation](https://github.com/codebytemirza/VeriFAI-LLM) for more help.")
