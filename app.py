"""Main entry point orchestrating Auth, UI, and Module Tabs."""

import streamlit as st
from auth import init_supabase, show_auth_page
from ui_components import inject_custom_css
from tab_roadmap import render_roadmap_tab
from tab_roadmap_tests import render_roadmap_tests_tab
from tab_direct_mcq import render_direct_mcq_tab
from tab_analytics import render_analytics_tab

# Page Configuration
st.set_page_config(
    page_title="AI Study Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply global styling
inject_custom_css()

# Authentication Check
if "user" not in st.session_state:
    show_auth_page()
    st.stop()

# User Profile Sidebar & Logout
user = st.session_state["user"]
supabase = init_supabase()

st.sidebar.markdown("### 👤 Student Profile")
st.sidebar.write(f"Logged in as:\n`{user.email}`")

if st.sidebar.button("Log Out", type="secondary"):
    supabase.auth.sign_out()
    del st.session_state["user"]
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("Navigate through the top tabs to build roadmaps, take tests, and track progress.")

# Header
st.title("🎓 AI Study Platform")

# Render Functional Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ Study Roadmap",
    "📝 Section Tests",
    "⚡ Direct MCQ Test",
    "📊 Progress & Analytics",
])

with tab1:
    render_roadmap_tab()

with tab2:
    render_roadmap_tests_tab()

with tab3:
    render_direct_mcq_tab()

with tab4:
    render_analytics_tab()
