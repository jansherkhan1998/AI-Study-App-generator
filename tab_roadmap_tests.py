"""Tab 2: Sectional Tests based on Generated Roadmap."""

import streamlit as st
from workflow import call_groq_json


def render_roadmap_tests_tab():
    st.header("📝 Sectional Practice Tests")
    st.write("Take targeted test modules based on the sections in your study roadmap.")

    if "roadmap_sections" not in st.session_state:
        st.info("ℹ️ No roadmap found. Please generate a roadmap in Tab 1 first!")
        return

    sections = st.session_state["roadmap_sections"]
    section_options = [f"Section {s['section_number']}: {s['title']}" for s in sections]
    selected_sec = st.selectbox("Select Roadmap Section to Test", section_options)

    sec_idx = section_options.index(selected_sec)
    active_sec = sections[sec_idx]

    if st.button(f"Generate Test for Section {active_sec['section_number']}", type="primary"):
        with st.spinner("Generating section test..."):
            prompt = f"""
            Generate 5 MCQs strictly for Section '{active_sec['title']}' covering key concepts: {active_sec['key_concepts']}.
            Return raw JSON array with keys: 'id', 'question', 'options', 'answer', 'explanation'.
            """
            try:
                mcqs = call_groq_json(prompt)
                st.session_state["sec_test_mcqs"] = mcqs
                st.session_state["sec_test_title"] = active_sec["title"]
            except Exception as e:
                st.error(f"Failed to generate section test: {e}")

    if "sec_test_mcqs" in st.session_state:
        st.markdown("---")
        st.subheader(f"🧪 Test: {st.session_state['sec_test_title']}")
        for q in st.session_state["sec_test_mcqs"]:
            st.markdown(f"**Q{q['id']}. {q['question']}**")
            st.radio("Select Answer:", q["options"], key=f"sec_q_{q['id']}")
            with st.expander("View Answer"):
                st.write(f"**Correct:** {q['answer']}")
                st.write(f"**Explanation:** {q['explanation']}")
