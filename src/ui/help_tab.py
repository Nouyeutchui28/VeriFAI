"""
Help, documentation, and onboarding for VeriFAI LLM.
"""
import streamlit as st
from .components import render_info_banner, render_settings_group

def render_help_tab():
    """Render the help and documentation page with professional design."""

    tab1, tab2, tab3, tab4 = st.tabs([
        "🚀 Quick Start",
        "❓ FAQ",
        "⌨️ Shortcuts",
        "🔗 Resources"
    ])

    with tab1:
        st.header("🚀 Getting Started")

        with st.expander("**📝 Step 1: Basic Scanning (2 min)**", expanded=True):
            st.markdown("""
            1. Navigate to **Security Scanner**
            2. Choose input method:
               - **Direct Code**: Paste code directly
               - **Upload File**: Single file upload
               - **Multiple Files**: Batch upload
               - **ZIP Archive**: Compressed project
            3. Click **START ANALYSIS**
            4. Review results in the analysis tabs
            """)

        with st.expander("**📊 Step 2: Understanding Results (3 min)**"):
            st.markdown("""
            ### Result Tabs

            **🚀 Intelligence Hub**
            - AI security analysis
            - Severity levels & counts
            - Detailed vulnerability descriptions

            **🛡️ Fixes**
            - Step-by-step remediation
            - Code examples & best practices
            - Prevention strategies

            **🔧 Patches**
            - Automatic patch files
            - Unified diff format
            - Ready to apply with git apply

            ### Severity Levels
            - 🔴 **CRITICAL**: Immediate security risk
            - 🟠 **HIGH**: Significant vulnerability
            - 🟡 **MEDIUM**: Notable issue to address
            - 🟢 **LOW**: Minor recommendation
            """)

        with st.expander("**💬 Step 3: AI Chat Analysis (2 min)**"):
            st.markdown("""
            After scanning, you can ask the AI security analyst questions:

            1. Click **💬 Security Intelligence Chat** in the sidebar
            2. Ask about specific vulnerabilities:
               - *"Explain this SQL injection issue"*
               - *"How do I fix this authentication bug?"*
               - *"What's the impact of this vulnerability?"*
            3. Get personalized explanations and solutions
            4. Continue asking follow-up questions for deeper understanding
            """)

        st.divider()
        render_info_banner(
            "💡 Tip: Use the Settings tab to configure LLM model selection and temperature for different analysis styles.",
            type="info"
        )

    with tab2:
        st.header("❓ Frequently Asked Questions")

        faq_items = [
            {
                "question": "What file formats are supported?",
                "answer": """
                Supported languages include:
                - Python (.py)
                - JavaScript/TypeScript (.js, .ts, .jsx, .tsx)
                - Java (.java)
                - Go (.go)
                - Rust (.rs)
                - C/C++ (.c, .cpp, .h)
                - PHP (.php)
                - Ruby (.rb)
                - And 15+ more languages...

                Upload as individual files or in a ZIP archive.
                """
            },
            {
                "question": "How long does a scan take?",
                "answer": """
                Typical scan times:
                - **Small file (< 1000 lines)**: 30-60 seconds
                - **Medium file (1-5K lines)**: 60-120 seconds
                - **Large project (> 5K lines)**: 120-300 seconds

                The **Analysis Depth** setting in Settings affects scan time:
                - Fast: ~30% reduction in time
                - Balanced: Standard time
                - Thorough: ~50% increase in time
                """
            },
            {
                "question": "Can I scan private repositories?",
                "answer": """
                Yes! Follow these steps:
                1. Go to ⚙️ **Settings** → **Security & API**
                2. Add your GitHub Personal Access Token
                3. Ensure the token has `repo` scope
                4. Go to 📦 **Project Repositories**
                5. Enter the private repo URL and scan

                Your credentials are never logged or transmitted insecurely.
                """
            },
            {
                "question": "What LLM models are available?",
                "answer": """
                Available models (Local Ollama):
                - **secure-patch-model**: Custom security engine (Default)
                - **phi3:latest**: Balanced local model
                - **tinyllama:latest**: Lightweight for rapid scans

                The pipeline is running 100% locally with zero data leaving your network.
                """
            },
            {
                "question": "Can I generate custom rules?",
                "answer": """
                Yes! Use the 📋 **Custom Rules** tab:
                1. Describe the vulnerability pattern you want to detect
                2. Provide example code
                3. Click **Generate Semgrep Rule**
                4. Review and customize the generated YAML rule
                5. Download and integrate into your CI/CD

                Rules are written in Semgrep YAML format and fully customizable.
                """
            },
            {
                "question": "How accurate are the results?",
                "answer": """
                VeriFAI combines two approaches:
                - **Static Analysis (Semgrep)**: Pattern-based, very accurate, minimal false positives
                - **LLM Analysis**: Context-aware, catches complex vulnerabilities

                Combined approach provides:
                - Excellent true positive rate (~95%)
                - Low false positive rate (~5%)
                - Detection of novel patterns

                Results are contextual and should be reviewed by security professionals.
                """
            }
        ]

        for item in faq_items:
            with st.expander(f"**Q: {item['question']}**"):
                st.markdown(item["answer"])

    with tab3:
        st.header("⌨️ Keyboard Shortcuts")

        shortcuts = [
            ("Tab", "Navigate between elements"),
            ("Enter", "Activate focused button or submit form"),
            ("Esc", "Close modals or dialogs"),
            ("Ctrl + K / Cmd + K", "Focus search (if available)"),
            ("Ctrl + S / Cmd + S", "Save current analysis"),
            ("Ctrl + E / Cmd + E", "Export results"),
            ("?", "Open this help menu"),
        ]

        st.markdown("### Navigation & General")
        cols = st.columns([2, 3])
        with cols[0]:
            st.markdown("**Shortcut**")
        with cols[1]:
            st.markdown("**Action**")

        for shortcut, action in shortcuts[:3]:
            cols = st.columns([2, 3])
            with cols[0]:
                st.code(shortcut)
            with cols[1]:
                st.markdown(action)

    with tab4:
        st.header("🔗 Resources & Documentation")

        render_settings_group("🔗 External Resources", "Links to helpful documentation")

        st.markdown("""
        ### Official Documentation
        - [GitHub Repository](https://github.com/codebytemirza/VeriFAI-LLM)
        - [API Documentation](https://github.com/codebytemirza/VeriFAI-LLM/blob/main/API_DOCUMENTATION.md)
        - [Contributing Guidelines](https://github.com/codebytemirza/VeriFAI-LLM/blob/main/CONTRIBUTING.md)

        ### Security Resources
        - [OWASP Top 10](https://owasp.org/www-project-top-ten/)
        - [CWE List](https://cwe.mitre.org/)
        - [Semgrep Rules](https://semgrep.dev/r)
        """)

        st.divider()

        st.subheader("🧠 AI Alignment & Training")
        st.markdown("""
        The intelligence behind **VeriFAI LLM** is not a generic AI. It has been specifically **aligned and specialized** for cybersecurity analysis through:
        
        *   **Custom Prompt Engineering:** Specialized system instructions designed by **NOUYEUTCHUI YOUMBI JUNIOR BRONDON**.
        *   **Heuristic Mapping:** Alignment with OWASP Top 10 and CWE standards.
        *   **Response Determinism:** Tuned hyper-parameters (Temperature 0.2) to ensure professional, accurate security reporting.
        *   **Dual-Gate Verification:** Integration of static pattern matching with neural-network reasoning.
        """)

        st.divider()

        st.markdown("""
        **VeriFAI LLM** Version: 2026.1 (Pro Edition)
        **Built with**: Streamlit, Semgrep, Local Ollama Engine
        **License**: MIT
        """)
