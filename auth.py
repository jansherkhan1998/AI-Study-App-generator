"""Authentication and CAPTCHA management module."""

import random
import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["supabase"]["SUPABASE_URL"]
    key = st.secrets["supabase"]["SUPABASE_KEY"]
    return create_client(url, key)


def generate_captcha():
    if "captcha_num1" not in st.session_state or "captcha_num2" not in st.session_state:
        st.session_state["captcha_num1"] = random.randint(1, 10)
        st.session_state["captcha_num2"] = random.randint(1, 10)


def refresh_captcha():
    st.session_state["captcha_num1"] = random.randint(1, 10)
    st.session_state["captcha_num2"] = random.randint(1, 10)


def show_auth_page():
    supabase = init_supabase()
    st.title("🎓 AI Study Platform")
    st.subheader("Please sign in or register to continue")

    generate_captcha()
    num1 = st.session_state["captcha_num1"]
    num2 = st.session_state["captcha_num2"]
    expected_sum = num1 + num2

    tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        user_captcha = st.number_input(
            f"🤖 CAPTCHA Verification: What is {num1} + {num2}?", step=1, key="login_captcha"
        )

        if st.button("Log In", type="primary"):
            if user_captcha != expected_sum:
                st.error("❌ Incorrect CAPTCHA. Please try again.")
                refresh_captcha()
            else:
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state["user"] = res.user
                    st.success("Logged in successfully!")
                    refresh_captcha()
                    st.rerun()
                except Exception as e:
                    error_msg = str(e)
                    if "Email not confirmed" in error_msg:
                        st.warning("✉️ Please check your email inbox and click the confirmation link before logging in!")
                    else:
                        st.error(f"❌ Login failed: {error_msg}")
                    refresh_captcha()

    with tab_register:
        reg_email = st.text_input("Email", key="reg_email")
        reg_pass = st.text_input("Password", type="password", key="reg_pass")
        reg_captcha = st.number_input(
            f"🤖 CAPTCHA Verification: What is {num1} + {num2}?", step=1, key="reg_captcha"
        )

        if st.button("Sign Up"):
            if reg_captcha != expected_sum:
                st.error("❌ Incorrect CAPTCHA. Please try again.")
                refresh_captcha()
            else:
                try:
                    supabase.auth.sign_up({"email": reg_email, "password": reg_pass})
                    st.success("Account created! You can now log in.")
                    refresh_captcha()
                except Exception as e:
                    st.error(f"Registration failed: {e}")
                    refresh_captcha()
