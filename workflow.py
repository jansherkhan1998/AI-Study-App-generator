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

# Your current Groq limit is 8,000 TPM.
# We deliberately stay below that limit.
SAFE_TOKEN_BUDGET = 7000

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
    """Read Groq API key from environment variables or Streamlit Secrets."""

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
# CONTEXT COMPRESSION
# ============================================================

def trim_text(text, max_chars):
    """
    Keep workflow context within a safe size.

    We use characters instead of tokenizers so the application
    does not require another dependency.
    """

    if not text:
        return ""

    text = str(text).strip()

    if len(text) <= max_chars:
        return text

    return (
        text[:max_chars]
        + "\n\n[Earlier content truncated to preserve API limits.]"
    )


def estimate_tokens(text):
    """
    Conservative token estimate.

    Approximately 4 characters per token is used.
    """

    if not text:
        return 0

    return max(1, len(text) // 4)


def build_safe_prompt(prompt, max_output_tokens):
    """
    Ensure the request stays comfortably below the
    organization's 8K TPM limit.

    The prompt itself is already compact because previous
    workflow outputs are trimmed before being inserted.
    """

    estimated_input = estimate_tokens(prompt)

    requested_total = (
        estimated_input + max_output_tokens
    )

    if requested_total <= SAFE_TOKEN_BUDGET:
        return prompt, max_output_tokens

    available_output = (
        SAFE_TOKEN_BUDGET - estimated_input
    )

    # Never request an unusably tiny completion.
    available_output = max(
        800,
        available_output,
    )

    return prompt, available_output


# ============================================================
# GROQ CALL
# ============================================================

def call_groq(
    client,
    prompt,
    temperature=0.4,
    max_output_tokens=2000,
):
    """
    Call Groq while keeping the combined request
    safely below the current TPM limit.
    """

    safe_prompt, safe_output_tokens = build_safe_prompt(
        prompt,
        max_output_tokens,
    )

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
                        "content": safe_prompt,
                    },
                ],

                temperature=temperature,

                max_completion_tokens=safe_output_tokens,

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

            error_text = str(exc).lower()

            # A request-size / TPM error will not be fixed
            # by retrying the exact same request.
            if (
                "rate_limit_exceeded" in error_text
                or "request too large" in error_text
                or "413" in error_text
            ):
                raise RuntimeError(
                    "Groq rejected the request because it exceeded "
                    "the available token limit. The workflow context "
                    "should be reduced."
                ) from exc

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
    max_output_tokens=2000,
):
    """Execute one workflow stage."""

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
# COMPLETE WORKFLOW
# ============================================================

def generate_study_pack(
    request,
    api_key,
    progress_callback=None,
):
    """
    Execute:

    1. Planning
    2. Content Generation
    3. Assessment
    4. Review
    5. Refinement

    Previous outputs are deliberately compressed before
    being passed to later stages.
    """

    client = create_client(api_key)

    state = WorkflowState(
        request=request
    )


    # ========================================================
    # STAGE 1 — PLANNING
    # ========================================================

    state.plan = run_stage(
        client,
        state,
        "Planning",
        planning_prompt(request),
        progress_callback,
        temperature=0.25,
        max_output_tokens=1800,
    )


    # ========================================================
    # STAGE 2 — CONTENT GENERATION
    # ========================================================

    compact_plan = trim_text(
        state.plan,
        5000,
    )

    state.content = run_stage(
        client,
        state,
        "Content Generation",
        content_prompt(
            request,
            compact_plan,
        ),
        progress_callback,
        temperature=0.4,
        max_output_tokens=2400,
    )


    # ========================================================
    # STAGE 3 — ASSESSMENT
    # ========================================================

    compact_plan = trim_text(
        state.plan,
        3000,
    )

    compact_content = trim_text(
        state.content,
        7000,
    )

    state.assessment = run_stage(
        client,
        state,
        "Assessment",
        assessment_prompt(
            request,
            compact_plan,
            compact_content,
        ),
        progress_callback,
        temperature=0.45,
        max_output_tokens=2800,
    )


    # ========================================================
    # STAGE 4 — REVIEW
    # ========================================================

    compact_plan = trim_text(
        state.plan,
        2000,
    )

    compact_content = trim_text(
        state.content,
        5000,
    )

    compact_assessment = trim_text(
        state.assessment,
        7000,
    )

    state.review = run_stage(
        client,
        state,
        "Review",
        review_prompt(
            request,
            compact_plan,
            compact_content,
            compact_assessment,
        ),
        progress_callback,
        temperature=0.2,
        max_output_tokens=1600,
    )


    # ========================================================
    # STAGE 5 — FINAL REFINEMENT
    # ========================================================

    compact_plan = trim_text(
        state.plan,
        1500,
    )

    compact_content = trim_text(
        state.content,
        4000,
    )

    compact_assessment = trim_text(
        state.assessment,
        5500,
    )

    compact_review = trim_text(
        state.review,
        3500,
    )

    state.final_pack = run_stage(
        client,
        state,
        "Refinement",
        refinement_prompt(
            request,
            compact_plan,
            compact_content,
            compact_assessment,
            compact_review,
        ),
        progress_callback,
        temperature=0.3,
        max_output_tokens=2800,
    )


    return state
