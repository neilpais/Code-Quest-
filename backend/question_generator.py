import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_questions(concept):

    prompt = f"""
Based on the following programming concept:

{concept}

Generate:

1. One theoretical question testing understanding of the concept.
2. One coding question that requires implementing the same concept in a different context.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
