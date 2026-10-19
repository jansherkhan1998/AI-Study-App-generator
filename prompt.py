"""
Prompt templates and dictionary builder for AI Study Pack Generator.
"""


def build_request_dict(
    subject: str,
    topic: str,
    exam_type: str,
    level: str,
    preparation_time: str,
    mcq_count: int,
    mcq_difficulty: str,
    short_question_count: int,
    output_style: str,
) -> dict:
    """Build a clean request dictionary from user input form fields."""
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


SYSTEM_PROMPT = """
You are an expert academic curriculum designer, study-skills coach,
and exam-preparation specialist.

Your task is to generate a comprehensive, highly structured, and pedagogically
sound study pack tailored specifically to the user's subject, topic, target exam,
preparation timeframe, and academic level.

Follow this 5-stage creation method internally:
1. Planning: Structure a strategic study timeline based on the preparation time.
2. Content Generation: Explain core principles, key definitions, formulas, and common pitfalls.
3. Assessment: Create practice questions matching the target exam's style and difficulty.
4. Review: Provide full answer keys, detailed step-by-step explanations, and scoring criteria.
5. Refinement: Ensure clarity, accuracy, formatting, and high practical utility.

Output guidelines:
- Present clear markdown formatting.
- Include structured sections for Study Strategy, Core Concepts, MCQ Practice, Short Questions (if requested), and Explanations.
- Tailor the tone and depth to the student's stated level (Beginner, Intermediate, Advanced).
"""


def build_user_prompt(request: dict) -> str:
    """Construct the final prompt sent to Groq Llama-3.3-70b."""
    return f"""
Generate a complete Study Pack using the details below:

- Subject: {request['subject']}
- Topic / Chapter: {request['topic']}
- Target Exam: {request['exam_type']}
- Student Level: {request['level']}
- Preparation Time Available: {request['preparation_time']}
- Number of MCQs Needed: {request['mcq_count']}
- MCQ Difficulty: {request['mcq_difficulty']}
- Number of Short Questions Needed: {request['short_question_count']}
- Desired Output Style: {request['output_style']}

Please ensure:
1. A clear day-by-day or stage-by-stage study timeline.
2. Conceptual summaries with clear headings.
3. Exactly {request['mcq_count']} multiple-choice questions with options (A, B, C, D).
4. Exactly {request['short_question_count']} short conceptual questions.
5. A comprehensive Answer Key section containing explanations for all answers.
"""


def build_roadmap_request(subject, topic, level, prep_time, exam_type, output_style):
    return {
        "subject": subject,
        "topic": topic,
        "level": level,
        "prep_time": prep_time,
        "exam_type": exam_type,
        "output_style": output_style,
    }


def get_direct_mcq_prompt(subject, topic, count, difficulty):
    return f"""
    You are an expert exam designer. Generate {count} Multiple-Choice Questions (MCQs) on the subject '{subject}', topic '{topic}'.
    Difficulty: {difficulty}.

    Return ONLY a valid JSON array of objects with keys:
    - "id": integer
    - "question": string
    - "options": list of 4 strings
    - "answer": string
    - "explanation": string
    Do NOT wrap in markdown syntax. Return raw JSON.
    """
