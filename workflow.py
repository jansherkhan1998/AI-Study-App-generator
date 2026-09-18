"""Multi-stage Groq AI workflow for personalized study-pack generation."""

import os
import time
from dataclasses import dataclass, field
from typing import Dict, List

from groq import Groq

from prompt import (
    SYSTEM_INSTRUCTION,
    planning_prompt,
    content_prompt,
    assessment_prompt,
    review_prompt,
    refinement_prompt,
)


# ============================================================
# GROQ CONFIGURATION
# ============================================================

DEFAULT_MODEL = "openai/gpt-oss-120b"
MAX_RETRIES = 2


# ============================================================
# WORKFLOW STATE
# ============================================================

@dataclass
class WorkflowState:
    request: Dict
    plan: str = ""
    content: str = ""
    assessment: str = ""
    review: str = ""
    final_pack: str = ""
    errors: List[str] = field(default_factory=list)


# ============================================================
# API KEY
# ============================================================

def get_api_key(streamlit_secrets=None):
    """Read the Groq API key from environment variables or Streamlit Secrets."""

    key = os.getenv("GROQ_API_KEY", "").strip()

    if key:
        return key

    if streamlit_secrets is not None:
        try:
            return str(
                streamlit_secrets["GROQ_API_KEY"]
            ).strip()
        except Exception:
            pass

    return ""


# ============================================================
# GROQ CLIENT
# ============================================================

def create_client(api_key):
    """Create the Groq client."""

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to Streamlit Secrets."
        )

    return Groq(api_key=api_key)


# ============================================================
# GROQ API CALL
# ============================================================

def call_groq(
    client,
    prompt,
    temperature=0.4,
    max_output_tokens=12000,
):
    """
    Send a request to Groq using OpenAI GPT-OSS 120B.
    Includes bounded retries for temporary failures.
    """

    last_error = None

    for attempt in range(MAX_RETRIES + 1):

        try:

            response = client.chat.completions.create(
                model=DEFAULT_MODEL,

                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_INSTRUCTION,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],

                temperature=temperature,

                max_completion_tokens=max_output_tokens,

                reasoning_effort="medium",

                include_reasoning=False,
            )

            message = response.choices[0].message

            text = getattr(
                message,
                "content",
                None,
            )

            if text and text.strip():
                return text.strip()

            raise RuntimeError(
                "Groq returned an empty response."
            )

        except Exception as exc:

            last_error = exc

            if attempt < MAX_RETRIES:
                time.sleep(
                    1.5 * (attempt + 1)
                )

    raise RuntimeError(
        f"Groq request failed after retries: {last_error}"
    )


# ============================================================
# WORKFLOW STAGE EXECUTOR
# ============================================================

def run_stage(
    client,
    state,
    stage_name,
    prompt,
    progress_callback,
    temperature=0.4,
    max_output_tokens=12000,
):
    """Execute one workflow stage and handle errors."""

    try:

        if progress_callback:
            progress_callback(
                stage_name,
                "running",
            )

        result = call_groq(
            client,
            prompt,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

        if progress_callback:
            progress_callback(
                stage_name,
                "completed",
            )

        return result

    except Exception as exc:

        message = (
            f"{stage_name} failed: {exc}"
        )

        state.errors.append(message)

        if progress_callback:
            progress_callback(
                stage_name,
                "failed",
            )

        raise RuntimeError(
            message
        ) from exc


# ============================================================
# COMPLETE STUDY PACK WORKFLOW
# ============================================================

def generate_study_pack(
    request,
    api_key,
    progress_callback=None,
):
    """
    Execute the complete sequential AI workflow:

    Planning
        ↓
    Content Generation
        ↓
    Assessment
        ↓
    Review
        ↓
    Refinement
    """

    client = create_client(api_key)

    state = WorkflowState(
        request=request
    )

    # --------------------------------------------------------
    # STAGE 1 — PLANNING
    # --------------------------------------------------------

    state.plan = run_stage(
        client,
        state,
        "Planning",
        planning_prompt(request),
        progress_callback,
        temperature=0.25,
        max_output_tokens=7000,
    )

    # --------------------------------------------------------
    # STAGE 2 — CONTENT GENERATION
    # --------------------------------------------------------

    state.content = run_stage(
        client,
        state,
        "Content Generation",
        content_prompt(
            request,
            state.plan,
        ),
        progress_callback,
        temperature=0.45,
        max_output_tokens=12000,
    )

    # --------------------------------------------------------
    # STAGE 3 — ASSESSMENT
    # --------------------------------------------------------

    state.assessment = run_stage(
        client,
        state,
        "Assessment",
        assessment_prompt(
            request,
            state.plan,
            state.content,
        ),
        progress_callback,
        temperature=0.5,
        max_output_tokens=12000,
    )

    # --------------------------------------------------------
    # STAGE 4 — REVIEW / QUALITY CONTROL
    # --------------------------------------------------------

    state.review = run_stage(
        client,
        state,
        "Review",
        review_prompt(
            request,
            state.plan,
            state.content,
            state.assessment,
        ),
        progress_callback,
        temperature=0.2,
        max_output_tokens=9000,
    )

    # --------------------------------------------------------
    # STAGE 5 — REFINEMENT
    # --------------------------------------------------------

    state.final_pack = run_stage(
        client,
        state,
        "Refinement",
        refinement_prompt(
            request,
            state.plan,
            state.content,
            state.assessment,
            state.review,
        ),
        progress_callback,
        temperature=0.35,
        max_output_tokens=15000,
    )

    return state
