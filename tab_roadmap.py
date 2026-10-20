"""
Tab 1: Dynamic Exam Roadmap Generator
Generates pattern-verified, 3-Phase nested study schedules with day-by-day subject mapping.
"""

from datetime import date
import streamlit as st
from exam_data import EXAM_PATTERNS
from workflow import call_groq_json, get_groq_api_key


def render_roadmap_tab():
    st.header("🗺️ Day-by-Day Exam Roadmap")
    st.write(
        "Generate a structured 3-Phase study schedule (Foundation -> Mastery -> Final Sprint) "
        "mapped with daily subject-wise topics and designated testing targets."
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

        st.info(
            f"⏳ **Days Remaining:** `{days_left} Days` \n"
            f"📌 **Structure Strategy:** `Nested 3-Phase Roadmap`"
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
            f"Building 3-Phase structured roadmap for {custom_exam_name} ({days_left} days)..."
        ):
            pattern_info = (
                str(EXAM_PATTERNS.get(exam_type, {}))
                if exam_type in EXAM_PATTERNS
                else "Custom Exam Pattern"
            )

            prompt = f"""
            You are an expert academic strategy assistant. Create a 3-Phase structured study roadmap for '{custom_exam_name}'.
            - Total Days Remaining: {days_left}
            - Daily Study Time: {daily_hours} hours per day
            - Current Student Level: {prep_level}
            - Official Syllabus & Weightages: {pattern_info}

            RULES FOR STRUCTURE:
            1. Divide the overall schedule strictly into 3 Macro-Phases:
               - Phase 1: Foundation & Core Coverage (~50% of total days)
               - Phase 2: High-Yield Mastery & Mixed Drills (~30% of total days)
               - Phase 3: Final Sprint & Full Simulations (~20% of total days)
            2. Inside each Phase, break down the schedule into 2 to 4 manageable "blocks" (e.g., Week 1-2, Block 1).
            3. Inside each Block, map specific named syllabus chapters and sub-topics for each core subject.
            4. NEVER use generic placeholders like "High-Yield Topics", "General Review", or "Final Prep". Always name concrete textbook chapters/topics (e.g. "Biology: Bioenergetics - Light & Dark Reactions", "Chemistry: Stoichiometry & Limiting Reactants").
            5. Provide daily time splits, quantitative practice targets, and explicit testing benchmarks that will feed into evaluation.

            Return ONLY a valid JSON array containing EXACTLY 3 objects corresponding to the 3 Macro-Phases.

            JSON Schema:
            [
              {{
                "phase_number": 1,
                "phase_name": "Phase 1: Foundation & Core Coverage",
                "days_range": "Days 1 - X",
                "phase_objective": "Comprehensive coverage of core concepts and foundational problem-solving.",
                "blocks": [
                  {{
                    "block_title": "Block 1: Days 1-7 (Fundamental Concepts)",
                    "daily_schedule": [
                      {{
                        "day_label": "Day 1-2",
                        "subject_topics": [
                          "Biology: Cell Structure & Organelles",
                          "Chemistry: Stoichiometry & Mole Calculations",
                          "Physics: Scalars, Vectors & Equilibrium"
                        ],
                        "daily_hours_breakdown": {{"Concept Reading": "2.0 hrs", "MCQ Practice": "2.0 hrs"}},
                        "daily_mcq_target": ["Biology: 30 MCQs", "Chemistry: 20 MCQs", "Physics: 20 MCQs"]
                      }}
                    ],
                    "block_testing_target": "Chapter Quiz: Cell Bio, Stoichiometry, & Vectors",
                    "target_pass_score": "Score >= 75% accuracy"
                  }}
                ]
              }},
              ... (Repeat for Phase 2 and Phase 3)
            ]
            """

            try:
                phases = call_groq_json(prompt, api_key)
                st.session_state["roadmap_phases"] = phases
                st.session_state["roadmap_exam"] = custom_exam_name
                st.session_state["roadmap_days_left"] = days_left
                st.success("Structured 3-Phase Roadmap successfully generated!")
            except Exception as e:
                st.error(f"Error generating roadmap: {e}")

    # Display Output
    if "roadmap_phases" in st.session_state:
        st.markdown("---")
        st.subheader(
            f"📅 Active Plan: {st.session_state.get('roadmap_exam')} "
            f"({st.session_state.get('roadmap_days_left')} Days Total)"
        )

        phases = st.session_state["roadmap_phases"]

        # Render 3 Top-Level Macro Phase Tabs
        phase_tabs = st.tabs([f"🎯 {p.get('phase_name', f'Phase {i+1}')}" for i, p in enumerate(phases)])

        for idx, tab in enumerate(phase_tabs):
            phase = phases[idx]
            with tab:
                st.markdown(f"### 📌 {phase.get('phase_name')} (`{phase.get('days_range')}`)")
                st.info(f"**Objective:** {phase.get('phase_objective', 'N/A')}")

                # Render Blocks inside Phase
                for block in phase.get("blocks", []):
                    with st.expander(f"📦 {block.get('block_title')}", expanded=False):
                        
                        # Daily Schedule Breakdown
                        for day in block.get("daily_schedule", []):
                            st.markdown(f"#### 🗓️ {day.get('day_label')}")
                            col_a, col_b = st.columns([2, 1])

                            with col_a:
                                st.markdown("**📖 Subject-Wise Specific Topics:**")
                                for top in day.get("subject_topics", []):
                                    st.write(f"- {top}")

                                st.markdown("**🎯 Daily MCQ Practice Target:**")
                                for mcq in day.get("daily_mcq_target", []):
                                    st.write(f"- {mcq}")

                            with col_b:
                                st.markdown("**⏱️ Daily Time Allocation:**")
                                for activity, hrs in day.get("daily_hours_breakdown", {}).items():
                                    st.write(f"- **{activity}:** `{hrs}`")

                            st.markdown("---")

                        # Testing & Benchmarks (Bridge to Tab 2)
                        st.markdown(f"📝 **Designated Phase Test:** `{block.get('block_testing_target', 'N/A')}`")
                        st.markdown(f"📊 **Required Target Score:** `{block.get('target_pass_score', 'N/A')}`")
