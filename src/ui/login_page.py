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
    /* CUSTOM BLUE BUTTON STYLING */
    div.stButton > button:first-child {
        background-color: #00e5ff !important;
        color: #000000 !important;
        font-weight: 700 !important;
        border: none !important;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.2) !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        transition: all 0.2s ease-in-out !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #00ffff !important;
        box-shadow: 0 0 25px rgba(0, 229, 255, 0.5) !important;
        transform: translateY(-2px) !important;
    }
    /* SECONDARY BUTTONS (FORGOT PASSWORD, BACK) */
    div.stButton > button[kind="secondary"] {
        background-color: transparent !important;
        border: 1px solid #1d2b3f !important;
        color: #e2e8f0 !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        border-color: #00e5ff !important;
        color: #00e5ff !important;
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
        # Initialize session states
        if 'otp_verification_email' not in st.session_state:
            st.session_state.otp_verification_email = None
        if 'recovery_mode' not in st.session_state:
            st.session_state.recovery_mode = False
        if 'recovery_email' not in st.session_state:
            st.session_state.recovery_email = None

        # 1. EMAIL VERIFICATION FLOW (OTP)
        if st.session_state.otp_verification_email and not st.session_state.recovery_mode:
            st.markdown("### 📧 Email Verification")
            st.info(f"Verification code sent to **{st.session_state.otp_verification_email}**")

            with st.form("otp_form"):
                otp_code = st.text_input("6-Digit Code", placeholder="000000", max_chars=6)
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
                
            return

        # 2. PASSWORD RECOVERY FLOW
        if st.session_state.recovery_mode:
            st.markdown("### 🔑 Password Recovery")
            
            if not st.session_state.recovery_email:
                # Step 1: Enter Email
                with st.form("recovery_request_form"):
                    rec_email = st.text_input("Enter your account email", placeholder="name@company.com")
                    submit_rec = st.form_submit_button("Send Reset Code", use_container_width=True, type="primary")
                    
                    if submit_rec:
                        if not rec_email:
                            st.error("Please enter your email")
                        else:
                            api_client = get_api_client()
                            with st.spinner("Sending reset code..."):
                                response = api_client.recover_password(rec_email)
                                if "error" not in response and "message" not in response:
                                    st.session_state.recovery_email = rec_email
                                    st.success(f"✅ Reset code sent to {rec_email}")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    error_msg = response.get('message', response.get('error', 'Recovery failed'))
                                    st.error(f"❌ {error_msg}")
            else:
                # Step 2: Enter OTP and New Password
                st.info(f"Enter the 6-digit code sent to **{st.session_state.recovery_email}**")
                with st.form("recovery_verify_form"):
                    otp_code = st.text_input("6-Digit Code", placeholder="000000", max_chars=6)
                    new_password = st.text_input("New Password", type="password", placeholder="••••••••")
                    confirm_password = st.text_input("Confirm New Password", type="password", placeholder="••••••••")
                    reset_btn = st.form_submit_button("Reset Password", use_container_width=True, type="primary")
                    
                    if reset_btn:
                        if not otp_code or len(otp_code) != 6:
                            st.error("Please enter a valid 6-digit code")
                        elif not new_password:
                            st.error("Please enter a new password")
                        elif new_password != confirm_password:
                            st.error("Passwords do not match")
                        else:
                            api_client = get_api_client()
                            with st.spinner("Resetting password..."):
                                response = api_client.reset_password(st.session_state.recovery_email, otp_code, new_password)
                                if "error" not in response and "message" not in response:
                                    st.success("✅ Password reset successfully! You can now sign in.")
                                    st.session_state.recovery_mode = False
                                    st.session_state.recovery_email = None
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    error_msg = response.get('message', response.get('error', 'Reset failed'))
                                    st.error(f"❌ {error_msg}")
            
            if st.button("⬅️ Back to Login", key="back_from_recovery"):
                st.session_state.recovery_mode = False
                st.session_state.recovery_email = None
                st.rerun()
            return

        # 3. STANDARD LOGIN / SIGNUP TABS
        tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Create Account"])
        
        with tab1:
            with st.form("signin_form"):
                email = st.text_input("Email Address", placeholder="name@company.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                
                # Forgot Password Link (simulated with a button inside or outside)
                submit_button = st.form_submit_button("Sign In", use_container_width=True, type="primary")
                
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
            
            # Forgot Password Button
            if st.button("Forgot Password?", key="forgot_pw_btn", use_container_width=True, kind="secondary"):
                st.session_state.recovery_mode = True
                st.rerun()
        
        with tab2:
            with st.form("signup_form"):
                new_email = st.text_input("Email Address", placeholder="name@company.com")
                new_password = st.text_input("Password", type="password", placeholder="••••••••")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••••")
                
                signup_button = st.form_submit_button("Create Account", use_container_width=True, type="primary")
                
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

    st.markdown("""
    <div style="text-align: center; margin-top: 3rem; color: #64748b; font-size: 0.875rem;">
        VeriFAI LLM Security Scanner | © 2026
    </div>
    """, unsafe_allow_html=True)
