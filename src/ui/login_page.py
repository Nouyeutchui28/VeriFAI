import streamlit as st
from src.ui.api_client import get_api_client
import time

def render_login_page():
    """Render professional login page matching malware analyzer theme."""

    st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #070b14 0%, #0a0f1a 100%);
    }
    .login-container {
        max-width: 500px;
        margin: 4rem auto;
        padding: 2.5rem;
        background: linear-gradient(135deg, #0f182b 0%, #0a111c 100%);
        border: 1px solid #1d2b3f;
        border-radius: 8px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    }
    .login-header {
        text-align: center;
        margin-bottom: 2.5rem;
    }
    .login-header h1 {
        color: #e2e8f0;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
    }
    .login-header p {
        color: #8b9bb4;
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .login-subtext {
        color: #8b9bb4;
        font-size: 0.85rem;
        margin-top: 3rem;
        text-align: center;
    }
    .cyber-divider {
        background: linear-gradient(90deg, transparent, #1d2b3f, transparent);
        height: 1px;
        margin: 1.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-container">
        <div class="login-header">
            <h1>🛡️ VeriFAI LLM</h1>
            <p>Security Analysis Platform</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if 'otp_verification_email' not in st.session_state:
            st.session_state.otp_verification_email = None

        if st.session_state.otp_verification_email:
            st.markdown("### 📧 Email Verification")
            st.info(f"Verification code sent to **{st.session_state.otp_verification_email}**")

            with st.form("otp_form"):
                otp_code = st.text_input("6-Digit Code", placeholder="000000", max_chars=6, label_visibility="collapsed")
                verify_btn = st.form_submit_button("✅ Verify & Login", use_container_width=True, type="primary")

                if verify_btn:
                    if not otp_code or len(otp_code) != 6:
                        st.error("❌ Please enter a valid 6-digit code")
                    else:
                        api_client = get_api_client()
                        with st.spinner("🔍 Verifying..."):
                            response = api_client.verify_token_insforge(st.session_state.otp_verification_email, otp_code)

                            if "error" not in response and "message" not in response:
                                st.session_state.access_token = response.get("accessToken")
                                st.session_state.user_info = response.get("user")
                                st.session_state.user_id = response.get("user", {}).get("id")
                                st.session_state.authenticated = True
                                st.session_state.otp_verification_email = None
                                st.success("✅ Email verified successfully!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                error_msg = response.get('message', response.get('error', 'Verification failed'))
                                st.error(f"❌ {error_msg}")
            
            if st.button("⬅️ Back to Login"):
                st.session_state.otp_verification_email = None
                st.rerun()
                
            return # Exit early to only show OTP form

        # Standard Login/Signup Tabs
        tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Create Account"])
        
        with tab1:
            with st.form("signin_form"):
                email = st.text_input("Email Address", placeholder="name@company.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                
                submit_button = st.form_submit_button("Sign In", use_container_width=True)
                
                if submit_button:
                    if not email or not password:
                        st.error("Please fill in all fields")
                    else:
                        api_client = get_api_client()
                        with st.spinner("Authenticating..."):
                            response = api_client.signin(email, password)
                            
                            if "error" not in response and "message" not in response:
                                st.session_state.access_token = response.get("accessToken")
                                st.session_state.user_info = response.get("user")
                                st.session_state.user_id = response.get("user", {}).get("id")
                                st.session_state.authenticated = True
                                
                                st.success("✅ Welcome back!")
                                time.sleep(1)
                                st.rerun()
                            elif response.get('error') == 'EMAIL_NOT_VERIFIED' or 'verify' in str(response.get('message', '')).lower():
                                st.session_state.otp_verification_email = email
                                st.warning("⚠️ Email not verified. Please enter the OTP.")
                                time.sleep(1)
                                st.rerun()
                            else:
                                error_msg = response.get('message', response.get('error', 'Login failed'))
                                st.error(f"Login failed: {error_msg}")
            
            # Google OAuth Login
            st.markdown("---")
            st.markdown("<div style='text-align: center; margin-bottom: 1rem; color: #94a3b8;'>Or continue with</div>", unsafe_allow_html=True)
            
            api_client = get_api_client()
            # Fixed redirect to port 8503
            google_oauth_url = f"{api_client.auth_url}/authorize?provider=google&redirect_to=http://localhost:8503"
            
            if st.button("🌐 Continue with Google", key="google_signin", use_container_width=True):
                st.markdown(f'<meta http-equiv="refresh" content="0;url={google_oauth_url}">', unsafe_allow_html=True)
                st.info("Redirecting to Google...")
                # Fallback for session
                time.sleep(1)

            # Offline / Local Mode Bypass (Always works)
            st.markdown("---")
            if st.button("🔌 Offline Mode: Continue as Local User", use_container_width=True, type="primary"):
                st.session_state.access_token = "offline_token"
                st.session_state.user_info = {
                    "id": "local-user-1",
                    "email": "local@verifai-llm.offline",
                    "role": "local_admin",
                    "name": "Local User"
                }
                st.session_state.user_id = "local-user-1"
                st.session_state.authenticated = True
                st.success("✅ Logged in to Local Mode")
                time.sleep(1)
                st.rerun()
        
        with tab2:
            with st.form("signup_form"):
                new_email = st.text_input("Email Address", placeholder="name@company.com")
                new_password = st.text_input("Password", type="password", placeholder="••••••••")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••••")
                
                signup_button = st.form_submit_button("Create Account", use_container_width=True)
                
                if signup_button:
                    if not new_email or not new_password:
                        st.error("Please fill in all fields")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        api_client = get_api_client()
                        with st.spinner("Creating account..."):
                            response = api_client.signup(new_email, new_password)
                            
                            if "error" not in response and "message" not in response:
                                if response.get("requireEmailVerification"):
                                    st.session_state.otp_verification_email = new_email
                                    st.success("✅ Account created! Please verify your email.")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.success("✅ Account created! Please sign in.")
                                    time.sleep(1)
                            else:
                                error_msg = response.get('message', response.get('error', 'Signup failed'))
                                st.error(f"Signup failed: {error_msg}")
            
            # Google OAuth Signup
            st.markdown("---")
            st.markdown("<div style='text-align: center; margin-bottom: 1rem; color: #94a3b8;'>Or sign up with</div>", unsafe_allow_html=True)
            if st.button("🌐 Sign up with Google", key="google_signup", use_container_width=True):
                st.markdown(f'<meta http-equiv="refresh" content="0;url={google_oauth_url}">', unsafe_allow_html=True)
                st.info("Redirecting to Google...")
                # Fallback for dev mode simulation
                time.sleep(1)
                st.session_state.access_token = "google_dev_token"
                st.session_state.user_info = {"id": "google-123", "email": "user@gmail.com", "name": "Google User"}
                st.session_state.user_id = "google-123"
                st.session_state.authenticated = True
                st.success("✅ Google authentication simulated for development!")
                time.sleep(1)
                st.rerun()

    st.markdown("""
    <div style="text-align: center; margin-top: 3rem; color: #64748b; font-size: 0.875rem;">
        Managed via <a href="https://insforge.app" style="color: #38bdf8; text-decoration: none;">InsForge Dashboard</a>
    </div>
    """, unsafe_allow_html=True)
