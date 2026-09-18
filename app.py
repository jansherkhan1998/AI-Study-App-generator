"""Main Streamlit application for AI Study Pack Generator."""

import os

import streamlit as st

from prompt import build_request_dict
from workflow import generate_study_pack


# ============================================================
# APP CONFIGURATION
# ============================================================

APP_TITLE = "AI Study Pack Generator"


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🎓",
    layout="wide",
)


# ============================================================
# INPUT VALIDATION
# ============================================================

def validate_inputs(
    subject,
    topic,
    mcq_count,
    short_count,
):

    if not subject.strip():
        return "Please enter a subject."

    if not topic.strip():
        return "Please enter a topic or chapter."

    if not 1 <= int(mcq_count) <= 30:
        return "MCQ count must be between 1 and 30."

    if not 0 <= int(short_count) <= 15:
        return (
            "Short-answer count must be between 0 and 15."
        )

    return None


# ============================================================
# GROQ API KEY
# ============================================================

def get_groq_api_key():
    """
    Read GROQ_API_KEY from environment variables
    or Streamlit Secrets.
    """

    key = os.getenv(
        "GROQ_API_KEY",
        "",
    ).strip()

    if key:
        return key

    try:
        return str(
            st.secrets["GROQ_API_KEY"]
        ).strip()

    except Exception:
        return ""


# ============================================================
# PAGE HEADER
# ============================================================

st.title("🎓 AI Study Pack Generator")

st.write(
    "Generate a personalized study pack through "
    "a five-stage AI workflow:"
)

st.caption(
    "Planning → Content Generation → Assessment → "
    "Review → Refinement"
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("Student Profile")

    subject = st.text_input(
        "Subject",
        placeholder="e.g. Physics",
    )

    topic = st.text_input(
        "Topic / Chapter",
        placeholder="e.g. Electromagnetic Induction",
    )

    exam_type = st.selectbox(
        "Exam Type",
        [
            "MDCAT",
            "ECAT",
            "NTS",
            "NUST NET",
            "GAT",
            "CSS",
            "University Exam",
            "School/College Exam",
            "Other",
        ],
    )

    level = st.selectbox(
        "Student Level",
        [
            "Beginner",
            "Intermediate",
            "Advanced",
        ],
    )

    preparation_time = st.selectbox(
        "Available Preparation Time",
        [
            "1 day",
            "3 days",
            "1 week",
            "2 weeks",
            "1 month",
            "Custom",
        ],
    )

    mcq_count = st.slider(
        "Number of MCQs",
        min_value=1,
        max_value=30,
        value=10,
    )

    mcq_difficulty = st.selectbox(
        "MCQ Difficulty",
        [
            "Easy",
            "Medium",
            "Hard",
            "Mixed",
        ],
    )

    short_question_count = st.slider(
        "Number of Short Questions",
        min_value=0,
        max_value=15,
        value=5,
    )

    output_style = st.selectbox(
        "Output Style",
        [
            "Detailed",
            "Balanced",
            "Quick Revision",
        ],
    )

    generate_button = st.button(
        "🚀 Generate Study Pack",
        type="primary",
        use_container_width=True,
    )


# ============================================================
# SESSION STATE
# ============================================================

if "workflow_state" not in st.session_state:
    st.session_state.workflow_state = None


# ============================================================
# GENERATE STUDY PACK
# ============================================================

if generate_button:

    error = validate_inputs(
        subject,
        topic,
        mcq_count,
        short_question_count,
    )

    if error:

        st.error(error)

    else:

        request = build_request_dict(
            subject,
            topic,
            exam_type,
            level,
            preparation_time,
            mcq_count,
            mcq_difficulty,
            short_question_count,
            output_style,
        )

        api_key = get_groq_api_key()

        if not api_key:

            st.error(
                "GROQ_API_KEY is missing. "
                "Add it in Streamlit Secrets."
            )

        else:

            status = st.empty()

            progress = st.progress(0)

            stage_numbers = {
                "Planning": 1,
                "Content Generation": 2,
                "Assessment": 3,
                "Review": 4,
                "Refinement": 5,
            }

            def update_progress(
                stage,
                state,
            ):

                number = stage_numbers.get(
                    stage,
                    0,
                )

                if state == "running":

                    status.info(
                        f"🔄 {stage} stage is running..."
                    )

                elif state == "completed":

                    status.success(
                        f"✅ {stage} stage completed."
                    )

                    progress.progress(
                        number / 5
                    )

                elif state == "failed":

                    status.error(
                        f"❌ {stage} stage failed."
                    )

            try:

                with st.spinner(
                    "Running Groq AI workflow..."
                ):

                    result = generate_study_pack(
                        request,
                        api_key,
                        progress_callback=update_progress,
                    )

                st.session_state.workflow_state = result

                status.success(
                    "🎉 Study pack generated successfully!"
                )

                progress.progress(1.0)

            except Exception as exc:

                st.error(
                    f"Workflow stopped: {exc}"
                )


# ============================================================
# DISPLAY RESULTS
# ============================================================

state = st.session_state.workflow_state


if state:

    st.divider()

    st.subheader("🔄 AI Workflow")

    cols = st.columns(5)

    stages = [
        ("1", "Planning"),
        ("2", "Content"),
        ("3", "Assessment"),
        ("4", "Review"),
        ("5", "Refinement"),
    ]

    for col, (number, name) in zip(
        cols,
        stages,
    ):

        with col:

            st.success(
                f"{number}. {name}"
            )


    # --------------------------------------------------------
    # RESULT TABS
    # --------------------------------------------------------

    tabs = st.tabs(
        [
            "🎯 Plan",
            "📚 Content",
            "📝 Assessment",
            "🔎 Review",
            "🎓 Final Pack",
        ]
    )


    with tabs[0]:

        st.markdown(
            state.plan
        )


    with tabs[1]:

        st.markdown(
            state.content
        )


    with tabs[2]:

        st.markdown(
            state.assessment
        )


    with tabs[3]:

        st.markdown(
            state.review
        )


    with tabs[4]:

        st.markdown(
            state.final_pack
        )

        st.download_button(
            "⬇️ Download Study Pack",
            data=state.final_pack,
            file_name="ai_study_pack.md",
            mime="text/markdown",
            use_container_width=True,
        )
