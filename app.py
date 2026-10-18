import streamlit as st
from supabase import create_client, Client

# --- 1. SUPABASE INITIALIZATION ---
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["supabase"]["SUPABASE_URL"]
    key = st.secrets["supabase"]["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# --- 2. AUTHENTICATION SYSTEM ---
def show_auth_page():
    st.set_page_config(page_title="Login | AI Study Pack Generator", page_icon="🔒")
    st.title("🎓 AI Study Pack Generator")
    st.subheader("Please sign in or register to continue")

    tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Log In", type="primary"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state["user"] = res.user
                st.success("Logged in successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Login failed: {e}")

    with tab_register:
        reg_email = st.text_input("Email", key="reg_email")
        reg_pass = st.text_input("Password", type="password", key="reg_pass")
        if st.button("Sign Up"):
            try:
                res = supabase.auth.sign_up({"email": reg_email, "password": reg_pass})
                st.success("Account created! You can now log in.")
            except Exception as e:
                st.error(f"Registration failed: {e}")

# Block unauthenticated users
if "user" not in st.session_state:
    show_auth_page()
    st.stop()

# --- 3. MAIN APPLICATION (LOGGED IN USERS ONLY) ---
st.set_page_config(page_title="AI Study Pack Generator", page_icon="📚", layout="wide")

# Sidebar User Info & Logout
user = st.session_state["user"]
st.sidebar.write(f"Logged in as: **{user.email}**")
if st.sidebar.button("Log Out"):
    supabase.auth.sign_out()
    del st.session_state["user"]
    st.rerun()

st.title("📚 AI Study Pack Generator")
st.write("Welcome to your workspace! Your progress will automatically be saved.")

# --- YOUR EXISTING APP LOGIC HERE ---
