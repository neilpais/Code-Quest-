from dotenv import load_dotenv
import os
import json
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Example syllabus (you can expand this later)
SYLLABUS = {
    "week_1": ["Introduction to the course"],
    "week 2": ["Variables and Assignment statemens"],
    "week 3": ["Branching"],
    "week 4": ["Loops"],
    "week 5": ["User-defined Functions"],
    "week 6": ["User-defined Functions (continued)"],
    "week 7": ["One and two dimensional Arrays"],
    "week 8": ["Input / Output, Files (Sequential)"],
    "week 9": ["Structures"],
    "week 10":["Recursion"],
    "week 11":["Pointers"],
    "week 12":["Catchup and Review"]
}


def analyze_code(code, assignment="A1"):
    current_assignment = {
        "assignment": assignment,
        "allowed_concepts": ["Use basic C statements", "expressions", "and operators to solve a given problem", "Apply decision-making and looping constructs to control program behavior", "Read and follow problem requirements carefully when designing a solution", "Develop step-by-step problem-solving skills to translate ideas into working C code", "Produce a clear, correct, and well-formatted C program that compiles and runs properly" ],
        "expected_concepts": ["branching"]
    }

    prompt = f"""
You are an expert programming tutor.

----------------------------------------
SYLLABUS:
{json.dumps(SYLLABUS, indent=2)}

CURRENT ASSIGNMENT:
{json.dumps(current_assignment, indent=2)}

STUDENT CODE:
{code}
----------------------------------------

STEP 1: Identify programming concepts used in the code.

STEP 2: Compare with allowed concepts:
- Detect concepts used BEFORE they are taught (ahead_of_syllabus)
- Detect missing expected concepts

STEP 3: Pedagogical reasoning:
- If student used advanced concepts → ask WHY
- If student missed required concepts → ask HOW to fix
- If student used correct concepts → reinforce understanding

----------------------------------------

STRICT REQUIREMENTS:

- Generate EXACTLY 6 questions:
  → 6 "general_programming" (multiple choice)

- DO NOT use any other types (NO reflection, concept_gap, etc.)

----------------------------------------

RULES FOR MULTIPLE CHOICE:

- Provide EXACTLY 4 options
- Only ONE correct answer
- Include "correct_answer" as "A", "B", "C", or "D"
- Questions MUST be based on the student's code

----------------------------------------

STRICT INSTRUCTIONS:

- Questions MUST relate to the student's code
- MUST align with assignment concepts
- DO NOT introduce unrelated topics
- DO NOT generate generic questions

----------------------------------------

RETURN ONLY VALID JSON IN THIS FORMAT:

{{
  "concept_analysis": {{
    "concepts_used": [],
    "allowed_concepts": [],
    "ahead_of_syllabus": [],
    "missing_concepts": [],
    "notes": ""
  }},
  "questions": [
    {{
      "type": "general_programming",
      "question": "...",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct_answer": "A"
    }}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.2
        )

        content = response.choices[0].message.content
        return json.loads(content)

    except Exception as e:
        return {
            "error": "Failed to analyze code",
            "details": str(e)
        }

