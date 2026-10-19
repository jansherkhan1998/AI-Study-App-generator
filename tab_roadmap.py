"""
Tab module for Roadmap view.
"""

import streamlit as st
from workflow import call_groq_json, get_groq_api_key


def render_roadmap_tab():
    st.header("🗺️ Day-by-Day Study Roadmap")
    st.write("Plan your full preparation schedule divided into distinct study sections.")

    col1, col2 = st.columns(2)
    with col1:
        subject = st.text_input("Subject", placeholder="e.g. Physics", key="rm_subj")
        topic = st.text_input("Topic / Chapter", placeholder="e.g. Electromagnetism", key="rm_top")
    with col2:
        prep_time = st.selectbox("Preparation Time", ["3 Days", "7 Days", "14 Days", "30 Days"], key="rm_time")
        level = st.selectbox("Student Level", ["Beginner", "Intermediate", "Advanced"], key="rm_lvl")

    if st.button("🚀 Generate Roadmap", type="primary", key="btn_rm"):
        if not subject or not topic:
            st.warning("Please provide both subject and topic.")
        else:
            api_key = get_groq_api_key()
            if not api_key:
                st.error("GROQ_API_KEY is missing. Add it in Streamlit Secrets.")
                return

            with st.spinner("Building your daily study roadmap..."):
                prompt = f"""
                Create a structured study roadmap for Subject: '{subject}', Topic: '{topic}' over {prep_time} for a {level} student.
                Divide the preparation into exactly 5 clear study sections.
                Return ONLY a JSON array of 5 objects with keys:
                - "section_number": integer
                - "title": string
                - "key_concepts": list of strings
                - "recommended_focus": string
                """
                try:
                    sections = call_groq_json(prompt, api_key)
                    st.session_state["roadmap_sections"] = sections
                    st.session_state["roadmap_subject"] = subject
                    st.session_state["roadmap_topic"] = topic
                    st.success("Roadmap created successfully! Check Tab 2 for section tests.")
                except Exception as e:
                    st.error(f"Failed to generate roadmap: {e}")

    if "roadmap_sections" in st.session_state:
        st.markdown("---")
        st.subheader(f"📅 Daily Roadmap: {st.session_state['roadmap_subject']} - {st.session_state['roadmap_topic']}")
        for sec in st.session_state["roadmap_sections"]:
            with st.expander(f"Section {sec['section_number']}: {sec['title']}", expanded=True):
                st.write(f"**Recommended Focus:** {sec['recommended_focus']}")
                st.write("**Key Concepts:**")
                for item in sec["key_concepts"]:
                    st.write(f"- {item}")
