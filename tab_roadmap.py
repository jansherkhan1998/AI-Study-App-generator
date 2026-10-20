"""
Tab 1: Dynamic Exam Roadmap Generator
Generates pattern-verified, chapter-mapped study schedules.
"""

from datetime import date
import streamlit as st
from exam_data import EXAM_PATTERNS
from workflow import call_groq_json, get_groq_api_key


def calculate_section_count(days_remaining: int) -> tuple[int, str]:
    """
    Determines section count and strategic focus based on days remaining.
    Returns (section_count, strategic_description)
    """
    if days_remaining <= 15:
        return 4, "4-Phase Rapid Sprint (High-Yield Focus)"
    elif days_remaining <= 30:
        return 6, "6-Unit Chapter-Wise Acceleration"
    elif days_remaining <= 60:
        return 10, "10 Mini-Units (Frequent 5-6 Day Testing Loop)"
    elif days_remaining <= 120:
        return 14, "14 Weekly Milestones + Monthly Cumulative Mocks"
    else:
        return 16, "16-Section 3-Phase Loop (Foundation -> Mastery -> Final Sprint)"


def render_roadmap_tab():
    st.header("🗺️ Day-by-Day Exam Roadmap")
    st.write(
        "Generate a verified, chapter-mapped study schedule structured strictly according to official syllabus weightages."
    )

    col1, col2 = st.columns(2)

    with col1:
        exam_type = st.selectbox(
            "Select Target Exam",
            ["MDCAT", "ECAT", "NUMS", "NUST NET", "Custom Exam"],
            key="rm_exam_select",
        )

        if exam_type == "Custom Exam":
            custom_exam_name = st.text_input(
                "Custom Exam Name", placeholder="e.g. SAT / GRE", key="rm_custom_name"
            )
        else:
            custom_exam_name = exam_type

        exam_date = st.date_input(
            "Target Exam Date", min_value=date.today(), key="rm_exam_date"
        )
        days_left = max((exam_date - date.today()).days, 1)

        section_count, strategy_label = calculate_section_count(days_left)

        st.info(
            f"⏳ **Days Remaining:** `{days_left} Days`  \n"
            f"📌 **Structure Strategy:** `{strategy_label}` (`{section_count} Sections`)"
        )

    with col2:
        daily_hours = st.slider(
            "Daily Available Hours",
            min_value=1,
            max_value=12,
            value=4,
            key="rm_hours",
        )
        prep_level = st.selectbox(
            "Current Preparation Level",
            ["Beginner", "Intermediate", "Advanced"],
            key="rm_level",
        )

    # Official Exam Breakdown Display
    st.markdown("---")
    st.subheader(f"📋 Pattern Overview: {custom_exam_name}")

    if exam_type in EXAM_PATTERNS:
        pattern = EXAM_PATTERNS[exam_type]
        st.write(f"**Total MCQs:** `{pattern['total_mcqs']}`")

        subj_cols = st.columns(len(pattern["subjects"]))
        for idx, (subj, info) in enumerate(pattern["subjects"].items()):
            with subj_cols[idx]:
                st.metric(
                    label=subj,
                    value=f"{info['mcqs']} MCQs",
                    delta=info["weightage"],
                )
    else:
        st.info("ℹ️ Custom Exam selected. Proceed to generate schedule.")

    # Generate Action
    st.markdown("---")
    if st.button("🚀 Generate Detailed Roadmap", type="primary", key="btn_gen_roadmap"):
        api_key = get_groq_api_key()
        if not api_key:
            st.error("GROQ_API_KEY missing. Please configure it in Streamlit Secrets.")
            return

        with st.spinner(
            f"Building {section_count}-section roadmap for {custom_exam_name} ({days_left} days)..."
        ):
            pattern_info = (
                str(EXAM_PATTERNS.get(exam_type, {}))
                if exam_type in EXAM_PATTERNS
                else "Custom Exam Pattern"
            )

            prompt = f"""
            You are an expert academic strategy assistant. Create a granular study roadmap for '{custom_exam_name}'.
            - Total Days Remaining: {days_left}
            - Daily Study Time: {daily_hours} hours per day
            - Current Student Level: {prep_level}
            - Official Syllabus & Weightages: {pattern_info}

            RULES:
            1. Divide the plan into EXACTLY {section_count} chronological sections/units.
            2. Map specific syllabus chapters/units to each section according to official exam topic distributions.
            3. Provide a clear daily study time budget matching {daily_hours} hours total per day.
            4. Include concrete quantitative MCQ practice targets per subject.
            5. Define explicit testing benchmarks and passing targets required before completing each section.

            Return ONLY a valid JSON array of {section_count} objects. Each object MUST contain:
            - "section_number": integer
            - "title": string (e.g. "Section 1: Days 1-10 - Cell Biology & Fundamental Chemistry")
            - "chapters_covered": list of strings (specific chapter topics)
            - "daily_time_split": dictionary mapping activity name to hours (e.g. {{"Concept Reading": "2.0 hrs", "MCQ Practice": "2.0 hrs"}})
            - "practice_targets": list of strings (e.g. ["Biology: 120 MCQs", "Chemistry: 80 MCQs"])
            - "testing_target": string (e.g. "Take 1 Section Test covering Chapters 1-3")
            - "target_pass_score": string (e.g. "Score >= 75% accuracy")
            """

            try:
                sections = call_groq_json(prompt, api_key)
                st.session_state["roadmap_sections"] = sections
                st.session_state["roadmap_exam"] = custom_exam_name
                st.session_state["roadmap_days_left"] = days_left
                st.session_state["roadmap_section_count"] = section_count
                st.success("Roadmap successfully generated!")
            except Exception as e:
                st.error(f"Error generating roadmap: {e}")

    # Display Output
    if "roadmap_sections" in st.session_state:
        st.markdown("---")
        st.subheader(
            f"📅 Active Plan: {st.session_state.get('roadmap_exam')} "
            f"({st.session_state.get('roadmap_days_left')} Days | {st.session_state.get('roadmap_section_count')} Sections)"
        )

        for sec in st.session_state["roadmap_sections"]:
            with st.expander(
                f"📌 Section {sec.get('section_number')}: {sec.get('title')}",
                expanded=False,
            ):
                col_left, col_right = st.columns([2, 1])

                with col_left:
                    st.markdown("**📖 Specific Chapters & Topics:**")
                    for ch in sec.get("chapters_covered", []):
                        st.write(f"- {ch}")

                    st.markdown("**🎯 Daily MCQ Practice Volume:**")
                    for pt in sec.get("practice_targets", []):
                        st.write(f"- {pt}")

                with col_right:
                    st.markdown("**⏱️ Daily Time Allocation:**")
                    for activity, hrs in sec.get("daily_time_split", {}).items():
                        st.write(f"- **{activity}:** `{hrs}`")

                    st.markdown("---")
                    st.markdown(f"**📝 Test Required:** {sec.get('testing_target', 'Section Quiz')}")
                    st.markdown(f"**📊 Target Pass Score:** `{sec.get('target_pass_score', '>= 75%')}`")
