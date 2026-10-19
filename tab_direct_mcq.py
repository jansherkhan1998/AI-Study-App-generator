"""Tab 3: Instant Standalone MCQ Test Generator."""

import streamlit as st
from prompt import get_direct_mcq_prompt
from workflow import call_groq_json


def render_direct_mcq_tab():
    st.header("⚡ Instant MCQ Test Generator")
    st.write("Quickly generate a custom MCQ test set on any subject and topic.")

    col1, col2 = st.columns(2)
    with col1:
        subject = st.text_input("Subject", placeholder="e.g. Biology", key="dm_subj")
        topic = st.text_input("Topic", placeholder="e.g. Genetics", key="dm_top")
    with col2:
        count = st.slider("Number of MCQs", min_value=3, max_value=20, value=5, key="dm_cnt")
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], key="dm_diff")

    if st.button("⚡ Generate Instant Test", type="primary", key="btn_dm"):
        if not subject or not topic:
            st.warning("Please fill in both subject and topic.")
        else:
            with st.spinner("Creating direct MCQ test..."):
                prompt = get_direct_mcq_prompt(subject, topic, count, difficulty)
                try:
                    mcqs = call_groq_json(prompt)
                    st.session_state["direct_mcqs"] = mcqs
                    st.success("Test generated!")
                except Exception as e:
                    st.error(f"Failed to generate direct MCQs: {e}")

    if "direct_mcqs" in st.session_state:
        st.markdown("---")
        correct_count = 0
        total = len(st.session_state["direct_mcqs"])

        for item in st.session_state["direct_mcqs"]:
            st.markdown(f"**Q{item['id']}. {item['question']}**")
            user_ans = st.radio("Options:", item["options"], key=f"direct_q_{item['id']}")

            with st.expander("Reveal Correct Answer & Explanation"):
                st.write(f"**Correct Answer:** {item['answer']}")
                st.write(f"**Explanation:** {item['explanation']}")

        if st.button("Submit Test & Record Score"):
            # Save test score metrics into session state for Tab 4 Analytics
            st.session_state["tests_completed"] = st.session_state.get("tests_completed", 0) + 1
            st.session_state["total_questions_attempted"] = st.session_state.get("total_questions_attempted", 0) + total
            st.success("Test recorded! View your stats in Tab 4.")
