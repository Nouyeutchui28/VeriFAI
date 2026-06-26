import streamlit as st
from src.ui.api_client import get_api_client

def render_auth_ui():
    """Render authentication UI in sidebar."""
    with st.sidebar:
        st.markdown("---")

        # Check if user is authenticated
        if st.session_state.get("user_id"):
            # Show user info
            user_info = st.session_state.get("user_info", {})
            st.success(f":material/check_circle: Logged in as {user_info.get('name', 'User')}")

            # Show logout button
            if st.button(":material/logout: Logout", key="logout_button"):
                st.session_state.user_id = None
                st.session_state.access_token = None
                st.session_state.refresh_token = None
                st.session_state.user_info = None
                st.rerun()

            return True

        else:
            # Show login options
            st.subheader(":material/security: Login")

            login_option = st.radio(
                "Choose login provider",
                ["Google", "GitHub"],
                key="login_provider"
            )

            if st.button(f"Login with {login_option}", key="login_button"):
                # In production, this would redirect to OAuth provider
                st.info(f"""
                For production, you would be redirected to {login_option} OAuth.

                **For testing**, use these demo credentials:
                - Email: demo@verifai-llm.com
                - Provider: {login_option.lower()}
                """)

                # Demo login (replace with real OAuth in production)
                api_client = get_api_client()
                login_response = api_client.login(
                    oauth_provider=login_option.lower(),
                    oauth_id=f"{login_option.lower()}_demo_123",
                    email="demo@verifai-llm.com",
                    name="Demo User",
                    oauth_token="demo_token_xyz"
                )

                if "error" not in login_response:
                    # Store tokens and user info
                    st.session_state.access_token = login_response.get("access_token")
                    st.session_state.refresh_token = login_response.get("refresh_token")
                    st.session_state.user_info = login_response.get("user")
                    st.session_state.user_id = login_response.get("user", {}).get("id")

                    st.success(f":material/check_circle: Logged in as {login_response.get('user', {}).get('name')}")
                    st.rerun()
                else:
                    st.error(f"Login failed: {login_response.get('error')}")

            return False

def render_scan_history():
    """Render scan history in sidebar."""
    if not st.session_state.get("user_id"):
        return

    if st.sidebar.checkbox(":material/assignment: Show Scan History"):
        api_client = get_api_client()
        history = api_client.get_scan_history(limit=10)

        if "error" not in history and history:
            st.sidebar.subheader("Recent Scans")
            for scan in history:
                with st.sidebar.expander(f"{scan.get('project_name', 'Untitled')} - {scan.get('status')}"):
                    st.write(f"**URL:** {scan.get('repo_url', 'N/A')}")
                    st.write(f"**Status:** {scan.get('status')}")
                    st.write(f"**Files:** {scan.get('file_count', 0)}")
                    st.write(f"**Language:** {scan.get('primary_language', 'Unknown')}")

                    if st.button("View Results", key=f"view_{scan.get('id')}"):
                        st.session_state.selected_scan_id = scan.get('id')
                        st.rerun()
