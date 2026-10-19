"""Tab 4: Progress, Performance Tracking, and AI Feedback."""

import streamlit as st
from ui_components import render_metric


def render_analytics_tab():
    st.header("📊 Progress & Analytics")
    st.write("Track your study progress, overall test performance, and areas for improvement.")

    col1, col2, col3 = st.columns(3)
    with col1:
        completed = st.session_state.get("tests_completed", 0)
        render_metric("Tests Completed", str(completed))
    with col2:
        attempted = st.session_state.get("total_questions_attempted", 0)
        render_metric("Questions Attempted", str(attempted))
    with col3:
        has_rm = "Yes" if "roadmap_sections" in st.session_state else "None"
        render_metric("Active Roadmap", has_rm)

    st.markdown("---")
    st.subheader("💡 Study Recommendations")

    if completed == 0:
        st.info("Complete tests in Tab 2 or Tab 3 to generate detailed strength and weakness analytics.")
    else:
        st.success("Great job testing your knowledge! Here is your current profile:")
        st.write("✅ **Strengths:** Consistent participation in active retrieval practice.")
        st.write("⚠️ **Focus Areas:** Review explanations in expanded answer keys for missed questions.")
