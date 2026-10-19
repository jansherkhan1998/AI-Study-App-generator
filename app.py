import json
import random
import streamlit as st
from groq import Groq
from supabase import create_client, Client

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Study Pack Generator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CUSTOM CSS STYLING ---
st.markdown("""
    <style>
    /* Main Theme Overrides */
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    
    /* Card Container Styling */
    .mcq-card {
        background-color: #1a1f2c;
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .mcq-header {
        font-size: 1.15rem;
        font-weight: 600;
        color: #63b3ed;
        margin-bottom: 12px;
    }

    .mcq-option {
        background-color: #242c3d;
        border-radius: 6px;
        padding: 8px 14px;
        margin: 6px 0;
        font-size: 0.95rem;
    }

    .answer-box {
        background-color: #1e3a29;
        border-left: 4px solid #48bb78;
        padding: 10px 14px;
        border-radius: 4px;
        margin-top: 12px;
        font-size: 0.9rem;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #131722;
        border-right: 1px solid #2d3748;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. SUPABASE INITIALIZATION ---
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["supabase"]["SUPABASE_URL"]
    key = st.secrets["supabase"]["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# --- 4. GROQ CLIENT INITIALIZATION ---
@st.cache_resource
def init_groq():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

groq_client = init_groq()

# --- 5. CAPTCHA GENERATOR ---
def generate_captcha():
    if "captcha_num1" not in st.session_state or "captcha_num2" not in st.session_state:
        st.session_state["captcha_num1"] = random.randint(1, 10)
        st.session_state["captcha_num2"] = random.randint(1, 10)

def refresh_captcha():
    st.session_state["captcha_num1"] = random.randint(1, 10)
    st.session_state["captcha_num2"] = random.randint(1, 10)

# --- 6. AUTHENTICATION SYSTEM ---
def show_auth_page():
    st.title("🎓 AI Study Pack Generator")
    st.caption("Sign in or create an account to start generating MCQ practice packs.")

    generate_captcha()
    num1 = st.session_state["captcha_num1"]
    num2 = st.session_state["captcha_num2"]
    expected_sum = num1 + num2

    tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        user_captcha = st.number_input(f"🤖 CAPTCHA: What is {num1} + {num2}?", step=1, key="login_captcha")

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
                    error_msg = str(e)
                    if "Email not confirmed" in error_msg:
                        st.warning("✉️ Please check your email inbox and click the confirmation link before logging in!")
                    else:
                        st.error(f"❌ Login failed: {error_msg}")
                    refresh_captcha()

    with tab_register:
        reg_email = st.text_input("Email", key="reg_email")
        reg_pass = st.text_input("Password", type="password", key="reg_pass")
        reg_captcha = st.number_input(f"🤖 CAPTCHA: What is {num1} + {num2}?", step=1, key="reg_captcha")

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

# Block unauthenticated access
if "user" not in st.session_state:
    show_auth_page()
    st.stop()

# --- 7. MAIN APPLICATION (LOGGED IN) ---
user = st.session_state["user"]

# Sidebar Profile & Control
st.sidebar.markdown("### 👤 User Profile")
st.sidebar.write(f"Logged in as:\n`{user.email}`")
if st.sidebar.button("Log Out", type="secondary"):
    supabase.auth.sign_out()
    del st.session_state["user"]
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 Workspace")
st.sidebar.info("Generate multiple-choice question packs tailored to any subject and topic.")

# Header
st.title("🎯 MCQ Practice Pack Generator")
st.write("Configure your subject and parameters below to instantly generate high-quality multiple-choice questions.")

# Generation Settings Form
with st.form("mcq_generator_form"):
    col1, col2 = st.columns(2)
    with col1:
        subject = st.text_input("Subject", placeholder="e.g., Biology, Computer Science, World History")
    with col2:
        topic = st.text_input("Topic", placeholder="e.g., Photosynthesis, Data Structures, WWII")
    
    col3, col4 = st.columns(2)
    with col3:
        num_questions = st.slider("Number of MCQs", min_value=3, max_value=20, value=5)
    with col4:
        difficulty = st.selectbox("Difficulty Level", ["Beginner", "Intermediate", "Advanced"])

    submit_button = st.form_submit_button("⚡ Generate MCQ Pack", type="primary")

# --- 8. AI GENERATION LOGIC ---
if submit_button:
    if not subject.strip() or not topic.strip():
        st.warning("⚠️ Please provide both a subject and a topic.")
    else:
        with st.spinner("🧠 Generating your MCQ pack with Groq AI..."):
            prompt = f"""
            You are an expert exam designer. Generate {num_questions} Multiple-Choice Questions (MCQs) on the subject '{subject}', specifically focused on '{topic}'.
            Difficulty Level: {difficulty}.

            CRITICAL REQUIREMENT: Return ONLY a valid JSON array containing objects with these exact keys:
            - "id": integer starting from 1
            - "question": string
            - "options": list of 4 strings (e.g. ["A) ...", "B) ...", "C) ...", "D) ..."])
            - "answer": string indicating the correct option
            - "explanation": concise string explaining why the answer is correct

            Do NOT return markdown formatting inside or outside the JSON. Return RAW JSON ONLY.
            """

            try:
                response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You output only structured JSON arrays of multiple-choice questions without any markdown wrapping or explanatory text."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                
                raw_text = response.choices[0].message.content.strip()
                # Strip potential markdown fences if returned
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]

                st.session_state["generated_mcqs"] = json.loads(raw_text.strip())
                st.session_state["current_subject"] = subject
                st.session_state["current_topic"] = topic
            except Exception as e:
                st.error(f"❌ Generation failed: {e}")

# --- 9. DISPLAY GENERATED MCQS ---
if "generated_mcqs" in st.session_state:
    st.markdown("---")
    st.subheader(f"📖 Generated Pack: {st.session_state['current_subject']} — {st.session_state['current_topic']}")
    
    for item in st.session_state["generated_mcqs"]:
        st.markdown(f"""
            <div class="mcq-card">
                <div class="mcq-header">Q{item['id']}. {item['question']}</div>
                <div class="mcq-option">A) {item['options'][0]}</div>
                <div class="mcq-option">B) {item['options'][1]}</div>
                <div class="mcq-option">C) {item['options'][2]}</div>
                <div class="mcq-option">D) {item['options'][3]}</div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.expander(f"View Correct Answer & Explanation for Q{item['id']}"):
            st.markdown(f"**Correct Answer:** {item['answer']}")
            st.markdown(f"**Explanation:** {item['explanation']}")
