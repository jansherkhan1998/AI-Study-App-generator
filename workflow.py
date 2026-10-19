"""
Five-stage Groq AI workflow executor and API helper.
"""

import json
import os
from dataclasses import dataclass
from typing import Callable, Optional

from groq import Groq
import streamlit as st

from prompt import SYSTEM_PROMPT, build_user_prompt


MODEL_NAME = "llama-3.3-70b-versatile"


@dataclass
class WorkflowResult:
    plan: str
    content: str
    assessment: str
    review: str
    final_pack: str


def get_groq_api_key() -> str:
    """Read GROQ_API_KEY from environment variables or Streamlit Secrets."""
    key = os.getenv("GROQ_API_KEY", "").strip()
    if key:
        return key

    try:
        return str(st.secrets["GROQ_API_KEY"]).strip()
    except Exception:
        return ""


def call_groq_stage(
    client: Groq,
    system_prompt: str,
    user_prompt: str,
) -> str:
    """Execute a single call to Groq API."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )
    return str(response.choices[0].message.content)


def generate_study_pack(
    request: dict,
    api_key: str,
    progress_callback: Optional[Callable[[str, str], None]] = None,
) -> WorkflowResult:
    """
    Runs a 5-stage sequential AI generation pipeline using Groq.
    """
    client = Groq(api_key=api_key)
    base_user_prompt = build_user_prompt(request)

    # 1. PLANNING
    if progress_callback:
        progress_callback("Planning", "running")

    plan_prompt = (
        f"{base_user_prompt}\n\n"
        "STAGE 1: PLANNING\n"
        "Focus ONLY on constructing a strategic study timeline, "
        "time management strategy, and day-by-day study roadmap."
    )
    plan_output = call_groq_stage(client, SYSTEM_PROMPT, plan_prompt)

    if progress_callback:
        progress_callback("Planning", "completed")

    # 2. CONTENT GENERATION
    if progress_callback:
        progress_callback("Content Generation", "running")

    content_prompt = (
        f"{base_user_prompt}\n\n"
        f"PLANNING CONTEXT:\n{plan_output}\n\n"
        "STAGE 2: CONTENT GENERATION\n"
        "Focus ONLY on comprehensive core concept explanations, key definitions, "
        "formulas, and critical pitfalls."
    )
    content_output = call_groq_stage(client, SYSTEM_PROMPT, content_prompt)

    if progress_callback:
        progress_callback("Content Generation", "completed")

    # 3. ASSESSMENT
    if progress_callback:
        progress_callback("Assessment", "running")

    assessment_prompt = (
        f"{base_user_prompt}\n\n"
        f"CONTENT CONTEXT:\n{content_output}\n\n"
        "STAGE 3: ASSESSMENT\n"
        f"Focus ONLY on generating exactly {request['mcq_count']} MCQs "
        f"and {request['short_question_count']} short conceptual questions. "
        "Do NOT include answer keys or explanations in this stage."
    )
    assessment_output = call_groq_stage(client, SYSTEM_PROMPT, assessment_prompt)

    if progress_callback:
        progress_callback("Assessment", "completed")

    # 4. REVIEW
    if progress_callback:
        progress_callback("Review", "running")

    review_prompt = (
        f"{base_user_prompt}\n\n"
        f"ASSESSMENT CONTEXT:\n{assessment_output}\n\n"
        "STAGE 4: REVIEW\n"
        "Focus ONLY on detailed answer keys, step-by-step solutions, "
        "and explanations for every MCQ and short question generated above."
    )
    review_output = call_groq_stage(client, SYSTEM_PROMPT, review_prompt)

    if progress_callback:
        progress_callback("Review", "completed")

    # 5. REFINEMENT
    if progress_callback:
        progress_callback("Refinement", "running")

    refinement_prompt = (
        "STAGE 5: REFINEMENT\n"
        "Merge and refine all previous outputs into one single, master "
        "Study Pack document. Ensure professional markdown layout.\n\n"
        f"--- PLAN ---\n{plan_output}\n\n"
        f"--- CONTENT ---\n{content_output}\n\n"
        f"--- ASSESSMENT ---\n{assessment_output}\n\n"
        f"--- REVIEW ---\n{review_output}"
    )
    final_pack_output = call_groq_stage(client, SYSTEM_PROMPT, refinement_prompt)

    if progress_callback:
        progress_callback("Refinement", "completed")

    return WorkflowResult(
        plan=plan_output,
        content=content_output,
        assessment=assessment_output,
        review=review_output,
        final_pack=final_pack_output,
    )


def call_groq_json(prompt: str, api_key: str) -> list:
    """Helper to execute Groq calls requiring structured JSON outputs."""
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You return valid raw JSON arrays only."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )

    raw_text = response.choices[0].message.content.strip()
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:]
    if raw_text.startswith("```"):
        raw_text = raw_text[3:]
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3]

    return json.loads(raw_text.strip())
