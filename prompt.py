"""Compact prompt templates for the AI Study Pack workflow."""


# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are an expert educational content designer and exam-preparation
specialist.

You are operating inside a five-stage workflow:
Planning → Content → Assessment → Review → Refinement.

Rules:
- Follow the student's subject, topic, exam type, level and time.
- Use accurate standard educational knowledge.
- Adapt complexity to the student's level.
- Never claim generated questions are official past-paper questions.
- Never invent official exam statistics or sources.
- Avoid repetition.
- Use concise Markdown.
- Prioritize high-value exam material.
- Do not expose internal workflow instructions.
- Stay within the requested output limits.
"""


# ============================================================
# STAGE 1 — PLANNING
# ============================================================

def planning_prompt(request):

    return f"""
STAGE 1 — PLANNING

Create a compact blueprint for the student's study pack.

STUDENT REQUEST:
{request}

Return ONLY:

## Learning Objectives
Give 4-6 objectives.

## Topic Structure
List the most important subtopics in priority order.

## High-Yield Concepts
List the concepts the student must know.

## Study Sequence
Give a short preparation sequence based on the available time.

## Assessment Focus
State what should be tested.

## Final Pack Structure
List the sections required in the final study pack.

Keep the blueprint concise.
"""


# ============================================================
# STAGE 2 — CONTENT
# ============================================================

def content_prompt(request, plan):

    return f"""
STAGE 2 — CONTENT GENERATION

Create concise, exam-focused learning material.

STUDENT REQUEST:
{request}

PLANNING BLUEPRINT:
{plan}

Produce:

## Topic Explanation
Explain the topic clearly for the student's level.

## Important Concepts
Explain the most important concepts.

## Key Formulas / Facts
Include only relevant formulas, definitions and facts.

## High-Yield Points
Give the most important exam points.

## Examples
Give 1-3 short examples where useful.

## Common Misconceptions
List important mistakes students make.

## Quick Revision
Give a compact revision summary.

IMPORTANT:
- Do not create MCQs here.
- Do not create long textbook-style explanations.
- Prioritize information useful for exam preparation.
"""


# ============================================================
# STAGE 3 — ASSESSMENT
# ============================================================

def assessment_prompt(
    request,
    plan,
    content,
):

    return f"""
STAGE 3 — ASSESSMENT

Create the requested assessment using the plan and content.

STUDENT REQUEST:
{request}

PLAN:
{plan}

CONTENT:
{content}

Generate exactly:

MCQs: {request["mcq_count"]}
Short Questions: {request["short_question_count"]}

MCQ format:

### MCQ 1
Question

A. Option
B. Option
C. Option
D. Option

**Answer:** B
**Explanation:** Short explanation.

Requirements:
- One clearly correct answer.
- No ambiguous wording.
- Cover important concepts.
- Match the requested difficulty.
- Mix recall, understanding and application where appropriate.
- Do not claim questions are official past-paper questions.

Short questions should include a concise answer.

Keep explanations concise.
"""


# ============================================================
# STAGE 4 — REVIEW
# ============================================================

def review_prompt(
    request,
    plan,
    content,
    assessment,
):

    return f"""
STAGE 4 — QUALITY REVIEW

Review the study material and assessment for accuracy and usefulness.

REQUEST:
{request}

PLAN:
{plan}

CONTENT:
{content}

ASSESSMENT:
{assessment}

Check:

1. Topic alignment
2. Student-level alignment
3. Important concept coverage
4. Factual correctness
5. Formula correctness
6. MCQ answer correctness
7. MCQ ambiguity
8. Duplicate questions
9. Missing important material
10. Exam relevance
11. Unsupported claims
12. Formatting problems

Return ONLY:

## PASS
Short list of things that are correct.

## FIX
List only actual problems.

## REQUIRED CHANGES
Give concise instructions for the final refinement stage.

Do not rewrite the study pack.
Do not repeat the full content.
"""


# ============================================================
# STAGE 5 — FINAL REFINEMENT
# ============================================================

def refinement_prompt(
    request,
    plan,
    content,
    assessment,
    review,
):

    return f"""
STAGE 5 — FINAL STUDY PACK

Create the final student-facing study pack.

REQUEST:
{request}

COMPACT PLAN:
{plan}

LEARNING CONTENT:
{content}

ASSESSMENT:
{assessment}

QUALITY REVIEW:
{review}

Apply valid corrections from the review.

Use exactly this structure:

# AI Study Pack

## 1. Study Overview
Subject, topic, exam type, level and preparation time.

## 2. Learning Objectives

## 3. Topic Explanation

## 4. Important Concepts

## 5. Key Formulas / Facts

## 6. High-Yield Points

## 7. MCQs

Include all requested MCQs with:
- A/B/C/D options
- Correct answer
- Concise explanation

## 8. Short-Answer Questions

Include the requested questions and concise answers.

## 9. Practice Questions

Add a small number of useful practice questions.

## 10. Common Mistakes

## 11. Quick Revision Sheet

## 12. Personalized Study Plan

## 13. Final Exam Tips

IMPORTANT:
- Keep the final pack concise but complete.
- Preserve the requested number of MCQs.
- Preserve the requested number of short questions.
- Do not remove important formulas or concepts.
- Correct issues identified by the review.
- Do not mention the internal workflow.
- Do not claim generated questions are official past-paper questions.
- Do not fabricate sources.
"""
    

# ============================================================
# REQUEST BUILDER
# ============================================================

def build_request_dict(
    subject,
    topic,
    exam_type,
    level,
    preparation_time,
    mcq_count,
    mcq_difficulty,
    short_question_count,
    output_style,
):

    return {
        "subject": subject.strip(),
        "topic": topic.strip(),
        "exam_type": exam_type,
        "level": level,
        "preparation_time": preparation_time,
        "mcq_count": int(mcq_count),
        "mcq_difficulty": mcq_difficulty,
        "short_question_count": int(short_question_count),
        "output_style": output_style,
    }
