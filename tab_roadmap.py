"""
Tab 1: Exam-Specific Roadmap Generator.
"""

from datetime import date
import streamlit as st
from exam_data import EXAM_PATTERNS
from workflow import call_groq_json, get_groq_api_key


def render_roadmap_tab():
    st.header("🗺️ Exam Preparation Roadmap Generator")
    st.write("Generate an authenticated day-by-day study schedule aligned with official exam patterns.")

    col1, col2 = st.columns(2)

    with col1:
        exam_type = st.selectbox(
            "Select Target Exam",
            ["MDCAT", "ECAT", "NUMS", "NUST NET", "Custom Exam"],
            key="rm_exam_select",
        )

        if exam_type == "Custom Exam":
            custom_exam_name = st.text_input("Custom Exam Name", placeholder="e.g. SAT / GRE", key="rm_custom_name")
        else:
            custom_exam_name = exam_type

        exam_date = st.date_input("Target Exam Date", min_value=date.today(), key="rm_exam_date")
        days_left = (exam_date - date.today()).days

        if days_left <= 0:
            st.warning("⚠️ Target exam date must be in the future.")
            days_left = 1

        st.info(f"⏳ **Days Remaining Until Exam:** `{days_left} Days`")

    with col2:
        daily_hours = st.slider("Daily Study Hours Available", min_value=1, max_value=12, value=4, key="rm_hours")
        prep_level = st.selectbox("Current Preparation Level", ["Beginner", "Intermediate", "Advanced"], key="rm_level")

    # Display Official Pattern Overview
    st.markdown("---")
    st.subheader(f"📋 Official Pattern: {custom_exam_name}")

    if exam_type in EXAM_PATTERNS:
        pattern = EXAM_PATTERNS[exam_type]
        st.write(f"**Total MCQs:** `{pattern['total_mcqs']}`")

        # Display Subject Breakdown
        subj_cols = st.columns(len(pattern["subjects"]))
        for idx, (subj, info) in enumerate(pattern["subjects"].items()):
            with subj_cols[idx]:
                st.metric(label=subj, value=f"{info['mcqs']} MCQs", delta=info["weightage"])
    else:
        st.info("ℹ️ Custom Exam selected. Enter custom details below or proceed with generation.")

    # Generate Action
    st.markdown("---")
    if st.button("🚀 Generate Exam Roadmap", type="primary", key="btn_gen_roadmap"):
        api_key = get_groq_api_key()
        if not api_key:
            st.error("GROQ_API_KEY missing. Add it in Streamlit Secrets.")
            return

        with st.spinner(f"Creating customized {days_left}-day roadmap for {custom_exam_name}..."):
            pattern_str = (
                str(EXAM_PATTERNS.get(exam_type, {}))
                if exam_type in EXAM_PATTERNS
                else "Custom structure"
            )

            prompt = f"""
            Generate a structured preparation roadmap for the exam '{custom_exam_name}'.
            - Days remaining until exam: {days_left} days
            - Available study hours per day: {daily_hours} hours/day
            - Student preparation level: {prep_level}
            - Official Subject Breakdown & Weightages: {pattern_str}

            Divide the remaining preparation time into exactly 5 logical study sections leading up to the test.
            Return ONLY a valid JSON array of 5 objects with keys:
            - "section_number": integer
            - "title": string (e.g., Section 1: Days 1-5 - Biology & Chemistry Fundamentals)
            - "key_concepts": list of strings (specific subtopics to study)
            - "recommended_focus": string (strategy for this timeframe)
            """

            try:
                sections = call_groq_json(prompt, api_key)
                st.session_state["roadmap_sections"] = sections
                st.session_state["roadmap_exam"] = custom_exam_name
                st.session_state["roadmap_days_left"] = days_left
                st.success("Roadmap generated successfully! Proceed to Tab 2 for Sectional Tests.")
            except Exception as e:
                st.error(f"Failed to generate roadmap: {e}")

    # Display Active Roadmap
    if "roadmap_sections" in st.session_state:
        st.markdown("---")
        st.subheader(
            f"📅 Study Schedule for {st.session_state.get('roadmap_exam')} ({st.session_state.get('roadmap_days_left')} Days Timeline)"
        )

        for sec in st.session_state["roadmap_sections"]:
            with st.expander(f"Section {sec['section_number']}: {sec['title']}", expanded=True):
                st.write(f"**Recommended Strategy:** {sec['recommended_focus']}")
                st.write("**Key Topics Covered:**")
                for item in sec["key_concepts"]:
                    st.write(f"- {item}")
