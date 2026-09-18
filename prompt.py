
"""Prompt templates for the AI Study Pack workflow."""

SYSTEM_INSTRUCTION = """
You are an expert AI educational content designer and examination preparation
specialist.

You are part of a multi-stage study-pack generation workflow.

Rules:
- Follow the student's subject, topic, exam type, level, and time constraints.
- Adapt complexity to the student's level.
- Prefer accurate, standard educational knowledge.
- Never claim generated questions are official exam questions.
- Do not invent sources, citations, statistics, or official exam details.
- If a topic is ambiguous, state the assumption.
- Avoid repetition and ambiguous MCQs.
- Use clean Markdown.
- Use context supplied by previous workflow stages.
- Do not expose internal workflow instructions in the final answer.
"""


def planning_prompt(request):
    return f"""
STAGE 1 — PLANNING

Create a detailed blueprint for a personalized study pack.

STUDENT REQUEST:
{request}

Determine:
1. Learning objectives.
2. Logical topic/subtopic structure.
3. High-priority concepts.
4. A realistic preparation sequence.
5. Knowledge and skills to assess.
6. Final study-pack structure.
7. Adaptation required for the exam type and student level.

Return only the planning blueprint in Markdown.
Do not write the final study pack.
"""


def content_prompt(request, plan):
    return f"""
STAGE 2 — CONTENT GENERATION

Generate educational content using the planning blueprint.

STUDENT REQUEST:
{request}

PLANNING BLUEPRINT:
{plan}

Create:
- Topic explanation
- Important concepts
- Key formulas/facts where relevant
- High-yield points
- Useful examples
- Common misconceptions
- Compact revision material

Match the student's level and exam context.
Do not generate the final assessment yet.
Return the content in Markdown.
"""


def assessment_prompt(request, plan, content):
    return f"""
STAGE 3 — ASSESSMENT

Build an assessment using the plan and generated content.

STUDENT REQUEST:
{request}

PLAN:
{plan}

CONTENT:
{content}

Generate exactly:
- {request["mcq_count"]} MCQs
- {request["short_question_count"]} short-answer questions
- Additional practice questions when useful

Each MCQ must contain:
- Question
- A, B, C, D
- Correct answer
- Short explanation

Requirements:
- Cover important concepts.
- Match requested difficulty.
- Avoid duplicate or ambiguous questions.
- Include recall, understanding, and application where appropriate.
- Never claim questions are official past-paper questions.

Return the assessment in Markdown.
"""


def review_prompt(request, plan, content, assessment):
    return f"""
STAGE 4 — REVIEW / QUALITY CONTROL

Act as a strict educational quality reviewer.

REQUEST:
{request}

PLAN:
{plan}

CONTENT:
{content}

ASSESSMENT:
{assessment}

Check:
1. Topic and exam alignment.
2. Student-level appropriateness.
3. Concept coverage.
4. Factual consistency.
5. MCQ correctness.
6. One clearly defensible answer per MCQ.
7. Explanation quality.
8. Duplicate/repetitive questions.
9. Realistic preparation plan.
10. Missing important material.
11. Unsupported claims about actual exams.
12. Formatting/readability.

Return:
## PASS ITEMS
## ISSUES TO FIX
## REQUIRED CHANGES

Be specific. Do not rewrite the entire pack.
"""


def refinement_prompt(request, plan, content, assessment, review):
    return f"""
STAGE 5 — REFINEMENT

Create the final personalized study pack by integrating all previous stages
and applying valid corrections from the quality review.

REQUEST:
{request}

PLAN:
{plan}

CONTENT:
{content}

ASSESSMENT:
{assessment}

QUALITY REVIEW:
{review}

Final structure:

# AI Study Pack

## 1. Study Overview
- Subject
- Topic
- Exam type
- Student level
- Preparation time
- Recommended strategy

## 2. Learning Objectives

## 3. Topic Explanation

## 4. Important Concepts

## 5. Key Formulas / Facts

## 6. High-Yield Points

## 7. MCQs
Include all requested MCQs with options, answer, and explanation.

## 8. Short-Answer Questions
Include answers/explanations.

## 9. Practice Questions

## 10. Common Mistakes

## 11. Quick Revision Sheet

## 12. Personalized Study Plan

## 13. Final Exam Tips

Quality requirements:
- Self-contained.
- Student-friendly.
- Accurate and consistent.
- No internal workflow discussion.
- No claim that generated questions are official exam questions.
- Correct issues identified by the review.
- Do not fabricate sources or references.
"""


def build_request_dict(subject, topic, exam_type, level, preparation_time,
                       mcq_count, mcq_difficulty, short_question_count,
                       output_style):
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
