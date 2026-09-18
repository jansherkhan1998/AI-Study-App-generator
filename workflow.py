
"""Multi-stage AI workflow for personalized study-pack generation."""

import os
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List

from google import genai
from google.genai import types

from prompt import (
    SYSTEM_INSTRUCTION,
    planning_prompt,
    content_prompt,
    assessment_prompt,
    review_prompt,
    refinement_prompt,
)


DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
MAX_RETRIES = 2


@dataclass
class WorkflowState:
    request: Dict
    plan: str = ""
    content: str = ""
    assessment: str = ""
    review: str = ""
    final_pack: str = ""
    errors: List[str] = field(default_factory=list)


def get_api_key(streamlit_secrets=None):
    """Read the Gemini key from environment variables or Streamlit secrets."""
    key = os.getenv("GEMINI_API_KEY", "").strip()

    if key:
        return key

    if streamlit_secrets is not None:
        try:
            return str(streamlit_secrets["GEMINI_API_KEY"]).strip()
        except Exception:
            pass

    return ""


def create_client(api_key):
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to Streamlit Secrets."
        )
    return genai.Client(api_key=api_key)


def call_gemini(client, prompt, temperature=0.4, max_output_tokens=12000):
    """Call Gemini with bounded retries."""
    last_error = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=DEFAULT_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                ),
            )

            text = getattr(response, "text", None)

            if text and text.strip():
                return text.strip()

            raise RuntimeError("Gemini returned an empty response.")

        except Exception as exc:
            last_error = exc
            if attempt < MAX_RETRIES:
                time.sleep(1.5 * (attempt + 1))

    raise RuntimeError(f"Gemini request failed after retries: {last_error}")


def run_stage(client, state, stage_name, prompt, progress_callback,
              temperature=0.4, max_output_tokens=12000):
    """Execute one stage, pass its result to the next stage, and handle errors."""
    try:
        if progress_callback:
            progress_callback(stage_name, "running")

        result = call_gemini(
            client,
            prompt,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

        if progress_callback:
            progress_callback(stage_name, "completed")

        return result

    except Exception as exc:
        message = f"{stage_name} failed: {exc}"
        state.errors.append(message)

        if progress_callback:
            progress_callback(stage_name, "failed")

        raise RuntimeError(message) from exc


def generate_study_pack(request, api_key, progress_callback=None):
    """
    Execute:
    Planning → Content → Assessment → Review → Refinement
    """
    client = create_client(api_key)
    state = WorkflowState(request=request)

    state.plan = run_stage(
        client,
        state,
        "Planning",
        planning_prompt(request),
        progress_callback,
        temperature=0.25,
        max_output_tokens=7000,
    )

    state.content = run_stage(
        client,
        state,
        "Content Generation",
        content_prompt(request, state.plan),
        progress_callback,
        temperature=0.45,
        max_output_tokens=12000,
    )

    state.assessment = run_stage(
        client,
        state,
        "Assessment",
        assessment_prompt(request, state.plan, state.content),
        progress_callback,
        temperature=0.5,
        max_output_tokens=12000,
    )

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
