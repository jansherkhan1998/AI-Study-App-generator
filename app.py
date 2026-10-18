import random
import streamlit as st
from supabase import create_client, Client

# --- 1. SUPABASE INITIALIZATION ---
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["supabase"]["SUPABASE_URL"]
    key = st.secrets["supabase"]["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# --- 2. CAPTCHA GENERATOR ---
def generate_captcha():
    if "captcha_num1" not in st.session_state or "captcha_num2" not in st.session_state:
        st.session_state["captcha_num1"] = random.randint(1, 10)
        st.session_state["captcha_num2"] = random.randint(1, 10)

def refresh_captcha():
    st.session_state["captcha_num1"] = random.randint(1, 10)
    st.session_state["captcha_num2"] = random.randint(1, 10)

# --- 3. AUTHENTICATION SYSTEM WITH CAPTCHA ---
def show_auth_page():
    st.set_page_config(page_title="Login | AI Study Pack Generator", page_icon="🔒")
    st.title("🎓 AI Study Pack Generator")
    st.subheader("Please sign in or register to continue")

    generate_captcha()
    num1 = st.session_state["captcha_num1"]
    num2 = st.session_state["captcha_num2"]
    expected_sum = num1 + num2

    tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        
        # CAPTCHA verification field
        user_captcha = st.number_input(f"🤖 CAPTCHA Verification: What is {num1} + {num2}?", step=1, key="login_captcha")

        if st.button("Log In", type="primary"):
            if user_captcha != expected_sum:
                st.error("❌ Incorrect CAPTCHA. Please try again.")
                refresh_captcha()
            else:
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state["user"] = res.user
                    st.success("Logged in successfully!")
                    refresh_captcha()
                    st.rerun()
                except Exception as e:
                    # =========================================================================
                    # REPLACED AREA START: Customized error handling for unconfirmed emails
                    # =========================================================================
                    error_msg = str(e)
                    if "Email not confirmed" in error_msg:
                        st.warning("✉️ Please check your email inbox and click the confirmation link before logging in!")
                    else:
                        st.error(f"❌ Login failed: {error_msg}")
                    # =========================================================================
                    # REPLACED AREA END
                    # =========================================================================
                    refresh_captcha()

    with tab_register:
        reg_email = st.text_input("Email", key="reg_email")
        reg_pass = st.text_input("Password", type="password", key="reg_pass")
        
        # CAPTCHA verification field
        reg_captcha = st.number_input(f"🤖 CAPTCHA Verification: What is {num1} + {num2}?", step=1, key="reg_captcha")

        if st.button("Sign Up"):
            if reg_captcha != expected_sum:
                st.error("❌ Incorrect CAPTCHA. Please try again.")
                refresh_captcha()
            else:
                try:
                    res = supabase.auth.sign_up({"email": reg_email, "password": reg_pass})
                    st.success("Account created! You can now log in.")
                    refresh_captcha()
                except Exception as e:
                    st.error(f"Registration failed: {e}")
                    refresh_captcha()

# Block unauthenticated users
if "user" not in st.session_state:
    show_auth_page()
    st.stop()

# --- 4. MAIN APPLICATION (LOGGED IN USERS ONLY) ---
st.set_page_config(page_title="AI Study Pack Generator", page_icon="📚", layout="wide")

user = st.session_state["user"]
st.sidebar.write(f"Logged in as: **{user.email}**")
if st.sidebar.button("Log Out"):
    supabase.auth.sign_out()
    del st.session_state["user"]
    st.rerun()

st.title("📚 AI Study Pack Generator")
st.write("Welcome to your workspace! Your progress will automatically be saved.")

# --- YOUR EXISTING APP LOGIC HERE ---
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
            "NUMS",
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
